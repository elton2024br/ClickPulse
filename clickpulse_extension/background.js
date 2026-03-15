chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(console.error);

function getTodayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

async function getStorageData() {
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
    handleClick(message.data);
    sendResponse({ ok: true });
  } else if (message.type === 'GET_DATA') {
    getStorageData().then(result => sendResponse(result));
    return true;
  } else if (message.type === 'TOGGLE_PAUSE') {
    chrome.storage.local.get('clickpulse_paused', (r) => {
      const newVal = !r.clickpulse_paused;
      chrome.storage.local.set({ clickpulse_paused: newVal }, () => {
        sendResponse({ paused: newVal });
      });
    });
    return true;
  } else if (message.type === 'RESET_DATA') {
    const freshData = createFreshData();
    const todayKey = getTodayKey();
    chrome.storage.local.set({
      clickpulse_data: freshData,
      clickpulse_date: todayKey
    }, () => sendResponse({ ok: true }));
    return true;
  }
});

async function handleClick(clickData) {
  const { data, paused } = await getStorageData();
  if (paused) return;

  const btnName = getButtonName(clickData.button);
  const now = new Date();
  const hour = now.getHours();
  const halfHourSlot = hour * 2 + (now.getMinutes() >= 30 ? 1 : 0);

  if (btnName === 'left') data.totalLeft++;
  else if (btnName === 'right') data.totalRight++;
  else if (btnName === 'middle') data.totalMiddle++;

  if (data.hourly[hour]) {
    data.hourly[hour][btnName]++;
  }

  data.timeline[halfHourSlot] = true;

  const feedEntry = {
    id: `${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
    timestamp: now.toISOString(),
    type: btnName,
    x: clickData.x || 0,
    y: clickData.y || 0
  };
  data.liveFeed = [feedEntry, ...(data.liveFeed || [])].slice(0, 30);

  if (!data.firstClickTime) data.firstClickTime = now.toISOString();
  data.lastClickTime = now.toISOString();

  await chrome.storage.local.set({
    clickpulse_data: data,
    clickpulse_date: getTodayKey()
  });
}
