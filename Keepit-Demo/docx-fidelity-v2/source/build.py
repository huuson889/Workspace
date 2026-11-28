"""Build one offline HTML. python build.py [--inputs PATH] [--output PATH]
Requires PyMuPDF. Missing fixtures download from the recorded immutable Git commit.
"""
from pathlib import Path
import argparse,base64,hashlib,json,re,urllib.request
import pymupdf as fitz
p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,default=Path.home()/'.cache/docx-fidelity-v2-inputs');p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent/'keepit-docx-fidelity-demo-v2.html');args=p.parse_args()
r=Path(__file__).resolve().parent;args.inputs.mkdir(parents=True,exist_ok=True)
def script(s):return '<script>'+s.replace('</script','<\\/script')+'</script>'
def json_safe(x):return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def b64(b):return base64.b64encode(b).decode()
stable=json.loads((r/'stable-worker.json').read_text())
prefix=stable.split('<script>',1)[0]
fallback='@font-face{font-family:Carlito;font-weight:400;font-style:normal;src:url(data:font/ttf;base64,'+b64((r/'Carlito-Regular.ttf').read_bytes())+') format("truetype");}'
prefix=prefix.replace('</head>','<style>'+fallback+'</style></head>')
worker=prefix+''.join(script((r/name).read_text()) for name in ['jszip.min.js','docx-preview-patched.js','engine.js'])
controller=stable[stable.rfind('<script>')+8:stable.rfind('</script>')]
worker+=script(controller)+'</body></html>'
samples={};provenance={}
for key,name,commit,profile in [('annual','Annual Report Summary','3b1678e57d6e01401cc8bc301ecc7554f4cecac2','enhanced'),('book','Book Report','3b1678e57d6e01401cc8bc301ecc7554f4cecac2','enhanced'),('hr','Monthly HR Report','94286d971c12fa4577d4872464694ab1d01a9671','stable')]:
    files={}
    for ext in ['docx','pdf']:
        filename='report_templates_'+name+' Doc.'+ext;path=args.inputs/filename
        url='https://raw.githubusercontent.com/huuson889/Workspace/'+commit+'/Uploads/'+urllib.parse.quote(filename)
        if not path.exists():path.write_bytes(urllib.request.urlopen(url).read())
        files[ext]=path
        provenance[filename]={'url':url,'bytes':len(path.read_bytes()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    refs=[]
    with fitz.open(files['pdf']) as pdf:
        for i,page in enumerate(pdf):refs.append({'page':i+1,'src':'data:image/png;base64,'+b64(page.get_pixmap(matrix=fitz.Matrix(4/3,4/3)).tobytes('png'))})
    samples[key]={'filename':files['docx'].name,'bytes':b64(files['docx'].read_bytes()),'references':refs,'profile':profile}
html=(r/'shell.html').read_text().replace('__SAMPLE__',json_safe(samples)).replace('__REFERENCES__','[]').replace('__WORKER__',json_safe({'stable':stable,'enhanced':worker})).replace('id="sampledata" type="application/octet-stream"','id="sampledata" type="application/json"')
licenses='\n\n'.join((r/name).read_text() for name in ['LICENSE-jszip.txt','LICENSE-docx-preview.txt','OFL.txt'])
html=html.replace('</body>','<script type="text/plain" id="third-party-licenses">'+licenses.replace('</script','<\\/script')+'</script></body>')
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(html)
(r.parent/'inputs.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False)+'\n')
print(args.output,len(args.output.read_bytes()),hashlib.sha256(args.output.read_bytes()).hexdigest())
