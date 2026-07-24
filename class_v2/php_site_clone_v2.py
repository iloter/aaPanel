# coding: utf-8
import json
import os
import re
import shlex
import shutil
import threading
import time

import public

try:
    import OpenSSL
except Exception:
    OpenSSL = None


class PHPSiteCloneService:
    status_file = '/tmp/php_site_clone.log'
    lock_file = '/tmp/php_site_clone.lock'

    def __init__(self, site_manager):
        self.site = site_manager

    @staticmethod
    def _to_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        value = str(value).strip().lower()
        if value == '':
            return default
        if value in ['1', 'true', 'yes', 'on']:
            return True
        if value in ['0', 'false', 'no', 'off']:
            return False
        return default

    @staticmethod
    def _normalize_domain(domain):
        domain = str(domain or '').strip()
        domain = re.sub(r'^https?://', '', domain, flags=re.I)
        return domain.split('/')[0].split(':')[0].strip().lower()

    @staticmethod
    def _replace_text(text, replacements):
        if not isinstance(text, str):
            return text
        for old, new in replacements:
            if old and new and old != new:
                text = text.replace(str(old), str(new))
        return text

    def _replace_obj(self, obj, replacements):
        if isinstance(obj, dict):
            return {self._replace_text(k, replacements): self._replace_obj(v, replacements) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._replace_obj(v, replacements) for v in obj]
        if isinstance(obj, str):
            return self._replace_text(obj, replacements)
        return obj

    @staticmethod
    def _result_msg(res):
        if isinstance(res, dict):
            msg = res.get('message', res.get('msg', res))
            if isinstance(msg, dict):
                return msg.get('result', str(msg))
            return str(msg)
        return str(res)

    @staticmethod
    def _default_db_name(domain):
        name = re.sub(r'[^A-Za-z0-9_]+', '_', domain).strip('_').lower()
        if not name:
            name = 'php_clone'
        if name[0].isdigit():
            name = 'db_' + name
        return name[:48]

    @staticmethod
    def _db_name_in_recycle_bin(db_name):
        try:
            if not os.path.isdir('/www/.Recycle_bin'):
                return False
            prefix = 'BTDB_{}_t_'.format(db_name)
            for item in os.listdir('/www/.Recycle_bin'):
                if item == db_name or item.startswith(prefix):
                    return True
        except Exception:
            pass
        return False

    def _ensure_available_db_name(self, db_name):
        base_name = public.ensure_unique_db_name(db_name)
        candidate = base_name
        index = 1
        while self._db_name_in_recycle_bin(candidate):
            suffix = '_{}'.format(index)
            candidate = '{}{}'.format(base_name[:64 - len(suffix)], suffix)
            candidate = public.ensure_unique_db_name(candidate)
            index += 1
        return candidate

    def _log(self, msg):
        public.print_log('[php_clone] {}'.format(msg))

    def _default_progress(self):
        steps = {
            'validate_source': 'Validate source site',
            'create_site': 'Create new PHP site',
            'copy_files': 'Copy website files',
            'switch_webservice': 'Switch web service',
            'clone_config': 'Clone website config',
            'clone_database': 'Clone database',
            'reload_service': 'Reload web service',
            'clone_ssl': 'Clone or apply SSL',
        }
        return {
            'status': 0,
            'success': False,
            'current': 'validate_source',
            'start_time': int(time.time()),
            'update_time': int(time.time()),
            'end_time': 0,
            'error': '',
            'warnings': [],
            'result': {},
            'steps': {
                key: {'status': 2, 'ps': 'Pending', 'error': '', 'title': title}
                for key, title in steps.items()
            },
        }

    def _write_progress(self, progress):
        progress['update_time'] = int(time.time())
        public.writeFile(self.status_file, json.dumps(progress, ensure_ascii=False))

    def _read_progress(self):
        if not os.path.exists(self.status_file):
            return {}
        return json.loads(public.readFile(self.status_file) or '{}')

    def _step(self, progress, name, status, ps=None, error=''):
        if name in progress.get('steps', {}):
            progress['current'] = name
            progress['steps'][name]['status'] = status
            if ps is not None:
                progress['steps'][name]['ps'] = ps
            progress['steps'][name]['error'] = error or ''
        self._write_progress(progress)

    def _write_worker_lock(self):
        with open(self.lock_file, 'w') as f:
            f.write(str(threading.get_ident()))
            f.flush()
            os.fsync(f.fileno())

    def _worker_alive(self):
        if not os.path.exists(self.lock_file):
            return False
        try:
            thread_id = int((public.readFile(self.lock_file) or '').strip())
        except Exception:
            return False
        return any(t.ident == thread_id for t in threading.enumerate() if t)

    def get_progress(self, args):
        if not os.path.exists(self.status_file):
            return public.success_v2({'status': 1})
        try:
            progress = self._read_progress()
        except Exception as e:
            return public.return_message(-1, 0, public.lang('Failed to read clone progress: {}', str(e)))

        if int(progress.get('status', 1)) == 0 and os.path.exists(self.lock_file):
            stale_seconds = int(time.time()) - int(progress.get('update_time', 0) or 0)
            if stale_seconds > 30 and not self._worker_alive():
                public.progress_release_lock(self.lock_file)
                progress['status'] = 1
                progress['success'] = False
                progress['end_time'] = int(time.time())
                progress['error'] = 'Clone task was interrupted.'
                self._write_progress(progress)

        return public.success_v2(progress)

    def start(self, args):
        from concurrent.futures import ThreadPoolExecutor
        from flask import Flask

        if not public.progress_acquire_lock(self.lock_file):
            return public.return_message(
                -1, 0, public.lang('Other PHP site clone task is running. Please wait for completion!')
            )

        try:
            clean_args = public.to_dict_obj(dict(args))
        except Exception:
            clean_args = args

        self._write_progress(self._default_progress())
        app = Flask(__name__)
        ThreadPoolExecutor(max_workers=1).submit(self._run, clean_args, app)
        public.set_module_logs('PHP', 'clone_php_site', 1)

        # progress = {}
        # site_id = 0
        # deadline = time.time() + 10
        # while time.time() < deadline:
        #     try:
        #         progress = self._read_progress()
        #     except Exception:
        #         progress = {}
        #     result = progress.get('result', {}) if isinstance(progress, dict) else {}
        #     try:
        #         site_id = int(result.get('site_id') or 0)
        #     except Exception:
        #         site_id = 0
        #     if site_id or int(progress.get('status', 0) or 0) == 1:
        #         break
        #     time.sleep(0.2)
        #
        # return public.return_message(0, 0, {
        #     'result': public.lang('Successful startup!'),
        #     'site_id': site_id,
        #     'task_status': int(progress.get('status', 0) or 0) if isinstance(progress, dict) else 0,
        #     'current': progress.get('current', 'validate_source') if isinstance(progress, dict) else 'validate_source',
        #     'error': progress.get('error', '') if isinstance(progress, dict) else '',
        # })

        return public.return_message(0, 0, public.lang('Successful startup!'))

    def _validate_target_path(self, source_path, target_path, clone_files):
        source_abs = os.path.abspath(source_path)
        target_abs = os.path.abspath(target_path)
        source_prefix = source_abs.rstrip(os.sep) + os.sep
        target_prefix = target_abs.rstrip(os.sep) + os.sep

        if source_abs == target_abs or target_abs.startswith(source_prefix) or source_abs.startswith(target_prefix):
            raise ValueError('The new website path cannot be the same as or nested with the source website path.')

        if clone_files and os.path.exists(target_abs):
            exists_items = [x for x in os.listdir(target_abs) if x != '.user.ini']
            if exists_items:
                raise ValueError('The new website path is not empty. Please use an empty directory.')

    def _copy_site_files(self, source_path, target_path):
        if not os.path.isdir(source_path):
            raise ValueError('Source website directory does not exist: {}'.format(source_path))
        if not os.path.isdir(target_path):
            os.makedirs(target_path, 0o755, exist_ok=True)

        for name in os.listdir(target_path):
            if name == '.user.ini':
                continue
            full_path = os.path.join(target_path, name)
            if os.path.isdir(full_path) and not os.path.islink(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
            else:
                try:
                    os.remove(full_path)
                except FileNotFoundError:
                    pass

        cmd = 'tar -cf - -C {} --exclude=.user.ini . | tar -xf - -C {}'.format(
            shlex.quote(source_path), shlex.quote(target_path)
        )
        public.ExecShell(cmd)
        public.ExecShell('chmod -R 755 {}'.format(shlex.quote(target_path)))
        public.ExecShell('chown -R www:www {}'.format(shlex.quote(target_path)))

    def _copy_text_file(self, src_file, dst_file, replacements):
        if not os.path.exists(src_file):
            return False
        os.makedirs(os.path.dirname(dst_file), 0o755, exist_ok=True)
        try:
            with open(src_file, 'rb') as f:
                body = f.read()
            try:
                text = body.decode('utf-8')
                text = self._replace_text(text, replacements)
                with open(dst_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            except UnicodeDecodeError:
                shutil.copy2(src_file, dst_file)
            try:
                shutil.copystat(src_file, dst_file)
            except Exception:
                pass
            return True
        except Exception as e:
            raise ValueError('Failed to copy config file [{}]: {}'.format(src_file, str(e)))

    def _copy_tree_with_replace(self, src_dir, dst_dir, replacements, skip_files=None):
        if not os.path.exists(src_dir):
            return 0
        skip_files = set(skip_files or [])
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir, ignore_errors=True)

        count = 0
        for root, dirs, files in os.walk(src_dir):
            rel = os.path.relpath(root, src_dir)
            rel = '' if rel == '.' else self._replace_text(rel, replacements)
            target_root = os.path.join(dst_dir, rel)
            os.makedirs(target_root, 0o755, exist_ok=True)
            for filename in files:
                if filename in skip_files:
                    continue
                dst_name = self._replace_text(filename, replacements)
                self._copy_text_file(os.path.join(root, filename), os.path.join(target_root, dst_name), replacements)
                count += 1
        return count

    def _duplicate_json_list(self, conf_file, source_name, new_name, replacements, key='sitename'):
        if not os.path.exists(conf_file):
            return 0
        try:
            data = json.loads(public.readFile(conf_file) or '[]')
        except Exception:
            return 0
        if not isinstance(data, list):
            return 0

        source_items = [x for x in data if isinstance(x, dict) and x.get(key) == source_name]
        if not source_items:
            return 0

        new_data = [x for x in data if not (isinstance(x, dict) and x.get(key) == new_name)]
        for item in source_items:
            new_item = self._replace_obj(item, replacements)
            new_item[key] = new_name
            new_data.append(new_item)
        public.writeFile(conf_file, json.dumps(new_data, ensure_ascii=False))
        return len(source_items)

    def _duplicate_json_dict(self, conf_file, source_name, new_name, replacements):
        if not os.path.exists(conf_file):
            return 0
        try:
            data = json.loads(public.readFile(conf_file) or '{}')
        except Exception:
            return 0
        if not isinstance(data, dict) or source_name not in data:
            return 0
        data[new_name] = self._replace_obj(data[source_name], replacements)
        public.writeFile(conf_file, json.dumps(data, ensure_ascii=False))
        return 1

    def _clone_configs(self, source_name, new_name, source_path, new_path, clone_ssl):
        vhost = self.site.setupPath + '/panel/vhost'
        replacements = [(source_path, new_path), (source_name, new_name)]
        warnings = []
        copied = {
            'rewrite': 0,
            'extension': 0,
            'proxy': 0,
            'redirect': 0,
            'dir_auth': 0,
            'pass': 0,
            'other_php': 0,
        }

        try:
            rewrite_dir = os.path.join(vhost, 'rewrite')
            if os.path.exists(rewrite_dir):
                for filename in os.listdir(rewrite_dir):
                    if filename == source_name + '.conf' or filename.startswith(source_name + '_'):
                        dst_name = self._replace_text(filename, replacements)
                        if self._copy_text_file(os.path.join(rewrite_dir, filename),
                                                os.path.join(rewrite_dir, dst_name), replacements):
                            copied['rewrite'] += 1
        except Exception as e:
            warnings.append('Clone rewrite config failed: {}'.format(str(e)))

        for server in ['nginx', 'apache']:
            for part in ['extension', 'proxy', 'dir_auth', 'redirect']:
                try:
                    copied[part] += self._copy_tree_with_replace(
                        os.path.join(vhost, server, part, source_name),
                        os.path.join(vhost, server, part, new_name),
                        replacements,
                    )
                except Exception as e:
                    warnings.append('Clone {} {} config failed: {}'.format(server, part, str(e)))

        try:
            copied['proxy'] += self._copy_tree_with_replace(
                os.path.join(vhost, 'openlitespeed', 'proxy', source_name),
                os.path.join(vhost, 'openlitespeed', 'proxy', new_name),
                replacements,
            )
        except Exception as e:
            warnings.append('Clone openlitespeed proxy config failed: {}'.format(str(e)))

        try:
            copied['redirect'] += self._copy_tree_with_replace(
                os.path.join(vhost, 'openlitespeed', 'redirect', source_name),
                os.path.join(vhost, 'openlitespeed', 'redirect', new_name),
                replacements,
                [] if clone_ssl else ['force_https.conf'],
            )
        except Exception as e:
            warnings.append('Clone openlitespeed redirect config failed: {}'.format(str(e)))

        try:
            copied['other_php'] += self._copy_tree_with_replace(
                os.path.join(vhost, 'other_php', source_name),
                os.path.join(vhost, 'other_php', new_name),
                replacements,
            )
        except Exception as e:
            warnings.append('Clone custom PHP config failed: {}'.format(str(e)))

        try:
            copied['pass'] += self._copy_tree_with_replace(
                '/www/server/pass/{}'.format(source_name),
                '/www/server/pass/{}'.format(new_name),
                replacements,
            )
        except Exception as e:
            warnings.append('Clone password file failed: {}'.format(str(e)))

        try:
            proxy_count = self._duplicate_json_list(
                '{}/data/proxyfile.json'.format(public.get_panel_path()), source_name, new_name, replacements
            )
            if proxy_count:
                self.site.SetNginx(public.to_dict_obj({'sitename': new_name}))
                self.site.SetApache(new_name)
                copied['proxy'] += proxy_count
        except Exception as e:
            warnings.append('Clone proxy data failed: {}'.format(str(e)))

        try:
            redirect_count = self._duplicate_json_list(
                '{}/data/redirect.conf'.format(public.get_panel_path()), source_name, new_name, replacements
            )
            if redirect_count:
                self.site.SetRedirectNginx(public.to_dict_obj({'sitename': new_name}))
                self.site.SetRedirectApache(new_name)
                copied['redirect'] += redirect_count
        except Exception as e:
            warnings.append('Clone redirect data failed: {}'.format(str(e)))

        try:
            dir_auth_count = self._duplicate_json_dict(
                '{}/data/site_dir_auth.json'.format(public.get_panel_path()), source_name, new_name, replacements
            )
            if dir_auth_count:
                import site_dir_auth_v2
                site_dir_auth_v2.SiteDirAuth().set_conf(new_name, 'create')
                copied['dir_auth'] += dir_auth_count
        except Exception as e:
            warnings.append('Clone dir auth data failed: {}'.format(str(e)))

        try:
            source_id = public.M('sites').where('name=?', (source_name,)).getField('id')
            new_id = public.M('sites').where('name=?', (new_name,)).getField('id')
            run_res = self.site.GetSiteRunPath(public.to_dict_obj({'id': int(source_id)}))
            if int(run_res.get('status', -1)) == 0:
                run_path = run_res.get('message', {}).get('runPath', '/')
                if run_path and run_path != '/':
                    target_run = os.path.join(new_path, run_path.strip('/'))
                    if os.path.isdir(target_run):
                        set_res = self.site.SetSiteRunPath(public.to_dict_obj({'id': int(new_id), 'runPath': run_path}))
                        if int(set_res.get('status', -1)) != 0:
                            warnings.append('Set run path failed: {}'.format(self._result_msg(set_res)))
                    else:
                        warnings.append('Run path skipped because directory does not exist: {}'.format(run_path))
        except Exception as e:
            warnings.append('Clone run path failed: {}'.format(str(e)))

        return copied, warnings

    def _clone_database(self, source_site_id, new_site_id, new_domain, args):
        source_db = public.M('databases').where('pid=?', (source_site_id,)).field(
            'id,name,username,password,accept,ps,addtime,db_type,sid,conn_config'
        ).find()
        if not isinstance(source_db, dict):
            raise ValueError('The source website has no associated database in panel.')

        db_name = str(args.get('new_db_name') or args.get('db_name') or '').strip().lower()
        if not db_name:
            db_name = self._ensure_available_db_name(self._default_db_name(new_domain))
        elif self._db_name_in_recycle_bin(db_name):
            raise ValueError('Database [{}] already at the recycle bin, please recover or delete it first.'.format(db_name))
        db_password = str(args.get('new_db_password') or args.get('db_password') or public.gen_password(16)).strip()
        if not db_password:
            db_password = public.gen_password(16)

        import database
        create_res = database.database().AddDatabase(public.to_dict_obj({
            'name': db_name,
            'db_user': db_name,
            'password': db_password,
            'codeing': args.get('codeing', 'utf8mb4') or 'utf8mb4',
            'address': args.get('db_address', '127.0.0.1') or '127.0.0.1',
            'ps': new_domain,
            'pid': new_site_id,
            'sid': args.get('sid', args.get('sid/d', 0)),
        }))
        if not create_res.get('status'):
            raise ValueError('Create database failed: {}'.format(self._result_msg(create_res)))

        tmp_path = public.make_panel_tmp_path()
        try:
            from public import mysqlmgr
            dump_info = mysqlmgr.dumpsql_with_aap(int(source_db['id']), tmp_path)
            restore_res = mysqlmgr.restore(db_name, dump_info.file)
            if not restore_res.success:
                raise ValueError('Import database failed: {}'.format(restore_res.msg))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                shutil.rmtree(tmp_path, ignore_errors=True)

        db_id = public.M('databases').where('pid=? and name=?', (new_site_id, db_name)).getField('id')
        return {
            'database_id': db_id,
            'database_name': db_name,
            'database_user': db_name,
            'database_password': db_password,
            'source_database': source_db.get('name', ''),
            'notice': 'The site database configuration file was not updated automatically. Please configure it manually.',
        }

    @staticmethod
    def _domain_match(cert_domain, domain):
        cert_domain = str(cert_domain or '').lower().strip()
        domain = str(domain or '').lower().strip()
        if cert_domain == domain:
            return True
        if cert_domain.startswith('*.'):
            suffix = cert_domain[1:]
            return domain.endswith(suffix) and domain.count('.') == suffix.count('.')
        return False

    def _cert_covers_domain(self, cert_pem, domain):
        if OpenSSL is None:
            return False
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)
        names = []
        subject = cert.get_subject()
        if getattr(subject, 'CN', None):
            names.append(subject.CN)
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                for item in str(ext).split(','):
                    item = item.strip()
                    if item.startswith('DNS:'):
                        names.append(item[4:])
                    elif item.startswith('IP Address:'):
                        names.append(item[11:])
        return any(self._domain_match(name, domain) for name in names)

    def _apply_ssl(self, source_name, new_name, new_site_id, force_ssl):
        cert_dir = '/www/server/panel/vhost/cert/{}'.format(source_name)
        cert_file = os.path.join(cert_dir, 'fullchain.pem')
        key_file = os.path.join(cert_dir, 'privkey.pem')
        result = {'status': False, 'type': '', 'msg': '', 'force_ssl': False}

        try:
            if os.path.exists(cert_file) and os.path.exists(key_file):
                cert_pem = public.readFile(cert_file)
                key_pem = public.readFile(key_file)
                if cert_pem and key_pem and self._cert_covers_domain(cert_pem, new_name):
                    res = self.site.SetSSL(public.to_dict_obj({
                        'siteName': new_name,
                        'key': key_pem,
                        'csr': cert_pem,
                        'type': 1,
                    }))
                    if int(res.get('status', -1)) == 0:
                        result.update({'status': True, 'type': 'copy', 'msg': 'Source certificate applied.'})
                    else:
                        result.update({'type': 'copy', 'msg': self._result_msg(res)})
                else:
                    result['msg'] = 'Source certificate does not cover the new domain.'
            else:
                result['msg'] = 'Source certificate files not found.'
        except Exception as e:
            result.update({'type': 'copy', 'msg': 'Source certificate check/apply failed: {}'.format(str(e))})

        if not result['status']:
            try:
                from ssl_domainModelV2.service import _prepare_site_domains
                domains = _prepare_site_domains(int(new_site_id))
                if not domains:
                    result.update({'type': 'auto', 'msg': 'No valid domains found for site.'})
                else:
                    @public.try_to_apply_ssl
                    def _start_site_ssl():
                        return {'ssl_site_id': int(new_site_id)}
                    _start_site_ssl()
                    result.update({
                        'status': True,
                        'type': 'auto',
                        'async': True,
                        'domains': domains,
                        'msg': 'SSL application task started.',
                    })
            except Exception as e:
                result.update({'type': 'auto', 'msg': str(e)})

        if result['status'] and force_ssl and not result.get('async'):
            try:
                force_res = self.site.HttpToHttps(public.to_dict_obj({'siteName': new_name}))
                if int(force_res.get('status', -1)) == 0:
                    result['force_ssl'] = True
                else:
                    result['force_ssl_error'] = self._result_msg(force_res)
            except Exception as e:
                result['force_ssl_error'] = str(e)
        elif result['status'] and force_ssl and result.get('async'):
            result['force_ssl_pending'] = True
        return result

    def _run(self, args, app):
        progress = self._default_progress()
        new_site_id = None
        rollback_needed = False
        try:
            with app.app_context():
                self._write_worker_lock()
                self._log('Run start.')
                self._step(progress, 'validate_source', 0, 'Validating source site')

                source_id = int(args.get('source_id') or args.get('site_id') or args.get('id') or 0)
                new_name = self._normalize_domain(args.get('new_domain') or args.get('domain') or args.get('site_name'))
                if source_id <= 0:
                    raise ValueError('source_id is required.')
                if not new_name:
                    raise ValueError('new_domain is required.')

                clone_files = self._to_bool(args.get('clone_files'), True)
                clone_config = self._to_bool(args.get('clone_config'), True)
                clone_database = self._to_bool(args.get('clone_database') if 'clone_database' in args else args.get('database'), False)
                clone_ssl = self._to_bool(args.get('clone_ssl') if 'clone_ssl' in args else args.get('ssl'), False)
                force_ssl = self._to_bool(args.get('force_ssl'), False)

                source_site = public.M('sites').where('id=?', (source_id,)).find()
                if not isinstance(source_site, dict):
                    raise ValueError('Source website does not exist.')
                if (source_site.get('project_type') or 'PHP').upper() != 'PHP':
                    raise ValueError('Only PHP websites can be cloned.')

                source_name = source_site['name']
                source_path = source_site['path']
                new_path = str(args.get('new_path') or args.get('path') or '').strip()
                if not new_path:
                    new_path = '{}/{}'.format(public.get_site_path().rstrip('/'), new_name)
                self._validate_target_path(source_path, new_path, clone_files)

                php_version = public.get_site_php_version(source_name) or '00'
                if php_version == 'Static':
                    php_version = '00'
                source_service_type = str(source_site.get('service_type') or 'nginx').strip().lower()

                self._log('Validated: source_id={}, source={}, new={}, path={}, php={}, files={}, config={}, db={}, ssl={}'.format(
                    source_id, source_name, new_name, new_path, php_version, clone_files, clone_config, clone_database, clone_ssl
                ))
                self._step(progress, 'validate_source', 1, 'Source site validated')

                self._step(progress, 'create_site', 0, 'Creating new PHP site')
                add_res = self.site.AddSite(public.to_dict_obj({
                    'webname': json.dumps({'domain': new_name, 'domainlist': [], 'count': 0}),
                    'type': 'PHP',
                    'project_type': 'PHP',
                    'ps': args.get('ps') or new_name,
                    'path': new_path,
                    'version': php_version,
                    'sql': 'false',
                    'datapassword': '',
                    'codeing': args.get('codeing', 'utf8mb4') or 'utf8mb4',
                    'port': str(args.get('port', '80') or '80'),
                    'type_id': int(source_site.get('type_id') or 0),
                    'force_ssl': 0,
                    'ftp': False,
                    'is_create_default_file': not clone_files,
                    'ssl_auto': 0,
                    'sub_dir': '',
                }), multiple=1)
                if int(add_res.get('status', -1)) != 0:
                    raise ValueError('Create website failed: {}'.format(self._result_msg(add_res)))

                new_site_id = int(add_res.get('message', {}).get('siteId', 0))
                new_site = public.M('sites').where('id=?', (new_site_id,)).find()
                if not isinstance(new_site, dict):
                    raise ValueError('Create website failed: new site record not found.')
                new_path = new_site.get('path') or new_path
                rollback_needed = True
                progress['result'].update({'site_id': new_site_id, 'site_name': new_name, 'site_path': new_path})
                self._log('Created new site: id={}, name={}, path={}'.format(new_site_id, new_name, new_path))
                self._step(progress, 'create_site', 1, 'New PHP site created')

                if clone_files:
                    self._step(progress, 'copy_files', 0, 'Copying website files')
                    self._copy_site_files(source_path, new_path)
                    self._step(progress, 'copy_files', 1, 'Website files copied')
                else:
                    self._step(progress, 'copy_files', 1, 'Skipped')

                if public.get_multi_webservice_status() and source_service_type != 'nginx':
                    # 判断多服务情况下  如果站点不是仅nginx的情况 再做切换
                    self._step(progress, 'switch_webservice', 0, 'Switching web service')
                    switch_res = self.site.switch_webservice(public.to_dict_obj({
                        'site_id': new_site_id,
                        'service_type': source_service_type,
                        'is_reload': False,
                    }))
                    switch_msg = self._result_msg(switch_res)
                    if int(switch_res.get('status', -1)) == 0 or 'already' in switch_msg.lower() or '已经' in switch_msg:
                        progress['result']['service_type'] = source_service_type
                        self._step(progress, 'switch_webservice', 1, 'Web service switched')
                    else:
                        progress['warnings'].append('Switch web service failed: {}'.format(switch_msg))
                        self._step(progress, 'switch_webservice', 1, 'Switch web service skipped with warning')
                else:
                    progress['result']['service_type'] = source_service_type
                    self._step(progress, 'switch_webservice', 1, 'Skipped')

                if clone_config:
                    self._step(progress, 'clone_config', 0, 'Cloning website config')
                    copied, warnings = self._clone_configs(source_name, new_name, source_path, new_path, clone_ssl)
                    progress['result']['config'] = copied
                    progress['warnings'].extend(warnings)
                    self._step(progress, 'clone_config', 1, 'Website config cloned')
                else:
                    self._step(progress, 'clone_config', 1, 'Skipped')

                if clone_database:
                    self._step(progress, 'clone_database', 0, 'Cloning database')
                    progress['result']['database'] = self._clone_database(source_id, new_site_id, new_name, args)
                    self._step(progress, 'clone_database', 1, 'Database cloned')
                else:
                    self._step(progress, 'clone_database', 1, 'Skipped')

                self._step(progress, 'reload_service', 0, 'Checking and reloading web service')
                check_res = public.checkWebConfig()
                if isinstance(check_res, str):
                    raise ValueError('Web configuration check failed: {}'.format(check_res))
                if not check_res:
                    raise ValueError('Web configuration check failed.')
                public.serviceReload()
                self._step(progress, 'reload_service', 1, 'Web service reloaded')

                if clone_ssl:
                    self._step(progress, 'clone_ssl', 0, 'Applying SSL')
                    ssl_info = self._apply_ssl(source_name, new_name, new_site_id, force_ssl)
                    progress['result']['ssl'] = ssl_info
                    if ssl_info.get('status'):
                        if ssl_info.get('force_ssl_error'):
                            progress['warnings'].append('Force HTTPS failed: {}'.format(ssl_info.get('force_ssl_error')))
                        if ssl_info.get('async'):
                            self._step(progress, 'clone_ssl', 1, 'SSL application started')
                        else:
                            self._step(progress, 'clone_ssl', 1, 'SSL applied')
                    else:
                        progress['warnings'].append('SSL apply failed: {}'.format(ssl_info.get('msg', '')))
                        self._step(progress, 'clone_ssl', 1, 'SSL failed with warning')
                else:
                    if force_ssl:
                        progress['warnings'].append('force_ssl ignored because clone_ssl is disabled.')
                    self._step(progress, 'clone_ssl', 1, 'Skipped')

                rollback_needed = False
                progress['status'] = 1
                progress['success'] = True
                progress['end_time'] = int(time.time())
                progress['current'] = 'finished'
                self._write_progress(progress)
                self._log('Run finished: site_id={}, status=success'.format(new_site_id))
                public.write_log_gettext('Site manager', 'PHP website [{}] cloned to [{}] successfully!', (source_name, new_name))
        except Exception as e:
            import traceback
            err = str(e)
            self._log('Run failed: {}'.format(err))
            public.print_log(traceback.format_exc())
            progress['status'] = 1
            progress['success'] = False
            progress['end_time'] = int(time.time())
            progress['error'] = err
            if progress.get('current') in progress.get('steps', {}):
                current = progress['current']
                progress['steps'][current]['status'] = -1
                progress['steps'][current]['error'] = err
                progress['steps'][current]['ps'] = 'Failed'

            if rollback_needed and new_site_id:
                try:
                    from public import websitemgr
                    rollback_res = websitemgr.remove_site(new_site_id)
                    progress['rollback'] = {'status': bool(rollback_res.success), 'msg': rollback_res.msg}
                except Exception as rollback_error:
                    progress['rollback'] = {'status': False, 'msg': str(rollback_error)}
            self._write_progress(progress)
        finally:
            public.progress_release_lock(self.lock_file)
