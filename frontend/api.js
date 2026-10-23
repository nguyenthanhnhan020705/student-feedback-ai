// Gọi API theo docs/specs/api-contract.md v1.0. URL tương đối vì FastAPI phục vụ cả UI lẫn API.
const MOCK = new URLSearchParams(location.search).get("mock"); // ok | notready | invalid | error; null = API thật
const TIMEOUT_MS = 10000;
const MAX_CHARS = 5000;

const LABELS = { // bảng ánh xạ trong hợp đồng API, mục 1
  sentiment: { negative: "Tiêu cực", neutral: "Trung tính", positive: "Tích cực" },
  topic: { lecturer: "Giảng viên", curriculum: "Chương trình đào tạo", facility: "Cơ sở vật chất", other: "Khác" }
};

// kind: network | timeout | invalid (422) | not_ready (503) | server (500 và còn lại)
class ApiError extends Error {
  constructor(kind, status) { super(kind); this.kind = kind; this.status = status; }
}

const wait = ms => new Promise(r => setTimeout(r, ms));

async function request(path, options) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  let res;
  try {
    res = await fetch(path, { ...options, signal: ctrl.signal });
  } catch (e) {
    throw new ApiError(e.name === "AbortError" ? "timeout" : "network");
  } finally {
    clearTimeout(timer);
  }
  let body = null;
  try { body = await res.json(); } catch (e) { /* giữ null */ }
  if (res.ok) return body;
  const kind = res.status === 422 ? "invalid" : res.status === 503 ? "not_ready" : "server";
  throw new ApiError(kind, res.status); // UI dựa vào HTTP/code, không so khớp message
}

// Dữ liệu MOCK chỉ để phát triển giao diện (xem banner trên trang), không phải fallback của API thật.
async function mockRequest(path) {
  await wait(500);
  if (path === "/api/health") {
    const ready = MOCK !== "notready";
    return { status: "ok", ready, models: { sentiment: ready ? "ready" : "missing", topic: "ready" }, contract_version: "1.0" };
  }
  if (MOCK === "notready") throw new ApiError("not_ready", 503);
  if (MOCK === "invalid") throw new ApiError("invalid", 422);
  if (MOCK === "error") throw new ApiError("server", 500);
  return { sentiment: "positive", topic: "lecturer", contract_version: "1.0" };
}

function checkHealth() {
  return MOCK ? mockRequest("/api/health") : request("/api/health");
}

// Gửi nguyên văn text, không trim/viết thường/bỏ dấu.
async function predict(text) {
  const data = MOCK ? await mockRequest("/api/predict")
    : await request("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
  if (!data || !LABELS.sentiment[data.sentiment] || !LABELS.topic[data.topic]) throw new ApiError("server", 200);
  return data;
}
