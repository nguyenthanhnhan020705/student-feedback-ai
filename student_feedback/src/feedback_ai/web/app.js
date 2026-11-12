"use strict";
const $=id=>document.getElementById(id);
const box=$("text"),button=$("go"),out=$("out"),health=$("health");
const state={ready:false,busy:false,revision:0,healthRevision:0};
const ERRORS={
  invalid:"Nội dung không hợp lệ. Hãy nhập 1 đến 5000 ký tự Unicode.",
  not_ready:"Chưa thể phân tích. Bạn vui lòng thử lại kết nối.",
  timeout:"Máy chủ phản hồi quá 10 giây. Bạn vui lòng thử lại.",
  network:"Không kết nối được máy chủ. Hãy kiểm tra lại kết nối.",
  server:"Không thể phân tích phản hồi. Bạn vui lòng thử lại."
};

function inputProblem() {
  if(!box.value.trim())return "Nội dung không được chỉ có khoảng trắng.";
  if([...box.value].length>MAX_CHARS)return "Nội dung vượt quá 5000 ký tự.";
  if(!box.value.isWellFormed())return "Nội dung có ký tự Unicode không hợp lệ.";
  return "";
}
function refresh() {
  const n=[...box.value].length,problem=inputProblem();
  $("count").textContent=n+" / 5000";
  $("hint").textContent=n?problem:"";
  $("hint").className="hint"+(problem&&n?" bad":"");
  button.disabled=state.busy||!state.ready||Boolean(problem);
}
function message(text,isError=false) {
  const paragraph=document.createElement("p");
  paragraph.className=isError?"error":"hint";
  paragraph.textContent=text;out.replaceChildren(paragraph);
}
function render(data) {
  const icons={sentiment:{positive:'\u{1F60A}',negative:'\u{1F61E}',mixed:'\u{1F914}',undetermined:'\u{2753}'},topic:{lecturer:'\u{1F469}\u{200D}\u{1F3EB}',curriculum:'\u{1F4DA}',facility:'\u{1F3EB}',education_quality:'\u{1F393}',other_domain:'\u{2753}'}};
  const appendLabel=(target,task,key)=>{
    const label=document.createElement('span'),icon=document.createElement('span');
    label.className='result-label';icon.className='result-icon';
    icon.setAttribute('aria-hidden','true');icon.textContent=icons[task][key]||'\u{2753}';
    label.append(document.createTextNode(LABELS[task][key]+' '),icon);target.append(label);
  };
  const result=document.createElement("div");result.className="res";
  for(const [task,title] of [["sentiment","Cảm xúc"],["topic","Chủ đề"]]) {
    const cell=document.createElement("div"),small=document.createElement("small"),value=document.createElement("b");
    small.textContent=title;
    const labels=task==='topic'&&data.topics?data.topics:[data[task]];
    labels.forEach((key,index)=>{if(index)value.append(document.createTextNode(' + '));appendLabel(value,task,key);});
    cell.append(small,value);result.append(cell);
  }
  out.replaceChildren(result);
}
async function loadHealth() {
  const revision=++state.healthRevision;
  health.textContent="Đang kết nối…";$("recheck").hidden=true;
  try {
    const data=await checkHealth();
    if(revision!==state.healthRevision)return;
    state.ready=data.ready;health.textContent=data.ready?"Đã kết nối":"Chưa sẵn sàng";$("recheck").hidden=data.ready;health.dataset.ready=String(data.ready);
  } catch(error) {
    if(revision!==state.healthRevision)return;
    state.ready=false;health.textContent="Mất kết nối";$("recheck").hidden=false;health.dataset.ready="false";
  }
  refresh();
}
button.addEventListener("click",async()=>{
  if(state.busy||!state.ready||inputProblem())return;
  const revision=state.revision,submittedText=box.value;
  state.busy=true;message("Đang phân tích…");refresh();
  try {
    const result=await predict(submittedText);
    if(state.revision===revision)render(result);
  } catch(error) {
    if(error.kind==="not_ready") {
      state.ready=false;++state.healthRevision;health.textContent="Chưa sẵn sàng";$("recheck").hidden=false;health.dataset.ready="false";
    }
    if(state.revision===revision)message(ERRORS[error.kind]||ERRORS.server,true);
  } finally {state.busy=false;refresh();}
});
box.addEventListener("input",()=>{++state.revision;out.replaceChildren();refresh();});
$("recheck").addEventListener("click",loadHealth);
refresh();loadHealth();
