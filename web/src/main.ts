import './styles/theme.css';
import { store } from './state/store';
import { renderHeader, bindHeaderEvents } from './components/Header';
import { renderConditionMonitors, bindConditionEvents } from './components/ConditionMonitors';
import { renderModifiersBar, bindModifiersEvents } from './components/ModifiersBar';
import { renderAttributesPanel, bindAttributesEvents } from './components/AttributesPanel';
import { renderCombatPanel, bindCombatEvents } from './components/CombatPanel';
import { renderSkillsPanel, bindSkillsEvents } from './components/SkillsPanel';
import { renderMatrixRiggingPanel, bindMatrixEvents } from './components/MatrixRiggingPanel';
import { renderMagicPanel, bindMagicEvents } from './components/MagicPanel';
import { renderGearPanel, bindGearEvents } from './components/GearPanel';
import { renderContactsPanel, bindContactsEvents } from './components/ContactsPanel';
import { renderDiceTray, bindDiceEvents } from './components/DiceTray';
import { renderRulesDrawer, bindRulesEvents } from './components/RulesDrawer';
import { renderNavigation, bindNavigationEvents } from './components/Navigation';

function renderApp() {
  const root = document.getElementById('app');
  if (!root) return;

  // Set document theme
  const theme = store.getTheme();
  document.body.setAttribute('data-theme', theme);

  const activeTab = store.activeTab;

  root.innerHTML = `
    <div class="app-container">
      ${renderHeader()}
      ${renderConditionMonitors()}
      ${renderModifiersBar()}
      ${renderAttributesPanel()}

      <!-- Dynamic Tab Content -->
      <main>
        <section class="tab-content ${activeTab === 'dashboard' ? 'active' : ''}" id="tab-dashboard">
          ${renderCombatPanel()}
          <div style="margin-top:24px;"></div>
          ${renderSkillsPanel()}
        </section>

        <section class="tab-content ${activeTab === 'combat' ? 'active' : ''}" id="tab-combat">
          ${renderCombatPanel()}
        </section>

        <section class="tab-content ${activeTab === 'skills' ? 'active' : ''}" id="tab-skills">
          ${renderSkillsPanel()}
        </section>

        <section class="tab-content ${activeTab === 'matrix' ? 'active' : ''}" id="tab-matrix">
          ${renderMatrixRiggingPanel()}
        </section>

        <section class="tab-content ${activeTab === 'magic' ? 'active' : ''}" id="tab-magic">
          ${renderMagicPanel()}
        </section>

        <section class="tab-content ${activeTab === 'gear' ? 'active' : ''}" id="tab-gear">
          ${renderGearPanel()}
        </section>

        <section class="tab-content ${activeTab === 'contacts' ? 'active' : ''}" id="tab-contacts">
          ${renderContactsPanel()}
        </section>
      </main>

      ${renderDiceTray()}
      ${renderRulesDrawer()}
      ${renderNavigation()}
    </div>
  `;

  // Bind interactive DOM events
  bindHeaderEvents(root);
  bindConditionEvents(root);
  bindModifiersEvents(root);
  bindAttributesEvents(root);
  bindCombatEvents(root);
  bindSkillsEvents(root);
  bindMatrixEvents(root);
  bindMagicEvents(root);
  bindGearEvents(root);
  bindContactsEvents(root);
  bindDiceEvents(root);
  bindRulesEvents(root);
  bindNavigationEvents(root);
}

import { defaultBundle } from './data/defaultBundle';

// Initial bootstrapping
function init() {
  // Check for embedded data bundle, default bundled data, or HTTP fetch
  const embeddedBundle = (window as any).__SR6_DATA_BUNDLE__;
  if (embeddedBundle) {
    store.initBundle(embeddedBundle, (window as any).__SR6_INITIAL_CHAR__);
  } else if (defaultBundle && Object.keys(defaultBundle).length > 0) {
    store.initBundle(defaultBundle, 'reiko');
  } else if (typeof fetch !== 'undefined' && location.protocol.startsWith('http')) {
    fetch('/api/bundle')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.characters) {
          store.initBundle(data.characters);
        }
      })
      .catch(() => {});
  }

  // Subscribe store changes
  store.subscribe(() => {
    renderApp();
  });

  renderApp();

  // Register service worker if available
  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
}

// DOMContentLoaded listener
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
