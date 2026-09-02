import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderSkillsPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const skills = char.skills || [];

  const skillsHtml = skills
    .map((s) => {
      const effectivePool = store.getEffectiveSkillPool(s);
      const boughtHits = Math.floor(effectivePool / 4);
      const customOffset = store.getSkillOffset(s.name);

      // Render buff checkboxes if skill has modifiers or specialization
      let buffsHtml = '';
      if (s.buffs && s.buffs.length > 0) {
        buffsHtml = `
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:6px;">
            ${s.buffs
              .map((b) => {
                const buffKey = `${s.name}_${b.source}`;
                const isSpec = b.type === 'specialization';
                const isChecked = store.isBuffActive(buffKey, !isSpec);
                return `
                  <label class="chip" style="font-size:0.75rem; cursor:pointer; display:flex; align-items:center; gap:5px; ${
                    isChecked ? 'border-color:var(--accent-primary); background:rgba(0, 229, 255, 0.08);' : 'opacity:0.6;'
                  }">
                    <input type="checkbox" class="skill-buff-checkbox" data-buff-key="${buffKey}" ${
                  isChecked ? 'checked' : ''
                } style="cursor:pointer; accent-color:var(--accent-primary);">
                    <span>${isSpec ? `🎯 ${b.source} (+2)` : `${b.source} (+${b.value})`}</span>
                  </label>
                `;
              })
              .join('')}
          </div>
        `;
      }

      return `
      <div class="tactical-card skill-card-row" data-skill-name="${s.name.toLowerCase()}">
        <div class="tactical-card-header">
          <div>
            <div class="tactical-card-title">${s.name} ${s.rating ? `(Rating ${s.rating})` : ''}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">
              ${s.breakdown_text || s.attribute.toUpperCase()}
              ${customOffset !== 0 ? `<span style="color:var(--accent-gold); font-weight:700;">[Adjusted: ${customOffset > 0 ? `+${customOffset}` : customOffset}d6]</span>` : ''}
            </div>
          </div>
          
          <div style="display:flex; align-items:center; gap:6px;">
            <!-- Fine-grained pool stepper -->
            <div style="display:flex; gap:2px;">
              <button class="icon-btn btn-skill-step" data-skill="${s.name}" data-delta="-1" style="width:22px; height:22px; font-size:0.75rem;">-</button>
              <button class="icon-btn btn-skill-step" data-skill="${s.name}" data-delta="1" style="width:22px; height:22px; font-size:0.75rem;">+</button>
            </div>

            <button class="pool-btn" data-action="roll-skill" data-skill-name="${s.name}" data-pool="${effectivePool}">
              <span>🎲 ${effectivePool}d6</span>
              <span class="bought-hits">(${boughtHits} Hits)</span>
            </button>
          </div>
        </div>

        ${buffsHtml}
      </div>
    `;
    })
    .join('');

  return `
    <div class="section-title">
      <h2><span>📊</span> ACTIVE SKILLS & ACTION POOLS</h2>
      <input type="text" id="skill-search-input" placeholder="🔍 Search skills..."
             style="background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:8px; padding:6px 12px; color:var(--text-primary); font-family:var(--font-mono); font-size:0.8rem; width:160px;">
    </div>
    <div class="card-stack" id="skills-list-container">
      ${skillsHtml}
    </div>
  `;
}

export function bindSkillsEvents(container: HTMLElement) {
  // Skill search filtering
  const searchInput = container.querySelector('#skill-search-input') as HTMLInputElement;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase();
      container.querySelectorAll('.skill-card-row').forEach((row) => {
        const name = row.getAttribute('data-skill-name') || '';
        (row as HTMLElement).style.display = name.includes(q) ? 'block' : 'none';
      });
    });
  }

  // Buff checkbox toggles
  container.querySelectorAll('.skill-buff-checkbox').forEach((cb) => {
    cb.addEventListener('change', (e) => {
      const el = e.target as HTMLInputElement;
      const buffKey = el.getAttribute('data-buff-key');
      if (buffKey) {
        sound.playClick();
        store.toggleBuff(buffKey, el.checked);
      }
    });
  });

  // Manual skill stepper buttons
  container.querySelectorAll('.btn-skill-step').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const skillName = el.getAttribute('data-skill');
      const delta = parseInt(el.getAttribute('data-delta') || '0', 10);
      if (skillName) {
        sound.playClick();
        store.adjustSkillOffset(skillName, delta);
      }
    });
  });

  // Tap-to-roll skill pool
  container.querySelectorAll('[data-action="roll-skill"]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const skillName = el.getAttribute('data-skill-name') || 'Skill Test';
      const pool = parseInt(el.getAttribute('data-pool') || '6', 10);

      sound.playClick();
      window.dispatchEvent(
        new CustomEvent('sr6-trigger-roll', {
          detail: { pool, actionName: skillName },
        })
      );
    });
  });
}
