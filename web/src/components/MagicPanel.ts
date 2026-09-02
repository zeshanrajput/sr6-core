import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderMagicPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const spells = char.spells || [];
  const complexForms = char.complex_forms || [];
  const adeptPowers = char.adept_powers || [];
  const globalMod = store.getTotalGlobalModifier();

  const isVelvet = char.identity?.is_velvet || store.activeCharId === 'velvet';
  const isTechnomancer = (char.attributes?.resonance || 0) > 0;

  // Drain / Fading resistance pool using effective attributes
  const wil = store.getEffectiveAttributeVal('WIL').val;
  const logVal = store.getEffectiveAttributeVal('LOG').val;
  const cha = store.getEffectiveAttributeVal('CHA').val;

  // Shinto / Musok Drain: WIL + CHA (or Hermetic/Techno: WIL + LOG)
  const drainAttrSum = isVelvet ? wil + cha : (isTechnomancer ? wil + logVal : wil + logVal);
  const effectiveDrainPool = Math.max(0, drainAttrSum + globalMod);

  // Find Sorcery & Conjuring skills
  const sorcerySkill = char.skills?.find((s) => s.name.toLowerCase() === 'sorcery');
  const conjuringSkill = char.skills?.find((s) => s.name.toLowerCase() === 'conjuring');

  const sorcerySpecPool = sorcerySkill ? store.getEffectiveSkillPool(sorcerySkill, true) : 13;
  const sorceryBasePool = sorcerySkill ? store.getEffectiveSkillPool(sorcerySkill, false) : 11;
  const conjuringPool = conjuringSkill ? store.getEffectiveSkillPool(conjuringSkill, false) : 12;

  const spellsHtml = spells
    .map(
      (s) => `
    <div class="tactical-card" style="border-left: 4px solid var(--accent-purple);">
      <div class="tactical-card-header">
        <div>
          <div class="tactical-card-title">✨ ${s.name}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:2px;">
            ${s.category || 'Health'} • ${s.type || 'Physical'}
          </div>
        </div>
        <div class="tactical-card-badge" style="color:var(--accent-purple); font-weight:800; font-size:0.85rem;">
          DRAIN ${s.drain}
        </div>
      </div>
      <div class="weapon-stats-row" style="margin: 8px 0;">
        <div>Range: <strong>${s.range || 'LOS'}</strong></div>
        <div>Duration: <strong>${s.duration || 'Instant'}</strong></div>
        ${s.damage ? `<div>DV: <strong>${s.damage}</strong></div>` : ''}
      </div>
      ${s.notes || s.description ? `<div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:10px; line-height:1.4;">${s.notes || s.description}</div>` : ''}
      <button class="action-btn btn-cast-grimoire" data-name="Cast ${s.name}" data-drain="${s.drain}" data-pool="${sorcerySpecPool}"
              style="width:100%; background:rgba(168, 85, 247, 0.12); border-color:rgba(168, 85, 247, 0.4); text-align:left; padding:8px 12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:800; color:var(--text-primary);">✨ Cast ${s.name}</span>
          <span style="color:var(--accent-purple); font-family:var(--font-mono); font-weight:900;">${sorcerySpecPool}d6 (${Math.floor(sorcerySpecPool / 4)} Hits)</span>
        </div>
      </button>
    </div>
  `
    )
    .join('');

  const complexFormsHtml = complexForms
    .map(
      (cf) => `
    <div class="tactical-card" style="border-left: 4px solid var(--accent-primary);">
      <div class="tactical-card-header">
        <div class="tactical-card-title">🌀 ${cf.name}</div>
        <div class="tactical-card-badge" style="color:var(--accent-primary);">FADING ${cf.fading}</div>
      </div>
      <div class="weapon-stats-row" style="margin: 8px 0;">
        <div>Duration: <strong>${cf.duration}</strong></div>
        ${cf.target ? `<div>Target: <strong>${cf.target}</strong></div>` : ''}
      </div>
      ${cf.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary);">${cf.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  const adeptPowersHtml = adeptPowers
    .map(
      (ap) => `
    <div class="tactical-card" style="border-left: 4px solid var(--accent-gold);">
      <div class="tactical-card-header">
        <div class="tactical-card-title">⚡ ${ap.name} ${ap.level ? `(Level ${ap.level})` : ''}</div>
        <div class="tactical-card-badge" style="color:var(--accent-gold);">${ap.cost ? `${ap.cost} PP` : 'ADEPT'}</div>
      </div>
      ${ap.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">${ap.notes}</div>` : ''}
    </div>
  `
    )
    .join('');

  return `
    <div class="section-title">
      <h2><span>🔮</span> ${isTechnomancer ? 'RESONANCE & FADING' : 'MAGIC & DRAIN'}</h2>
    </div>

    <!-- 1. PRIMARY SORCERY / SPELLCASTING & DRAIN TESTS -->
    ${
      !isTechnomancer && spells.length > 0
        ? `
      <div class="tactical-card" style="margin-bottom:16px; background:rgba(8,14,28,0.85); border-left:4px solid var(--accent-purple);">
        <div class="tactical-card-header">
          <div>
            <div class="tactical-card-title" style="font-size:1.1rem; color:var(--text-primary);">🔮 SPELLCASTING & SORCERY TESTS</div>
            <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:2px;">
              Sorcery (${sorcerySkill?.rating || 5}) + Magic (${store.getEffectiveAttributeVal('MAG').val || 6}) ${sorcerySkill?.specialization ? `+ Spec (${sorcerySkill.specialization} +2)` : ''}
            </div>
          </div>
          <div class="tactical-card-badge" style="color:var(--accent-purple); font-weight:800;">
            SORCERY
          </div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:8px; margin-top:10px;">
          <!-- Spellcasting Specialized Roll -->
          <button class="action-btn btn-cast-spell" data-name="Sorcery (Spellcasting)" data-pool="${sorcerySpecPool}"
                  style="background:rgba(168, 85, 247, 0.15); border-color:var(--accent-purple); text-align:left; padding:10px 12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:800; color:var(--text-primary);">✨ Cast (Spellcasting)</span>
              <span style="color:var(--accent-purple); font-family:var(--font-mono); font-size:1.15rem; font-weight:900;">${sorcerySpecPool}d6</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">${Math.floor(sorcerySpecPool / 4)} Bought Hits</div>
          </button>

          <!-- General Sorcery Roll -->
          <button class="action-btn btn-cast-spell" data-name="Sorcery (Base)" data-pool="${sorceryBasePool}"
                  style="background:rgba(0, 240, 255, 0.08); border-color:rgba(0, 240, 255, 0.3); text-align:left; padding:10px 12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:800; color:var(--text-primary);">🔮 General Sorcery</span>
              <span style="color:var(--accent-primary); font-family:var(--font-mono); font-size:1.15rem; font-weight:900;">${sorceryBasePool}d6</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">${Math.floor(sorceryBasePool / 4)} Bought Hits</div>
          </button>

          <!-- Conjuring Roll -->
          ${
            conjuringSkill
              ? `
          <button class="action-btn btn-cast-spell" data-name="Conjuring (Summoning)" data-pool="${conjuringPool}"
                  style="background:rgba(16, 185, 129, 0.08); border-color:rgba(16, 185, 129, 0.3); text-align:left; padding:10px 12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:800; color:var(--text-primary);">👻 Conjuring</span>
              <span style="color:var(--accent-emerald); font-family:var(--font-mono); font-size:1.15rem; font-weight:900;">${conjuringPool}d6</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">${Math.floor(conjuringPool / 4)} Bought Hits</div>
          </button>
          `
              : ''
          }
        </div>
      </div>
    `
        : ''
    }

    <!-- 2. DRAIN / FADING TEST CARD -->
    <div class="tactical-card" style="margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-size:0.9rem; font-family:var(--font-tech); font-weight:700;">
            ${isTechnomancer ? '🌀 Fading Resistance Test (WIL + LOG):' : '✨ Spell Drain Resistance Test (WIL + CHA):'}
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono); margin-top:2px;">
            ${isVelvet ? `WIL (${wil}) + CHA (${cha})` : isTechnomancer ? `WIL (${wil}) + LOG (${logVal})` : `WIL (${wil}) + LOG (${logVal})`}
          </div>
        </div>
        <button class="pool-btn btn-cast-spell" data-name="${isTechnomancer ? 'Fading Resistance' : 'Drain Resistance'}" data-pool="${effectiveDrainPool}">
          <span>🛡️ ${effectiveDrainPool}d6</span>
          <span class="bought-hits">(${Math.floor(effectiveDrainPool / 4)} Hits)</span>
        </button>
      </div>
    </div>

    <!-- 3. GRIMOIRE / SPELLS -->
    ${
      spells.length > 0
        ? `
      <div class="section-title">
        <h2><span>📖</span> GRIMOIRE & SPELLS (${spells.length})</h2>
      </div>
      <div class="card-stack" style="margin-bottom:16px;">
        ${spellsHtml}
      </div>
    `
        : ''
    }

    <!-- 4. COMPLEX FORMS -->
    ${
      complexForms.length > 0
        ? `
      <div class="section-title">
        <h2><span>🌀</span> COMPLEX FORMS (${complexForms.length})</h2>
      </div>
      <div class="card-stack" style="margin-bottom:16px;">
        ${complexFormsHtml}
      </div>
    `
        : ''
    }

    <!-- 5. ADEPT POWERS -->
    ${
      adeptPowers.length > 0
        ? `
      <div class="section-title">
        <h2><span>⚡</span> ADEPT POWERS (${adeptPowers.length})</h2>
      </div>
      <div class="card-stack" style="margin-bottom:16px;">
        ${adeptPowersHtml}
      </div>
    `
        : ''
    }
  `;
}

export function bindMagicEvents(container: HTMLElement) {
  // Cast Spell and Drain Rolls
  container.querySelectorAll('.btn-cast-spell, .btn-cast-grimoire').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const name = target.getAttribute('data-name') || 'Spellcast';
      const pool = parseInt(target.getAttribute('data-pool') || '12', 10);

      sound.playDiceRoll();
      const dice = Array.from({ length: pool }, () => Math.floor(Math.random() * 6) + 1);
      const hits = dice.filter((d) => d >= 5).length;
      const ones = dice.filter((d) => d === 1).length;

      store.addRollResult({
        id: `magic_roll_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        pool,
        dice,
        hits,
        ones,
        isGlitch: ones > pool / 2 && hits === 0,
        isCriticalGlitch: ones > pool / 2 && hits === 0,
        isExploding: false,
        actionName: `🔮 ${name} (${pool}d6)`,
        woundPenaltyApplied: store.getWoundModifier(),
      });

      store.toggleDiceTray(true);
      if (hits >= 4) sound.playSuccess();
    });
  });
}
