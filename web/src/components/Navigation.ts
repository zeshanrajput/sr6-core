import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderNavigation(): string {
  const activeTab = store.activeTab;

  const tabs = [
    { id: 'dashboard', label: 'OVERVIEW', icon: '📊' },
    { id: 'combat', label: 'COMBAT', icon: '⚔️' },
    { id: 'skills', label: 'SKILLS', icon: '🎯' },
    { id: 'matrix', label: 'MATRIX / RIG', icon: '🌐' },
    { id: 'magic', label: 'MAGIC', icon: '🔮' },
    { id: 'gear', label: 'GEAR', icon: '⚙️' },
    { id: 'contacts', label: 'CONTACTS', icon: '👥' },
  ];

  const itemsHtml = tabs
    .map(
      (t) => `
    <button class="nav-item ${activeTab === t.id ? 'active' : ''}" data-tab-id="${t.id}">
      <span class="nav-icon">${t.icon}</span>
      <span>${t.label}</span>
    </button>
  `
    )
    .join('');

  return `
    <nav class="bottom-nav">
      ${itemsHtml}
    </nav>
  `;
}

export function bindNavigationEvents(container: HTMLElement) {
  container.querySelectorAll('.nav-item').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const tabId = (e.currentTarget as HTMLElement).getAttribute('data-tab-id');
      if (tabId) {
        sound.playClick();
        store.setActiveTab(tabId);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });
}
