# Vận hành và kiểm thử

## Môi trường

Python 3.13.x 64-bit, scikit-learn 1.6.1 (bắt buộc: artifact đã đóng băng được tạo với phiên bản này; loader kiểm tra phiên bản trong metadata).
`requirements/lock.txt` khóa phiên bản; `runtime.txt`, `train.txt`, `test.txt`, `browser.txt` là các nhóm con tham chiếu lock.
Cài: `pip install -r requirements/lock.txt` rồi `pip install -e . --no-deps` (hoặc cài wheel: `python -m build`/`pip wheel . --no-deps`).
Wheel chứa `resources/rules.json` và toàn bộ `web/*`; app chạy được từ bất kỳ cwd nào.

## Trạng thái bundle

`GET /api/health` → `{status, ready, models:{rules,sentiment,topic}, model, contract_version}`.
`ready=false` khi thiếu/hỏng một thành phần; UI hiển thị "Chưa sẵn sàng" và giữ nội dung đã nhập. Thay bundle rồi khởi động lại (không hot reload).

## Kiểm thử

| Nhóm | Thư mục | Cần | Ghi chú |
| --- | --- | --- | --- |
| unit | `tests/unit` | không | fixture tự dựng; 3 test dữ liệu thật cần `TV2_RUN_REAL_DATA=1` |
| integration | `tests/integration` | bundle + dữ liệu | toàn vẹn bundle, phát hiện sửa file, cô lập khỏi mã cũ, quy trình ML, notebook, wheel |
| parity | `tests/parity` | bundle | so với 30 ca bản cũ ghi trong `baseline.json` (tạo bởi `tools/capture_baseline.py`) |
| browser | `tests/browser` | bundle + Chrome + Edge | 3 tab, nhập CSV/XLSX, retry, xuất, mobile |

Thiếu điều kiện → **fail** (không skip), để skip không bị hiểu nhầm là đạt. Máy không có Chrome/Edge: `-m "not browser"`.
Trên Windows nếu thư mục temp hệ thống bị chặn quyền: thêm `--basetemp=outputs/tmp-pytest`.

## Kiểm chứng độc lập

`python tools/verify_standalone.py --output <thư mục mới>` sao chép project (không gồm `.venv`) ra thư mục tạm, tạo venv mới từ lock,
cài bằng wheel, bỏ `PYTHONPATH`, rồi chạy health/predict, `data validate`, `train` + `evaluate` bằng đường dẫn mới và ghi báo cáo JSON.
Ngoại lệ: dữ liệu và bundle được sao chép vào bản tạm vì chúng không nằm trong Git.

## Migration một lần

`tools/capture_baseline.py` (ghi baseline từ bản cũ), `bundle import` (nhập bundle từ checkout cũ) và `tools/migrate_*.py` chỉ phục vụ việc chuyển đổi;
chúng nhận đường dẫn nguồn cũ tường minh. Server/train/evaluate không bao giờ đọc repo cũ.
