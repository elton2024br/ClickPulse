let lastSendTime = 0;
const THROTTLE_MS = 50;

document.addEventListener('mousedown', (e) => {
  const now = Date.now();
  if (now - lastSendTime < THROTTLE_MS) return;
  lastSendTime = now;

  try {
    chrome.runtime.sendMessage({
      type: 'CLICK_EVENT',
      data: {
        button: e.button,
        x: e.clientX,
        y: e.clientY,
        url: window.location.href,
        timestamp: now
      }
    }).catch(() => {});
  } catch (_) {}
}, true);
