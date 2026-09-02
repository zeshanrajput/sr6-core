import { store } from '../state/store';
import { sound } from '../utils/audio';

interface RuleTopic {
  id: string;
  title: string;
  category: string;
  color: string;
  summary: string;
  detailsHtml: string;
}

const CANONICAL_RULES: RuleTopic[] = [
  {
    id: 'edge_actions',
    title: 'Edge Actions & Boosts (SR6 Core p. 45-47)',
    category: 'Edge',
    color: 'var(--accent-primary)',
    summary: 'Rules for spending Edge on action tests, defense, and healing.',
    detailsHtml: `
      <ul style="margin: 8px 0 0 16px; font-size: 0.85rem; line-height: 1.5;">
        <li><strong>1 Edge:</strong> Reroll one single die (< 5), OR add +1 to a single die roll, OR add +3 to Initiative score.</li>
        <li><strong>2 Edge:</strong> Gain +1 Edge on Opposed Test, OR heal 1 Stun damage box instantly.</li>
        <li><strong>3 Edge:</strong> Heal 1 Physical damage box, OR buy 1 automatic hit directly on an action test.</li>
        <li><strong>4 Edge (Reroll All Failures):</strong> Reroll <em>all</em> failed dice (< 5) on the roll, keeping all existing hits.</li>
        <li><strong>4 Edge (Boost Pool & Explode):</strong> Add your Edge attribute rating directly to the dice pool with exploding 6s (Rule of Six).</li>
        <li><strong>5 Edge (Negate Glitch):</strong> Completely negate a Glitch or Critical Glitch result.</li>
      </ul>
    `,
  },
  {
    id: 'attributes',
    title: 'Attributes & Derived Ratings (SR6 Core p. 64-66)',
    category: 'Core',
    color: 'var(--accent-emerald)',
    summary: 'Physical, Mental, and Special attributes definitions and caps.',
    detailsHtml: `
      <ul style="margin: 8px 0 0 16px; font-size: 0.85rem; line-height: 1.5;">
        <li><strong>Body (BOD):</strong> Physical toughness and damage resistance soak pool. Condition boxes = 8 + (BOD / 2).</li>
        <li><strong>Agility (AGI):</strong> Hand-eye coordination, ranged firearms, melee accuracy, and acrobatics.</li>
        <li><strong>Reaction (REA):</strong> Reflexes and physical defense pool (REA + INT). Determines Physical Initiative (REA + INT + 1d6).</li>
        <li><strong>Strength (STR):</strong> Physical power, jumping, carrying capacity, and melee damage baselines.</li>
        <li><strong>Willpower (WIL):</strong> Mental fortitude, spell drain resistance, and Stun condition monitor = 8 + (WIL / 2).</li>
        <li><strong>Logic (LOG):</strong> Analytical reasoning, hacking actions, decker combat, First Aid, and Biotech.</li>
        <li><strong>Intuition (INT):</strong> Gut instinct, perception tests, Matrix defense, and Initiative.</li>
        <li><strong>Charisma (CHA):</strong> Personal magnetism, social tests (Con, Negotiation, Etiquette), and shamanic drain.</li>
        <li><strong>Edge (EDG):</strong> Luck, tactical momentum, and rule-bending prowess. Max gain per combat round = 2 Edge.</li>
      </ul>
    `,
  },
  {
    id: 'wound_penalties',
    title: 'Wound Penalties & Damage Tracks (SR6 Core p. 118)',
    category: 'Combat',
    color: 'var(--accent-gold)',
    summary: 'Damage track box math, overflow, and -1 dice pool thresholds.',
    detailsHtml: `
      <p style="font-size: 0.85rem; margin: 6px 0;">
        For every <strong>3 full boxes</strong> of damage marked on your Physical and/or Stun condition monitors, you suffer a cumulative <strong>-1 dice pool penalty</strong> to all action tests (except Damage Resistance soak tests).
      </p>
      <div style="font-size: 0.8rem; font-family:var(--font-mono); color:var(--text-secondary); background:rgba(0,0,0,0.3); padding:8px; border-radius:6px;">
        1-2 Boxes: 0 Penalty<br>
        3-5 Boxes: -1 Penalty<br>
        6-8 Boxes: -2 Penalty<br>
        9-11 Boxes: -3 Penalty<br>
        12+ Boxes: -4 Penalty
      </div>
    `,
  },
  {
    id: 'matrix_actions',
    title: 'Matrix Actions & ASDF Living Persona (SR6 Core p. 174-185)',
    category: 'Matrix',
    color: 'var(--accent-primary)',
    summary: 'Attack, Sleaze, Data Processing, Firewall, and Major Matrix actions.',
    detailsHtml: `
      <ul style="margin: 8px 0 0 16px; font-size: 0.85rem; line-height: 1.5;">
        <li><strong>Brute Force:</strong> Cybercombat + Logic vs. Firewall + Willpower (Major Action). Places User Access or Admin on target.</li>
        <li><strong>Hack on the Fly:</strong> Hacking + Logic vs. Firewall + Intuition (Major Action). Stealthily gains User Access without triggering alarms.</li>
        <li><strong>Data Spike:</strong> Cybercombat + Logic vs. Firewall + Willpower (Major Action). Base DV = Attack Rating / 2 Matrix damage.</li>
        <li><strong>Matrix Perception:</strong> Computer + Intuition vs. Sleaze + Willpower (Minor Action). Analyzes icons and hidden nodes.</li>
        <li><strong>Control Device:</strong> Electronics / Engineering + Logic vs. Device Defense (Major Action). Controls cameras, turrets, maglocks.</li>
      </ul>
    `,
  },
  {
    id: 'combat_firing_modes',
    title: 'Weapon Firing Modes & Ammo Usage (SR6 Core p. 108)',
    category: 'Combat',
    color: 'var(--accent-rose)',
    summary: 'SS, SA, BF, and FA firing mode mechanics and ammo expenditure.',
    detailsHtml: `
      <p style="font-size: 0.82rem; margin: 4px 0 8px; color: var(--text-secondary);">
        <strong>Core Rule:</strong> <em>All ranged weapons can be fired in Single Shot (SS) mode (1 round).</em> Any listed modes (SA, BF, FA) represent additional capabilities in addition to SS.
      </p>
      <ul style="margin: 8px 0 0 16px; font-size: 0.85rem; line-height: 1.5;">
        <li><strong>SS (Single Shot):</strong> 1 round expended. Standard single attack (always available for all ranged weapons).</li>
        <li><strong>SA (Semi-Automatic):</strong> 2 rounds expended. Can split attacks across 2 targets or attack 1 target.</li>
        <li><strong>BF (Burst Fire):</strong> 4 rounds expended. Grants +2 Attack Rating (AR) or increases DV by +1 against primary target.</li>
        <li><strong>FA (Full Auto):</strong> 10 rounds expended. Area suppressive fire or maximum damage burst (+4 AR or +2 DV).</li>
      </ul>
    `,
  },
  {
    id: 'magic_drain',
    title: 'Spellcasting Drain & Technomancy Fading (SR6 Core p. 130-142)',
    category: 'Magic',
    color: 'var(--accent-gold)',
    summary: 'Drain values, drain resistance tests, and physical vs stun drain conversion.',
    detailsHtml: `
      <ul style="margin: 8px 0 0 16px; font-size: 0.85rem; line-height: 1.5;">
        <li><strong>Hermetic Drain:</strong> Willpower + Logic vs. Spell Drain Value (DV).</li>
        <li><strong>Shamanic Drain:</strong> Willpower + Charisma vs. Spell Drain Value (DV).</li>
        <li><strong>Technomancer Fading:</strong> Willpower + Logic vs. Complex Form Fading Value.</li>
        <li><strong>Drain Type:</strong> If Drain hits rolled &lt; Drain Value, remaining unsoaked points become Stun damage. If hits scored on spellcasting test exceed Magic attribute, Drain becomes <em>Physical</em> damage!</li>
      </ul>
    `,
  },
];

export function renderRulesDrawer(): string {
  const isOpen = store.isRulesDrawerOpen;
  const drawer = store.drawerContent;

  const rulesCardsHtml = CANONICAL_RULES.map(
    (r) => `
    <div class="tactical-card rule-topic-card" data-topic-id="${r.id}" data-keywords="${r.title} ${r.category} ${r.summary}" style="margin-bottom:12px; cursor:pointer;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <strong style="color:${r.color}; font-size:0.95rem;">${r.title}</strong>
        <span class="chip" style="font-size:0.65rem;">${r.category}</span>
      </div>
      <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:8px;">${r.summary}</p>
      ${r.detailsHtml}
    </div>
  `
  ).join('');

  return `
    <!-- Universal Drill-Down Drawer -->
    <div class="drill-down-drawer ${drawer ? 'open' : ''}" id="universal-drilldown-drawer">
      <div class="drawer-header">
        <h3 style="color:var(--text-primary); font-family:var(--font-tech);">${drawer ? drawer.title : 'Details'}</h3>
        <button class="icon-btn" id="btn-close-drilldown" style="width:32px; height:32px;">✕</button>
      </div>
      <div class="drawer-body">
        ${drawer ? drawer.html : ''}
      </div>
    </div>

    <!-- Quick Rules Reference Drawer -->
    <div class="drill-down-drawer ${isOpen ? 'open' : ''}" id="rules-reference-drawer">
      <div class="drawer-header">
        <h3 style="color:var(--accent-primary); font-family:var(--font-tech);">📖 RULES & STAT LOOKUP</h3>
        <button class="icon-btn" id="btn-close-rules" style="width:32px; height:32px;">✕</button>
      </div>
      <div class="drawer-body">
        <input type="text" id="rules-filter-input" placeholder="🔍 Search rules, edge, attributes, matrix, drain..."
               style="width:100%; background:var(--bg-card); border:1px solid var(--border-accent); border-radius:10px; padding:10px 14px; color:var(--text-primary); font-family:var(--font-mono); font-size:0.9rem; margin-bottom:14px;">

        <div id="rules-quick-results">
          ${rulesCardsHtml}
        </div>
      </div>
    </div>
  `;
}

export function bindRulesEvents(container: HTMLElement) {
  // Close drill-down
  const closeDrilldown = container.querySelector('#btn-close-drilldown');
  if (closeDrilldown) {
    closeDrilldown.addEventListener('click', () => {
      sound.playClick();
      store.closeDrawer();
    });
  }

  // Close rules
  const closeRules = container.querySelector('#btn-close-rules');
  if (closeRules) {
    closeRules.addEventListener('click', () => {
      sound.playClick();
      store.toggleRulesDrawer(false);
    });
  }

  // Live filter input
  const filterInput = container.querySelector('#rules-filter-input') as HTMLInputElement;
  if (filterInput) {
    filterInput.addEventListener('input', (e) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
      const cards = container.querySelectorAll('.rule-topic-card') as NodeListOf<HTMLElement>;
      cards.forEach((card) => {
        const keywords = (card.getAttribute('data-keywords') || '').toLowerCase();
        if (!q || keywords.includes(q)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
}
