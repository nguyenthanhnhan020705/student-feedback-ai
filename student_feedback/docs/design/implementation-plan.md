# Standalone Student Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Tạo student_feedback/ chạy độc lập, gồm ứng dụng hiện tại và quy trình dữ liệu, huấn luyện, đánh giá.

**Architecture:** Package feedback_ai theo src layout, tài nguyên web/rules đóng gói cùng package. Serving sử dụng bundle frozen có manifest; training ghi candidate riêng. Module compatibility chỉ phục vụ tải pickle cũ, không phụ thuộc source bên ngoài project.

**Tech Stack:** Python 3.13, FastAPI, Pydantic, scikit-learn 1.6.1, HTML/CSS/JS, openpyxl, pytest, Playwright; giữ phiên bản lock hiện tại.

**Spec:** ../specs/2026-11-04-standalone-project-design.md (đã duyệt).

## Global Constraints

- Làm trong worktree .local-tools/integration-p0, nhánh chore/project-cleanup; không tạo Git repo lồng nhau.
- Chỉ thêm student_feedback/ và tài liệu thiết kế/kế hoạch; giữ nguồn cũ nguyên vẹn.
- Giữ API 3.0, UI 3 tab, 5000 codepoint/phản hồi, 500 phản hồi, 5 MiB/file.
- Giữ byte artifact/rules và logic preprocessing, labels, selection; không train lại để thay serving.
- Dữ liệu/model local ignored; không tự tải hay đưa payload lên Git.
- Chạy bản mới cổng 8003 khi đối chiếu với bản cũ 8002.
- Mọi task commit riêng sau kiểm tra; không merge main. Không tự suy ra quyền push từ việc commit kế hoạch.

## Review Focus

- Pickle tham chiếu module cũ: phải tải được trong subprocess chỉ cài package mới (task 2).
- Cwd khác và wheel thiếu static assets: package phải tìm được rules/web/template (tasks 1, 7).
- Input Unicode, nhiều dòng, dấu bằng đầu ô: giữ validation và cell type Excel (task 4).
- Tab đổi khi request pending hoặc retry lỗi: không gán nhầm dữ liệu/ghi đè kết quả (task 5).
- Train ghi vào serving hoặc test dùng test split để chọn winner: từ chối ghi đè, selection chỉ dùng validation (task 6).

## File map và conventions

Tất cả đường dẫn dưới đây tương đối với student_feedback/ trừ nguồn đọc đã ghi rõ. Mỗi package Python có __init__.py. API/services/inference/data/training/evaluation/io/common theo spec; tests chia unit/integration/browser/parity. Dùng package resources cho web/rules; cấu hình đường dẫn dữ liệu bên ngoài package qua project root hoặc CLI option.

CLI công khai: `feedback-ai serve`, `bundle import`, `data import`, `data acquire`, `data validate`, `data eda`, `train`, `evaluate`, `experiment`. Serve nhận --project-root và --port (8003 mặc định). Data/train/evaluate nhận --project-root và đường dẫn input/output explicit, resolve tương đối project root. Không tự search parent repo.

Lệnh verification sau task 1 dùng Python của venv riêng `.venv` trong project mới: `python -m pytest <test path>`. Khi chưa có venv dùng Python 3.13 hiện có để bootstrap. Không coi kết quả test từ repo cũ là test package mới.

### Task 1: Baseline và package độc lập

**Files:** Create pyproject.toml, requirements/{runtime,train,test,browser,lock}.txt, .gitignore, README.md, src/feedback_ai/{config,cli}.py, src/feedback_ai/common/hashing.py, tools/capture_baseline.py, tests/unit/test_config.py, tests/parity/cases.json. Local generated outputs/migration/baseline.json ignored.

**Interfaces:** `Settings.from_root(root: Path) -> Settings`, fields root, data_dir, artifacts_dir, outputs_dir; `digest(path: Path) -> str`; `cli.main(argv: list[str] | None = None) -> int`.

- [ ] Ghi hash source cũ/artifact/rules trước khi thay đổi; capture API corpus gồm đa chủ đề, hỗn hợp, thông tin, emoji, quotes, phủ định, lỗi input. Script baseline nhận explicit --legacy-root/--legacy-url, chỉ phục vụ migration.
- [ ] Viết test `test_paths_do_not_follow_cwd`: đổi cwd rồi assert Settings paths vẫn dưới root; `test_missing_root_is_reported`: báo lỗi rõ ràng, không fallback source cũ.
- [ ] Chạy `python -m pytest tests/unit/test_config.py -q`, xác nhận thất bại vì package chưa có.
- [ ] Tạo src package, CLI help, project config và nhóm dependency giữ lock cũ; thêm openpyxl/et_xmlfile theo requirements-batch. Khai báo package data web/resources và compatibility packages.
- [ ] Tạo venv riêng, cài editable package và dependencies; chạy test config và CLI --help. Ghi phiên bản/pip check thật.
- [ ] Commit `build: initialize standalone feedback project` với danh sách file task này.

### Task 2: Bundle model và tương thích artifact

**Files:** src/feedback_ai/inference/{bundle,model_loader,signals,policy}.py, common/json_io.py, data/preprocessing.py, tools/import_bundle.py, tests/integration/test_bundle.py, tests/unit/test_bundle_manifest.py; src/ml/preprocessing.py và src/reports/*.py chỉ khi pickle yêu cầu.

**Interfaces:** `import_bundle(source_root: Path, destination: Path) -> Path` trả manifest path; `load_bundle(manifest: Path) -> FrozenModels`; FrozenModels có ready: bool, status: dict, `predict(text: str) -> dict` tương đương demo_v2.DemoService.predict. `extract_signals(pipeline, texts: list[str], task: str) -> list[dict]` giữ semantics hiện có.

- [ ] Viết tests thiếu artifact, hash sai, version sai và `test_frozen_prediction_matches_legacy`; test subprocess chỉ có package mới trong sys.path và xác nhận module __file__ không ở source cũ.
- [ ] Chạy test để xác nhận RED, phân biệt lỗi thiếu fixture với lỗi module chưa triển khai.
- [ ] Inventory artifact callbacks và receipt graph. Chuyển logic loader từ backend/model_service.py, signals từ reports/ct5_selective_prediction.py, policy từ demo_v2/policy.py; chuyển normalize/unaccent thật vào package mới.
- [ ] Import bundle bằng allowlist, copy artifact/metadata/config/threshold/receipt cần thiết; ghi manifest tương đối, kiểm tra checksum và provenance gốc. Không sửa receipt/checksum hoặc deserialize tùy tiện để tìm dependencies.
- [ ] Tạo shim tối thiểu cho các callback được phát hiện; không sys.path.insert, không import code cũ. Lưu manifest mapping source digest và vị trí mới.
- [ ] Chạy tests unit và integration với bundle thật; kiểm tra hash artifact không đổi. Commit `refactor: isolate frozen model bundle and inference`.

### Task 3: Engine phân tích và API đơn

**Files:** inference/{detector,ontology}.py, resources/rules.json, services/analysis.py, api/{app,schemas,errors}.py, api/routes/{health,predict}.py, tests/parity/test_prediction.py, tests/unit/test_api_errors.py.

**Interfaces:** `AnalysisService(bundle: FrozenModels, rules_path: Path)`, ready/status, `analyze(text: str) -> tuple[dict, dict]`, `predict(text: str) -> dict`; `create_app(settings: Settings, service=None) -> FastAPI`.

- [ ] Viết parity test assert output/HTTP của corpus task 1 bằng bản cũ, và tests 5000/5001 codepoint, surrogate, malformed JSON, extra field, thiếu model, inference exception.
- [ ] Chạy tests mới, xác nhận RED.
- [ ] Chuyển detector/ontology/service từ demo_v3, bảo toàn rules byte/hash, audit-only CT4 và thứ tự core topics. Chuyển API schemas/error handlers đúng mã/JSON hiện tại.
- [ ] Service không nạp model hoặc khởi động server như side effect khi import module; app factory nạp một lần theo cấu hình.
- [ ] Chạy parity, lỗi, health readiness; kiểm tra bản cũ hash không đổi. Commit `refactor: port analysis engine and API without behavior changes`.

### Task 4: Import, batch và export Excel

**Files:** io/{imports,exports}.py, services/aspects.py, api/{batch_schemas.py,routes/batch.py}, tests/unit/test_file_io.py, tests/parity/test_batch.py.

**Interfaces:** `parse_upload(filename: str, raw: bytes) -> dict`, `aspects(clauses: list[dict]) -> dict`, `workbook(name: str, rows: list[dict]) -> bytes`; Row/ExportRequest schemas giữ fields/constraints của demo_v3/batch.py.

- [ ] Viết tests bảo toàn duplicate/blank/multiline/ID/source_row; 5 MiB, 500 rows, 100 columns, 10 sheets, 25 MiB uncompressed; tests XLSX formula text/control characters.
- [ ] Viết parity export so sánh sheet names, cell values/types, summary denominator và aspects, không so raw ZIP hash. Chạy RED.
- [ ] Tách đúng các hàm từ demo_v3/batch.py và đăng ký /api/v3/import, /analyze-row, /export; giữ streaming size cap, threadpool và lỗi hiện có.
- [ ] Chạy `python -m pytest tests/unit/test_file_io.py tests/parity/test_batch.py -q`; đối chiếu API thật với bundle. Commit `refactor: separate feedback import and Excel export`.

### Task 5: Giao diện 3 tab và kiểm thử browser tự chứa

**Files:** src/feedback_ai/web/{index.html,styles.css,batch.css,mau-phan-hoi.xlsx}, web/js/{api,single,tabs,batch_state,batch_import,batch_render,batch_actions}.js, tests/conftest.py, tests/browser/{test_single,test_tabs,test_batch}.py.

**Interfaces:** API URLs/JSON giữ task 3–4; `createBatchController(root: HTMLElement)` quản lý sessions paste/file, render và event handlers; entry module gọi controller một lần. JS module API export request/checkHealth/predict và LABELS. Assets phục vụ cùng origin qua allowlist/package resources.

- [ ] Chuyển acceptance hiện có vào tests mới, fixture server tự chọn port và browser fixture ở conftest.py; bỏ import test_ui đã mất. Assertions dùng UI/nhãn hiện tại.
- [ ] Thêm tests pending request + sửa input, tab state isolation, keyboard, lỗi health và retry, stop/resume, filtered export, import tự nhận diện và file nhiều sheets cần chọn; xác nhận RED.
- [ ] Copy UI hiện tại, tách JS theo trách nhiệm, định dạng code dễ đọc; không đổi layout/copy hoặc thứ tự nghiệp vụ. Đóng gói template và assets.
- [ ] Chạy browser tests Chrome/Edge sẵn có, desktop/mobile; xem screenshots, kiểm tra không tràn ngang trang và table scroll vẫn dùng được.
- [ ] Commit `refactor: package three-tab frontend and browser tests`.

### Task 6: Data, training, evaluation và research workflow

**Files:** data/{acquire,loader,validate,eda}.py, training/{sentiment,topic,selection,artifacts}.py, evaluation/{metrics,compare,errors}.py, training/experiments/{baseline,class_weights,word_char,augmentation,selective}.py, configs/{baseline,experiments}.json, notebooks/{01_eda,02_sentiment,03_topic}.ipynb, tests/unit/{test_data,test_training,test_evaluation,test_experiments}.py, tests/integration/test_ml_workflow.py.

**Interfaces:** `load_dataset(data_dir: Path) -> dict[str, DataFrame]`; `train(task: str, data_dir: Path, output_dir: Path, manifest: Path) -> dict`; `evaluate(task: str, artifact: Path, data_dir: Path, output_dir: Path) -> dict`; `run_experiment(name: str, config: dict, output_dir: Path) -> dict`. CLI dispatch data/train/evaluate/experiment vào các hàm này, bắt buộc output mới, không serving.

- [ ] Chuyển tests data/labels/preprocessing/metrics hiện tại; thêm tests train chỉ fit train, selection chỉ đọc validation, output existing/serving bị từ chối, dataset checksum/split invalid báo lỗi. Chạy RED.
- [ ] Chuyển loader/acquisition/EDA từ ml và docs/data; tách training/evaluation dùng shared metrics và metadata. Bảo toàn seed/params/tie-break/normalization và mappings.
- [ ] Chuyển logic CT1–CT5 từ reports thành experiment modules, xuất config/provenance/metrics vào outputs/<run>; loại coupling tới frozen historical paths bằng config explicit. Giữ receipts gốc trong bundle riêng.
- [ ] Notebook gọi package mới; CLI/data acquire chỉ tải khi người chạy chỉ định, không tự tải khi import/test/server.
- [ ] Chạy fixture tests từng experiment. Chạy workflow local thật: import dataset -> validate -> EDA -> train hai baseline -> evaluate outputs mới; xác nhận serving bundle hash không đổi. Ghi rõ CT1–CT5 chưa chạy lại toàn bộ nếu chỉ chạy fixtures.
- [ ] Commit `feat: add self-contained data training and evaluation workflows`.

### Task 7: Kiểm chứng độc lập và bàn giao

**Files:** tools/verify_standalone.py, tests/integration/test_distribution.py, README.md, docs/{architecture,data,training,evaluation,operations}.md, outputs/verification/* (ignored).

**Interfaces:** `verify_standalone(project: Path, bundle: Path, dataset: Path, output: Path) -> dict` tạo thư mục tạm riêng, wheel/venv mới và report các checks; không xóa hay move source.

- [ ] Test wheel includes rules/web/XLSX; subprocess import origins chỉ thuộc package mới. Test cwd ngoài repo, thiếu/hỏng bundle và success bằng bundle thật.
- [ ] Build wheel; sao chép project độc lập, cài vào venv mới, unset PYTHONPATH. Chạy CLI, API, browser và data/train/evaluate bằng đường dẫn mới; kiểm tra không truy cập source cũ bằng audit hook allowlist (ngoại lệ stdlib/site-packages/system temp), có negative control cố truy cập source cũ phải bị chặn.
- [ ] Chạy toàn bộ `python -m pytest -q` trong project mới; báo test failed/skipped/warnings đúng thực tế, tích hợp thật là bước bắt buộc riêng.
- [ ] Đối chiếu corpus parity, XLSX semantics, artifact/rules và hash source cũ trước/sau. Kiểm tra Git diff chỉ trong phạm vi cho phép, không chứa dataset/model/secrets.
- [ ] Viết README lệnh install/bundle/data/serve/train/evaluate/test; ghi rõ nhãn serving vs baseline, không auto-promote model. Lưu kết quả kiểm chứng và hạn chế.
- [ ] Review toàn bộ thay đổi; sửa lỗi trong phạm vi và chạy lại check liên quan. Commit `docs: verify and document standalone project`.

## Self-review

Đã ánh xạ yêu cầu thiết kế: cấu trúc/cấu hình (1), frozen artifact và pickle (2), nhãn/API (3), file/batch (4), UI/tests (5), data/research/notebook (6), độc lập/phân phối/docs/parity (7). Các rủi ro Review Focus đều có test sở hữu. Bản cũ và snapshot giữ nguyên, không cleanup lịch sử bên ngoài folder mới.
