"use strict";
const MAX_CHARS=5000;
const LABELS=Object.freeze({
  sentiment:Object.freeze({positive:"Tích cực",negative:"Tiêu cực",mixed:"Hỗn hợp",undetermined:"Chưa xác định"}),
  topic:Object.freeze({lecturer:"Giảng viên",curriculum:"Chương trình đào tạo",facility:"Cơ sở vật chất",
    education_quality:"Chất lượng giáo dục",other_domain:"Chưa xác định"})
});
class ApiError extends Error {
  constructor(kind,status){super(kind);this.kind=kind;this.status=status;}
}

async function request(path,options={}) {
  const controller=new AbortController();
  let timer;
  const timeout=new Promise((resolve,reject)=>{
    timer=setTimeout(()=>{controller.abort();reject(new ApiError("timeout"));},10000);
  });
  const operation=(async()=>{
    const response=await fetch(path,{...options,signal:controller.signal});
    let data=null;
    try {data=await response.json();}
    catch(error){if(error.name!=="SyntaxError")throw error;}
    if(!response.ok)throw new ApiError(response.status===422?"invalid":response.status===503?"not_ready":"server",response.status);
    return data;
  })();
  try {return await Promise.race([operation,timeout]);}
  catch(error){
    if(error instanceof ApiError)throw error;
    throw new ApiError(error.name==="AbortError"?"timeout":"network");
  } finally {clearTimeout(timer);}
}

function ownObject(data,keys,exact=false) {
  return data!==null&&typeof data==="object"&&!Array.isArray(data)
    &&Object.getPrototypeOf(data)===Object.prototype
    &&keys.every(key=>Object.hasOwn(data,key))
    &&(!exact||Object.keys(data).length===keys.length);
}

async function predict(text) {
  const data=await request('/api/v3/predict',{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
  if(!ownObject(data,["contract_version","sentiment","topic"])
    ||Object.keys(data).some(key=>!["contract_version","sentiment","topic","topics"].includes(key))||data.contract_version!=="3.0"
    ||typeof data.sentiment!=="string"||typeof data.topic!=="string"
    ||!Object.hasOwn(LABELS.sentiment,data.sentiment)||!Object.hasOwn(LABELS.topic,data.topic))throw new ApiError("server",200);
  if(data.topic==="education_quality") {
    if(!Array.isArray(data.topics)||data.topics.length<2||data.topics.length>3
      ||new Set(data.topics).size!==data.topics.length
      ||data.topics.some(topic=>!["lecturer","curriculum","facility"].includes(topic)))throw new ApiError("server",200);
  } else if(Object.hasOwn(data,"topics"))throw new ApiError("server",200);
  return data;
}

async function checkHealth() {
  const data=await request('/api/health');
  if(!ownObject(data,["contract_version","model","ready"])||data.contract_version!=="3.0"
    ||data.model!=="ct4"||typeof data.ready!=="boolean")throw new ApiError("server",200);
  return data;
}
