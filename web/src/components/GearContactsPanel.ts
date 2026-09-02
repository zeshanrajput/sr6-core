import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderGearContactsPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const cyberware = char.cyberware || [];
  const bioware = char.bioware || [];
  const positiveQualities = char.qualities?.positive || [];
  const negativeQualities = char.qualities?.negative || [];
  const contacts = char.contacts || [];

  const augsHtml = [...cyberware, ...bioware]
    .map(
      (a) => `
    <div class="tactical-card">
      <div class="tactical-card-header">
        <div class="tactical-card-title">${a.name} ${a.rating ? `(R${a.rating})` : ''}</div>
        <div class="tactical-card-badge">${(a.grade || a.category || 'AUG').toUpperCase()}</div>
      </div>
      ${a.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary);">${a.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  const qualitiesHtml = [
    ...positiveQualities.map((q) => ({ ...q, isPos: true })),
    ...negativeQualities.map((q) => ({ ...q, isPos: false })),
  ]
    .map(
      (q) => `
    <div class="tactical-card">
      <div class="tactical-card-header">
        <div class="tactical-card-title">${q.name} ${q.rating ? `(Rating ${q.rating})` : ''}</div>
        <div class="tactical-card-badge" style="color:${q.isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
          ${q.isPos ? '+ POSITIVE' : '- NEGATIVE'}
        </div>
      </div>
      ${q.notes || q.summary ? `<div style="font-size:0.78rem; color:var(--text-secondary);">${q.notes || q.summary}</div>` : ''}
    </div>
  `
    )
    .join('');

  const contactsHtml = contacts
    .map(
      (c) => `
    <div class="tactical-card">
      <div class="tactical-card-header">
        <div class="tactical-card-title">👤 ${c.name} ${c.archetype ? `(${c.archetype})` : ''}</div>
        <div class="tactical-card-badge" style="color:var(--accent-gold);">
          ${c.favors ? `+${c.favors} FAVORS` : 'CONTACT'}
        </div>
      </div>
      <div class="weapon-stats-row">
        <div>Connection: <strong>${c.connection}</strong></div>
        <div>Loyalty: <strong>${c.loyalty}</strong></div>
        ${c.region ? `<div>Region: <strong>${c.region}</strong></div>` : ''}
      </div>
      ${c.description || c.notes ? `<div style="font-size:0.78rem; color:var(--text-muted);">${c.description || c.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  return `
    <div class="section-title">
      <h2><span>⚙️</span> AUGMENTATIONS & CYBERWARE</h2>
    </div>
    <div class="card-stack" style="margin-bottom:20px;">
      ${augsHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">None installed.</div>'}
    </div>

    <div class="section-title">
      <h2><span>🌟</span> QUALITIES & TRAITS</h2>
    </div>
    <div class="card-stack" style="margin-bottom:20px;">
      ${qualitiesHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">None listed.</div>'}
    </div>

    <div class="section-title">
      <h2><span>👥</span> CONTACT NETWORK & SRM FAVORS</h2>
    </div>
    <div class="card-stack">
      ${contactsHtml || '<div style="color:var(--text-muted); font-size:0.85rem;">No contacts registered.</div>'}
    </div>
  `;
}

export function bindGearEvents(_container: HTMLElement) {
  // No special bindings needed for now
}
