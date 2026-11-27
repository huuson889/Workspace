# Keepit · PPTX Renderer Demo v2

Bản thử độc lập mở **PPTX bất kỳ từ máy**, thay cho demo v1 chỉ dựng slide 1 nhúng sẵn. Không sửa extension Keepit-OCR 3.5.629.

## Dùng ngay

1. Tải `keepit-pptx-demo-v2.html` về máy, mở bằng Chrome hoặc Edge hiện đại.
2. Bấm **Mở PPTX từ máy** và chọn tệp `.pptx`, hoặc kéo tệp vào vùng mở tệp.
3. Dùng mũi tên Trước/Sau, ô số slide hoặc danh sách số để chuyển trang.
4. Có thể kéo chọn chữ, thu phóng và bật khung đối tượng.
5. Tùy chọn: mở bản PDF xuất từ **cùng tài liệu** để đối chiếu cùng số trang, chồng lớp hoặc đặt cạnh nhau. Demo không tự chuyển PPTX thành PDF, không tự xác nhận hai tệp khớp nhau.

**Phải tải HTML về và mở trong trình duyệt** nếu khung xem trước chặn hộp chọn tệp hoặc module/worker dạng Blob. Không cần cài thư viện hay chạy server. Đã kiểm thử đầy đủ luồng chức năng trong Chromium qua HTTP và mở được mẫu khi dùng `file://`; chưa nghiệm thu luồng chọn tệp ở `file://` trên mọi trình duyệt.

Tệp đọc cục bộ; mã demo không tải tài liệu lên mạng. Khi mở PPTX khác, PDF đối chiếu cũ bị xóa để tránh so nhầm. Nút **Xem mẫu nhúng** vẫn chỉ là slide 1 của mẫu cũ, không đại diện cho tệp vừa chọn.

## Phạm vi thực tế

- Đọc thứ tự slide từ `ppt/presentation.xml` và relationships, không cố định số lượng hay tên slide XML.
- Theo quan hệ từng slide → layout → master → theme; dựng một phần kế thừa vị trí/phông/màu.
- Dựng SVG từ custom geometry gồm move/line/cubic/quadratic/close; nhóm hình và một số preset cơ bản.
- Lớp chữ HTML trong SVG cho phép chọn chữ. Ảnh PNG/JPEG/GIF/WebP nhúng trong PPTX có hỗ trợ cơ bản, crop và transform.
- PDF.js chỉ dựng ảnh đối chiếu, không được dùng thay cho kết quả dựng PPTX.

**Mở được tệp không đồng nghĩa hiển thị giống PowerPoint.** SmartArt, bảng/biểu đồ, media/animation, ảnh EMF/WMF/SVG, ảnh ngoài tệp, công thức hình, một số connector/preset, gradient/effect, bullet, bố cục chữ và định dạng phức tạp chưa đầy đủ. Cảnh báo từng slide chỉ phát hiện một phần tính năng chưa hỗ trợ; không có cảnh báo cũng không bảo đảm chính xác. Phông Pangolin OFL đi kèm là bản thay thế cho mẫu; các phông khác dựa vào máy hoặc fallback, không giải mã toàn bộ phông nhúng của PPTX.

Demo dùng `foreignObject` cho chữ, **không** phải bản vá renderer production và không nới sanitizer của extension. Dịch/Đọc to/Ghi chú của extension không được sửa hoặc tích hợp vào demo này.

## Giới hạn đầu vào

- `.pptx` tối đa 50 MiB; không hỗ trợ `.ppt`, `.pptm`, tệp mã hóa hoặc hỏng.
- Tối đa 12.000 ZIP entry, 160 MiB theo kích thước giải nén khai báo, 50 MiB/thành phần, 2.000 slide.
- XML tối đa 8 MiB/phần; tối đa 15.000 shape và 300.000 điểm được đếm trên slide/layout/master.
- Bỏ qua quan hệ External; từ chối DTD/entity. Không chạy macro hoặc hyperlink trong tài liệu.
- Các giới hạn là biện pháp thử nghiệm, không phải sandbox an toàn tuyệt đối cho tệp độc hại. Tệp lớn/phức tạp vẫn có thể chậm hoặc tốn RAM.
- PDF tối đa 50 MiB; PDF có mật khẩu chưa hỗ trợ. Không kèm toàn bộ CMap/standard fonts/WASM của PDF.js, nên một số PDF có thể thiếu hình hoặc chữ.

## Build lại

Python 3.9+, không cần npm:

```sh
python prepare_deps.py --output /tmp/keepit-pptx-v2-deps
python build.py --deps /tmp/keepit-pptx-v2-deps --output keepit-pptx-demo-v2.html
```

Chạy trong thư mục này. `prepare_deps.py` tải 3 module từ commit GitHub cố định trong `dependencies.json` và đối chiếu SHA256. `build.py` kiểm lại hash trước khi nhúng module, mã first-party và giấy phép vào một HTML. Tải mạng chỉ ở bước chuẩn bị build; HTML hoàn chỉnh không cần tải các thư viện này. `template.html` đã chứa mẫu và phông/data URI nên không phụ thuộc cache để build. `assets/` giữ bản phông và OFL để truy xuất nguồn.

## Kiểm thử và giấy phép

Xem `QA.md`, `qa/report.json` và `THIRD_PARTY_NOTICES.md`. QA kiểm đường đi chức năng, không chứng nhận độ trung thực của 92 slide.
