/**
 * Activity Controller
 * Manages mode switching and user interaction logging.
 */

let currentActivity = 'browsing';

function selectActivity(activity) {
  currentActivity = activity;
  
  ['browsing', 'mail', 'streaming'].forEach(act => {
    const tab = document.getElementById(`tab-${act}`);
    const form = document.getElementById(`form-${act}`);
    
    if (act === activity) {
      tab.className = "py-2.5 px-3 text-xs md:text-sm font-bold rounded-lg transition flex items-center justify-center gap-2 bg-slate-800 text-white border border-slate-600 shadow-sm";
      if (form) form.classList.remove('hidden');
    } else {
      tab.className = "py-2.5 px-3 text-xs md:text-sm font-bold rounded-lg transition flex items-center justify-center gap-2 text-slate-400 hover:text-white hover:bg-slate-900";
      if (form) form.classList.add('hidden');
    }
  });
  
  if (typeof resetPlayback === 'function') {
    resetPlayback();
  }
}

function logActivity(message) {
  const logBox = document.getElementById('activity-log');
  if (!logBox) return;
  
  const time = new Date().toLocaleTimeString().split(' ')[0];
  const logItem = document.createElement('p');
  logItem.innerHTML = `<span class="text-slate-500">[${time}]</span> ${message}`;
  
  logBox.appendChild(logItem);
  logBox.scrollTop = logBox.scrollHeight;
}