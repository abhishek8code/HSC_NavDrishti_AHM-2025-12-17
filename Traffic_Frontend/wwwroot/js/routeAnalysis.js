// Route Analysis UI logic: pick start/end, analyze, render metrics and overlays
(function(){
  const state = {
    start: null, // [lon, lat]
    end: null,   // [lon, lat]
    routeId: 1   // default route id context; can be set from server
  };

  function setMarker(coord, type){
    const id = type === 'start' ? 'start-marker' : 'end-marker';
    if(map.getSource(id)){
      map.getSource(id).setData({ type:'Feature', geometry:{ type:'Point', coordinates: coord } });
    } else {
      map.addSource(id, { type:'geojson', data:{ type:'Feature', geometry:{ type:'Point', coordinates: coord } }});
      map.addLayer({ id: id, type:'circle', source:id, paint:{ 'circle-radius': 6, 'circle-color': type==='start' ? '#28a745' : '#dc3545' }});
    }
  }

  function drawRouteLine(coords){
    const id = 'selected-route-line';
    const data = { type:'Feature', geometry:{ type:'LineString', coordinates: coords } };
    if(map.getSource(id)){
      map.getSource(id).setData(data);
    } else {
      map.addSource(id, { type:'geojson', data });
      map.addLayer({ id, type:'line', source:id, paint:{ 'line-width': 4, 'line-color':'#1b6ec2' }});
    }
  }

  async function analyze(){
    if(!state.start || !state.end){
      alert('Please select both Start and End by clicking on the map.');
      return;
    }
    try{
      const coords = [ state.start, state.end ];
      const result = await apiClient.analyzeRoute(coords);
      if(result){
        // naive draw straight line; backend can return segments later
        drawRouteLine(coords);
        renderMetrics(result);
        // fetch alternatives
        const rec = await apiClient.recommendRoute(state.routeId, state.start[0], state.start[1], state.end[0], state.end[1]);
        window.dispatchEvent(new CustomEvent('routes:alternatives', { detail: rec }));
      }
    }catch(err){
      console.error('Analyze failed', err);
      alert('Analyze failed: ' + err.message);
    }
  }

  function renderMetrics(result){
    const el = document.getElementById('metricsBox');
    if(!el) return;
    el.innerHTML = `
      <div class="row">
        <div class="col-6"><strong>Length (deg):</strong> ${result.lengthDegrees?.toFixed?.(3) ?? result.lengthDegrees}</div>
        <div class="col-6"><strong>Segments:</strong> ${result.numSegments}</div>
        <div class="col-6"><strong>Approx. Length (km):</strong> ${result.approximateLengthKm?.toFixed?.(2) ?? result.approximateLengthKm}</div>
      </div>`;
  }

  // UI bindings
  document.addEventListener('DOMContentLoaded', ()=>{
    const analyzeBtn = document.getElementById('analyzeBtn');
    if(analyzeBtn){ analyzeBtn.addEventListener('click', analyze); }

    // map click handlers
    if(map){
      let selecting = 'start';
      const toggleBtn = document.getElementById('toggleSelection');
      if(toggleBtn){
        toggleBtn.addEventListener('click', ()=>{
          selecting = selecting === 'start' ? 'end' : 'start';
          toggleBtn.textContent = selecting === 'start' ? 'Select End' : 'Select Start';
        });
      }
      map.on('click', (e)=>{
        const coord = [e.lngLat.lng, e.lngLat.lat];
        if(selecting === 'start'){
          state.start = coord; setMarker(coord, 'start');
        } else {
          state.end = coord; setMarker(coord, 'end');
        }
      });
    }
  });
})();
