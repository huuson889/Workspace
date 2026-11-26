# Workspace nhẹ — GitHub là bản lưu chính

Repo: https://github.com/huuson889/Workspace — nhánh `main`.
Version app hiện hành xem `Keepit-OCR/manifest.json`; thay đổi quy trình lưu ZIP không sửa code/app/engine và không tăng version app.

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

Lệnh tải đủ vendor, kiểm hash, tạo ZIP có manifest ở gốc, kiểm CRC, rồi bỏ vendor cục bộ nếu không có chỉnh sửa. ZIP mặc định ở `Workspace/Keepit-OCR-Zip/Keepit - Optimize Test-v<version>.zip`. Không ghi đè ZIP cùng tên.

**Quy tắc người dùng:** mọi ZIP giao phải được commit/push lên GitHub `main` trong thư mục tương ứng `<thư-mục-nguồn>-Zip`; ví dụ `Keepit-OCR` → `Keepit-OCR-Zip`. Không chỉ lưu cache, không dùng GitHub Releases thay thế. Không tạo lại ZIP cũ đã xóa. Công cụ `pack` tạo gói nhưng không tự commit/push:

```bash
git add --sparse 'Keepit-OCR-Zip/Keepit - Optimize Test-v<version>.zip'
# Commit cùng thay đổi nguồn hoặc commit riêng nếu app đã được lưu.
git commit -m 'Publish Keepit-OCR ZIP v<version>'
git push origin main
```

Thư mục ZIP không nằm trong sparse checkout mặc định để Arena vẫn nhẹ; file vừa tạo cần `--sparse` khi stage. Sau push, đối chiếu blob ZIP với GitHub trước khi bỏ bản local (có thể chạy `python tools/workspace.py bootstrap` để áp lại layout thưa). Không coi việc bỏ bản local đã xác minh là yêu cầu xóa ZIP trên GitHub. Deploy key SSH hiện có đủ quyền Git để đẩy ZIP vào repo; không cần API Releases.

## Giới hạn thực tế

- Đây không phải ổ đĩa mạng: các tệp đã hydrate vẫn chiếm dung lượng trong phiên.
- Cache Git/tệp tạm còn chiếm ổ đĩa sandbox, nhưng `.cache` không nằm trong snapshot Arena. Không lưu công việc duy nhất ở đó.
- Mốc nguồn cố định và kiểm hash tránh phụ thuộc URL nhánh `main` thay đổi âm thầm. Nếu HEAD mới có vendor khác mốc, script dừng yêu cầu duyệt lock.
- Không thay đổi kết quả QA hoặc nâng trạng thái nghiệm thu app; các giới hạn unpacked/ảnh/video của bản 3.5.616 vẫn giữ nguyên.


## Kiểm chứng triển khai

- 7/7 kiểm thử an toàn công cụ: hash Git đúng, phát hiện thiếu tệp, từ chối xóa asset đã sửa/tệp mới và từ chối đường dẫn lock không an toàn.
- Tải lại đủ 804/804 tệp từ GitHub, đối chiếu toàn bộ Git blob hash thành công.
- Đóng ZIP thử 3.5.616 và kiểm độc lập đủ 413 entry, từng byte nội dung khớp lock, CRC hợp lệ và manifest ở gốc. Đã xóa ZIP thử sau kiểm tra; không khôi phục ZIP cũ đã xóa.
- Bỏ vendor và bản gốc, sau đó giả lập mất toàn bộ Git cache. Bootstrap khôi phục metadata partial/sparse thành công, giữ nguyên byte của 200 tệp cục bộ, kể cả thay đổi công cụ chưa commit; không tự tải lại vendor/original.
- Sau cùng: 194 tệp nguồn nhỏ của mốc khóa ở Arena, 220 tệp vendor và 390 tệp bản gốc chỉ ở GitHub khi chưa hydrate. Workspace chiếm khoảng 7.1 MiB theo `du`, Git metadata mới khoảng 213 KiB trong cache.
- Đã xóa cache Git đầy đủ dùng lúc publish (khoảng 131 MiB). Không sửa tệp app, không thay version, không chạy lại nghiệm thu UI/OCR của app vì đây chỉ là thay đổi công cụ lưu trữ.

Private deploy key cũng nằm trong cache và có thể mất giữa các phiên. Khi đó việc đọc repo công khai vẫn hoạt động; muốn push cần tạo/cấp lại deploy key, không chuyển private key vào source để giữ lâu.

## Cập nhật quy tắc ZIP — 2026-11-26

- Bản OCR 3.5.617 được đưa vào `Keepit-OCR-Zip/`, giữ nguyên byte ZIP đã kiểm offline; không đổi version/code app.
- Công cụ đóng gói mặc định dùng thư mục tương ứng trên repo thay vì cache; Git ignore cho phép ZIP trong thư mục `*-Zip`. Quy trình bắt buộc push và kiểm chứng remote trước khi bỏ bản local.
