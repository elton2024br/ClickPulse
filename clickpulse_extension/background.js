chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(console.error);

let clickQueue = [];
let flushTimer = null;
const FLUSH_INTERVAL = 200;

function getTodayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

async function getStorageData() {
  try {
    const todayKey = getTodayKey();
    const result = await chrome.storage.local.get(['clickpulse_data', 'clickpulse_date', 'clickpulse_paused']);
    const storedDate = result.clickpulse_date || '';
    const paused = result.clickpulse_paused || false;

    if (storedDate !== todayKey) {
      const freshData = createFreshData();
      await chrome.storage.local.set({
        clickpulse_data: freshData,
        clickpulse_date: todayKey
      });
      return { data: freshData, paused };
    }

    return { data: result.clickpulse_data || createFreshData(), paused };
  } catch (e) {
    console.error('ClickPulse: storage read error', e);
    return { data: createFreshData(), paused: false };
  }
}

function createFreshData() {
  const hourly = {};
  for (let i = 0; i < 24; i++) hourly[i] = { left: 0, right: 0, middle: 0 };
  return {
    totalLeft: 0,
    totalRight: 0,
    totalMiddle: 0,
    hourly,
    liveFeed: [],
    timeline: new Array(48).fill(false),
    firstClickTime: null,
    lastClickTime: null
  };
}

function getButtonName(button) {
  switch (button) {
    case 0: return 'left';
    case 2: return 'right';
    case 1: return 'middle';
    default: return 'left';
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CLICK_EVENT') {
    enqueueClick(message.data);
    sendResponse({ ok: true });
  } else if (message.type === 'GET_DATA') {
    getStorageData()
      .then(result => sendResponse(result))
      .catch(() => sendResponse({ data: createFreshData(), paused: false }));
    return true;
  } else if (message.type === 'TOGGLE_PAUSE') {
    chrome.storage.local.get('clickpulse_paused', (r) => {
      if (chrome.runtime.lastError) {
        sendResponse({ paused: false });
        return;
      }
      const newVal = !r.clickpulse_paused;
      chrome.storage.local.set({ clickpulse_paused: newVal }, () => {
        sendResponse({ paused: newVal });
      });
    });
    return true;
  } else if (message.type === 'RESET_DATA') {
    clickQueue = [];
    const freshData = createFreshData();
    const todayKey = getTodayKey();
    chrome.storage.local.set({
      clickpulse_data: freshData,
      clickpulse_date: todayKey
    }, () => {
      if (chrome.runtime.lastError) {
        console.error('ClickPulse: reset error', chrome.runtime.lastError);
      }
      sendResponse({ ok: true });
    });
    return true;
  }
});

function enqueueClick(clickData) {
  clickQueue.push(clickData);

  if (!flushTimer) {
    flushTimer = setTimeout(flushClicks, FLUSH_INTERVAL);
  }
}

let flushing = false;

async function flushClicks() {
  flushTimer = null;

  if (flushing || clickQueue.length === 0) return;
  flushing = true;

  const batch = clickQueue.splice(0, clickQueue.length);

  try {
    const { data, paused } = await getStorageData();
    if (paused) {
      flushing = false;
      return;
    }

    const now = new Date();

    for (const clickData of batch) {
      const btnName = getButtonName(clickData.button);
      const clickTime = new Date(clickData.timestamp || Date.now());
      const hour = clickTime.getHours();
      const halfHourSlot = hour * 2 + (clickTime.getMinutes() >= 30 ? 1 : 0);

      if (btnName === 'left') data.totalLeft++;
      else if (btnName === 'right') data.totalRight++;
      else if (btnName === 'middle') data.totalMiddle++;

      if (data.hourly[hour]) {
        data.hourly[hour][btnName]++;
      }

      data.timeline[halfHourSlot] = true;

      const feedEntry = {
        id: `${clickData.timestamp || Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        timestamp: clickTime.toISOString(),
        type: btnName,
        x: clickData.x || 0,
        y: clickData.y || 0
      };
      data.liveFeed.unshift(feedEntry);

      if (!data.firstClickTime) data.firstClickTime = clickTime.toISOString();
      data.lastClickTime = clickTime.toISOString();
    }

    data.liveFeed = data.liveFeed.slice(0, 30);

    await chrome.storage.local.set({
      clickpulse_data: data,
      clickpulse_date: getTodayKey()
    });
  } catch (e) {
    console.error('ClickPulse: flush error', e);
  }

  flushing = false;

  if (clickQueue.length > 0) {
    flushTimer = setTimeout(flushClicks, FLUSH_INTERVAL);
  }
}
