# Keepit — DOCX Fidelity Lab v1

## Chạy demo

Tải **`keepit-docx-fidelity-demo-v1.html`** và mở trực tiếp bằng Chrome/Edge. Một file HTML tự chứa thư viện, DOCX mẫu và ảnh PDF đối chiếu; không cần cài Word, Python, server hoặc kết nối mạng. Không tạo ZIP cho HTML độc lập này.

- Mặc định mở DOCX HR mẫu. Nút **Mở DOCX** đọc tệp khác trên máy, giới hạn30MB.
- Chuyển trang bằng sidebar/‹›/phím mũi tên; vừa rộng/vừa trang/zoom; giao diện sáng/tối.
- **Đối chiếu PDF** hiển thị ảnh của PDF mẫu ở khung riêng; KHÔNG thay nội dung DOCX bằng PDF. Tắt đối chiếu với file khác.
- Menu bộ dựng có bản cải thiện và thư viện gốc để tái hiện lỗi gộp một trang dài.
- Chi tiết kiểm tra cho biết geometry/cảnh báo và cho lưu JSON.

## Thực hiện và giới hạn

Không thay đổi app3.5.634. Dựng trực tiếp từ OOXML với JSZip3.10.1 và docx-preview0.3.7. Bản thư viện nhúng sửa hàm nhóm section (chỉ bật ở chế độ cải thiện) để tôn trọng section nextPage khi cùng kích thước giấy. Adapter thử nghiệm dựng DrawingML group/custom path/picture/textbox thành SVG + DOM chữ; tận dụng phông nhúng/altName, table indentation, ngắt trang theo section/cached break và đo khối khi tràn. Ảnh neo được đặt lại theo toạ độ trang/đoạn để không bị cắt trong column.

**Không cam kết giống Microsoft Word tuyệt đối.** Đã quan sát đối chiếu: vẫn lệch khoảng cách, giãn dòng/bullet/textbox và một số chi tiết. Giãn dòng lớn trong textbox hiện được xấp xỉ và có cảnh báo, không phải triển khai trọn Word line layout. Đúng4trang không chứng minh pixel/fidelity đúng. Chưa hỗ trợ đầy đủ bảng dài cần tách hàng/ô, đoạn dài cần tách dòng, nested groups/rotations, chart/SmartArt/OLE, textbox phức tạp, trang chẵn/lẻ, header/footer phức tạp hoặc mọi DOCX. Không có engine Microsoft Office, không convert server, không sửa nội dung theo chuỗi tên/báo cáo mẫu, không lấy số trang metadata/PDF để ép đầu ra4trang.

Viewer nằm trong iframe sandbox `allow-scripts` không same-origin, có CSP chặn kết nối ngoài. Bỏ external relationships; không dùng innerHTML với văn bản tài liệu trong adapter DrawingML. Đây là demo nghiên cứu, không phải bộ đọc đã được audit bảo mật cho production.

## Dữ liệu đối chiếu

Lấy từ commit `94286d971c12fa4577d4872464694ab1d01a9671` của repository, thư mục `Uploads`:

- `report_templates_Monthly HR Report Doc.docx`:2.568.082byte, SHA256 `52af949a3927649215b06835bd862bef64a9367de2f7d39413e972344597722b`.
- `report_templates_Monthly HR Report Doc.pdf`:267.303byte, SHA256 `858482655302b2999c8a11b138b54d6d719b8ccc060e4050cc071f8c3eeba27f`.

DOCX được nhúng nguyên byte (bao gồm phông vốn có); PDF chỉ raster thành4ảnh nhúng để đối chiếu. Font thương mại không bị trích thành thư viện font riêng. JSZip dùng MIT; docx-preview dùng Apache2.0. Giữ thông báo và văn bản license trong HTML (`third-party-licenses`).

## Kiểm tra thực tế

-34kiểm tra browser trên chính HTML cuối: DOCX mẫu4trang,1group/6textbox/3ảnh nhóm/5họ phông nhúng/11bảng; nội dung HR/logo/người gửi có trong DOM; chuyển đủ4trang, mỗi lần chỉ hiện1trang.
- Đo iframe1512/390px, mỗi cỡ sáng/tối qua nút demo: không tràn ngang root, fitwidth; đối chiếu PDF riêng, zoom, fitpage, details, chuyển thư viện gốc1trang dài → cải thiện4trang.
- DOCX độc lập2trang (không dùng file HR): mở qua handler đọc File, giữ literal `<img src=x onerror=alert(1)>` dạng text, bỏ external relationship, không gắn nhầm PDF mẫu; mở lại mẫu4trang.
- `console.error`/pageerror trong phạm vi lần kiểm cuối không ghi nhận lỗi; syntax5script outer/worker qua. Trong quá trình phát triển có1tab Chromium crash; không tái hiện trong lần kiểm cuối. Không gọi đây là chứng nhận ổn định mọi profile.
- Mở trực tiếp `file://` trong browser cũng dựng được mẫu4trang; kiểm thủ công đối chiếu trang1/trang4 và layout mobile. Không có bộ ảnh pixel tự động hoặc điểm tương đồng Word. Chưa kiểm native OS file-picker/drop/thiết bị cảm ứng/Firefox/Word thật trên máy người dùng; fixture2trang đi qua handlerFile, không giả nhận là native picker.
- Không chỉnh app, không tăng manifest, không dùng QA/demo để thay nghiệm thu extension.
