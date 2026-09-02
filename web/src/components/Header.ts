import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderHeader(): string {
  const char = store.getActiveCharacter();
  const charList = store.getCharacterList();
  const state = store.getActiveState();

  if (!char) {
    return `<div class="top-header"><h1>SR6 Tactical Dossier</h1></div>`;
  }

  const handle = char.identity?.handle || 'Unknown Runner';
  const role = char.identity?.role || 'Shadowrunner';
  const nuyen = (char.identity?.nuyen || 0).toLocaleString();
  const karmaAvail = char.identity?.karma ?? char.identity?.karma_avail ?? 0;
  const initialLetter = handle.charAt(0).toUpperCase();

  // Character switcher buttons
  const tabsHtml = charList
    .map(
      (c) => `
    <button class="char-tab-btn ${c.id === store.activeCharId ? 'active' : ''}" data-char-id="${c.id}">
      <span>${c.name}</span>
      <span class="tab-role">${c.role.split('/')[0].trim()}</span>
    </button>
  `
    )
    .join('');

  return `
    <header class="top-header">
      <div class="char-select-wrapper">
        <div class="char-avatar-badge" id="btn-char-avatar" title="Switch Runner Theme">
          ${initialLetter}
        </div>
        <div class="char-meta-info">
          <h1>${handle}</h1>
          <div class="role-tag">${role}</div>
        </div>
      </div>

      <div class="header-actions">
        <div class="currency-badge" title="Available Nuyen">
          <span>¥</span>
          <span class="nuyen-val">${nuyen}</span>
        </div>
        <div class="currency-badge" title="Available Karma">
          <span>⚡</span>
          <span class="karma-val">${karmaAvail}</span>
        </div>
        <button class="icon-btn ${store.isModifiersHudOpen ? 'active' : ''}" id="btn-toggle-modifiers" title="Toggle Modifiers & Sustaining HUD" style="font-size:1.05rem; ${store.isModifiersHudOpen ? 'background:var(--accent-primary); color:#000;' : ''}">
          ⚡
        </button>
        <button class="icon-btn" id="btn-toggle-sound" title="${sound.muted ? 'Unmute Audio' : 'Mute Audio'}">
          ${sound.muted ? '🔇' : '🔊'}
        </button>
        <button class="icon-btn ${store.isDiceTrayOpen ? 'active' : ''}" id="btn-open-dice" title="Open Cyberpunk Dice Tray">
          🎲
        </button>
        <button class="icon-btn ${store.isRulesDrawerOpen ? 'active' : ''}" id="btn-open-rules" title="Search Rules & Stat Cards">
          📖
        </button>
      </div>
    </header>

    <div class="char-switcher-tabs">
      ${tabsHtml}
    </div>
  `;
}

export function bindHeaderEvents(container: HTMLElement) {
  // Switch character tab
  container.querySelectorAll('.char-tab-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = (e.currentTarget as HTMLElement).getAttribute('data-char-id');
      if (target) {
        sound.playClick();
        store.setActiveCharacter(target);
      }
    });
  });

  // Toggle dice tray
  const diceBtn = container.querySelector('#btn-open-dice');
  if (diceBtn) {
    diceBtn.addEventListener('click', () => {
      sound.playClick();
      store.toggleDiceTray();
    });
  }

  // Toggle modifiers HUD
  const modBtn = container.querySelector('#btn-toggle-modifiers');
  if (modBtn) {
    modBtn.addEventListener('click', () => {
      sound.playClick();
      store.toggleModifiersHud();
    });
  }

  // Toggle sound mute
  const soundBtn = container.querySelector('#btn-toggle-sound');
  if (soundBtn) {
    soundBtn.addEventListener('click', () => {
      sound.toggleMute();
      if (!sound.muted) sound.playClick();
      const root = document.getElementById('app');
      if (root) {
        // Re-render header to update icon
        const hdr = root.querySelector('.top-header');
        if (hdr) {
          hdr.outerHTML = renderHeader().split('<div class="char-switcher-tabs">')[0];
          bindHeaderEvents(root);
        }
      }
    });
  }

  // Toggle rules drawer
  const rulesBtn = container.querySelector('#btn-open-rules');
  if (rulesBtn) {
    rulesBtn.addEventListener('click', () => {
      sound.playClick();
      store.toggleRulesDrawer();
    });
  }
}
