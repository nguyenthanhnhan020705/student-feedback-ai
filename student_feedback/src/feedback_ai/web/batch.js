"use strict";
(()=>{
  const el=id=>document.getElementById(id), topicNames={lecturer:'Giảng viên',curriculum:'Chương trình đào tạo',facility:'Cơ sở vật chất'};
  let rows=[],sheets=[],busy=false,stop=false;
  let analyzedPaste=null;
  const pasteText=()=>el('batch-text').value.replace(/\r\n?/g,'\n');
  const tabs=[...document.querySelectorAll('[role=tab]')];
  let mode='single';
  const sessions={paste:{rows:[],fields:{}},file:{rows:[],fields:{}}};
  const sessionFields=['batch-name','batch-search','sentiment-filter','topic-filter'];

  function selectMode(nextMode,focus=false){
    if(busy)return;
    if(mode!=='single')sessions[mode]={rows,fields:Object.fromEntries(sessionFields.map(id=>[id,el(id).value])),message:el('batch-message').textContent,preview:el('batch-preview').textContent};
    mode=nextMode;
    for(const id of ['batch-summary','batch-charts'])el(id).hidden=mode==='paste';
    if(mode!=='single'){
      const saved=sessions[mode];rows=saved.rows;
      sessionFields.forEach(id=>el(id).value=saved.fields[id]||'');
      message(saved.message||'');el('batch-preview').textContent=saved.preview||'';render();controls();
    }
    for(const tab of tabs){const active=tab.dataset.mode===mode;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;if(active&&focus)tab.focus();}
    for(const name of ['single','paste','file'])el('panel-'+name).hidden=name!==mode;
    el('batch').hidden=mode==='single';
  }
  tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>selectMode(tab.dataset.mode));tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%3;else if(event.key==='ArrowLeft')next=(index+2)%3;else if(event.key==='Home')next=0;else if(event.key==='End')next=2;else return;event.preventDefault();selectMode(tabs[next].dataset.mode,true);});});
  const message=(text,bad=false)=>{el('batch-message').textContent=text;el('batch-message').className=bad?'error':'hint';};
  function controls(){
    tabs.forEach(tab=>tab.disabled=busy);
    el('batch-results').hidden=!rows.length;
    el('batch-actions').hidden=mode!=='paste'&&!rows.length;
    for(const id of ['batch-file','sheet-select','column-select','id-select','preview-file','batch-name','batch-text'])el(id).disabled=busy;
    const changed=mode==='paste'&&pasteText()!==analyzedPaste;
    el('batch-run').disabled=busy||(mode==='paste'&&!pasteText().trim())||(!changed&&!rows.some(r=>r.status==='pending'||r.status==='error'));
    el('batch-stop').disabled=!busy;el('batch-export').disabled=busy||!rows.length;
  }
  function prepare(values,first=1,ids=[]){
    if(values.length>500)throw Error('Tối đa 500 phản hồi mỗi đợt.');
    if(values.some(t=>t.length>20000))throw Error('Có nội dung vượt quá 20.000 ký tự, hãy rút gọn trước khi nhập.');
    rows=values.map((text,i)=>{
      const error=!text.trim()?'Dòng trống.':[...text].length>5000?'Vượt quá 5.000 ký tự.':!text.isWellFormed()?'Unicode không hợp lệ.':'';
      return {id:(ids[i]||`PH${String(i+1).padStart(3,'0')}`).slice(0,100),source_row:first+i,text,status:error?'invalid':'pending',sentiment:null,topics:[],aspects:{},error};
    });
    el('batch-preview').textContent=`${rows.length} phản hồi · ${rows.filter(r=>r.status==='pending').length} hợp lệ · ${rows.filter(r=>r.status==='invalid').length} không hợp lệ.`;
    for(const id of ['batch-search','sentiment-filter','topic-filter'])el(id).value='';
    message('Danh sách đã sẵn sàng.');render();controls();
  }
  el('batch-text').addEventListener('input',controls);
  function options(select,items){select.replaceChildren();for(const [value,label] of items){const o=document.createElement('option');o.value=value;o.textContent=label;select.append(o);}}
  function columns(){
    const sheet=sheets[Number(el('sheet-select').value)];
    options(el('column-select'),sheet.headers.map((h,i)=>[i,`${i+1}. ${h}`]));
    options(el('id-select'),[['','Tự tạo mã'],...sheet.headers.map((h,i)=>[i,`${i+1}. ${h}`])]);
    const normalize=h=>h.trim().toLocaleLowerCase();
    const content=sheet.headers.findIndex(h=>['nội dung phản hồi','nội dung','feedback','text'].includes(normalize(h)));
    const id=sheet.headers.findIndex(h=>['mã phản hồi','id'].includes(normalize(h)));
    if(content>=0)el('column-select').value=String(content);
    if(id>=0&&id!==content)el('id-select').value=String(id);
    el('file-options').open=sheets.length>1||(sheet.headers.length>1&&content<0);
    return sheet.headers.length===1||content>=0;
  }
  el('sheet-select').onchange=columns;
  el('batch-file').onchange=async()=>{
    const file=el('batch-file').files[0];if(!file)return;
    if(file.size>5*1024*1024){message('File vượt quá 5 MiB.',true);return;}
    busy=true;controls();el('file-options').hidden=true;message('Đang đọc file…');
    try{const r=await fetch('/api/v3/import?filename='+encodeURIComponent(file.name),{method:'POST',body:file});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'Không đọc được file.');sheets=data.sheets;options(el('sheet-select'),sheets.map((s,i)=>[i,s.name]));const recognized=columns();el('file-options').hidden=false;if(recognized&&sheets.length===1){el('preview-file').onclick();}else{message('Chọn dữ liệu trong mục tùy chỉnh rồi bấm Áp dụng.');}}
    catch(e){message(e.message,true);}finally{busy=false;controls();}
  };
  el('preview-file').onclick=()=>{try{const sheet=sheets[Number(el('sheet-select').value)],column=Number(el('column-select').value),id=el('id-select').value;prepare(sheet.rows.map(r=>r[column]||''),sheet.first_row,id===''?[]:sheet.rows.map(r=>r[Number(id)]||''));}catch(e){message(e.message,true);}};
  function render(){
    const good=rows.filter(r=>r.status==='ok'),invalid=rows.filter(r=>['invalid','error'].includes(r.status)),pending=rows.filter(r=>r.status==='pending');
    el('batch-summary').textContent=`Tổng: ${rows.length} | Thành công: ${good.length} | Lỗi / không hợp lệ: ${invalid.length} | Chưa phân tích: ${pending.length}`;
    el('batch-progress').max=Math.max(1,rows.length);el('batch-progress').value=rows.length-pending.length;el('batch-progress-text').textContent=` ${rows.length-pending.length}/${rows.length}`;
    const charts=el('batch-charts');charts.replaceChildren();
    const colors={positive:'#238562',negative:'#d54b55',mixed:'#d69b24',undetermined:'#8795a5'},keys=Object.keys(colors);
    const make=(tag,cls,text)=>{const n=document.createElement(tag);n.className=cls;if(text!==undefined)n.textContent=text;return n;};
    const percentage=n=>good.length?(100*n/good.length).toFixed(1)+'%':'?';
    const cards=make('section','overview-cards');
    for(const [label,value] of [['Tổng phản hồi',rows.length],['Phân tích thành công',good.length],['Tỷ lệ tích cực',percentage(good.filter(r=>r.sentiment==='positive').length)],['Tỷ lệ tiêu cực',percentage(good.filter(r=>r.sentiment==='negative').length)]]){const card=make('div','overview-stat');card.append(make('span','',label),make('strong','',value));cards.append(card);}charts.append(cards);
    charts.append(make('p','overview-note',good.length?'Th\u1ed1ng k\u00ea to\u00e0n b\u1ed9 \u0111\u1ee3t; ch\u1ec9 t\u00ednh ph\u1ea3n h\u1ed3i th\u00e0nh c\u00f4ng. B\u1ed9 l\u1ecdc ch\u1ec9 \u00e1p d\u1ee5ng cho b\u1ea3ng.':'Ch\u01b0a c\u00f3 k\u1ebft qu\u1ea3 ph\u00e2n t\u00edch.'));
    const panel=title=>{const n=make('div','overview-chart');n.append(make('h3','',title));charts.append(n);return n;};
    const sentiments=panel('Phân bố cảm xúc'),donut=make('div','sentiment-donut'),legend=make('div','chart-legend');let start=0;const stops=[];
    for(const k of keys){const n=good.filter(r=>r.sentiment===k).length,end=start+(good.length?100*n/good.length:0);stops.push(`${colors[k]} ${start}% ${end}%`);start=end;const line=make('p','',`${LABELS.sentiment[k]}: ${n} (${percentage(n)})`);line.style.borderLeft=`8px solid ${colors[k]}`;line.style.paddingLeft='8px';legend.append(line);}
    donut.style.background=good.length?`conic-gradient(${stops.join(',')})`:'#e8edf0';donut.setAttribute('role','img');donut.setAttribute('aria-label','Phân bố cảm xúc, xem s? li?u ? ch? gi?i');donut.append(make('span','donut-center',`${good.length} phản hồi`));sentiments.append(donut,legend);
    const topics={...topicNames,unknown:'Chưa xác định'},selected=k=>good.filter(r=>k==='unknown'?!r.topics.length:r.topics.includes(k));
    const volume=panel('Số phản hồi theo chủ đề'),max=Math.max(1,...Object.keys(topics).map(k=>selected(k).length));
    for(const [k,label] of Object.entries(topics)){const n=selected(k).length;volume.append(make('p','',`${label}: ${n}`));const track=make('div','volume-track'),bar=make('div','volume-fill');bar.style.width=100*n/max+'%';track.append(bar);volume.append(track);}
    const aspects=panel('Cảm xúc theo chủ đề');aspects.classList.add('overview-wide');aspects.append(make('p','overview-note','M\u1ed9t ph\u1ea3n h\u1ed3i c\u00f3 th\u1ec3 thu\u1ed9c nhi\u1ec1u ch\u1ee7 \u0111\u1ec1. C\u1ea3m x\u00fac t\u00ednh ri\u00eang theo ch\u1ee7 \u0111\u1ec1; thi\u1ebfu k\u1ebft qu\u1ea3: ch\u01b0a x\u00e1c \u0111\u1ecbnh.'));
    for(const [k,label] of Object.entries(topics)){const group=selected(k),track=make('div','stack-track'),details=[];aspects.append(make('p','',`${label} ? ${group.length} phản hồi`));for(const key of keys){const n=group.filter(r=>(k==='unknown'?'undetermined':r.aspects[k]||'undetermined')===key).length,pct=group.length?100*n/group.length:0;details.push(`${LABELS.sentiment[key]}: ${n} (${pct.toFixed(1)}%)`);if(n){const seg=make('span','stack-segment',pct>=10?pct.toFixed(0)+'%':'');seg.style.width=pct+'%';seg.style.background=colors[key];seg.title=details[details.length-1];track.append(seg);}}track.setAttribute('role','img');track.setAttribute('aria-label',label+': '+details.join('; '));aspects.append(track,make('p','overview-note',group.length?details.join(' ? '):'Ch\u01b0a c\u00f3 ph\u1ea3n h\u1ed3i'));}
    const query=el('batch-search').value.toLocaleLowerCase(),sf=el('sentiment-filter').value,tf=el('topic-filter').value;
    const visible=rows.filter(r=>(!query||(r.id+' '+r.text).toLocaleLowerCase().includes(query))&&(!sf||r.sentiment===sf)&&(!tf||(tf==='unknown'?r.status==='ok'&&!r.topics.length:r.topics.includes(tf))));
    el('visible-count').textContent=`Hiển thị ${visible.length}/${rows.length} phản hồi.`;
    const body=el('batch-table').querySelector('tbody');body.replaceChildren();
    for(const r of visible){const tr=document.createElement('tr');const values=[`${r.id}\nDòng ${r.source_row}`,r.text,LABELS.sentiment[r.sentiment]||'—',r.topics.map(t=>topicNames[t]).join(' + ')||(r.status==='ok'?'Chưa xác định':'—'),Object.entries(r.aspects).map(([t,s])=>`${topicNames[t]}: ${LABELS.sentiment[s]}`).join('\n')||'—'];for(const value of values){const td=document.createElement('td');td.textContent=value;tr.append(td);}if(r.error){const note=document.createElement('p');note.className='error';note.textContent=r.error;tr.children[1].append(note);}body.append(tr);}
  }
  for(const id of ['batch-search','sentiment-filter','topic-filter'])el(id).addEventListener('input',render);
  el('batch-stop').onclick=()=>{stop=true;message('Sẽ dừng sau phản hồi hiện tại.');};
  el('batch-run').onclick=async()=>{
    if(busy)return;
    if(mode==='paste'&&pasteText()!==analyzedPaste){
      if(!pasteText().trim())return;
      try{prepare(pasteText().split('\n'));analyzedPaste=pasteText();}
      catch(e){message(e.message,true);return;}
    }
    busy=true;stop=false;controls();message('Đang phân tích…');
    for(const row of rows){
      if(stop)break;if(!['pending','error'].includes(row.status))continue;
      try{const data=await request('/api/v3/analyze-row',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:row.text})});
        if(!data||!Object.hasOwn(LABELS.sentiment,data.sentiment)||!Array.isArray(data.topics)||!data.topics.every(t=>Object.hasOwn(topicNames,t))||!data.aspects)throw Error('Kết quả không hợp lệ.');
        Object.assign(row,data,{status:'ok',error:''});
      }catch(e){row.status='error';row.error=e.kind==='timeout'?'Quá thời gian xử lý. Bấm Phân tích để thử lại.':'Không phân tích được dòng này. Kiểm tra kết nối/mô hình và thử lại.';}
      render();
    }
    busy=false;controls();message(stop?'Đã dừng; có thể tiếp tục hoặc xuất kết quả hiện có.':'Đã xử lý danh sách. Các dòng lỗi có thể thử lại.');
  };
  el('batch-export').onclick=async()=>{
    busy=true;controls();message('Đang tạo Excel…');
    try{const response=await fetch('/api/v3/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:el('batch-name').value,rows})});if(!response.ok)throw Error('Không xuất được Excel.');const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download='phan-hoi-sinh-vien.xlsx';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Đã xuất Excel toàn bộ đợt phân tích.');}
    catch(e){message(e.message,true);}finally{busy=false;controls();}
  };
  controls();
})();
