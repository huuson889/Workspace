"""Integration checks against a running demo; all fixture uploads are generated samples.
python tests/check_api.py --base http://localhost:8120 [--deck /path/to/authorized.pptx]
PyMuPDF is only a test dependency, not needed to run the app.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import argparse
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import time
import zipfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
p=argparse.ArgumentParser();p.add_argument('--base',default='http://localhost:8120');p.add_argument('--deck');p.add_argument('--output',required=True);a=p.parse_args()
rows=[]
def record(name, passed, **data):
    rows.append({'name':name,'pass':bool(passed),**data});print(('PASS' if passed else 'FAIL'),name,flush=True)
def request(path,method='GET',data=None,headers=None):
    try:
        with urlopen(Request(a.base+path,data=data,method=method,headers=headers or {}),timeout=50)as r:return r.status,r.read()
    except HTTPError as e:return e.code,e.read()
def upload(file,headers=None):
    return request('/api/convert','POST',file.read_bytes(),headers or {'X-Upload-Consent':'yes','X-Filename':file.name})
def complete(key):
    end=time.monotonic()+190
    while time.monotonic()<end:
        code,b=request('/api/jobs/'+key);j=json.loads(b)
        if code!=200:raise AssertionError(j)
        if j['status']in('ready','error'):return j
        time.sleep(.35)
    raise AssertionError('conversion timeout')

record('health engine ready',json.loads(request('/api/health')[1])['ok'])
fixture=root/'public/samples/keepit-sample.docx'
record('upload requires explicit consent',upload(fixture,{'X-Filename':fixture.name})[0]==400)
record('cross-site mutation rejected',upload(fixture,{'X-Filename':fixture.name,'X-Upload-Consent':'yes','Origin':'https://example.invalid'})[0]==403)
record('wrong format rejected',request('/api/convert','POST',b'bad',{'X-Filename':'bad.exe','X-Upload-Consent':'yes'})[0]==400)
record('invalid ZIP rejected',request('/api/convert','POST',b'bad',{'X-Filename':'bad.docx','X-Upload-Consent':'yes'})[0]==400)
record('private source is not a static route',request('/server.py')[0]==404)
record('unknown job cannot be fetched',request('/api/jobs/unknown/pdf')[0]==404)

spec=importlib.util.spec_from_file_location('demo_server',root/'server.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Preflight corruption/security cases, without invoking LibreOffice.
base=fixture.read_bytes()
def modified(name, content):
    b=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(base)) as zin,zipfile.ZipFile(b,'w')as zout:
        for i in zin.infolist():
            if i.filename!=name:zout.writestr(i,zin.read(i))
        zout.writestr(name,content)
    return b.getvalue()
for name,data in [
 ('path traversal',modified('../escape','x')),
 ('macro',modified('word/vbaProject.bin',b'x')),
 ('OLE',modified('word/embeddings/item.bin',b'x')),
 ('DTD',modified('word/document.xml','<!DOCTYPE x [<!ENTITY x "data">]><x/>')),
 ('external image',modified('word/_rels/document.xml.rels','<Relationships><Relationship TargetMode="External" Type="http://a/image" Target="https://example.invalid/image.png"/></Relationships>'))]:
    try:m.validate(data,'.docx');ok=False
    except ValueError:ok=True
    record('preflight rejects '+name,ok)
exp=m.STORE/'expiry-check';exp.mkdir();(exp/'source.pdf').write_bytes(b'test');m.JOBS['test']={'dir':exp,'status':'ready','expires':1};m.sweep_expired(now=2)
record('TTL sweep removes expired payload',not exp.exists() and 'test' not in m.JOBS)
shutil.rmtree(m.STORE,ignore_errors=True)
r=subprocess.run([sys.executable,str(root/'engine.py'),sys.executable,'-c','import socket; socket.socket(socket.AF_INET,socket.SOCK_STREAM)'],capture_output=True,text=True)
record('engine Internet socket denied',r.returncode!=0 and 'Operation not permitted' in r.stderr)

import pymupdf as fitz
for ext in ['docx','pptx']:
    f=root/f'public/samples/keepit-sample.{ext}'
    code,b=upload(f);assert code==202,(code,b)
    key=json.loads(b)['id'];j=complete(key);assert j['status']=='ready',j
    code,b=request('/api/jobs/'+key+'/pdf');doc=fitz.open(stream=b,filetype='pdf')
    text=''.join(p.get_text()for p in doc)
    record(ext+' produces selectable two-page PDF',code==200 and len(doc)==2 and 'Tiếng Việt' in text,pages=len(doc),pdfBytes=len(b),engineSeconds=j['duration'],textCharacters=len(text))
    record(ext+' deletion returns 404',request('/api/jobs/'+key,'DELETE')[0]==200 and request('/api/jobs/'+key+'/pdf')[0]==404)
# Queued/running cancellation is idempotent.
code,b=upload(fixture);key=json.loads(b)['id']
record('cancel queued or running job',request('/api/jobs/'+key,'DELETE')[0]==200 and request('/api/jobs/'+key)[0]==404)
record('delete is idempotent',request('/api/jobs/'+key,'DELETE')[0]==200)

if a.deck:
    f=Path(a.deck);code,b=upload(f);assert code==202,(code,b)
    key=json.loads(b)['id'];j=complete(key);assert j['status']=='ready',j
    code,b=request('/api/jobs/'+key+'/pdf');doc=fitz.open(stream=b,filetype='pdf');text=''.join(p.get_text()for p in doc)
    record('authorized original deck converts',code==200 and len(doc)==92,pages=len(doc),pdfBytes=len(b),engineSeconds=j['duration'],textCharacters=len(text),pagesWithText=sum(bool(p.get_text().strip())for p in doc))
    out=Path(a.output).parent;out.mkdir(parents=True,exist_ok=True);(out/'original-deck-converted.pdf').write_bytes(b)
    request('/api/jobs/'+key,'DELETE')
report={'rows':rows,'passed':all(r['pass']for r in rows),'engine':json.loads(request('/api/health')[1])['engine']}
Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2));assert report['passed']
