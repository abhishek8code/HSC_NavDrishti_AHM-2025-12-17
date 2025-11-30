// Scenario comparison: simulate alternative and compare metrics
(function(){
  function renderScenario(detail){
    const el = document.getElementById('scenarioPanel');
    if(!el) return;
    const rec = detail || {};
    const bestId = rec?.recommendedAlternativeId ?? '-';
    const altCount = rec?.allAlternatives?.length ?? 0;
    el.innerHTML = `
      <div class="small">
        <div><strong>Recommended ID:</strong> ${bestId}</div>
        <div><strong>Alternatives:</strong> ${altCount}</div>
        <div class="mt-2"><button class="btn btn-sm btn-outline-secondary" id="compareBtn">Compare ▶</button></div>
      </div>`;
    const btn = document.getElementById('compareBtn');
    if(btn){ btn.addEventListener('click', ()=>alert('Scenario comparison coming soon (Phase 3 step 2).')); }
  }

  window.addEventListener('routes:alternatives', (e)=>{
    const data = e.detail;
    // Render Alternatives panel
    const panel = document.getElementById('alternativesPanel');
    if(panel){
      if(!data || !data.allAlternatives || data.allAlternatives.length === 0){
        panel.innerHTML = '<p class="text-muted">No alternatives.</p>';
      } else {
        let html = '<div class="list-group">';
        data.allAlternatives.forEach(a=>{
          html += `<div class="list-group-item d-flex justify-content-between align-items-center">
            <div>
              <div><strong>Route ${a.routeId}</strong> • ${a.lengthKm.toFixed(2)} km • seg ${a.numSegments}</div>
              <small>Score: ${a.suitabilityScore.toFixed(2)} • Rank ${a.rank}</small>
            </div>
            <div>
              <button class="btn btn-sm btn-primary" data-route="${a.routeId}">Select</button>
            </div>
          </div>`;
        });
        html += '</div>';
        panel.innerHTML = html;
      }
    }
    renderScenario(data);
  });
})();
