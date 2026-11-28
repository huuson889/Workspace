# Keepit · DOCX Fidelity Lab v2 — bản thử nghiệm

**Chưa đạt fidelity hoàn toàn so với PDF. Không tích hợp vào app 3.5.634.**

Tệp để mở: **`keepit-docx-fidelity-demo-v2.html`** — một HTML offline tự chứa, không cần ZIP, Word, cài thư viện hoặc server. Tải về rồi mở bằng Chromium. Bản xem trước trong Arena có thể hạn chế iframe lồng; mở tệp đã tải nếu preview không dựng được.

## Sử dụng

- Chọn **Annual Report**, **Book Report** hoặc **HR · đã duyệt v1** ở đầu trang. Mỗi mẫu chứa DOCX gốc và ảnh của PDF tương ứng.
- **Đối chiếu PDF** mở ảnh tham chiếu ở khung riêng; ảnh này không được truyền vào bộ dựng DOCX.
- Khung DOCX dựng chữ HTML và DrawingML/SVG từ OOXML, không thay bằng ảnh PDF. Có thể bôi chọn chữ.
- **Mở DOCX** nhận tệp khác trên máy, tối đa 30 MB. Khi mở tệp khác, khung PDF mẫu bị tắt để tránh đối chiếu nhầm. Không tự tìm PDF cùng tên trên ổ đĩa.
- Có điều hướng từng trang, zoom, vừa rộng/vừa trang, sáng/tối và báo cáo JSON.

## Giữ bản HR đã duyệt

Mẫu HR mặc định chọn **Adapter v1 đã duyệt HR**. Đây là toàn bộ sandbox worker được lấy nguyên văn từ HTML v1 đã giao, gồm renderer, engine, CSS và controller — không chỉ một số nhánh trong engine v2. Worker UTF-8 SHA-256:

`2563897e4b5592cc21f4aa5e9267c2c93bad43fbe241ab1b9951d9a821edaeb9`

Có thể tự chọn v2 để thử HR, nhưng kết quả v2 **không** thay thế baseline đã duyệt. Lựa chọn profile là điều khiển công khai áp dụng cho mọi DOCX; engine v2 không kiểm tên tài liệu, hash mẫu, câu chữ hay số trang mong muốn để tạo bố cục.

Theo quy tắc chỉ giữ demo mới nhất ở cây hiện tại, v2 thay thư mục v1. Bản HTML v1 đã xác minh vẫn có nguyên trong lịch sử Git tại commit `b0ce80c9ba298347522409be44507ecae1f20b4d`, đường dẫn `Keepit-Demo/docx-fidelity-v1/keepit-docx-fidelity-demo-v1.html` (4,222,202 byte; SHA-256 `cd5ed9d33472e0d35a743f354e410ca08347155657eff481558ba1dd099f5384`). Worker v1 cũng được giữ ngay trong v2.

## Thay đổi v2

- Chuẩn hóa `mc:AlternateContent`: chọn DrawingML được hỗ trợ hoặc fallback, tránh dựng trùng cả hai.
- Đọc nhóm hình `wgp`/`grpSp`, shape `wsp`, ảnh neo và nhóm hình inline; giữ nội dung textbox, đường và ảnh.
- Gắn drawing với marker và đoạn sở hữu; đặt theo page/margin/paragraph/column/cell hoặc vị trí inline sau phân trang, thay cho coi mọi tọa độ là tọa độ trang.
- Chia bảng ở ranh giới hàng tràn, giữ cột và chuyển nội dung tiếp sang trang sau. Không ép tổng số trang.
- Đo line-height theo font và hệ số auto của đoạn; đọc kích thước/phông của paragraph mark rỗng. Đây vẫn là xấp xỉ của trình duyệt.
- Xử lý tab-stop rõ ràng cho các trường hợp left và một số bố cục hai vùng center; chưa phải toàn bộ thuật toán tab Word.
- Nhúng Carlito Regular (OFL) làm dự phòng cho font thường không có trong DOCX. Cảnh báo nêu tên font thay thế. Không tải font qua mạng.
- Vẫn có chế độ thư viện nền không chạy adapter để đối chiếu. Thư viện này có các patch tối thiểu về DOM/dataset của demo, không phải một binary upstream chưa sửa.

## Đã kiểm bằng trình duyệt

`qa-results.json`: **79/79 kiểm chức năng đạt**, lỗi JS ghi nhận rỗng. Các kiểm này KHÔNG chấm điểm tương đồng ảnh.

| Mẫu / profile mặc định | DOCX dựng | PDF tham chiếu | Kết quả đáng chú ý |
|---|---:|---:|---|
| Annual / v2 | 5 trang | 5 trang | 6 ảnh neo; 6 bảng OOXML thành 7 fragment; chia bảng theo hàng có chạy |
| Book / v2 | 3 trang | 3 trang | 7 nhóm, 13 textbox, 10 path, 3 ảnh; nhóm inline chứa Theme 2 đã được lấy lại |
| HR / nguyên worker v1 | 4 trang | 4 trang | Giữ 1 nhóm, 6 textbox, 2 path, 3 ảnh, 5 họ font; đổi v2 rồi trở lại v1 cho cùng report |
| Fixture độc lập / v2 | 2 trang | Không dùng | Bảng, ngắt trang, Việt/Hàn, literal HTML; bỏ external relationship |

Đã kiểm điều hướng từng trang và đúng ảnh PDF tương ứng cho cả ba mẫu; kích thước iframe ngoài 1512 và 390, sáng/tối, vừa rộng, không tràn ngang toàn UI; zoom/vừa trang/chi tiết; đổi profile; mở fixture qua File handler rồi quay về mẫu. Đo không thấy body block có chữ vượt mép nội dung trong các lần dựng này. Đo này không bao gồm mọi tình huống drawing/textbox chồng lấp.

Đã mở trực tiếp tệp cuối bằng `file://` và xác nhận Annual dựng 5 trang. Chưa kiểm đầy đủ cả bộ thao tác trên `file://`, OS file picker hoặc thả tệp thật; File handler được kiểm bằng đối tượng File trong harness. Không có nghiệm thu bằng ảnh pixel, Firefox/Safari, extension unpacked hay thiết bị thật.

## Còn sai / không được coi là hoàn thành

- **Annual:** PDF có hàng tiêu đề KPI cuối trang 1, còn v2 đưa cả hàng này sang trang 2. Đầu trang 3 Operational Excellence, trang 4 Customers and Branding và trang 5 Expand higher-margin đã ở các trang tương ứng, nhưng khoảng cách, đường biên và vị trí nội dung bên trong vẫn lệch.
- **Book:** đã phục hồi nhóm/nhãn bị thiếu và vị trí neo theo đoạn, nhưng khoảng cách dọc, chiều cao tiêu đề, textbox/quote và bố trí tab chưa khớp PDF hoàn toàn. Ba trang đúng không có nghĩa là bố cục đúng.
- PDF Annual ghi Calibri cho nhiều span mà DOCX khai báo font khác (ví dụ Forum/Inter); Forum không có font nhúng. V2 giữ các font có trong DOCX và dùng dự phòng cho font thiếu, không đổi font theo từng câu để bắt chước PDF. Khác biệt font và thuật toán layout vẫn là nguyên nhân quan trọng.
- Chưa có chia một hàng bảng quá cao, chia đoạn qua trang theo từng dòng, lặp header bảng hoàn chỉnh, widow/orphan/keep-with-next đầy đủ, wrapping quanh shape, tất cả tọa độ/rotation/crop/WordArt/chart/equation/VML hay header/footer nâng cao.
- Textbox có giãn dòng lớn và path phức tạp còn xấp xỉ. Renderer HTML không phải engine layout Word; không cam kết pixel-equivalent.

## Nguồn và build

`inputs.json` ghi URL commit cố định, số byte và SHA-256 cho từng DOCX/PDF. Annual và Book từ commit `3b1678e57d6e01401cc8bc301ecc7554f4cecac2`; HR từ `94286d971c12fa4577d4872464694ab1d01a9671`, repo `huuson889/Workspace`, thư mục `Uploads`.

Mã có thể sửa/rebuild ở `source/`. Cần Python và PyMuPDF **chỉ khi build**, không cần để mở HTML:

```sh
python -m pip install pymupdf
python source/build.py
# Hoặc dùng các tệp đầu vào đã có:
python source/build.py --inputs /path/to/fixtures
```

Build thiếu fixture sẽ tải đúng URL commit đã ghi; không tải khi người dùng mở HTML. Ảnh PDF chỉ được tạo ở bước build và nhúng vào phần dữ liệu tham chiếu của shell ngoài. Worker DOCX nhận bytes DOCX và lựa chọn adapter, không nhận ảnh/PDF.

Chạy lại QA tùy chọn: `python source/serve-qa.py`, mở `http://localhost:8132/source/qa.html`, bấm Run QA. Server QA chỉ phục vụ kiểm local, không phải thành phần của tệp giao. Fixture `source/independent.docx` là dữ liệu tổng hợp, không phải tài liệu người dùng.

JSZip 3.10.1 (MIT/GPL lựa chọn), docx-preview 0.3.7 (Apache-2.0), Carlito Regular (SIL OFL 1.1); license có ở `source/` và nhúng trong HTML. Font/ảnh của DOCX mẫu giữ theo tài liệu người dùng cung cấp; không tuyên bố giấy phép phân phối lại riêng cho chúng.

## An toàn / giới hạn

Sandbox iframe `allow-scripts` không `allow-same-origin`; CSP bên trong chặn kết nối mạng, form/base URL và script ngoài. Bỏ external relationship; từ chối XML DTD/entity, hơn 5,000 ZIP entry hoặc hơn 120 MB dữ liệu mở rộng khai báo. Không chạy macro/OLE/altChunk. Đây là biện pháp phòng thủ demo, **không phải kiểm toán an ninh** hoặc đảm bảo xử lý mọi DOCX độc hại.

**Demo v1 → v2; app vẫn 3.5.634, không sửa nguồn app hoặc tạo ZIP.**
