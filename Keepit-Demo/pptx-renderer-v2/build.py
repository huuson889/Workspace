"""Build self-contained file-picker PPTX demo v2. --deps supplies pinned local office/pdfjs modules."""
from pathlib import Path
import argparse,json,base64,html,hashlib
p=argparse.ArgumentParser();p.add_argument('--deps',required=True);p.add_argument('--output',required=True);a=p.parse_args();here=Path(__file__).parent;q=Path(a.deps)
lock=json.loads((here/'dependencies.json').read_text())
for name,item in lock['files'].items():
 if hashlib.sha256((q/name).read_bytes()).hexdigest()!=item['sha256']:raise SystemExit('Dependency hash mismatch: '+name)
deps={k:base64.b64encode((q/f).read_bytes()).decode()for k,f in [('zip','office.mjs'),('pdf','pdf.mjs'),('worker','pdf.worker.mjs')]}
loader="""<script type="module">try{const d=JSON.parse(document.getElementById('dependencies').textContent);const url=URL.createObjectURL(new Blob([Uint8Array.from(atob(d.zip),c=>c.charCodeAt(0))],{type:'text/javascript'}));try{const m=await import(url);window.PptxZip=m.JSZip;window.dispatchEvent(new Event('pptxzipready'));}finally{URL.revokeObjectURL(url);}}catch(e){document.getElementById('fileStatus').textContent='Không nạp được ZIP: '+e.message;}</script>"""
script=(here/'renderer.js').read_text()+'\n'+(here/'controller.js').read_text();script=script.replace('</script','<\\/script')
notices='<details><summary>Giấy phép thư viện đi kèm (ZIP / PDF)</summary>'+''.join('<h3>'+html.escape(p.name)+'</h3><pre>'+html.escape(p.read_text())+'</pre>'for p in sorted((here/'licenses').glob('*.txt')))+'</details>'
s=(here/'template.html').read_text().replace('</main>',notices+'</main>').replace('</body>','<script id="dependencies" type="application/json">'+json.dumps(deps)+'</script>'+loader+'<script>'+script+'</script></body>');Path(a.output).write_text(s);print(a.output,len(s.encode()))
