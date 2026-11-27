# Keepit Office → PDF Lab · v1

**Demo chạy thật:** chọn `.docx` / `.pptx` → xác nhận gửi → LibreOffice trên máy chủ chuyển PDF → trình duyệt mở bằng PDF.js có lớp chữ.

Đây là web app có backend, **không phải HTML độc lập mở bằng `file://`**, cũng chưa phải extension. Không sửa Keepit-OCR 3.5.629. Chưa nối các công cụ Dịch/Đọc to/Ghi chú của Keepit vào viewer thử nghiệm này.

## Thử trong Arena

Mở **Live Preview “Keepit · Office sang PDF”** khi máy chủ còn chạy. Chọn tệp riêng hoặc dùng hai nút DOCX/PPTX mẫu. Chọn tệp chưa gửi dữ liệu; nút Chuyển sang PDF mở hộp xác nhận, chỉ sau Đồng ý mới tải tệp lên. Tệp mẫu là tài liệu kiểm thử tự tạo, không giả lập kết quả chuyển đổi.

- Chuyển trang bằng mũi tên hoặc ô số.
- Thu phóng, xoay, kéo chọn chữ trên PDF thật.
- Tải PDF đã tạo hoặc bấm thùng rác để xóa phiên.
- Khi chuyển tệp mới, phiên cũ bị xóa.

Địa chỉ preview phụ thuộc phiên Arena và quyền truy cập của nền tảng; không phải dịch vụ triển khai vĩnh viễn. Đường dẫn e2b trực tiếp thiếu token có thể trả 403: dùng Live Preview do Arena cung cấp, không tắt cơ chế truy cập nền tảng.

## Chạy trên máy của bạn

Hỗ trợ Linux với LibreOffice và libseccomp2. Ví dụ Debian/Ubuntu:

```sh
chmod +x setup.sh run.sh
./setup.sh
./run.sh
# Mở http://127.0.0.1:8120
```

`setup.sh` có cài package hệ thống bằng sudo và package Python từ mạng; xem nội dung trước khi chạy. Script không gửi tài liệu. Nếu đã có môi trường phù hợp:

```sh
python -m pip install -r requirements.txt
python server.py --host 127.0.0.1 --port 8120
```

Muốn preview qua proxy: `python server.py --host 0.0.0.0 --port 8120`. Frontend dùng đường dẫn API tương đối cùng origin, không gọi localhost từ trình duyệt của người xem. Phiên bản LibreOffice dùng trong QA: **25.2.3.2**. PDF.js và worker được đóng gói trong `public/vendor`, không tải CDN lúc đọc. Cần có đủ phông trên máy chủ; `setup.sh` cài các phông thay thế Office phổ biến và Pangolin OFL kèm gói. Không cài font hệ thống trực tiếp từ tài liệu người dùng.

## Cách chuyển PPTX lớn

Máy chủ thử nghiệm có ngân sách RAM nhỏ. Tệp PPTX trên 12 slide được chia tạm thành nhóm 8 slide bằng cách giới hạn danh sách slide/master trong presentation XML. Nội dung XML từng slide không bị vẽ lại bằng renderer JS. LibreOffice chuyển từng nhóm; pypdf ghép các PDF theo đúng thứ tự. Mỗi nhóm phải xuất đúng số trang; không trả PDF một phần nếu có nhóm thất bại. Slide ẩn cũng được xuất để khớp danh sách đầu vào.

**Đánh đổi của chế độ nhóm:** không bảo đảm giữ hyperlink xuyên nhóm, section/custom show, số trang/slide tự động, bookmark hoặc toàn bộ cấu trúc tagged-PDF. Demo có thông báo khi dùng chế độ này. Không xem đây là phép chuyển không mất thông tin. Muốn production phải kiểm thử thêm hoặc dùng worker đủ RAM để chuyển toàn bộ trong một lần.

## Dữ liệu và giới hạn

- Chỉ DOCX/PPTX, tối đa 50 MiB; ZIP ≤200 MiB khai báo sau giải nén, ≤12.000 entry, ≤50 MiB/thành phần và ≤8 MiB/XML. PPTX ≤2.000 slide.
- Từ chối tệp ZIP/XML hỏng, DTD/entity, macro/OLE và quan hệ tài nguyên ngoài trừ hyperlink. Vì vậy có tài liệu Office bình thường nhưng chứa ảnh/link ngoài cũng bị từ chối trong demo.
- Tối đa 1 worker chuyển đổi, 3 tác vụ đang tải/chờ/chuyển, 12 phiên trong bộ nhớ.
- Giới hạn chuyển khoảng 180 giây tổng, 120 MiB PDF đầu ra; engine có CPU/không gian địa chỉ/data/file-size limit. Đây là biện pháp hạn chế, không phải quota cgroup hay bảo đảm chống DoS tuyệt đối.
- Mỗi job dùng thư mục tạm riêng và profile LibreOffice riêng. Nguồn, profile và các batch tạm bị xóa khi tác vụ kết thúc. PDF giữ khoảng 30 phút từ khi xong, quét xóa mỗi 30 giây; truy cập sau hết hạn cũng kích hoạt dọn. Có thể xóa sớm bằng nút thùng rác.
- Dừng server bình thường bằng SIGINT/SIGTERM sẽ dừng worker và dọn thư mục hiện tại. Crash/SIGKILL/mất điện không bảo đảm chạy cleanup; triển khai thật cần TTL volume riêng và bộ dọn độc lập.
- PDF đã tải về hoặc đang nằm trong bộ nhớ trình duyệt không bị thu hồi khi máy chủ xóa. Đóng PDF trong giao diện chỉ giải phóng bản trong trang này.
- Không lưu lịch sử thư viện và không cache tài liệu lâu dài trong demo. Tải lại trang sẽ mất liên kết phiên ở UI; server vẫn xóa theo TTL.

## Bảo mật: chỉ dùng để thử nghiệm với tài liệu tin cậy

Demo không có đăng nhập. URL job ngẫu nhiên đóng vai trò capability: ai có URL có thể lấy/xóa job, nên không chia sẻ URL. Không có API liệt kê tất cả job. Không ghi nội dung, tên tài liệu hay URL job vào access log. Backend không gửi tài liệu đến API chuyển đổi bên thứ ba.

Tiến trình LibreOffice chạy qua `engine.py`: seccomp chặn tạo socket AF_INET/AF_INET6/AF_PACKET, để lại UNIX socket cục bộ; từ chối chạy trên hệ thống thiếu libseccomp thay vì fallback không hạn chế. Profile đặt mức bảo mật macro cao; đầu vào có macro/OLE bị từ chối trước.

**Chưa phải sandbox đầy đủ:** LibreOffice vẫn có quyền filesystem của user chạy server, Python HTTP server không phải hardened production gateway, và engine xử lý tài liệu là bề mặt tấn công. Không đặt bí mật/khóa trong user/container phục vụ engine thật. Production cần worker không đặc quyền trong container/VM riêng, read-only root, cgroup, không network, xác thực, rate limiting, upload proxy, cleanup độc lập và cập nhật engine. Không đưa tài liệu nhạy cảm lên bản demo công khai.

## Chất lượng

Mở/chuyển được không bảo đảm giống Microsoft Office. Thiếu font, SmartArt, biểu đồ, các kiểu layout, công thức và field có thể khác. PPTX là slide tĩnh, không giữ animation/video tương tác. DOCX có thể phân trang lại. Nếu chữ gốc là ảnh, PDF vẫn là ảnh; demo không chạy OCR. Không đóng gói toàn bộ CMap/standard fonts/WASM bổ sung của PDF.js nên một số PDF đặc biệt có thể render thiếu.

Xem `QA.md` cho kết quả và phạm vi. Bản PDF đối chiếu do người dùng từng gửi không được dùng để giả làm đầu ra chuyển đổi.

## Cấu trúc

- `server.py`: upload, preflight, hàng đợi, job, TTL, route PDF và static.
- `engine.py`: launcher LibreOffice có resource limit và seccomp.
- `pptx_batches.py`: chia danh sách slide/master cho chế độ RAM thấp.
- `public/`: giao diện HTML/CSS/JS, PDF.js, hai mẫu Office tự tạo.
- `public/qa.html`, `public/qa.js`: kiểm thử browser bằng mẫu tự tạo, chỉ chạy khi bấm nút.
- `tests/check_api.py`: integration/preflight checks; cần thêm PyMuPDF khi chạy test.
- `tests/make_samples.py`: tạo lại mẫu; cần python-docx/python-pptx, không cần khi chạy app.
- `fonts/`: Pangolin và OFL; `requirements.txt`: thư viện Python của app.

## Giấy phép bên thứ ba

PDF.js: Apache-2.0, văn bản tại `public/vendor/LICENSE-pdfjs.txt`. Pangolin: SIL OFL 1.1, `fonts/OFL.txt`; nguồn Google Fonts Pangolin project. LibreOffice là dependency hệ thống, không nhúng binary trong ZIP; xem https://www.libreoffice.org/about-us/licenses/ . pypdf và lxml được cài theo requirements, giấy phép do các package tương ứng cung cấp (BSD-family); không vendor code package vào gói này. Các tài liệu mẫu không chứa dữ liệu cá nhân.
