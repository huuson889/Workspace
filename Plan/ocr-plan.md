# Kế hoạch tích hợp UI OCR demo vào Keep-it

**Trạng thái:** Đề xuất — chưa triển khai, chưa có quyết định nghiệm thu UI hoặc engine OCR.  
**Keep-it hiện tại:** v3.5.612.  
**Version phát hành đích:** v3.5.613 — gộp toàn bộ phạm vi đã chốt vào một bản; không tăng version trung gian. Chỉ tăng version sau khi hoàn tất và nghiệm thu.
**Nguồn tham khảo:** `Keepit-Demo-Zip/Keepit-OCR-demo-2.9.7.33.zip`. Tài liệu trong ZIP nói UI được giữ từ demo 2.9.7.28; bản 2.9.7.33 chủ yếu bổ sung adapter tích hợp và hành vi theo trang khi OCR liên tục/hai trang.

## 1. Mục tiêu

Tích hợp giao diện và luồng OCR của demo vào Documents của Keep-it, giữ nguyên trải nghiệm và tính năng Documents hiện có. UI phải dùng renderer, viewer, theme, ngôn ngữ và kho tài liệu hiện có của Keep-it; không đưa nguyên extension demo hoặc một viewer/kho thứ hai vào ứng dụng.

Đánh giá riêng hai kết quả:

1. **Tương đồng UI:** bố cục, trạng thái, điều khiển và phản hồi tương ứng với demo.
2. **OCR hoạt động trong app:** engine chạy trên trang/tệp đang mở; kết quả được quản lý theo tài liệu và có hành vi được chốt rõ.

Không tuyên bố “đúng 100%” trước khi qua cả tiêu chí hình ảnh lẫn hành vi ở mục 7.

## 2. Phạm vi đã khảo sát

### Demo

- Có hộp cấu hình OCR, chọn trang/phạm vi, ngôn ngữ và chế độ; thẻ tiến độ/kết quả; bảng chữ nhận dạng; khung vùng chữ; chọn/sửa vùng; hủy, chạy lại và xuất TXT/PDF.
- Có ba lựa chọn engine trong UI: Tesseract cho chữ in, PP-OCR “Nhanh” và Fusor “Viết tay”. Tài liệu demo nêu PDF và ảnh là đầu vào OCR; DOCX/PPTX chỉ được hiển thị.
- `index.html`, `app.js`, `glue.js` và `style.css` là một UI độc lập, DOM-bound. `INTEGRATION.md` nói cần chuyển điều khiển sang component của Keep-it trước khi đưa vào màn hình sản phẩm.
- ZIP nặng 59,055,447 byte và bung ra khoảng 108,516,743 byte. Có worker/WASM, model OCR, thư viện PDF và giấy phép phụ thuộc.

### Keep-it v3.5.612

- Documents đã có viewer PDF/ảnh/Office, renderer, lưu tệp cục bộ, lớp chữ PDF và các công cụ chọn chữ/dịch/đọc/ghi chú.
- Nhật ký v3.5.612 ghi rõ chưa triển khai OCR; UI hiện không có luồng chạy OCR.
- Theme Documents lấy từ `lhnSettings.sidebarTheme`; nhãn ứng dụng nằm trong `js/core/languages.js` (en/vi/ko). Demo hiện có chuỗi tiếng Việt và lưu theme riêng trong `localStorage`.

## 3. Ràng buộc tích hợp

- Giữ renderer và kho Documents hiện có làm nguồn sự thật; không mở cùng tệp lần hai, không nhân đôi dữ liệu hoặc viewer.
- Tài liệu demo chỉ xác nhận OCR cho PDF và ảnh. Không hiển thị OCR khả dụng cho DOCX/PPTX nếu chưa có hỗ trợ thực.
- Giới hạn nhập hiện tại của app là 50 MB mỗi tài liệu và 30 MB mỗi ảnh; OCR không được âm thầm vượt các giới hạn này.
- Adapter demo `document-adapter.mjs` yêu cầu PDF renderer cung cấp `sourceDocument`. Renderer Keep-it hiện tại không công khai trường này; gọi `open()` nguyên trạng sẽ không tương thích. Adapter cũng tự chuẩn bị renderer và có thể ghi metadata/tệp vào Store lần nữa.
- Viewer Keep-it hiện có `.docsSource` cho trang đang hiển thị; cần dùng canvas/ảnh của trang đó hoặc API tối thiểu từ renderer hiện hành, không dựng renderer song song.
- Manifest demo có COEP/COOP, worker/WASM và nguồn model ngoài. Không sao chép manifest/permissions của demo; xác định từng yêu cầu, kiểm tra tương thích Chromium/Firefox, quyền mạng, CSP, tải model, hiệu năng và giấy phép trước khi đóng gói.
- Chưa có quyết định về nơi lưu kết quả OCR và việc kết quả có tham gia chọn chữ, dịch, TTS, tìm kiếm hoặc AI hay chỉ xem/xuất.

## 4. Các giai đoạn đề xuất

### Giai đoạn 0 — Chốt phạm vi và chuẩn đối chiếu

- Chốt phiên bản demo làm nguồn UI và danh sách trạng thái/luồng phải giữ.
- Chốt engine cần hỗ trợ: cả ba lựa chọn của demo hay một tập con; ngôn ngữ, loại tài liệu và yêu cầu chạy offline/online.
- Chốt đầu ra OCR: chỉ xem/sửa/xuất, hay còn lưu trong thư viện và dùng được với tính năng chọn chữ/dịch/đọc.
- Ghi nhận giới hạn tệp, quyền mạng, chính sách model, yêu cầu quyền riêng tư và tiêu chí “khớp 100%”.

### Giai đoạn 1 — Tách UI thành phần Keep-it

- Chuyển UI OCR khỏi trang demo thành component được Documents hiện tại quản lý.
- Tái sử dụng toolbar/menu, sheet/modal, panel, nút, theme token và quy tắc dọc/ngang, chạm/chuột của Keep-it.
- Đổi mọi chuỗi UI/aria sang hệ thống nhãn hiện có, đủ en/vi/ko.
- Chuyển theme sang `lhnSettings.sidebarTheme`; không dùng một kho theme riêng.
- Giữ nguyên các màn hình và hành vi Documents ngoài phạm vi OCR.

### Giai đoạn 2 — Kết nối tài liệu và vòng đời

- Nhận tài liệu đang mở, trang hiện tại, trang đang render và trạng thái viewer từ Documents.
- Cấp canvas/ảnh đúng trang cho engine; hỗ trợ từng trang, cuộn liên tục và hai trang mà không OCR nhầm trang.
- Khi OCR chạy, hiện đúng hiệu ứng scan của demo trên **trang engine đang xử lý**, không chỉ trang viewer đang chọn; ở cuộn liên tục/hai trang, hiệu ứng phải chuyển theo page đích của từng lượt OCR.
- Khớp hiệu ứng bề mặt scan của demo (nền/texture trang, lớp chữ scan và vệt ngang); giữ đúng ở theme sáng/tối.
- Khi OCR hoàn tất, bị hủy, lỗi, đổi tệp hoặc đóng viewer, dừng hiệu ứng và xóa trạng thái scan khỏi trang cũ; không để hiệu ứng mắc kẹt hoặc hiện sai trang.
- Xử lý đổi tài liệu/trang, đóng viewer, hủy OCR và giải phóng worker/model/tài nguyên.
- Sửa hoặc thay adapter để khớp renderer hiện hành; tránh parse, fingerprint, import hoặc ghi đè metadata lần hai.

### Giai đoạn 3 — Engine, kết quả và quyền riêng tư

- Chỉ đưa engine đã được chốt vào app; kiểm tra model, worker, WASM, đa luồng, bộ nhớ, offline/online và tương thích trình duyệt.
- Nối tiến độ, lỗi, hủy, chạy lại, kết quả chữ/hộp tọa độ và sửa vùng vào trạng thái Documents.
- Thiết kế lưu kết quả theo document ID/trang/version engine nếu cần; giữ nguyên tệp gốc. Nếu kết quả được đưa vào chọn chữ/dịch/TTS/AI, định nghĩa cách ánh xạ tọa độ và nguồn chữ trước khi làm.
- Kiểm tra giấy phép runtime/model và ghi attribution phù hợp. Không gửi tệp lên dịch vụ ngoài nếu chưa được cho phép và công bố rõ.

### Giai đoạn 4 — Hồi quy, nghiệm thu và phát hành

- Chạy kiểm thử logic/adapter và UI trên extension thật, không chỉ trên demo/mockup.
- Kiểm tra PDF có text layer, PDF scan nhiều trang, ảnh, tệp mật khẩu, giới hạn kích thước, ngôn ngữ được chọn, lỗi tải model, hủy giữa chừng, chọn/sửa vùng, lưu sau reload và không làm hỏng annotations/ghi chú.
- Kiểm tra hiệu ứng scan ở đúng trang engine đang xử lý trong chế độ từng trang/cuộn liên tục/hai trang; xác nhận hiệu ứng chuyển theo từng lượt OCR và được dừng/dọn khi hoàn tất, hủy, lỗi, đổi tệp hoặc đóng viewer.
- Chụp/đo UI tại 1512 px và 390 px, sáng/tối; thêm ảnh 4× cho chi tiết 1–2 px. `console.error` và `pageerror` phải rỗng.
- Báo riêng điều đã xác minh và chưa kiểm được (profile thật, tệp người dùng, thiết bị/trình duyệt thật, cảm giác dùng, tốc độ).
- Chỉ sau khi toàn bộ phạm vi được nghiệm thu mới tăng `manifest.json` một lần từ **3.5.612 lên 3.5.613**; không phát hành/tăng version trung gian. Sau đó cập nhật snapshot và nhật ký mục 5 trong `PROJECT.md`, tạo ZIP đúng tên `Keepit - Optimize Test-v3.5.613.zip` và commit theo quy ước.

## 5. Tiêu chí nghiệm thu đề xuất

- UI nằm trong Documents hiện có, không còn trang OCR demo/DOM độc lập cần mở riêng.
- Các trạng thái và luồng đã chốt có bố cục/điều khiển tương ứng với demo; không mất chức năng Documents hiện tại.
- Hiệu ứng scan khớp demo, chỉ phủ trang engine đang xử lý, chuyển đúng trang trong mọi chế độ xem và được dọn sạch sau khi hoàn tất, hủy, lỗi, đổi tệp hoặc đóng viewer; xác minh ở sáng/tối.
- Nhãn, aria-label, theme và bố cục tuân thủ hệ thống Keep-it.
- OCR chỉ bật với loại tệp/engine thực sự hỗ trợ; kết quả và trạng thái lỗi/hủy không giả lập.
- Không import hoặc lưu trùng tài liệu; kết quả không bị mất sau reload nếu phạm vi đã chốt yêu cầu lưu.
- Đạt kiểm tra ảnh/số đo và kiểm thử chức năng nêu ở Giai đoạn 4; mọi phần chưa kiểm được được ghi rõ.

## 6. Rủi ro và việc cần quyết định

1. **Phạm vi engine:** Tesseract, PP-OCR và Fusor có tài nguyên, model và yêu cầu runtime khác nhau; thêm cả ba làm tăng dung lượng và chi phí bảo trì.
2. **Cách dùng kết quả:** panel/xuất tệp là phạm vi nhỏ hơn; tích hợp kết quả vào chọn chữ, dịch, TTS, tìm kiếm/AI cần thiết kế dữ liệu và ánh xạ riêng.
3. **Tài nguyên và quyền:** model lớn, worker/WASM, tải model ngoài và cấu hình cross-origin có thể ảnh hưởng kích thước gói, quyền, hiệu năng và tương thích trình duyệt.
4. **Bằng chứng UI:** tài liệu demo nhắc script QA bên ngoài ZIP; hiện chưa có ảnh/số đo độc lập chứng minh bản demo và app khớp ở các kích thước/theme bắt buộc.

## 7. Trạng thái hiện tại

- Khảo sát tĩnh đã thực hiện trên ZIP demo và mã nguồn Keep-it v3.5.612.
- Chưa sửa mã nguồn, chưa chạy OCR, chưa chạy extension hoặc kiểm thử trình duyệt; chưa có ảnh/số đo nghiệm thu.
- Trước khi triển khai cần chốt các quyết định ở mục 6 và xác nhận tiêu chí đầu ra OCR ở Giai đoạn 0.
