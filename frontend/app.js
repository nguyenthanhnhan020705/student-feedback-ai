'use strict';

const $ = (id) => document.getElementById(id);
const labels = {
  negative: 'Tiêu cực', neutral: 'Trung tính', positive: 'Tích cực',
  lecturer: 'Giảng viên', training_program: 'Chương trình đào tạo',
  facility: 'Cơ sở vật chất', other: 'Khác'
};
let currentRows = [];
let busy = false;

function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function message(id, text, error = false) {
  $(id).textContent = text;
  $(id).classList.toggle('error', error);
}

async function api(path, options) {
  let response;
  try { response = await fetch(path, options); }
  catch { throw new Error('Không kết nối được backend. Kiểm tra ứng dụng đang chạy và thử lại.'); }
  const data = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg).join('; ') : data.detail;
    throw new Error(detail || `Yêu cầu thất bại (HTTP ${response.status}).`);
  }
  return data;
}

function selectTab(id, focus = false) {
  document.querySelectorAll('[role="tab"]').forEach((tab) => {
    const active = tab.dataset.tab === id;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    $(tab.dataset.tab).hidden = !active;
    if (active && focus) tab.focus();
  });
}

const tabs = [...document.querySelectorAll('[role="tab"]')];
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab.dataset.tab));
  tab.addEventListener('keydown', (event) => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectTab(tabs[next].dataset.tab, true); }
  });
});

async function refreshHealth() {
  $('refresh-health').disabled = true;
  try {
    const data = await api('/api/health');
    const modelText = Object.entries(data.models_loaded)
      .map(([task, loaded]) => `${task}: ${loaded ? 'đã tải' : 'chưa sẵn sàng'}`).join(' · ');
    $('health').textContent = `${data.status === 'ready' ? 'Sẵn sàng phân tích' : 'Cần thiết lập mô hình'} — ${modelText}`;
  } catch (error) { $('health').textContent = error.message; }
  finally { $('refresh-health').disabled = false; }
}

function chart(id, counts, total) {
  const target = $(id);
  target.replaceChildren();
  Object.entries(counts).forEach(([label, count]) => {
    const heading = element('div'); heading.className = 'bar-label';
    heading.append(element('span', labels[label] || label), element('strong', count));
    const track = element('div'); track.className = 'bar-track'; track.setAttribute('aria-hidden', 'true');
    const fill = element('div'); fill.className = 'bar-fill';
    fill.style.width = `${total ? count / total * 100 : 0}%`;
    track.append(fill); target.append(heading, track);
  });
}

function renderRows(rows) {
  currentRows = rows;
  $('export').disabled = !rows.length;
  $('table-empty').hidden = Boolean(rows.length);
  $('results-table').hidden = !rows.length;
  $('dashboard-empty').hidden = Boolean(rows.length);
  $('dashboard-content').hidden = !rows.length;
  $('results-body').replaceChildren();
  const counts = {
    sentiment: { negative: 0, neutral: 0, positive: 0 },
    topic: { lecturer: 0, training_program: 0, facility: 0, other: 0 }
  };
  rows.forEach((row) => {
    const tr = element('tr');
    tr.append(element('td', row.text), element('td', labels[row.sentiment] || row.sentiment),
      element('td', labels[row.topic] || row.topic));
    $('results-body').append(tr);
    counts.sentiment[row.sentiment] += 1;
    counts.topic[row.topic] += 1;
  });
  $('total').textContent = rows.length ? String(rows.length) : '—';
  chart('sentiment-chart', counts.sentiment, rows.length);
  chart('topic-chart', counts.topic, rows.length);
}

async function analyze(messageId, operation) {
  if (busy) return;
  busy = true;
  $('single-submit').disabled = $('batch-submit').disabled = true;
  renderRows([]);
  $('sentiment-result').textContent = $('topic-result').textContent = 'Chưa có kết quả';
  message('single-message', ''); message('batch-message', '');
  message(messageId, 'Đang xử lý…');
  try { await operation(); }
  catch (error) { message(messageId, error.message, true); }
  finally {
    busy = false;
    $('single-submit').disabled = $('batch-submit').disabled = false;
    await refreshHealth();
  }
}

$('single-form').addEventListener('submit', (event) => {
  event.preventDefault();
  analyze('single-message', async () => {
    const data = await api('/api/predict', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: $('feedback').value })
    });
    $('sentiment-result').textContent = data.sentiment.label_vi;
    $('topic-result').textContent = data.topic.label_vi;
    renderRows([{ text: data.text, sentiment: data.sentiment.label, topic: data.topic.label }]);
    message('single-message', 'Đã phân tích bằng hai mô hình. Xem tổng hợp ở Dashboard.');
  });
});

$('batch-form').addEventListener('submit', (event) => {
  event.preventDefault();
  analyze('batch-message', async () => {
    const file = $('csv-file').files[0];
    if (!file || !file.name.toLowerCase().endsWith('.csv')) throw new Error('Vui lòng chọn tệp .csv.');
    if (file.size > 2 * 1024 * 1024) throw new Error('Tệp vượt giới hạn 2 MB.');
    const form = new FormData(); form.append('file', file);
    const data = await api('/api/predict-batch', { method: 'POST', body: form });
    renderRows(data.results);
    message('batch-message', `Đã phân tích ${data.total} phản hồi bằng mô hình. Xem phân bố ở Dashboard.`);
  });
});

function csvCell(value) {
  let text = String(value);
  // Preserve content as spreadsheet text if it could be interpreted as a formula.
  if (/^[\t\r\n]|^\s*[=+\-@]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}

$('export').addEventListener('click', () => {
  if (!currentRows.length) return;
  const records = [['text', 'sentiment', 'topic'],
    ...currentRows.map((row) => [row.text, row.sentiment, row.topic])];
  const csv = '\ufeff' + records.map((row) => row.map(csvCell).join(',')).join('\r\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  const link = element('a'); link.href = url; link.download = 'feedback-results.csv';
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

async function refreshMetrics() {
  $('refresh-metrics').disabled = true;
  $('metrics-content').replaceChildren();
  message('metrics-message', 'Đang tải báo cáo…');
  try {
    const data = await api('/api/metrics');
    message('metrics-message', data.available ? 'Đã tải báo cáo của hai mô hình.' : 'Chưa có đủ báo cáo thực nghiệm. Không hiển thị chỉ số giả.');
    for (const task of ['sentiment', 'topic']) {
      const report = data[task];
      const card = element('article'); card.append(element('h3', task === 'sentiment' ? 'Mô hình cảm xúc' : 'Mô hình chủ đề'));
      if (!report.available) {
        card.append(element('p', report.error || report.reason || 'Chưa có báo cáo.'));
      } else {
        card.append(element('p', `Mô hình: ${report.model} · Tập: ${report.split}`));
        const list = element('ul'); list.className = 'metric-list';
        for (const [key, title] of [['accuracy', 'Accuracy'], ['precision_macro', 'Macro Precision'], ['recall_macro', 'Macro Recall'], ['f1_macro', 'Macro F1']]) {
          list.append(element('li', `${title}: ${report[key].toFixed(4)}`));
        }
        card.append(list);
        const wrap = element('div'); wrap.className = 'table-wrap';
        const table = element('table'); table.append(element('caption', 'Confusion Matrix · hàng: nhãn thật, cột: dự đoán; thứ tự mã tăng dần'));
        const tbody = element('tbody');
        report.confusion_matrix.forEach((row) => {
          const tr = element('tr'); row.forEach((value) => tr.append(element('td', value))); tbody.append(tr);
        });
        table.append(tbody); wrap.append(table); card.append(wrap);
      }
      $('metrics-content').append(card);
    }
  } catch (error) { message('metrics-message', error.message, true); }
  finally { $('refresh-metrics').disabled = false; }
}

$('refresh-health').addEventListener('click', refreshHealth);
$('refresh-metrics').addEventListener('click', refreshMetrics);
refreshHealth();
refreshMetrics();
