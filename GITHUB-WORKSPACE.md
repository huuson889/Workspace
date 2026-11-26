# Workspace nhẹ — GitHub là bản lưu chính

Repo: https://github.com/huuson889/Workspace — nhánh `main`.
Ứng dụng vẫn **3.5.616**; thay đổi này chỉ là công cụ phát triển, không sửa code/app/engine.

## Mặc định lưu gì tại Arena?

- Giữ mã first-party, assets nhỏ và tài liệu `Keepit-OCR/`, cùng `Plan/` và công cụ `tools/`.
- `Keepit-OCR/vendor/` chỉ tải khi kiểm thử/chạy extension/đóng gói (khoảng 43.2 MiB).
- Bản gốc `Keep-it/` có trên GitHub; chỉ tải khi cần đối chiếu (khoảng 21.8 MiB).
- `workspace.lock.json` ghi commit, Git blob hash và kích thước của 804 tệp nguồn đã xác minh.
- Thư mục rỗng không được Git lưu. Không tái tạo ZIP cũ đã được người dùng yêu cầu xóa.

**Đây là working copy thiếu thư viện có chủ đích, không phải extension chạy được ngay.**
Không được xóa model/thư viện khỏi GitHub hay thay đường dẫn runtime bằng URL mạng. Gói extension offline vẫn phải đầy đủ.

## Lệnh dùng hàng ngày

Chạy tại `/home/user/Workspace` (Python 3.9+ và Git hỗ trợ partial clone):

```bash
python tools/workspace.py status
python tools/workspace.py hydrate ocr-assets  # trước khi chạy UI/OCR/test hoặc Load unpacked
python tools/workspace.py verify ocr-assets
python tools/workspace.py evict ocr-assets    # sau khi dùng; từ chối nếu tệp đã bị sửa

python tools/workspace.py hydrate original   # lấy bản Keep-it gốc
python tools/workspace.py verify original
python tools/workspace.py evict original
```

- `hydrate all` / `evict all` áp dụng cho hai nhóm tải theo nhu cầu, KHÔNG xóa code đang sửa.
- Có thể chỉnh code first-party bình thường. `verify working` so với mốc khóa, vì vậy sẽ báo khác khi có chỉnh sửa hợp lệ.
- Evict kiểm hash và từ chối tệp mới/đã sửa thay vì xóa mất công việc.
- Nếu thay vendor/model hay cập nhật nguồn khóa, phải duyệt và cập nhật `workspace.lock.json` sau khi lưu an toàn trên GitHub; không tự bỏ qua lỗi hash. App code thay đổi không đồng nghĩa được bỏ kiểm hash vendor.

## Git nhẹ và khôi phục khi cache Arena mất

Root `.git` là tệp trỏ tới `~/.cache/keepit-workspace/repository.git`.
Metadata dùng **partial clone `blob:none`, shallow fetch và sparse checkout**. Không checkout các thư mục không cần.
Cache có thể mất giữa các phiên, không được coi là bản sao lưu. `workspace.lock.json`, script và code nhỏ nằm trong Workspace được giữ lại.

```bash
python tools/workspace.py bootstrap
```

Script dựng lại metadata từ repo công khai mà không cần private key để đọc. Không force checkout, không tự pull đè code đang sửa. Sau khi bootstrap, kiểm `git status` trước khi commit/push.

Nếu đang chỉnh code/vendor, commit và push trước khi kết thúc phiên. Không dùng `git add -A` từ một bản tải thiếu không có sparse metadata hợp lệ; không được coi các file chưa hydrate là yêu cầu xóa trên GitHub.

Lịch sử Git riêng của bản OCR 3.5.614–616 được lưu ở nhánh `archive/keepit-ocr-3.5.616` trước khi bỏ metadata lồng cục bộ. Git metadata không được nhét vào ZIP.

## Đóng gói offline khi cần

```bash
python tools/workspace.py pack --evict
```

Lệnh tải đủ vendor, kiểm hash, tạo ZIP có manifest ở gốc, kiểm CRC, rồi bỏ vendor cục bộ nếu không có chỉnh sửa. ZIP mặc định ở `~/.cache/keepit-workspace/packages/`, không nằm trong snapshot source. Không ghi đè ZIP cùng tên.

GitHub Releases thích hợp lưu ZIP phát hành lâu dài, nhưng **deploy key SSH chỉ cho Git, không cấp quyền API upload Releases**. Chưa tự động tạo Release/upload ZIP; cần đăng nhập API/GitHub CLI phù hợp hoặc người dùng tự upload. Không yêu cầu gửi token vào chat.

## Giới hạn thực tế

- Đây không phải ổ đĩa mạng: các tệp đã hydrate vẫn chiếm dung lượng trong phiên.
- Cache Git/tệp tạm còn chiếm ổ đĩa sandbox, nhưng `.cache` không nằm trong snapshot Arena. Không lưu công việc duy nhất ở đó.
- Mốc nguồn cố định và kiểm hash tránh phụ thuộc URL nhánh `main` thay đổi âm thầm. Nếu HEAD mới có vendor khác mốc, script dừng yêu cầu duyệt lock.
- Không thay đổi kết quả QA hoặc nâng trạng thái nghiệm thu app; các giới hạn unpacked/ảnh/video của bản 3.5.616 vẫn giữ nguyên.
