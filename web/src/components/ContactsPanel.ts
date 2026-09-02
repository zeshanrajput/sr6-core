import { store } from '../state/store';
import { sound } from '../utils/audio';
import { ContactData } from '../types/sr6';

export function renderContactsPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const allContacts = char.contacts || [];
  const filter = store.contactFilter;

  // Calculate Character's Influence + Charisma pool for the Willingness test
  const influenceSkill = char.skills?.find((s) => s.name.toLowerCase() === 'influence');
  const chaVal = char.attributes?.charisma || 1;
  const baseInfluencePool = influenceSkill ? influenceSkill.buffed_pool || influenceSkill.base_pool : chaVal;

  // Collect all unique regions and types for filter chips
  const regionSet = new Set<string>();
  const typeSet = new Set<string>();

  allContacts.forEach((c) => {
    if (c.region) regionSet.add(c.region);
    if (c.types && Array.isArray(c.types)) {
      c.types.forEach((t) => typeSet.add(t));
    }
  });

  const uniqueRegions = Array.from(regionSet).sort();
  const uniqueTypes = Array.from(typeSet).sort();

  // Filter contacts
  let filtered = allContacts.filter((c) => {
    // 1. Search text
    if (filter.search) {
      const q = filter.search.toLowerCase();
      const matchName = c.name.toLowerCase().includes(q);
      const matchArch = (c.archetype || '').toLowerCase().includes(q);
      const matchReg = (c.region || '').toLowerCase().includes(q);
      const matchDesc = (c.description || '').toLowerCase().includes(q);
      const matchType = c.types?.some((t) => t.toLowerCase().includes(q));
      if (!matchName && !matchArch && !matchReg && !matchDesc && !matchType) {
        return false;
      }
    }

    // 2. Region
    if (filter.region !== 'ALL' && c.region !== filter.region) {
      return false;
    }

    // 3. Type
    if (filter.type !== 'ALL') {
      if (!c.types || !c.types.includes(filter.type)) {
        return false;
      }
    }

    // 4. Has Favors Only
    if (filter.hasFavorsOnly && (!c.favors || c.favors <= 0)) {
      return false;
    }

    return true;
  });

  // Sort contacts
  filtered.sort((a, b) => {
    if (filter.sortBy === 'conn_desc') {
      return (b.connection || 0) - (a.connection || 0);
    } else if (filter.sortBy === 'loy_desc') {
      return (b.loyalty || 0) - (a.loyalty || 0);
    } else if (filter.sortBy === 'favors_desc') {
      return (b.favors || 0) - (a.favors || 0);
    } else {
      return a.name.localeCompare(b.name);
    }
  });

  // Render Region Chips
  const regionChipsHtml = [
    `<button class="chip chip-contact-region ${filter.region === 'ALL' ? 'active' : ''}" data-region="ALL" style="cursor:pointer;">ALL REGIONS</button>`,
    ...uniqueRegions.map(
      (r) => `<button class="chip chip-contact-region ${filter.region === r ? 'active' : ''}" data-region="${r}" style="cursor:pointer;">📍 ${r}</button>`
    ),
  ].join('');

  // Render Type Chips
  const typeChipsHtml = [
    `<button class="chip chip-contact-type ${filter.type === 'ALL' ? 'active' : ''}" data-type="ALL" style="cursor:pointer;">ALL TYPES</button>`,
    ...uniqueTypes.map(
      (t) => `<button class="chip chip-contact-type ${filter.type === t ? 'active' : ''}" data-type="${t}" style="cursor:pointer;">🏷️ ${t}</button>`
    ),
  ].join('');

  const contactsHtml = filtered
    .map((c, index) => {
      const conn = c.connection || 1;
      const loy = c.loyalty || 1;
      const knowledgePool = conn * 2;
      const sharePool = baseInfluencePool + loy;

      const typesBadges = (c.types || [])
        .map(
          (t) =>
            `<span class="chip chip-contact-type-tag" data-type="${t}" style="cursor:pointer; font-size:0.7rem; padding:2px 6px; background:rgba(0, 240, 255, 0.08); border-color:rgba(0, 240, 255, 0.25); color:var(--text-secondary);">${t}</span>`
        )
        .join(' ');

      return `
      <div class="tactical-card" data-contact-idx="${index}" style="border-left: 4px solid var(--accent-primary);">
        <div class="tactical-card-header">
          <div>
            <div class="tactical-card-title" style="font-size:1.05rem;">👤 ${c.name}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:2px;">
              ${c.archetype ? `<strong>${c.archetype}</strong>` : 'Contact'} ${c.region ? `• 📍 ${c.region}` : ''}
            </div>
          </div>
          <div class="tactical-card-badge" style="color:var(--accent-gold); font-size:0.8rem;">
            ${c.favors ? `+${c.favors} FAVORS` : 'SRM CONTACT'}
          </div>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:4px; margin: 6px 0;">
          ${typesBadges}
        </div>

        <div class="weapon-stats-row" style="margin: 8px 0;">
          <div>Connection: <strong style="color:var(--accent-primary); font-size:1.1rem;">${conn}</strong></div>
          <div>Loyalty: <strong style="color:var(--accent-emerald); font-size:1.1rem;">${loy}</strong></div>
          <div>Region: <strong>${c.region || 'Seattle'}</strong></div>
        </div>

        ${c.description || c.notes ? `<div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:12px; line-height:1.4;">${c.description || c.notes}</div>` : ''}

        <!-- 3 Standard Contact Action Tests -->
        <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono); margin-bottom:6px; text-transform:uppercase; letter-spacing:0.04em;">
          Contact Tactical Rolls:
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:8px;">
          <!-- 1. Availability -->
          <button class="action-btn btn-contact-avail" data-name="${c.name}" data-conn="${conn}" data-loy="${loy}"
                  style="background:rgba(0, 240, 255, 0.08); border-color:rgba(0, 240, 255, 0.35); text-align:left; padding:8px 10px; font-size:0.75rem;">
            <div style="font-weight:800; color:var(--text-primary); display:flex; justify-content:space-between;">
              <span>📞 1. Available?</span>
              <span style="color:var(--accent-primary); font-family:var(--font-mono);">1d6 + ${loy} > ${conn}</span>
            </div>
            <div style="font-size:0.68rem; color:var(--text-muted); margin-top:2px;">1d6 + Loyalty vs Connection</div>
          </button>

          <!-- 2. What they know -->
          <button class="action-btn btn-contact-know" data-name="${c.name}" data-pool="${knowledgePool}"
                  style="background:rgba(16, 185, 129, 0.08); border-color:rgba(16, 185, 129, 0.35); text-align:left; padding:8px 10px; font-size:0.75rem;">
            <div style="font-weight:800; color:var(--text-primary); display:flex; justify-content:space-between;">
              <span>🧠 2. Knowledge</span>
              <span style="color:var(--accent-emerald); font-family:var(--font-mono);">${knowledgePool}d6</span>
            </div>
            <div style="font-size:0.68rem; color:var(--text-muted); margin-top:2px;">Connection + Connection (${conn} + ${conn})</div>
          </button>

          <!-- 3. What they share -->
          <button class="action-btn btn-contact-share" data-name="${c.name}" data-pool="${sharePool}" data-loy="${loy}"
                  style="background:rgba(245, 158, 11, 0.08); border-color:rgba(245, 158, 11, 0.35); text-align:left; padding:8px 10px; font-size:0.75rem;">
            <div style="font-weight:800; color:var(--text-primary); display:flex; justify-content:space-between;">
              <span>💬 3. Willingness</span>
              <span style="color:var(--accent-gold); font-family:var(--font-mono);">${sharePool}d6</span>
            </div>
            <div style="font-size:0.68rem; color:var(--text-muted); margin-top:2px;">Influence (${baseInfluencePool}) + Loyalty (${loy})</div>
          </button>
        </div>
      </div>
    `;
    })
    .join('');

  return `
    <div class="section-title">
      <h2><span>👥</span> CONTACT NETWORK & SRM FAVORS (${filtered.length} / ${allContacts.length})</h2>
    </div>

    <!-- FILTER & SEARCH HUD -->
    <div class="tactical-card" style="margin-bottom:16px; background:rgba(8, 14, 28, 0.85); border-color:rgba(0, 240, 255, 0.25);">
      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px;">
        <input type="text" id="contact-search-input" placeholder="🔍 Search contacts by name, type, region, archetype..." 
               value="${filter.search}"
               style="flex:1; min-width:220px; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 12px; color:var(--text-primary); font-size:0.85rem;">
        
        <select id="contact-sort-select" style="background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 12px; color:var(--text-primary); font-size:0.8rem; font-weight:700;">
          <option value="name" ${filter.sortBy === 'name' ? 'selected' : ''}>Sort: Name (A-Z)</option>
          <option value="conn_desc" ${filter.sortBy === 'conn_desc' ? 'selected' : ''}>Sort: Connection (High-Low)</option>
          <option value="loy_desc" ${filter.sortBy === 'loy_desc' ? 'selected' : ''}>Sort: Loyalty (High-Low)</option>
          <option value="favors_desc" ${filter.sortBy === 'favors_desc' ? 'selected' : ''}>Sort: Favors (High-Low)</option>
        </select>

        <button class="chip ${filter.hasFavorsOnly ? 'active' : ''}" id="btn-toggle-favors-only" style="cursor:pointer; padding:8px 12px; font-weight:800;">
          ⭐ HAS FAVORS ONLY
        </button>

        ${
          filter.search || filter.region !== 'ALL' || filter.type !== 'ALL' || filter.hasFavorsOnly
            ? `<button class="chip" id="btn-clear-contact-filters" style="cursor:pointer; background:rgba(239, 68, 68, 0.15); border-color:rgba(239, 68, 68, 0.4); color:var(--accent-rose);">✕ Reset</button>`
            : ''
        }
      </div>

      <!-- REGION CHIPS -->
      <div style="font-size:0.7rem; font-weight:800; color:var(--text-muted); font-family:var(--font-mono); margin-bottom:4px; text-transform:uppercase;">
        Filter by Region:
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:10px;">
        ${regionChipsHtml}
      </div>

      <!-- TYPE CHIPS -->
      <div style="font-size:0.7rem; font-weight:800; color:var(--text-muted); font-family:var(--font-mono); margin-bottom:4px; text-transform:uppercase;">
        Filter by Contact Type:
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:4px;">
        ${typeChipsHtml}
      </div>
    </div>

    <div class="card-stack">
      ${contactsHtml || '<div style="color:var(--text-muted); font-size:0.85rem; padding:20px; text-align:center;">No contacts match the active filters.</div>'}
    </div>
  `;
}

export function bindContactsEvents(container: HTMLElement) {
  // Search Input
  const searchInput = container.querySelector('#contact-search-input') as HTMLInputElement;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const val = (e.target as HTMLInputElement).value;
      store.setContactFilter({ search: val });
    });
  }

  // Sort Dropdown
  const sortSelect = container.querySelector('#contact-sort-select') as HTMLSelectElement;
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      const val = (e.target as HTMLSelectElement).value;
      sound.playClick();
      store.setContactFilter({ sortBy: val });
    });
  }

  // Favors Toggle
  const favorsBtn = container.querySelector('#btn-toggle-favors-only');
  if (favorsBtn) {
    favorsBtn.addEventListener('click', () => {
      sound.playClick();
      store.setContactFilter({ hasFavorsOnly: !store.contactFilter.hasFavorsOnly });
    });
  }

  // Clear Filters
  const clearBtn = container.querySelector('#btn-clear-contact-filters');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      sound.playClick();
      store.setContactFilter({ search: '', region: 'ALL', type: 'ALL', hasFavorsOnly: false, sortBy: 'name' });
    });
  }

  // Region Filter Chips
  container.querySelectorAll('.chip-contact-region').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const reg = target.getAttribute('data-region') || 'ALL';
      sound.playClick();
      store.setContactFilter({ region: reg });
    });
  });

  // Type Filter Chips
  container.querySelectorAll('.chip-contact-type').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const t = target.getAttribute('data-type') || 'ALL';
      sound.playClick();
      store.setContactFilter({ type: t });
    });
  });

  // Card Type Tags (Click tag on contact card to filter by that type)
  container.querySelectorAll('.chip-contact-type-tag').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const t = target.getAttribute('data-type') || 'ALL';
      sound.playClick();
      store.setContactFilter({ type: t });
    });
  });

  // 1. Availability Roll (1d6 + Loyalty > Connection)
  container.querySelectorAll('.btn-contact-avail').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const name = target.getAttribute('data-name') || 'Contact';
      const conn = parseInt(target.getAttribute('data-conn') || '1', 10);
      const loy = parseInt(target.getAttribute('data-loy') || '1', 10);

      const d6Roll = Math.floor(Math.random() * 6) + 1;
      const total = d6Roll + loy;
      const isAvailable = total > conn;

      sound.playDiceRoll();

      store.addRollResult({
        id: `contact_avail_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        pool: 1,
        dice: [d6Roll],
        hits: isAvailable ? 1 : 0,
        ones: d6Roll === 1 ? 1 : 0,
        isGlitch: false,
        isCriticalGlitch: false,
        isExploding: false,
        actionName: `📞 ${name}: Availability (${isAvailable ? 'AVAILABLE ✅' : 'UNAVAILABLE ❌'})`,
        woundPenaltyApplied: 0,
      });

      store.toggleDiceTray(true);
      if (isAvailable) {
        sound.playSuccess();
      } else {
        sound.playGlitch();
      }
    });
  });

  // 2. Knowledge Test (Connection + Connection)
  container.querySelectorAll('.btn-contact-know').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const name = target.getAttribute('data-name') || 'Contact';
      const pool = parseInt(target.getAttribute('data-pool') || '4', 10);

      sound.playDiceRoll();
      const dice = Array.from({ length: pool }, () => Math.floor(Math.random() * 6) + 1);
      const hits = dice.filter((d) => d >= 5).length;
      const ones = dice.filter((d) => d === 1).length;

      store.addRollResult({
        id: `contact_know_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        pool,
        dice,
        hits,
        ones,
        isGlitch: ones > pool / 2 && hits === 0,
        isCriticalGlitch: ones > pool / 2 && hits === 0,
        isExploding: false,
        actionName: `🧠 ${name}: Knowledge Test (${pool}d6)`,
        woundPenaltyApplied: 0,
      });

      store.toggleDiceTray(true);
      if (hits >= 3) sound.playSuccess();
    });
  });

  // 3. Willingness / Negotiation Test (Influence + Charisma + Loyalty)
  container.querySelectorAll('.btn-contact-share').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const name = target.getAttribute('data-name') || 'Contact';
      const pool = parseInt(target.getAttribute('data-pool') || '6', 10);

      sound.playDiceRoll();
      const dice = Array.from({ length: pool }, () => Math.floor(Math.random() * 6) + 1);
      const hits = dice.filter((d) => d >= 5).length;
      const ones = dice.filter((d) => d === 1).length;

      store.addRollResult({
        id: `contact_share_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        pool,
        dice,
        hits,
        ones,
        isGlitch: ones > pool / 2 && hits === 0,
        isCriticalGlitch: ones > pool / 2 && hits === 0,
        isExploding: false,
        actionName: `💬 ${name}: Willingness & Favors (${pool}d6)`,
        woundPenaltyApplied: 0,
      });

      store.toggleDiceTray(true);
      if (hits >= 3) sound.playSuccess();
    });
  });
}
