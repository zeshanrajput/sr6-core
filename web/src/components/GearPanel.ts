import { store } from '../state/store';

export function renderGearPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const inventory = char.inventory || {};
  const gearList: string[] = inventory.gear || char.gear || [];
  const commlinks = inventory.commlinks || [];
  const hosts = inventory.hosts || [];
  const programs: string[] = inventory.programs || [];
  const autosofts: string[] = inventory.autosofts || [];
  const sins = char.sins || inventory.sins || [];
  const lifestyles = char.lifestyles || inventory.lifestyles || [];

  const cyberware = char.cyberware || [];
  const bioware = char.bioware || [];
  const augmentations = [...cyberware, ...bioware, ...(char.augmentations || [])];

  const positiveQualities = char.qualities?.positive || [];
  const negativeQualities = char.qualities?.negative || [];

  // 1. SINs & Fake Licenses Cards
  const sinsHtml = sins
    .map((s: any) => {
      const licBadges = (s.licenses || [])
        .map(
          (lic: string) =>
            `<span class="chip" style="font-family:var(--font-mono); font-size:0.75rem; background:rgba(0, 240, 255, 0.08); border:1px solid rgba(0, 240, 255, 0.3); color:var(--text-primary);">📜 ${lic}</span>`
        )
        .join(' ');

      return `
      <div class="tactical-card" style="margin-bottom:10px; border-left: 4px solid var(--accent-gold);">
        <div class="tactical-card-header">
          <div class="tactical-card-title" style="font-size:1.05rem;">🪪 ${s.name}</div>
          <div class="tactical-card-badge" style="color:var(--accent-gold); font-size:0.8rem; font-weight:800;">
            ${s.quality && s.quality !== 'Standard' ? `${s.quality.toUpperCase()} • ` : ''}RATING ${s.rating}
          </div>
        </div>
        <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:4px; margin-bottom:8px;">
          ATTACHED BROADCAST LICENSES:
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:6px;">
          ${licBadges || '<span style="color:var(--text-muted); font-size:0.75rem;">No attached licenses.</span>'}
        </div>
      </div>
    `;
    })
    .join('');

  // 2. Lifestyles Cards
  const lifestylesHtml = lifestyles
    .map(
      (l: any) => `
    <div class="tactical-card" style="margin-bottom:10px; border-left: 4px solid var(--accent-emerald);">
      <div class="tactical-card-header">
        <div class="tactical-card-title">🛋️ ${l.name}</div>
        <div class="tactical-card-badge" style="color:var(--accent-emerald);">MONTHLY UPKEEP PAID</div>
      </div>
      <div class="weapon-stats-row" style="margin-top:8px;">
        <div>Comfort: <strong style="text-transform:capitalize;">${l.comfort || 'Low'}</strong></div>
        <div>Neighborhood: <strong style="text-transform:capitalize;">${l.neighborhood || 'Low'}</strong></div>
        <div>Security: <strong style="text-transform:capitalize;">${l.security || 'Low'}</strong></div>
      </div>
    </div>
  `
    )
    .join('');

  // 3. Gear Items
  const gearHtml = gearList
    .map((g) => {
      const gName = typeof g === 'string' ? g : (g as any).name || 'Gear Item';
      const qty = typeof g === 'object' && (g as any).qty ? `(x${(g as any).qty})` : '';
      return `
      <div class="tactical-card" style="padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-weight:700; color:var(--text-primary); font-size:0.9rem;">
          📦 ${gName} <span style="color:var(--accent-primary); font-family:var(--font-mono); font-size:0.8rem;">${qty}</span>
        </div>
      </div>
    `;
    })
    .join('');

  // 4. Commlinks & Hosts
  const commlinksHtml = commlinks
    .map(
      (c: any) => `
    <div class="tactical-card" style="margin-bottom:8px;">
      <div class="tactical-card-header">
        <div class="tactical-card-title">📱 ${c.name}</div>
        <div class="tactical-card-badge">DR ${c.device_rating || 5}</div>
      </div>
      <div class="weapon-stats-row">
        <div>Data Processing: <strong>${c.data_processing || 5}</strong></div>
        <div>Firewall: <strong>${c.firewall || 4}</strong></div>
      </div>
    </div>
  `
    )
    .join('');

  const hostsHtml = hosts
    .map(
      (h: any) => `
    <div class="tactical-card" style="margin-bottom:8px; border-color:rgba(0, 240, 255, 0.3);">
      <div class="tactical-card-header">
        <div class="tactical-card-title">🏛️ ${h.name}</div>
        <div class="tactical-card-badge" style="color:var(--accent-primary);">HOST R${h.rating || 2}</div>
      </div>
      ${h.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:6px;">${h.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  // 5. Software Programs & Autosofts Badges
  const programsBadges = programs
    .map((p) => `<span class="chip" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-primary); background:rgba(0,240,255,0.08); border:1px solid rgba(0,240,255,0.25);">${p}</span>`)
    .join('');

  const autosoftsBadges = autosofts
    .map((a) => `<span class="chip" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-emerald); background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25);">${a}</span>`)
    .join('');

  // 6. Augmentations
  const augsHtml = augmentations
    .map(
      (a: any) => `
    <div class="tactical-card" style="margin-bottom:8px;">
      <div class="tactical-card-header">
        <div class="tactical-card-title">🦾 ${a.name} ${a.rating ? `(Rating ${a.rating})` : ''}</div>
        <div class="tactical-card-badge">${(a.grade || a.category || 'AUG').toUpperCase()}</div>
      </div>
      ${a.essence ? `<div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">Essence Cost: ${a.essence}</div>` : ''}
      ${a.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">${a.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  // 7. Qualities
  const qualitiesHtml = [
    ...positiveQualities.map((q) => ({ ...q, isPos: true })),
    ...negativeQualities.map((q) => ({ ...q, isPos: false })),
  ]
    .map(
      (q) => `
    <div class="tactical-card" style="margin-bottom:8px;">
      <div class="tactical-card-header">
        <div class="tactical-card-title">${q.name} ${q.rating ? `(Rating ${q.rating})` : ''}</div>
        <div class="tactical-card-badge" style="color:${q.isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
          ${q.isPos ? '+ POSITIVE' : '- NEGATIVE'}
        </div>
      </div>
      ${q.notes || q.summary ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">${q.notes || q.summary}</div>` : ''}
    </div>
  `
    )
    .join('');

  return `
    <!-- 1. IDENTITIES, FAKE SINS & LICENSES -->
    <div class="section-title">
      <h2><span>🪪</span> IDENTITIES, FAKE SINS & LICENSES (${sins.length})</h2>
    </div>
    <div style="margin-bottom:24px;">
      ${sinsHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">No broadcast SINs configured.</div>'}
    </div>

    <!-- 2. LIFESTYLE & HOUSING -->
    ${
      lifestyles.length > 0
        ? `
      <div class="section-title">
        <h2><span>🏠</span> LIFESTYLE & HOUSING (${lifestyles.length})</h2>
      </div>
      <div style="margin-bottom:24px;">
        ${lifestylesHtml}
      </div>
    `
        : ''
    }

    <!-- 3. FIELD GEAR & HARDWARE -->
    <div class="section-title">
      <h2><span>🎒</span> FIELD GEAR & HARDWARE INVENTORY (${gearList.length})</h2>
    </div>
    <div style="margin-bottom:24px;">
      ${gearHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">No standard gear listed.</div>'}
    </div>

    <!-- 4. MATRIX REPOSITORY & SOFTWARE -->
    <div class="section-title">
      <h2><span>📱</span> MATRIX REPOSITORY & SOFTWARE (${programs.length + autosofts.length} Softs)</h2>
    </div>
    <div style="margin-bottom:24px;">
      ${commlinksHtml}
      ${hostsHtml}

      <div class="tactical-card" style="margin-top:12px; background:rgba(8,14,28,0.7);">
        <div style="font-size:0.75rem; font-weight:800; color:var(--accent-primary); font-family:var(--font-mono); margin-bottom:8px;">
          SOFTWARE PROGRAMS LIBRARY (${programs.length}):
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px;">
          ${programsBadges || '<span style="color:var(--text-muted); font-size:0.75rem;">None loaded.</span>'}
        </div>

        <div style="font-size:0.75rem; font-weight:800; color:var(--accent-emerald); font-family:var(--font-mono); margin-bottom:8px;">
          AUTOSOFT SOFTWARE LICENSES (${autosofts.length}):
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:6px;">
          ${autosoftsBadges || '<span style="color:var(--text-muted); font-size:0.75rem;">None loaded.</span>'}
        </div>
      </div>
    </div>

    <!-- 5. AUGMENTATIONS (if present) -->
    ${
      augmentations.length > 0
        ? `
      <div class="section-title">
        <h2><span>🦾</span> AUGMENTATIONS & CYBERWARE (${augmentations.length})</h2>
      </div>
      <div style="margin-bottom:24px;">
        ${augsHtml}
      </div>
    `
        : ''
    }

    <!-- 6. QUALITIES & TRAITS -->
    <div class="section-title">
      <h2><span>🌟</span> QUALITIES & CHARACTER TRAITS</h2>
    </div>
    <div>
      ${qualitiesHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">None listed.</div>'}
    </div>
  `;
}

export function bindGearEvents(_container: HTMLElement) {
  // Static panel presentation
}
