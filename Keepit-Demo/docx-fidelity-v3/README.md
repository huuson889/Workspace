# DOCX Fidelity Lab v3 — sửa lỗi layout, chưa đạt fidelity Word

Mở **`keepit-docx-fidelity-demo-v3.html`**, một HTML offline tự chứa (~24.8 MB), không cần ZIP, Word, server hoặc thư viện cài trên máy. Có năm mẫu DOCX và PDF tương ứng: Annual Report, Book Report, Small Business Quarterly Report, Weekly Operations Report, HR. PDF chỉ là ảnh tham chiếu trong khung riêng, không tham gia dựng DOCX.

**Không coi phiên bản này là đã sửa xong mọi sai lệch với PDF. App 3.5.634 không thay đổi.**

## Sửa từ v2

1. **Ảnh inline trong ô bảng:** tính vùng giao giữa ảnh và ô sau phân trang, áp dụng CSS clip-path riêng cho ảnh. Ảnh hoàn toàn ngoài ô bị che; không xóa drawing theo tên/ID/nội dung hoặc che cả chữ trong ô. Annual có một ảnh tick inline trùng hình neo nhưng nằm ngoài ô; trước đây nó lộ ra ở mép trang như ảnh báo lỗi của người dùng. V3 che đúng ảnh ngoài ô; năm ảnh tick neo vẫn còn.
2. **Các hình neo cùng đoạn:** loại marker của anchor khỏi normal flow; các hình `wrapTopAndBottom` chia sẻ phần chiều cao bằng chiều cao lớn nhất, không cộng dồn từng hình. Weekly trước đây tính ba thẻ ngang thành ba khối dọc (312 px); v3 giữ một vùng 104 px. Vị trí Y của anchor vẫn được áp dụng riêng khi đặt artwork. Đây là xấp xỉ vùng wrap, chưa là thuật toán exclusion đầy đủ của Word.
3. **Cột:** giữ marker ngắt cột OOXML, chia thành các vùng grid khi có ngắt cột rõ ràng; đọc độ rộng/khoảng cách từng cột thay vì ép mọi cột bằng nhau. Trường hợp không có ngắt cột rõ ràng vẫn dùng CSS columns, có đọc khoảng cách cột được khai báo.
4. **Bảng nổi neo theo text:** xử lý trường hợp tọa độ Y dương, neo vào đoạn tiếp theo; đưa bảng xuống đúng thứ tự hiển thị với khoảng cách theo OOXML thay vì CSS float đẩy tiêu đề sang một dải hẹp. Trong Small Business, Inventory metrics không còn bị bảng đè/làm cao bất thường. Không tuyên bố hỗ trợ mọi kiểu floating table hoặc wrap quanh bảng.
5. **Font dự phòng:** ưu tiên font hệ thống/local tương ứng, sau đó mới dùng fallback. Không còn ép cả Arial/Times New Roman sẵn có thành Carlito như v2. Có alias Liberation khi môi trường Linux thiếu tên font Microsoft. Máy Windows có thể có số đo khác do font thực được chọn.
6. Đọc paragraph mark của đoạn không chữ, kể cả đoạn chứa hình neo; giữ nhóm hình inline, chia bảng theo hàng và các xử lý v2 còn lại.

Các quy tắc engine không kiểm tên tệp, hash mẫu, câu chữ hoặc số trang mong muốn. Tên mẫu và profile mặc định chỉ có trong shell/build, tách khỏi thuật toán layout.

## Giữ HR đã duyệt

HR mặc định dùng **toàn bộ worker v1 nguyên văn**: renderer, engine, CSS và controller. Không ghép các thay đổi v3 vào worker này. SHA-256 của chuỗi worker UTF-8:

`2563897e4b5592cc21f4aa5e9267c2c93bad43fbe241ab1b9951d9a821edaeb9`

Mọi mẫu và tệp mở từ máy đều có thể chọn profile v3/v1/thư viện nền công khai. Chuyển HR sang v3 chỉ là phép thử, không thay baseline đã duyệt. QA xác nhận chuyển về v1 cho report y hệt trước khi chuyển.

## Kiểm chứng thực tế

`qa-results.json`: **131/131 kiểm chức năng và hình học DOM đạt**, không ghi nhận lỗi JS. Không phải điểm tương đồng ảnh, nghiệm thu pixel hoặc nghiệm thu extension.

| Mẫu mặc định | DOCX dựng / PDF | Kết quả được kiểm |
|---|---|---|
| Annual / v3 | 5 / 5 trang | Ảnh tick ngoài ô có vùng giao bằng 0, clip-path inset(100%); neo không bị xóa; có chia bảng theo hàng |
| Book / v3 | 3 / 3 trang | 7 nhóm, 13 textbox, nội dung/nhãn được giữ; điều hướng và PDF tương ứng |
| Small Business / v3 | 6 / 6 trang | Inventory metrics đứng trước bảng, khoảng cách giữa heading và bảng không âm |
| Weekly / v3 | 3 / 3 trang | Không còn 4 trang như v2 trong phép thử ban đầu; phần wrap các thẻ ngang không bị cộng dồn, cột bất đối xứng được dựng |
| HR / nguyên worker v1 | 4 / 4 trang | Giữ thống kê baseline và report khi chuyển lại |

Hai fixture độc lập:
- `independent.docx`: 2 trang, bảng/ngắt trang/chữ Việt-Hàn, literal HTML không thực thi, external relationship bị bỏ; không hiện nhầm PDF mẫu khi mở File.
- `layout-rules.docx`: 1 trang, ba hình chữ nhật neo chung một đoạn, mỗi hình cao 60 px → vùng flow **60**, không phải 180 px; hai cột đúng **192 và 368 px** từ OOXML; bảng nổi không chồng heading. Fixture được tạo từ `make-layout-fixture.py`, không dùng tên/nội dung mẫu người dùng.

Đã kiểm năm mẫu ở khung ngoài 1512 và 390, sáng/tối, không tràn ngang UI, vừa rộng; điều hướng tất cả trang và đúng ảnh PDF của từng trang; đổi profile, zoom/vừa trang/chi tiết; File handler và trở về mẫu. Đo body block có chữ không vượt mép nội dung trong các lần dựng này. Đo không bao gồm mọi chồng lấp drawing/textbox hoặc mọi tình huống clip.

Đã kiểm cú pháp các script nhúng và worker v1 giữ nguyên. Build lặp lại cùng input phải đúng byte. Đã mở tệp cuối trực tiếp bằng file://: Annual dựng 5 trang và chuyển được đến trang 3; chưa kiểm đầy đủ native picker/OS drop, Firefox/Safari, Windows của người dùng hay extension unpacked. Các kiểm responsive chạy trong iframe có chiều rộng tương ứng, không giả làm kiểm thiết bị thật.

## Giới hạn vẫn còn — cần kiểm tiếp

- Annual: hàng KPI vẫn sang trang 2 thay vì cuối trang 1 của PDF; font/giãn dòng và khoảng cách dọc chưa khớp hoàn toàn.
- Book: khoảng cách, tiêu đề, textbox và quote còn xấp xỉ.
- Small Business và Weekly: vị trí chữ/hình, cỡ chữ, khoảng trắng, header/footer và wrapping vẫn có thể lệch đáng kể. Footer/banner neo xa đoạn có thể nằm ngoài trang; **đúng 6/3 trang không phải bằng chứng fidelity**.
- V3 chỉ sửa các lỗi được nêu, không cung cấp engine dàn trang Word. Auto line-height, cân cột, wrap quanh hình/bảng, anchor giữa đoạn, hàng bảng quá cao, chia đoạn theo dòng, widow/orphan và keep-with-next chưa đầy đủ.
- Font trong DOCX và PDF có trường hợp khác nhau. Giữ font nhúng và fallback có cảnh báo, không đổi font theo từng câu để bắt chước PDF. Font hệ thống khác nhau có thể đổi số đo.
- Chưa có bộ so pixel từ ảnh chụp trình duyệt với PDF; các kiểm DOM không thể thay thế việc đó. Không tuyên bố đã xem/so mọi pixel của 21 trang tham chiếu.

## Cách dùng / dữ liệu

Chọn mẫu ở đầu trang; bật Đối chiếu PDF khi cần. Mở DOCX khác từ máy sẽ tắt ảnh tham chiếu để tránh dùng nhầm PDF mẫu. Chỉ nhận DOCX, tối đa 30 MB; không upload tệp qua mạng. Có điều hướng, zoom, vừa rộng/trang, sáng/tối và xuất report JSON.

`inputs.json` ghi URL commit cố định, số byte và SHA-256 từng đầu vào, gồm hai cặp mới tại `c7e8daa1b4335ce8331d1749e1d86d2c8e998f51`. Annual/Book tại `3b1678e57d6e01401cc8bc301ecc7554f4cecac2`, HR tại `94286d971c12fa4577d4872464694ab1d01a9671`, repo huuson889/Workspace, thư mục Uploads.

Mã build và QA ở `source/` (không cần để mở HTML):

```sh
python -m pip install pymupdf
python source/build.py --inputs /path/to/fixtures
# Không truyền inputs: build tải fixture thiếu từ đúng commit ghi trên.
python source/serve-qa.py
# Mở http://localhost:8132/source/qa.html rồi bấm Run QA.
```

Muốn tạo lại fixture tổng hợp: cài thêm python-docx và chạy `python source/make-layout-fixture.py`. Không chạy script này khi chỉ mở demo.

HTML v3 thay v2 trong cây hiện tại theo quy tắc chỉ giữ demo mới nhất. V2 còn trong lịch sử commit `9484928b8d1f20b436aada6df01a6be436b824be`, đường dẫn `Keepit-Demo/docx-fidelity-v2/keepit-docx-fidelity-demo-v2.html`, SHA-256 `112d12df2030aed25d8fb4b730a54128605bb5c9644e5f5222a3320d3762dec2`. V1 còn tại commit `b0ce80c9ba298347522409be44507ecae1f20b4d`; worker v1 cũng nằm nguyên trong v3.

## Thư viện / an toàn

JSZip 3.10.1 (MIT/GPL lựa chọn), docx-preview 0.3.7 (Apache-2.0), Carlito Regular (SIL OFL 1.1); license ở source và nhúng trong HTML. Font/ảnh của DOCX mẫu giữ theo tài liệu người dùng cung cấp; không tuyên bố quyền phân phối lại riêng.

Worker trong iframe sandbox allow-scripts, không allow-same-origin; CSP chặn mạng, form/base và script ngoài; external relationship bị loại. Từ chối DTD/entity, hơn 5,000 ZIP entry hoặc hơn 120 MB dữ liệu mở rộng khai báo; không thực thi macro/OLE/altChunk. Đây không phải kiểm toán an ninh hoặc bảo đảm xử lý mọi DOCX độc hại.

**Demo v2 → v3; app vẫn 3.5.634; không tạo ZIP.**
