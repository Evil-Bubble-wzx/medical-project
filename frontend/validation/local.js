"use strict";
async function checkLocalStatus(){
 const el=document.querySelector('#local-status');el.textContent='正在检查本机服务…';
 try {const r=await fetch('/api/v1/validation/status',{cache:'no-store'});if(!r.ok)throw new Error();const s=await r.json();
 el.textContent=`服务在线 · 可检索片段 ${s.chunks} · 本地模型${s.model_available?'已安装':'待安装'} · 生成配置${s.generation_state==='ready'?'就绪':'待配置'}。配置就绪不代表已完成真实生成或医学验收。`;
 }catch{el.textContent='状态读取失败，请查看启动窗口，确认服务仍在运行后重新检查。';}
}
document.querySelector('#local-refresh').addEventListener('click',checkLocalStatus);void checkLocalStatus();
