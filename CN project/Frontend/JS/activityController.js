let currentActivity = 'browsing';

function selectActivity(activity) {
  currentActivity = activity;
  ['browsing', 'mail', 'streaming'].forEach(act => {
    const tab = document.getElementById(`tab-${act}`);
    const form = document.getElementById(`form-${act}`);
    if (act === activity) {
      tab.className = "py-2 text-xs font-semibold rounded-md transition flex flex-col items-center gap-1 bg-blue-600 text-white shadow";
      form.classList.remove('hidden');
    } else {
      tab.className = "py-2 text-xs font-semibold rounded-md transition flex flex-col items-center gap-1 text-slate-400 hover:text-white hover:bg-slate-800";
      form.classList.add('hidden');
    }
  });
  resetPlayback();
}

function logActivity(message) {
  const logBox = document.getElementById('activity-log');
  const time = new Date().toLocaleTimeString().split(' ')[0];
  const logItem = document.createElement('p');
  logItem.innerHTML = `<span class="text-slate-500">[${time}]</span> ${message}`;
  logBox.appendChild(logItem);
  logBox.scrollTop = logBox.scrollHeight;
}