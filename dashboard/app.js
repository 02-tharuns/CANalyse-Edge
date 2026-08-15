const $ = id => document.getElementById(id);
async function load(){
  try{
    const health = await fetch('/api/components/drive-unit-1/health').then(r=>r.json());
    const faults = await fetch('/api/components/drive-unit-1/faults').then(r=>r.json());
    $('service').textContent='API online'; $('score').textContent=health.health_score;
    $('condition').textContent=health.condition.replaceAll('_',' '); $('confidence').textContent=(health.confidence*100).toFixed(1)+'%';
    $('anomaly').textContent=health.anomaly_score.toFixed(3); $('fault').textContent=faults[0]?.description || 'None';
    $('details').textContent=JSON.stringify({health,faults},null,2);
  }catch(error){$('service').textContent='Offline';$('details').textContent=String(error)}
}
$('refresh').onclick=async()=>{ $('refresh').disabled=true; await fetch('/api/components/drive-unit-1/operations/recompute-health',{method:'POST'}); await load(); $('refresh').disabled=false; };
load();
