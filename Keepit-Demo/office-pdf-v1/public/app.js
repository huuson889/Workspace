import * as pdfjs from './vendor/pdf.mjs';
pdfjs.GlobalWorkerOptions.workerSrc = new URL('./vendor/pdf.worker.mjs', import.meta.url).href;
const $ = id => document.getElementById(id);
const MB = 1024 * 1024;
let chosen = null, jobId = null, pdf = null, page = 1, rotation = 0, busy = false;
let operation = 0, renderVersion = 0, renderTask = null, textTask = null, timer = null, engineOK = false;
let latestStatus = null;
const bytes = n => n >= MB ? (n / MB).toFixed(1) + ' MB' : Math.ceil(n / 1024) + ' KB';
const pause = ms => new Promise(r => setTimeout(r, ms));
function status(text, error = false) { $('status').textContent = text; $('status').classList.toggle('error', error); }
function stages(n) { ['stageChoose','stageConvert','stageRead'].forEach((id,i) => { $(id).classList.toggle('current',i===n); $(id).classList.toggle('done',i<n); }); }
function locking(value) {
  busy = value;
  ['file','sampleDocx','samplePptx','unselect'].forEach(id => $(id).disabled = value);
  $('convert').disabled = value || !engineOK;
  $('cancel').hidden = !value;
}
function pick(file, sample = false) {
  if (!file || busy) return;
  if (!/\.(docx|pptx)$/i.test(file.name) || !file.size || file.size > 50 * MB) {
    status('Chọn DOCX/PPTX hợp lệ, tối đa 50 MB. Tệp chưa được gửi.', true); $('file').value=''; return;
  }
  chosen = file;
  $('chosen').hidden = false;
  $('filename').textContent = file.name;
  $('filename').title = file.name;
  $('filesize').textContent = bytes(file.size) + (sample ? ' · Mẫu kiểm thử tạo riêng' : ' · Chưa gửi lên máy chủ');
  const ppt = /\.pptx$/i.test(file.name);
  $('typeBadge').textContent = ppt ? 'P' : 'W';
  $('typeBadge').style.color = ppt ? '#bd704d' : '#507cb6';
  $('convert').disabled = !engineOK;
  stages(0);
  status('Đã chọn tệp. Bấm chuyển đổi để xem và xác nhận trước khi gửi.');
}
async function sample(ext) {
  try {
    const r = await fetch('/samples/keepit-sample.' + ext);
    if (!r.ok) throw Error('Không tải được mẫu.');
    pick(new File([await r.blob()], 'keepit-sample.' + ext), true);
  } catch(e) { status(e.message,true); }
}
async function eraseRemote(id) {
  if (!id) return;
  const response = await fetch('/api/jobs/' + id, { method: 'DELETE' });
  if (!response.ok) throw Error('Chưa xác nhận được việc xóa phiên trên máy chủ. Hãy thử lại.');
}
async function clearPDF() {
  ++renderVersion;
  renderTask?.cancel(); textTask?.cancel();
  if (pdf) { const old=pdf; pdf=null; await old.destroy(); }
  $('paper').hidden = true; $('textLayer').replaceChildren();
  $('download').hidden = true; $('download').removeAttribute('href'); $('remove').hidden = true;
  ['prev','next','pageNumber','zoom','rotate'].forEach(id=>$(id).disabled=true);
  $('pageNumber').value=1; $('pageTotal').textContent='/ —';
  $('documentTitle').textContent='Không gian đọc'; $('documentMeta').textContent='Chưa có tài liệu · PDF.js';
  $('selection').textContent='Kéo chọn chữ trong PDF để kiểm tra lớp văn bản.';
}
async function convert() {
  if (!chosen || busy) return;
  const file=chosen, token=++operation, started=Date.now();
  locking(true); stages(1); latestStatus=null;
  $('filesize').textContent=bytes(file.size)+' · Đang gửi để chuyển đổi';
  $('empty').hidden=true; $('loading').hidden=false;
  $('loadingTitle').textContent='Đang gửi tệp để chuyển đổi…';
  $('elapsed').textContent='Đang tải lên máy chủ demo.';
  status('Đang gửi tệp đã được bạn xác nhận…');
  timer=setInterval(()=>{ $('elapsed').textContent=Math.floor((Date.now()-started)/1000)+' giây · Không đóng tab trong khi chờ.'; },1000);
  try {
    if (jobId) { await eraseRemote(jobId); jobId=null; }
    await clearPDF();
    const r=await fetch('/api/convert', { method:'POST', headers:{ 'Content-Type':'application/octet-stream', 'X-Filename':encodeURIComponent(file.name), 'X-Upload-Consent':'yes' }, body:file });
    const data=await r.json();
    if (!r.ok) throw Error(data.error || 'Không gửi được tệp.');
    if (token!==operation) { await eraseRemote(data.id); return; }
    jobId=data.id;
    let result;
    while (token===operation) {
      const rr=await fetch('/api/jobs/'+jobId);
      result=await rr.json();
      if (!rr.ok) throw Error(result.error || 'Không tìm thấy phiên.');
      latestStatus=result;
      if (result.status==='ready') break;
      if (result.status==='error') throw Error(result.error);
      $('loadingTitle').textContent=result.status==='queued'?'Đang chờ engine trống…':'LibreOffice đang tạo PDF…';
      status(result.status==='queued'?'Tệp đã nhận. Đang chờ chuyển đổi.':(result.batched?'LibreOffice đang chuyển nhóm slide '+result.batch+' / '+result.totalBatches+' để giảm RAM.':'LibreOffice đang chuyển đổi thật. Có thể mất vài giây đến 3 phút.'));
      await pause(650);
    }
    if (token!==operation) return;
    $('loadingTitle').textContent='Đang mở bản PDF…';
    const pr=await fetch('/api/jobs/'+jobId+'/pdf');
    if (!pr.ok) throw Error('Không tải được PDF đã tạo.');
    const task=pdfjs.getDocument({data:new Uint8Array(await pr.arrayBuffer()), isEvalSupported:false, useSystemFonts:true});
    const doc=await task.promise;
    if (token!==operation) { await doc.destroy(); return; }
    pdf=doc; page=1; rotation=0; $('zoom').value='fit';
    $('documentTitle').textContent=file.name.replace(/\.(docx|pptx)$/i,'')+'.pdf';
    $('documentTitle').title=file.name;
    $('documentMeta').textContent=pdf.numPages+' trang · '+bytes(result.bytes)+' · LibreOffice → PDF';
    $('download').href='/api/jobs/'+jobId+'/pdf'; $('download').download=file.name.replace(/\.(docx|pptx)$/i,'.pdf');
    $('download').hidden=false; $('remove').hidden=false;
    $('zoom').disabled=false; $('rotate').disabled=false; $('pageNumber').disabled=false;
    $('loading').hidden=true;
    await draw();
    stages(2);
    $('filesize').textContent=bytes(file.size)+' · Đã gửi và chuyển thành PDF';
    status('Đã tạo PDF trong '+result.duration+' giây · '+pdf.numPages+' trang. '+(result.batched?'PPTX lớn được chia nhóm rồi ghép PDF; liên kết nội bộ và số slide tự động có thể khác. ':'')+'Có thể chọn chữ và tải PDF. Bản trên máy chủ tự xóa sau khoảng 30 phút.');
  } catch(e) {
    if (token===operation) {
      $('loading').hidden=true; $('empty').hidden=Boolean(pdf);
      if(jobId) $('remove').hidden=false;
      $('filesize').textContent=bytes(file.size)+' · Lần chuyển vừa rồi chưa hoàn tất';
      status(e.message || 'Chuyển đổi thất bại.',true);
    }
  } finally {
    if (token===operation) { clearInterval(timer); locking(false); }
  }
}
async function draw() {
  if (!pdf) return;
  const version=++renderVersion, doc=pdf, n=page;
  renderTask?.cancel(); textTask?.cancel();
  const p=await doc.getPage(n);
  if(version!==renderVersion || pdf!==doc) return;
  const base=p.getViewport({scale:1,rotation});
  const area=$('viewport');
  const pad=parseFloat(getComputedStyle(area).paddingLeft)*2;
  const scale=$('zoom').value==='fit'?Math.max(.1,(area.clientWidth-pad-2)/base.width):Number($('zoom').value);
  const vp=p.getViewport({scale,rotation});
  const dpr=Math.min(window.devicePixelRatio||1,2);
  // Detached canvas prevents a cancelled old render from painting a new page.
  const canvas=document.createElement('canvas'); canvas.id='canvas';
  canvas.width=Math.ceil(vp.width*dpr); canvas.height=Math.ceil(vp.height*dpr);
  canvas.style.width=vp.width+'px'; canvas.style.height=vp.height+'px';
  $('canvas').replaceWith(canvas);
  const layer=document.createElement('div'); layer.id='textLayer'; layer.className='textLayer';
  $('textLayer').replaceWith(layer);
  const paper=$('paper'); paper.style.width=vp.width+'px'; paper.style.height=vp.height+'px';
  paper.style.setProperty('--total-scale-factor',scale*(p.userUnit||1));
  paper.hidden=false; $('empty').hidden=true;
  const rt=renderTask=p.render({canvasContext:canvas.getContext('2d'),viewport:vp,transform:dpr===1?null:[dpr,0,0,dpr,0,0]});
  const tt=textTask=new pdfjs.TextLayer({textContentSource:p.streamTextContent({includeMarkedContent:true}),container:layer,viewport:vp});
  try { await Promise.all([rt.promise,tt.render()]); }
  catch(e) { if(e.name!=='RenderingCancelledException'&&e.name!=='AbortException') throw e; }
  if(version!==renderVersion) return;
  area.scrollTo(0,0);
  $('pageNumber').value=page; $('pageNumber').max=doc.numPages; $('pageTotal').textContent='/ '+doc.numPages;
  $('prev').disabled=page===1; $('next').disabled=page===doc.numPages;
}
async function navigate(n) {
  if(!pdf) return;
  page=Math.max(1,Math.min(pdf.numPages,Math.round(Number(n))||1));
  try { await draw(); } catch(e) { status('Không dựng được trang: '+e.message,true); }
}
$('file').addEventListener('change',e=>pick(e.target.files[0]));
$('sampleDocx').onclick=()=>sample('docx'); $('samplePptx').onclick=()=>sample('pptx');
$('unselect').onclick=()=>{chosen=null;$('file').value='';$('chosen').hidden=true;status('Đã bỏ chọn tệp.');};
$('convert').onclick=()=>{ if(chosen&&!busy){$('consentName').textContent=chosen.name;$('consent').showModal();} };
$('consent').addEventListener('close',()=>{if($('consent').returnValue==='confirm')convert();});
async function remove() {
  const id=jobId; ++operation; clearInterval(timer);
  try {
    await eraseRemote(id); jobId=null;
    await clearPDF(); $('empty').hidden=false;$('loading').hidden=true;locking(false);stages(0);
    if(chosen) $('filesize').textContent=bytes(chosen.size)+' · Phiên đã đóng / xóa';
    status(id?'Đã xóa phiên trên máy chủ và đóng bản PDF.':'Đã hủy. Nếu tệp đang gửi, phiên sẽ được xóa ngay khi máy chủ phản hồi.');
  } catch(e) {status(e.message,true);locking(false);$('remove').hidden=false;}
}
$('remove').onclick=remove; $('cancel').onclick=remove;
$('prev').onclick=()=>navigate(page-1); $('next').onclick=()=>navigate(page+1);
$('pageNumber').onchange=e=>navigate(e.target.value);
$('pageNumber').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();navigate(e.target.value);}};
$('zoom').onchange=()=>navigate(page);
$('rotate').onclick=()=>{rotation=(rotation+90)%360;navigate(page);};
$('theme').onclick=()=>document.body.classList.toggle('dark');
let resizeTimer;new ResizeObserver(()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(pdf&&$('zoom').value==='fit')navigate(page);},180);}).observe($('viewport'));
document.addEventListener('selectionchange',()=>{const s=getSelection();if(s?.anchorNode&&$('textLayer').contains(s.anchorNode)){$('selection').textContent=s.toString().trim()?'Đã chọn: '+s.toString().trim():'Kéo chọn chữ trong PDF để kiểm tra lớp văn bản.';}});
$('dropzone').addEventListener('dragover',e=>{e.preventDefault();if(!busy)$('dropzone').classList.add('dragging');});
$('dropzone').addEventListener('dragleave',()=>$('dropzone').classList.remove('dragging'));
$('dropzone').addEventListener('drop',e=>{e.preventDefault();$('dropzone').classList.remove('dragging');pick(e.dataTransfer.files[0]);});
try {const r=await fetch('/api/health'), h=await r.json();engineOK=h.ok;$('engine').textContent=h.ok?'LibreOffice · sẵn sàng':'Engine chưa sẵn sàng';$('engine').parentElement.classList.toggle('ready',h.ok);if(!h.ok)status('Cần cài LibreOffice trên máy chủ để chuyển đổi.',true);} catch(e){status('Không kết nối được máy chủ demo. Không thể chuyển đổi chỉ bằng HTML này.',true);$('engine').textContent='Mất kết nối engine';}
window.demoState=()=>({busy,jobId,pages:pdf?.numPages||0,page,chosen:chosen?.name,latestStatus});
