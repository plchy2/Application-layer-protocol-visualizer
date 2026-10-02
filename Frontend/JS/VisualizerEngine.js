// Render the protocol checklist based on active layer ('app' or 'transport')
function renderChecklist() {
  const container = document.getElementById('protocol-checklist');
  if (!container) return;

  // Retrieve current layer dataset directly based on global currentLayer state
  let steps = [];
  if (typeof currentLayer !== 'undefined' && currentLayer === 'app') {
    steps = (activeFlowData && activeFlowData.app_flow) ? activeFlowData.app_flow : [];
  } else {
    steps = (activeFlowData && activeFlowData.transport_flow) ? activeFlowData.transport_flow : [];
  }

  // Fallback if activeFlowData is structured as a flat array
  if (!steps.length && Array.isArray(activeFlowData)) {
    steps = activeFlowData;
  }

  if (!steps || steps.length === 0) {
    container.innerHTML = `<div class="text-xs text-slate-500 italic p-4 text-center">No protocol flow steps loaded. Execute a simulation to start.</div>`;
    return;
  }

  container.innerHTML = steps.map((item, index) => {
    const isL4 = typeof currentLayer === 'undefined' || currentLayer === 'transport';
    const isStopWait = item.protocol && (item.protocol.includes('Stop-and-Wait') || item.protocol.includes('ARQ'));

    return `
      <div class="p-3.5 bg-slate-950 border ${isStopWait ? 'border-sky-500/80 bg-sky-950/20 shadow-lg shadow-sky-500/10' : 'border-slate-800'} rounded-xl transition hover:border-slate-700">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center gap-2.5">
            <span class="w-6 h-6 rounded-full ${isStopWait ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-sky-400'} text-xs font-black flex items-center justify-center font-mono">
              ${item.step || index + 1}
            </span>
            <span class="font-bold text-sm text-slate-100">${item.protocol || 'Protocol Event'}</span>
          </div>
          <span class="text-[10px] font-mono px-2 py-0.5 rounded-full ${isStopWait ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' : 'bg-slate-800 text-slate-400'}">
            ${item.layer || item.pdu || 'L4 - Transport'}
          </span>
        </div>

        <p class="text-xs text-slate-300 ml-8 font-mono leading-relaxed">${item.summary || item.details}</p>

        ${isL4 && item.flags ? `
          <div class="ml-8 mt-2 pt-2 border-t border-slate-900/80 flex flex-wrap gap-3 text-[11px] font-mono text-slate-400">
            <span>Flags: <strong class="text-sky-400">${item.flags}</strong></span>
            <span>Seq: <strong class="text-slate-200">${item.seq}</strong></span>
            <span>Ack: <strong class="text-slate-200">${item.ack}</strong></span>
            <span>Win: <strong class="text-slate-200">${item.win}</strong></span>${item.direction ? `<span class="ml-auto text-slate-500">${item.direction}</span>` : ''}
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

// Update UI button highlights when toggling views
function updateToggleUI() {
  const btnApp = document.getElementById('btn-layer-app');
  const btnTransport = document.getElementById('btn-layer-transport');

  if (btnApp && btnTransport) {
    if (typeof currentLayer !== 'undefined' && currentLayer === 'app') {
      btnApp.className = "px-3 py-1.5 rounded-lg bg-sky-500 text-white shadow transition font-bold";
      btnTransport.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition";
    } else {
      btnTransport.className = "px-3 py-1.5 rounded-lg bg-sky-500 text-white shadow transition font-bold";
      btnApp.className = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-white transition";
    }
  }
}

// Global switch function called by the UI buttons
window.switchViewLayer = function(layer) {
  window.currentLayer = layer;
  updateToggleUI();
  renderChecklist();
  if (typeof logActivity === 'function') {
    logActivity(`Switched view layer to: ${layer === 'app' ? 'Application Layer' : 'Transport Layer (L4)'}`);
  }
};

// Global render triggers called by playback / app.js
window.resetPlayback = function() {
  updateToggleUI();
  renderChecklist();
};

window.startPlayback = function() {
  updateToggleUI();
  renderChecklist();
};

function logActivity(message) {
  const logContainer = document.getElementById('terminal-log');
  if (!logContainer) return;
  const timeStr = new Date().toLocaleTimeString();
  logContainer.innerHTML += `<div><span class="text-slate-600">[${timeStr}]</span> ${message}</div>`;
  logContainer.scrollTop = logContainer.scrollHeight;
}