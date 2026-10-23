const $ = id => document.getElementById(id);
const box = $("text"), btn = $("go"), out = $("out"), hint = $("hint"), count = $("count"), healthEl = $("health");
const state = { ready: false, busy: false };
const MODEL_VI = { ready: "sẵn sàng", missing: "chưa có", invalid: "không hợp lệ" };
const ERRORS = {
  network: ["err", "Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa, rồi bấm “Kiểm tra lại kết nối”."],
  timeout: ["err", "Máy chủ phản hồi quá 10 giây. Bấm “Phân tích” để thử lại."],
  invalid: ["err", "Nội dung không hợp lệ. Hãy nhập 1 đến 5000 ký tự, không chỉ có khoảng trắng."],
  not_ready: ["warn", "Mô hình chưa sẵn sàng. Thử lại sau khi backend nạp xong mô hình."],
  server: ["err", "Hệ thống gặp lỗi. Thử lại; nếu lỗi lặp lại, báo nhóm backend."]
};

if (MOCK) $("mockBanner").hidden = false;

function inputProblem() {
  const text = box.value;
  if (!text.trim()) return "Nhập nội dung phản hồi để phân tích.";
  if ([...text].length > MAX_CHARS) return "Nội dung vượt quá 5000 ký tự.";
  return "";
}

function refresh() {
  const n = [...box.value].length; // đếm Unicode code point, không dùng maxlength
  const problem = inputProblem();
  count.textContent = n + " / " + MAX_CHARS;
  hint.textContent = n === 0 ? "" : problem;
  hint.className = "hint" + (problem && n > 0 ? " bad" : "");
  btn.disabled = state.busy || !state.ready || !!problem;
}

function message(kind, text) {
  out.replaceChildren();
  const p = document.createElement("p");
  p.className = kind;
  p.textContent = text;
  out.append(p);
}

function showResult(r) {
  out.replaceChildren();
  const wrap = document.createElement("div");
  wrap.className = "res";
  [["Cảm xúc", LABELS.sentiment[r.sentiment]], ["Chủ đề", LABELS.topic[r.topic]]].forEach(([title, value]) => {
    const cell = document.createElement("div");
    const s = document.createElement("small"), b = document.createElement("b");
    s.textContent = title;
    b.textContent = value + (MOCK ? " (MOCK)" : "");
    cell.append(s, b);
    wrap.append(cell);
  });
  out.append(wrap);
}

async function loadHealth() {
  healthEl.textContent = "Đang kiểm tra máy chủ…";
  try {
    const h = await checkHealth();
    state.ready = h.ready === true;
    healthEl.textContent = state.ready ? "Mô hình sẵn sàng"
      : "Mô hình chưa sẵn sàng (cảm xúc: " + (MODEL_VI[h.models && h.models.sentiment] || "?") +
        ", chủ đề: " + (MODEL_VI[h.models && h.models.topic] || "?") + ")";
  } catch (e) {
    state.ready = false;
    healthEl.textContent = "Không kết nối được máy chủ";
  }
  refresh();
}

btn.addEventListener("click", async () => {
  if (state.busy || inputProblem()) return;
  state.busy = true;
  out.replaceChildren();
  message("hint", "Đang phân tích…");
  refresh();
  try {
    showResult(await predict(box.value));
  } catch (e) {
    const kind = e.kind || "server";
    if (kind === "not_ready") { state.ready = false; healthEl.textContent = "Mô hình chưa sẵn sàng"; }
    message(...ERRORS[kind]); // giữ nguyên nội dung đã nhập, kết quả cũ đã bị xóa
  } finally {
    state.busy = false;
    refresh();
  }
});

box.addEventListener("input", refresh);
$("recheck").addEventListener("click", loadHealth);
refresh();
loadHealth();
