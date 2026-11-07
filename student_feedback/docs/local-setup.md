# Chạy trên máy thành viên

Yêu cầu Python 3.13 và Git. Nhánh này chứa source, dữ liệu UIT-VSFC trong
`data/raw`, notebook và model trong `artifacts/serving`; không cần checkout cũ
hoặc huấn luyện lại để chạy web.

## Clone

```sh
git clone --branch source/upload-2026-11-07 https://github.com/nguyenthanhnhan020705/student-feedback-ai.git
cd student-feedback-ai/student_feedback
```

## Windows PowerShell

```powershell
py -3.13 -m venv .venv
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe -m pip install -r requirements/lock.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m feedback_ai --project-root . serve
```

## macOS / Linux

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements/lock.txt
.venv/bin/python -m pip install -e . --no-deps
.venv/bin/python -m feedback_ai --project-root . serve
```

Mở http://127.0.0.1:8003. `/api/health` phải có `ready: true`.
Cài thư viện cần Internet; dữ liệu và model đã có sẵn trong checkout.

## Xem notebook

Mở [simple_data_visualization.ipynb](../data/visualize/simple_data_visualization.ipynb)
trên GitHub để xem biểu đồ đã lưu. Muốn chạy lại, mở thư mục `student_feedback`
trong VS Code, cài extension Python và Jupyter, rồi chọn Python từ `.venv`.
Cài kernel bằng `.venv\Scripts\python.exe -m pip install ipykernel`
(macOS/Linux: `.venv/bin/python -m pip install ipykernel`), rồi Run All.

## Kiểm tra

Sau khi kích hoạt môi trường `.venv`:

```sh
python -m pip install setuptools wheel
python -m feedback_ai --project-root . data validate
python -c "from pathlib import Path; Path('outputs').mkdir(exist_ok=True)"
python -m pytest tests/unit tests/integration tests/parity -q --basetemp=outputs/tmp-pytest
```

`outputs`, `.venv`, cache và `.env` là file sinh trên từng máy, không cần đưa lên Git.
Thông tin nguồn dữ liệu được lưu trong `data/source.json`.
