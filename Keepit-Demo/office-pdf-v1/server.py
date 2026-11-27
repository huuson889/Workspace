"""Keepit Office -> PDF demo. Python stdlib + system LibreOffice, Linux only.
Run: python server.py --host 0.0.0.0 --port 8120
Temporary documents are never served as static files or logged by name.
"""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import ctypes.util
import hashlib
import io
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pptx_batches import batches

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
MAX_INPUT = 50 * 1024**2
MAX_EXPANDED = 200 * 1024**2
TTL = 30 * 60
JOBS = {}
LOCK = threading.RLock()
POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix='convert')
STORE = Path(tempfile.mkdtemp(prefix='keepit-office-pdf-'))
SOFFICE = shutil.which('libreoffice') or shutil.which('soffice')
VERSION = subprocess.check_output([SOFFICE, '--version'], text=True).strip() if SOFFICE else ''


def validate(data, ext):
    """Preflight OOXML before invoking the engine. Deliberately narrow demo policy."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        entries = z.infolist()
        if len(entries) > 12000 or sum(i.file_size for i in entries) > MAX_EXPANDED:
            raise ValueError('Tệp Office quá lớn sau giải nén (tối đa 200 MB / 12.000 mục).')
        names = {i.filename for i in entries}
        part = 'word/document.xml' if ext == '.docx' else 'ppt/presentation.xml'
        if part not in names or '[Content_Types].xml' not in names:
            raise ValueError('Nội dung không khớp định dạng DOCX/PPTX.')
        for info in entries:
            name = info.filename
            if info.flag_bits & 1 or info.file_size > 50 * 1024**2:
                raise ValueError('Không hỗ trợ tệp mã hóa hoặc thành phần vượt 50 MB.')
            if name.startswith('/') or '\\' in name or '..' in name.split('/'):
                raise ValueError('Đường dẫn OOXML không hợp lệ.')
            if 'vbaproject' in name.lower() or name.startswith(('word/embeddings/', 'ppt/embeddings/')):
                raise ValueError('Demo từ chối macro và đối tượng OLE nhúng.')
            if name.endswith(('.xml', '.rels')):
                if info.file_size > 8 * 1024**2:
                    raise ValueError('Một XML vượt 8 MB.')
                xml = z.read(info)
                if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
                    raise ValueError('DTD/entity không được hỗ trợ.')
                doc = ET.fromstring(xml)
                if name.endswith('.rels'):
                    for rel in doc:
                        if rel.get('TargetMode', '').lower() == 'external' and not rel.get('Type', '').endswith('/hyperlink'):
                            raise ValueError('Tệp chứa tài nguyên ngoài (ảnh/liên kết dữ liệu). Hãy nhúng tài nguyên trước khi thử.')
    except (zipfile.BadZipFile, ET.ParseError, RuntimeError, NotImplementedError, EOFError) as exc:
        raise ValueError('Tệp Office hỏng, mã hóa hoặc ZIP/XML không hợp lệ.') from exc


def clear_payload(job):
    shutil.rmtree(job['dir'], ignore_errors=True)


def worker(job_id):
    with LOCK:
        job = JOBS.get(job_id)
        if not job or job['cancel']:
            return
        job.update(status='converting', started=time.time())
    folder = job['dir']
    profile = folder / 'profile'
    user = profile / 'user'
    user.mkdir(parents=True)
    (user / 'registrymodifications.xcu').write_text('''<?xml version="1.0"?><oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop></item><item oor:path="/org.openoffice.Office.Common/Load"><prop oor:name="UpdateDocMode" oor:op="fuse"><value>0</value></prop></item></oor:items>''')
    pdf_filter = 'writer_pdf_Export' if job['ext'] == '.docx' else 'impress_pdf_Export'
    options = json.dumps({'UseTaggedPDF': {'type': 'boolean', 'value': 'true'},
                          'ExportBookmarks': {'type': 'boolean', 'value': 'true'},
                          'ExportNotesPages': {'type': 'boolean', 'value': 'false'},
                          'ExportHiddenSlides': {'type': 'boolean', 'value': 'true'}})
    proc = None
    writer = None
    try:
        source = folder / ('source' + job['ext'])
        if job['ext'] == '.pptx':
            with zipfile.ZipFile(source) as z:
                slide_count = len(ET.fromstring(z.read('ppt/presentation.xml')).find('{http://schemas.openxmlformats.org/presentationml/2006/main}sldIdLst'))
            if slide_count > 2000:
                raise ValueError('Too many slides')
            total_batches = (slide_count + 7) // 8 if slide_count > 12 else 1
            inputs = batches(source, folder)
        else:
            total_batches = 1
            inputs = [(source, None)]
        batched = total_batches > 1
        if batched:
            writer = PdfWriter()
        with LOCK:
            job.update(batched=batched, totalBatches=total_batches)
        output_size = 0
        for index, (input_path, expected_pages) in enumerate(inputs, 1):
            with LOCK:
                if job['cancel']:
                    return
                job['batch'] = index
            remaining = 180 - (time.time() - job['started'])
            if remaining <= 0:
                raise subprocess.TimeoutExpired('conversion', 180)
            cmd = [sys.executable, str(ROOT / 'engine.py'), SOFFICE,
                   '-env:UserInstallation=' + profile.as_uri(), '--headless', '--nologo',
                   '--nodefault', '--norestore', '--nofirststartwizard', '--convert-to',
                   'pdf:' + pdf_filter + ':' + options, '--outdir', str(folder), str(input_path)]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    start_new_session=True, cwd=folder,
                                    env={**os.environ, 'SAL_USE_VCLPLUGIN': 'svp'})
            with LOCK:
                job['proc'] = proc
                if job['cancel']:
                    os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate(timeout=remaining)
            result = input_path.with_suffix('.pdf')
            if proc.returncode != 0 or not result.exists() or result.stat().st_size < 5:
                raise ValueError('LibreOffice did not produce PDF')
            output_size += result.stat().st_size
            if output_size > 120 * 1024**2:
                raise ValueError('Output exceeds demo limit')
            reader = PdfReader(result)
            if expected_pages is not None and len(reader.pages) != expected_pages:
                raise ValueError('Incomplete conversion')
            if writer is not None:
                writer.append(reader, import_outline=False)
                result.unlink(missing_ok=True)
                input_path.unlink(missing_ok=True)
        pdf = folder / 'source.pdf'
        if writer is not None:
            writer.write(pdf)
            writer.close()
        with LOCK:
            if job['cancel']:
                return
            job.update(status='ready', bytes=pdf.stat().st_size,
                       duration=round(time.time() - job['started'], 2),
                       finished=time.time(), expires=time.time() + TTL)
    except subprocess.TimeoutExpired:
        if proc:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
        with LOCK:
            job.update(status='error', error='Chuyển đổi quá 180 giây. Hãy thử tệp nhỏ hơn.', expires=time.time() + TTL)
    except Exception:
        with LOCK:
            job.update(status='error', error='Không chuyển được tệp. Tệp có thể hỏng, có mật khẩu hoặc không được LibreOffice hỗ trợ.', expires=time.time() + TTL)
    finally:
        # Original uploads and Office profiles are removed as soon as conversion ends.
        if writer is not None:
            writer.close()
        for p in [folder / ('source' + job['ext']), profile, *folder.glob('batch-*')]:
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
        with LOCK:
            job.pop('proc', None)
            if job['cancel'] or job['status'] == 'error':
                clear_payload(job)


def sweep_expired(now=None):
    now = time.time() if now is None else now
    with LOCK:
        for key, job in list(JOBS.items()):
            if job['status'] in ('ready', 'error') and job['expires'] <= now:
                clear_payload(job)
                JOBS.pop(key, None)


def cleanup():
    while True:
        time.sleep(30)
        sweep_expired()


class Handler(BaseHTTPRequestHandler):
    server_version = 'KeepitDemo/1'

    def log_message(self, *_):
        pass  # No filenames, content or capability URLs in access logs.

    def send(self, status, data=b'', mime='application/json; charset=utf-8', extra=None):
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; font-src 'self' blob: data:; worker-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'none'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def error(self, code, message):
        self.send(code, {'error': message})

    def mutation_allowed(self):
        origin = self.headers.get('Origin')
        hosts = {self.headers.get('Host', ''), self.headers.get('X-Forwarded-Host', '')}
        if self.headers.get('Sec-Fetch-Site') == 'cross-site' or (origin and urlsplit(origin).netloc not in hosts):
            self.error(403, 'Yêu cầu phải đến từ cùng trang demo.')
            return False
        return True

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/health':
            self.send(200, {'ok': bool(SOFFICE), 'engine': VERSION, 'maxBytes': MAX_INPUT, 'ttlMinutes': TTL // 60})
            return
        if path.startswith('/api/jobs/'):
            sweep_expired()
            pieces = path.strip('/').split('/')
            key = pieces[2] if len(pieces) >= 3 else ''
            with LOCK:
                job = JOBS.get(key)
                if not job or job['cancel']:
                    self.error(404, 'Phiên đã xóa hoặc hết hạn. Hãy chọn tệp và chuyển lại.')
                    return
                if len(pieces) == 3:
                    self.send(200, {k: v for k, v in job.items() if k in ['status', 'name', 'bytes', 'duration', 'error', 'expires', 'sha256', 'batch', 'totalBatches', 'batched']})
                    return
                if pieces[3:] == ['pdf'] and job['status'] == 'ready':
                    pdf = job['dir'] / 'source.pdf'
                    self.send(200, pdf.read_bytes(), 'application/pdf', {'Content-Disposition': 'inline; filename="keepit-converted.pdf"'})
                    return
            self.error(404, 'PDF chưa sẵn sàng.')
            return
        from mimetypes import guess_type
        path = '/index.html' if path == '/' else path
        file = (PUBLIC / unquote(path).lstrip('/')).resolve()
        if PUBLIC not in file.parents or not file.is_file():
            self.error(404, 'Không tìm thấy.')
            return
        mime = 'text/javascript; charset=utf-8' if file.suffix == '.mjs' else guess_type(str(file))[0] or 'application/octet-stream'
        self.send(200, file.read_bytes(), mime)

    def do_POST(self):
        if not self.mutation_allowed():
            return
        if urlsplit(self.path).path != '/api/convert':
            self.error(404, 'Không tìm thấy.')
            return
        if self.headers.get('X-Upload-Consent') != 'yes':
            self.error(400, 'Cần đồng ý gửi tệp để chuyển đổi.')
            return
        if not SOFFICE:
            self.error(503, 'Máy chủ chưa cài LibreOffice.')
            return
        name = unquote(self.headers.get('X-Filename', 'document'))[:220]
        name = name.replace('\\', '/').split('/')[-1]
        ext = Path(name).suffix.lower()
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = 0
        if ext not in ('.docx', '.pptx') or not 0 < length <= MAX_INPUT:
            self.error(400, 'Chỉ nhận DOCX/PPTX từ 1 byte đến 50 MB.')
            return
        with LOCK:
            active = sum(j['status'] in ('queued', 'converting', 'uploading') for j in JOBS.values())
            if active >= 3 or len(JOBS) >= 12:
                self.error(429, 'Demo đang đầy. Hãy xóa phiên cũ hoặc thử lại sau.')
                return
            key = secrets.token_urlsafe(24)
            folder = STORE / key
            folder.mkdir(mode=0o700)
            job = {'dir': folder, 'status': 'uploading', 'ext': ext, 'name': name, 'cancel': False, 'expires': time.time() + TTL}
            JOBS[key] = job
        try:
            self.connection.settimeout(40)
            chunks, remain = [], length
            while remain:
                chunk = self.rfile.read(min(remain, 1024**2))
                if not chunk:
                    raise ValueError('Tải tệp bị gián đoạn.')
                chunks.append(chunk)
                remain -= len(chunk)
            data = b''.join(chunks)
            validate(data, ext)
            (folder / ('source' + ext)).write_bytes(data)
            with LOCK:
                job.update(status='queued', sha256=hashlib.sha256(data).hexdigest())
            POOL.submit(worker, key)
            self.send(202, {'id': key, 'status': 'queued'})
        except (ValueError, TimeoutError, ConnectionError) as exc:
            with LOCK:
                JOBS.pop(key, None)
                clear_payload(job)
            self.error(400, str(exc))
        except Exception:
            with LOCK:
                JOBS.pop(key, None)
                clear_payload(job)
            self.error(500, 'Không nhận được tệp. Hãy thử lại.')

    def do_DELETE(self):
        if not self.mutation_allowed():
            return
        path = urlsplit(self.path).path
        with LOCK:
            job = JOBS.get(path.split('/')[-1]) if path.startswith('/api/jobs/') else None
            if job:
                job['cancel'] = True
                proc = job.get('proc')
                if proc and proc.poll() is None:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                # Running worker owns cleanup until process is dead.
                if not proc and job['status'] != 'converting':
                    clear_payload(job)
                JOBS.pop(path.split('/')[-1], None)
        self.send(200, {'deleted': True})


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--host', default='127.0.0.1')
    args.add_argument('--port', type=int, default=8120)
    a = args.parse_args()
    if not sys.platform.startswith('linux') or not ctypes.util.find_library('seccomp'):
        raise SystemExit('This demo requires Linux and libseccomp. No unrestricted fallback.')
    threading.Thread(target=cleanup, daemon=True).start()
    print(f'Keepit Office → PDF · {VERSION or "LibreOffice not installed"} · port {a.port}', flush=True)
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with LOCK:
            for job in JOBS.values():
                job['cancel'] = True
                proc = job.get('proc')
                if proc and proc.poll() is None:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        POOL.shutdown(wait=True, cancel_futures=True)
        shutil.rmtree(STORE, ignore_errors=True)
