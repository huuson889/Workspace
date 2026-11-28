# DOCX Fidelity Lab v4 — sửa textbox Weekly

Mở **keepit-docx-fidelity-demo-v4.html**: một HTML offline tự chứa, không cần ZIP/Word/server. Mặc định mở Weekly Operations để kiểm lại các lỗi người dùng chỉ ra. Có đủ Annual, Book, Small Business Quarterly, Weekly và HR; PDF chỉ làm tham chiếu riêng, không thay DOCX. Chữ vẫn là chữ có thể chọn, không dùng ảnh/PDF để giả dựng tài liệu.

**App 3.5.634 không thay đổi. Chưa nghiệm thu khớp Word từng pixel.**

## Sửa trong v4

- Đọc DrawingML alpha, alphaMod, alphaOff và tint/shade. Nền ngày Weekly có alpha 9999/100000 (~10%), không còn bị tô đặc cùng màu chữ nâu.
- Đọc độ co ngang `w:w` và tracking `w:spacing` trong textbox. Đo advance của chữ đã chọn font rồi mới ngắt dòng; scale phần vẽ nhưng giữ advance tương ứng và chữ selectable. Tracking áp dụng sau co ngang, không bị co hai lần.
- Run không chỉ định font kế thừa font paragraph/document; chờ font tải trước khi đo. Không dựa vào font mặc định sai của SVG foreignObject.
- Textbox giữ paragraph spacing, indent và line-height; thuật toán đo/ngắt theo từ vẫn là xấp xỉ trình duyệt, không phải Word shaping đầy đủ.
- Giải theme alias bg1/tx1/bg2/tx2 và sysClr.lastClr; đọc default adjustment roundRect. Viền logo trắng/bo góc được vẽ lại từ thuộc tính DOCX.

Trong môi trường Chromium đã kiểm: tiêu đề Weekly có hai dòng **Weekly / Operations Report**; logo **Fortune / Insurance**; ngày **Jan 1, 2035** một dòng, màu chữ rgb(153,92,0), nền rgba(153,92,0,0.09999); frame trắng 1.25 pt, có bán kính bo góc.

Engine không kiểm tên file, nội dung câu, hash, số trang đích hoặc chèn ngắt dòng riêng cho Weekly. Tên mẫu/profile chỉ thuộc shell/build. Giữ các sửa chung v3: clipping ảnh inline theo ô, shared-anchor flow, cột không đều/ngắt cột, bảng nổi neo text, fallback font.

## Giữ HR đã duyệt

HR mặc định dùng toàn bộ worker v1 nguyên văn, không ghép engine v4. SHA-256 chuỗi UTF-8:

`2563897e4b5592cc21f4aa5e9267c2c93bad43fbe241ab1b9951d9a821edaeb9`

Có thể chủ động đổi profile để thử nhưng quay về stable phải khôi phục report baseline.

## Kiểm chứng và giới hạn

`qa-results.json`: **137/137 kiểm chức năng/hình học DOM**, không ghi nhận lỗi JS. Chạy chính standalone HTML trong iframe Chromium, không phải mock renderer. Năm mẫu giữ số trang quan sát được: Annual 5, Book 3, Small Business 6, Weekly 3, HR 4. Không ép số trang trong engine. Kiểm điều hướng tất cả trang, reference tương ứng, responsive 1512/390 sáng/tối, fit/zoom, profile và File handler. Hai fixture độc lập kiểm cột/anchor/bảng nổi và literal HTML/external relationship.

Sáu kiểm mới xác nhận dòng tiêu đề, hệ số co ngang, dòng/màu ngày, alpha nền, dòng logo và màu/độ dày/bo góc frame. Đây là **kiểm DOM/thuộc tính vẽ**, không phải phép so ảnh. Browser inspection đã dùng trong quá trình phát triển nhưng công cụ lần này không trả ảnh chụp để lưu/đối chiếu; **không khẳng định đã so pixel crop với Word/PDF**, không dùng 137 PASS làm bằng chứng toàn tài liệu giống Word. Cần người dùng kiểm trực quan bản HTML trên máy/font thực tế.

Còn giới hạn v3: Annual KPI vẫn sang trang 2 thay vì cuối trang 1 PDF; Book spacing/quote/textbox còn xấp xỉ; Small Business thiếu chart và có thể lệch banner/header/footer. Font hệ thống ảnh hưởng số đo. Auto line-height/wrap, chia đoạn theo dòng, widow/orphan, keep-with-next, anchor/exclusion, cân cột và floating table chưa đầy đủ. Đúng số trang không chứng minh fidelity. Chưa nghiệm thu Windows/Firefox/Safari, native OS drop/picker hay extension unpacked. V4 không được coi là engine thay thế Word đã hoàn chỉnh.

## Build / QA

`inputs.json` giữ URL commit cố định, kích thước và SHA-256 của năm cặp DOCX/PDF. `artifact.json` ghi hash HTML cuối.

```sh
python -m pip install pymupdf
python source/build.py --inputs /path/to/fixtures
# Không truyền --inputs: tải input thiếu từ commit cố định.
python source/serve-qa.py
# http://localhost:8135/source/qa.html → Run QA
```

Fixture layout-rules có thể tạo lại bằng source/make-layout-fixture.py (cần python-docx). Không cần để mở demo. Build cùng đầu vào phải đúng byte; script nhúng được kiểm cú pháp riêng.

V3 lưu trong lịch sử commit `54e49f82d9e0f0aac970f49d60ef169d109d5916`, đường dẫn `Keepit-Demo/docx-fidelity-v3/`, toàn bộ 21 file đã xác minh remote trước khi bỏ bản hiện hành. V2 tại `9484928b8d1f20b436aada6df01a6be436b824be`; v1 tại `b0ce80c9ba298347522409be44507ecae1f20b4d`.

## Thư viện / an toàn

JSZip 3.10.1 (MIT/GPL lựa chọn), docx-preview 0.3.7 (Apache-2.0), Carlito Regular (SIL OFL 1.1); license trong source/HTML. Asset tài liệu mẫu giữ theo dữ liệu người dùng cung cấp.

Không upload DOCX qua mạng. Worker iframe sandbox allow-scripts, không allow-same-origin; CSP chặn mạng/script ngoài; external relationships bị loại; từ chối DTD/entity, hơn 5,000 ZIP entries, hơn 120 MB expanded khai báo hoặc input hơn 30 MB. Không chạy macro/OLE/altChunk. Không phải kiểm toán an ninh.
