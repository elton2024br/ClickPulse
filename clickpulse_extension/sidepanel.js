const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const COLORS = {
  primary: '#7C3AED',
  primaryDim: 'rgba(124,58,237,0.5)',
  green: '#22C55E',
  red: '#EF4444',
  blue: '#3B82F6',
  yellow: '#F59E0B',
  border: '#3A3A50',
  textMuted: '#9CA3AF',
  textDim: '#6B7280',
  cardBg: '#2A2A3E',
  bg: '#1E1E2E'
};

let currentData = null;
let isPaused = false;

function init() {
  setupTabs();
  setupSettings();
  loadData();
  renderTimeline([]);

  chrome.storage.onChanged.addListener((changes) => {
    if (changes.clickpulse_data || changes.clickpulse_date) {
      loadData();
    }
    if (changes.clickpulse_paused) {
      isPaused = changes.clickpulse_paused.newValue || false;
      updatePauseUI();
    }
  });
}

function setupTabs() {
  $$('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      $$('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const target = tab.dataset.tab;
      $('#dashboardTab').classList.toggle('hidden', target !== 'dashboard');
      $('#settingsTab').classList.toggle('hidden', target !== 'settings');
    });
  });
}

function setupSettings() {
  $('#pauseToggle').addEventListener('change', () => {
    chrome.runtime.sendMessage({ type: 'TOGGLE_PAUSE' }, (res) => {
      if (chrome.runtime.lastError || !res) return;
      isPaused = res.paused;
      updatePauseUI();
    });
  });

  $('#resetBtn').addEventListener('click', () => {
    showConfirm('Resetar todos os dados de hoje?', () => {
      chrome.runtime.sendMessage({ type: 'RESET_DATA' }, () => {
        loadData();
      });
    });
  });
}

function showConfirm(msg, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'confirm-overlay';
  overlay.innerHTML = `
    <div class="confirm-box">
      <p>${msg}</p>
      <div class="confirm-actions">
        <button class="btn-cancel" id="confirmNo">Cancelar</button>
        <button class="btn-confirm" id="confirmYes">Confirmar</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelector('#confirmNo').addEventListener('click', () => overlay.remove());
  overlay.querySelector('#confirmYes').addEventListener('click', () => {
    onConfirm();
    overlay.remove();
  });
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.remove();
  });
}

function updatePauseUI() {
  $('#pauseToggle').checked = isPaused;
  const dot = $('#statusDot');
  const text = $('#statusText');
  if (isPaused) {
    dot.classList.add('paused');
    text.textContent = 'Pausado';
  } else {
    dot.classList.remove('paused');
    text.textContent = 'Ativo';
  }
}

function loadData() {
  chrome.runtime.sendMessage({ type: 'GET_DATA' }, (result) => {
    if (chrome.runtime.lastError || !result) return;
    currentData = result.data;
    isPaused = result.paused;
    updatePauseUI();
    renderAll(currentData);
  });
}

function renderAll(data) {
  if (!data) return;
  const total = (data.totalLeft || 0) + (data.totalRight || 0) + (data.totalMiddle || 0);

  const activeSlots = data.timeline ? data.timeline.filter(Boolean).length : 0;
  const activeMin = activeSlots * 30;
  const now = new Date();
  const minutesSinceMidnight = now.getHours() * 60 + now.getMinutes();
  const pauseMin = Math.max(0, minutesSinceMidnight - activeMin);

  const hoursElapsed = Math.max(1, now.getHours() + now.getMinutes() / 60);
  const rate = Math.round(total / hoursElapsed);

  const formatTime = (m) => `${Math.floor(m / 60)}h ${m % 60}m`;

  $('#statTotal').textContent = total.toLocaleString();
  $('#statActive').textContent = formatTime(activeMin);
  $('#statPause').textContent = formatTime(pauseMin);
  $('#statRate').textContent = rate.toLocaleString();

  renderBarChart(data.hourly);
  renderPieChart(data.totalLeft || 0, data.totalRight || 0, data.totalMiddle || 0, total);
  renderTimeline(data.timeline || []);
  renderLiveFeed(data.liveFeed || []);
}

function renderBarChart(hourly) {
  const canvas = $('#barChart');
  if (!canvas) return;

  const dpr = window.devicePixelRatio || 1;
  const displayW = canvas.parentElement.clientWidth - 16;
  const displayH = 160;
  canvas.style.width = displayW + 'px';
  canvas.style.height = displayH + 'px';
  canvas.width = displayW * dpr;
  canvas.height = displayH * dpr;

  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, displayW, displayH);

  const values = [];
  for (let h = 0; h < 24; h++) {
    const slot = hourly[h] || { left: 0, right: 0, middle: 0 };
    values.push(slot.left + slot.right + slot.middle);
  }

  const maxVal = Math.max(...values, 1);
  const padding = { top: 15, bottom: 30, left: 35, right: 5 };
  const chartW = displayW - padding.left - padding.right;
  const chartH = displayH - padding.top - padding.bottom;
  const barW = chartW / 24 - 2;

  ctx.strokeStyle = COLORS.border;
  ctx.lineWidth = 0.5;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartH / 4) * i;
    ctx.beginPath();
    ctx.setLineDash([3, 3]);
    ctx.moveTo(padding.left, y);
    ctx.lineTo(displayW - padding.right, y);
    ctx.stroke();
  }
  ctx.setLineDash([]);

  ctx.fillStyle = COLORS.textDim;
  ctx.font = '9px monospace';
  ctx.textAlign = 'right';
  for (let i = 0; i <= 4; i++) {
    const val = Math.round(maxVal * (4 - i) / 4);
    const y = padding.top + (chartH / 4) * i;
    ctx.fillText(val, padding.left - 4, y + 3);
  }

  ctx.textAlign = 'center';
  for (let h = 0; h < 24; h += 3) {
    const x = padding.left + (chartW / 24) * h + barW / 2;
    ctx.fillText(`${h.toString().padStart(2, '0')}h`, x, displayH - 5);
  }

  for (let h = 0; h < 24; h++) {
    const x = padding.left + (chartW / 24) * h + 1;
    const barH = (values[h] / maxVal) * chartH;
    const y = padding.top + chartH - barH;

    const grad = ctx.createLinearGradient(x, y, x, y + barH);
    if (values[h] > maxVal * 0.6) {
      grad.addColorStop(0, COLORS.primary);
      grad.addColorStop(1, COLORS.primaryDim);
    } else {
      grad.addColorStop(0, COLORS.primaryDim);
      grad.addColorStop(1, 'rgba(124,58,237,0.2)');
    }

    ctx.fillStyle = grad;
    const radius = Math.min(3, barW / 2);
    roundedRect(ctx, x, y, barW, barH, radius);
  }
}

function roundedRect(ctx, x, y, w, h, r) {
  if (h < 1) return;
  r = Math.min(r, h / 2, w / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, 0);
  ctx.arcTo(x, y + h, x, y, 0);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  ctx.fill();
}

function renderPieChart(left, right, middle, total) {
  const canvas = $('#pieChart');
  if (!canvas) return;

  const dpr = window.devicePixelRatio || 1;
  const size = 160;
  canvas.style.width = size + 'px';
  canvas.style.height = size + 'px';
  canvas.width = size * dpr;
  canvas.height = size * dpr;

  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, size, size);

  const cx = size / 2;
  const cy = size / 2;
  const outerR = 70;
  const innerR = 48;

  if (total === 0) {
    ctx.beginPath();
    ctx.arc(cx, cy, outerR, 0, Math.PI * 2);
    ctx.arc(cx, cy, innerR, 0, Math.PI * 2, true);
    ctx.fillStyle = COLORS.border;
    ctx.fill();
    $('#pieTotal').textContent = '0';
    $('#legendLeft').textContent = '0';
    $('#legendRight').textContent = '0';
    $('#legendMiddle').textContent = '0';
    return;
  }

  const slices = [
    { value: left, color: COLORS.blue },
    { value: right, color: COLORS.red },
    { value: middle, color: COLORS.yellow }
  ];

  const nonZeroSlices = slices.filter(s => s.value > 0);
  const gap = nonZeroSlices.length > 1 ? 0.04 : 0;
  let startAngle = -Math.PI / 2;

  nonZeroSlices.forEach(slice => {
    const sweep = Math.max(0.01, (slice.value / total) * Math.PI * 2 - gap);
    ctx.beginPath();
    ctx.arc(cx, cy, outerR, startAngle, startAngle + sweep);
    ctx.arc(cx, cy, innerR, startAngle + sweep, startAngle, true);
    ctx.closePath();
    ctx.fillStyle = slice.color;
    ctx.fill();
    startAngle += sweep + gap;
  });

  $('#pieTotal').textContent = total.toLocaleString();
  $('#legendLeft').textContent = left.toLocaleString();
  $('#legendRight').textContent = right.toLocaleString();
  $('#legendMiddle').textContent = middle.toLocaleString();
}

function renderTimeline(timeline) {
  const container = $('#timelineBar');
  if (!container) return;
  container.innerHTML = '';

  const slots = timeline.length === 48 ? timeline : new Array(48).fill(false);
  slots.forEach((active, i) => {
    const seg = document.createElement('div');
    seg.className = `timeline-segment ${active ? 'active' : 'inactive'}`;
    const h = Math.floor(i / 2);
    const m = i % 2 === 0 ? '00' : '30';
    seg.title = `${h.toString().padStart(2, '0')}:${m} — ${active ? 'Ativo' : 'Pausa'}`;
    container.appendChild(seg);
  });
}

function renderLiveFeed(feed) {
  const container = $('#liveFeedList');
  if (!container) return;

  if (!feed || feed.length === 0) {
    container.innerHTML = '<div class="feed-empty">Aguardando atividade do mouse...</div>';
    return;
  }

  const typeLabels = { left: 'Esquerdo', right: 'Direito', middle: 'Meio' };
  const displayed = feed.slice(0, 20);

  const html = displayed.map(click => {
    const time = new Date(click.timestamp);
    const timeStr = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}:${time.getSeconds().toString().padStart(2, '0')}`;

    return `<div class="feed-item" data-id="${click.id}">
      <div class="feed-item-left">
        <span class="feed-type ${click.type}">${typeLabels[click.type] || 'Clique'}</span>
        <span class="feed-coords">X:${String(click.x).padStart(4, ' ')} Y:${String(click.y).padStart(4, ' ')}</span>
      </div>
      <span class="feed-time">${timeStr}</span>
    </div>`;
  }).join('');

  container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', init);
