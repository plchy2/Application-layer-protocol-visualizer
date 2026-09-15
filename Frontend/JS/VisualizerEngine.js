/**
 * Protocol Visualizer Engine
 * Controls state, step animation, auto-playback, DOM updates.
 */

let currentStepIndex = 0;
let isPlaying = false;
let autoPlayTimer = null;
let activeFlowData = [];

function renderSteps() {
  const container = document.getElementById('sequence-container');
  if (!container || !activeFlowData || activeFlowData.length === 0) return;

  container.innerHTML = '';

  activeFlowData.forEach((item, index) => {
    const isCurrent = index === currentStepIndex;
    const isDone = index < currentStepIndex;

    const div = document.createElement('div');
    div.onclick = () => jumpToStep(index);
    div.className = `p-3 rounded-lg border text-xs cursor-pointer transition flex items-center justify-between ${
      isCurrent 
        ? 'bg-slate-900 border-sky-400 text-white shadow-md' 
        : isDone 
        ? 'bg-slate-950/40 border-slate-800 text-slate-400' 
        : 'bg-slate-950/20 border-slate-900 text-slate-600 opacity-50'
    }`;

    div.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] ${
          isCurrent ? 'bg-sky-400 text-slate-950' : isDone ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-500'
        }">${item.step}</span>
        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold ${isCurrent ? 'text-sky-300' : 'text-slate-200'}">${item.protocol}</span>
            <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">${item.pdu || 'PDU'}</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">${item.summary}</div>
        </div>
      </div>
      <i class="fa-solid ${item.direction.includes('client -> server') ? 'fa-arrow-right text-sky-400' : item.direction.includes('server -> client') ? 'fa-arrow-left text-emerald-400' : 'fa-arrows-rotate text-amber-400'}"></i>
    `;
    container.appendChild(div);
  });

  const activeData = activeFlowData[currentStepIndex];
  if (!activeData) return;
  
  document.getElementById('step-counter').innerText = `Step ${currentStepIndex + 1}/${activeFlowData.length}`;
  document.getElementById('inspect-protocol').innerText = activeData.layer || activeData.protocol;
  document.getElementById('packet-payload').innerText = activeData.details;
  document.getElementById('protocol-badge').innerText = activeData.layer || activeData.protocol;
  document.getElementById('server-label').innerText = activeData.serverName || "Target Server";

  const indicator = document.getElementById('packet-indicator');
  if (indicator) {
    if (activeData.direction.includes('client -> server')) {
      indicator.style.transform = 'translateX(200px)';
      indicator.className = "w-14 h-2 bg-sky-400 rounded-full absolute transition-all duration-500 shadow-md";
    } else if (activeData.direction.includes('server -> client')) {
      indicator.style.transform = 'translateX(0px)';
      indicator.className = "w-14 h-2 bg-emerald-400 rounded-full absolute transition-all duration-500 shadow-md";
    } else {
      indicator.style.transform = 'translateX(100px)';
      indicator.className = "w-14 h-2 bg-amber-400 rounded-full absolute transition-all duration-500 shadow-md";
    }
  }
}

function startPlayback() {
  isPlaying = true;
  const playIcon = document.getElementById('play-icon');
  if (playIcon) playIcon.className = 'fa-solid fa-pause text-xs';
  
  if (autoPlayTimer) clearInterval(autoPlayTimer);
  autoPlayTimer = setInterval(() => {
    if (currentStepIndex < activeFlowData.length - 1) {
      currentStepIndex++;
      renderSteps();
    } else {
      pausePlayback();
    }
  }, 2500);
}

function pausePlayback() {
  isPlaying = false;
  const playIcon = document.getElementById('play-icon');
  if (playIcon) playIcon.className = 'fa-solid fa-play text-xs';
  if (autoPlayTimer) clearInterval(autoPlayTimer);
}

function togglePlayPause() { isPlaying ? pausePlayback() : startPlayback(); }
function nextStep() { pausePlayback(); if (currentStepIndex < activeFlowData.length - 1) { currentStepIndex++; renderSteps(); } }
function prevStep() { pausePlayback(); if (currentStepIndex > 0) { currentStepIndex--; renderSteps(); } }
function jumpToStep(idx) { pausePlayback(); currentStepIndex = idx; renderSteps(); }
function resetPlayback() { pausePlayback(); currentStepIndex = 0; renderSteps(); }