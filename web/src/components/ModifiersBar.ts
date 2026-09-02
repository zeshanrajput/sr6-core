import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderModifiersBar(): string {
  if (!store.isModifiersHudOpen) return '';

  const state = store.getActiveState();
  const char = store.getActiveCharacter();
  if (!char) return '';

  const sustainedCount = state.sustainedSpellsCount || 0;
  const sustainedPenalty = store.getSustainedSpellsPenalty();
  const woundPenalty = store.getWoundModifier();
  const sitMod = store.getSituationalModifier();
  const netMod = store.getTotalGlobalModifier();

  const netModColor =
    netMod > 0 ? 'var(--accent-emerald)' : netMod < 0 ? 'var(--accent-rose)' : 'var(--text-muted)';
  const netModSign = netMod > 0 ? `+${netMod}` : `${netMod}`;

  return `
    <div class="tactical-card" style="margin-bottom: 16px; border-color: rgba(0, 229, 255, 0.25); background: rgba(8, 14, 28, 0.8);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; border-bottom:1px solid var(--border-subtle); padding-bottom:8px;">
        <div style="font-family:var(--font-tech); font-weight:800; font-size:0.9rem; color:var(--text-primary); display:flex; align-items:center; gap:8px;">
          <span>⚡ DYNAMIC MODIFIERS & SUSTAINING HUD</span>
        </div>
        <div class="chip" style="font-size:0.75rem; font-weight:800; color:${netModColor}; border-color:${netModColor};">
          NET GLOBAL MOD: ${netModSign}d6
        </div>
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px;">
        
        <!-- Sustained Spells Stepper -->
        <div style="background:var(--bg-card); padding:8px 12px; border-radius:8px; border:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-size:0.75rem; color:var(--accent-primary); font-weight:700;">🔮 SUSTAINED SPELLS (-2d6/spell):</div>
            <div style="font-size:0.85rem; color:var(--text-secondary);">
              <strong>${sustainedCount}</strong> sustained ${sustainedPenalty > 0 ? `<span style="color:var(--accent-rose);">(-${sustainedPenalty}d6)</span>` : '(No Penalty)'}
            </div>
          </div>
          <div style="display:flex; gap:6px; align-items:center;">
            <button class="icon-btn" id="btn-sustaining-dec" style="width:28px; height:28px; font-weight:900;" ${sustainedCount <= 0 ? 'disabled' : ''}>-</button>
            <span style="font-family:var(--font-tech); font-size:1.1rem; font-weight:800; width:20px; text-align:center;">${sustainedCount}</span>
            <button class="icon-btn" id="btn-sustaining-inc" style="width:28px; height:28px; font-weight:900;">+</button>
          </div>
        </div>

        <!-- Situational Modifier Stepper -->
        <div style="background:var(--bg-card); padding:8px 12px; border-radius:8px; border:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-size:0.75rem; color:var(--accent-gold); font-weight:700;">🌧️ SITUATIONAL (Cover/Lighting):</div>
            <div style="font-size:0.85rem; color:var(--text-secondary);">
              Offset: <strong style="color:${sitMod > 0 ? 'var(--accent-emerald)' : sitMod < 0 ? 'var(--accent-rose)' : 'var(--text-primary)'};">${sitMod > 0 ? `+${sitMod}` : sitMod}d6</strong>
            </div>
          </div>
          <div style="display:flex; gap:4px;">
            <button class="chip btn-sit-mod" data-val="-2" style="cursor:pointer; padding:3px 7px; ${sitMod === -2 ? 'background:var(--accent-rose); color:#fff;' : ''}">-2</button>
            <button class="chip btn-sit-mod" data-val="-1" style="cursor:pointer; padding:3px 7px; ${sitMod === -1 ? 'background:var(--accent-rose); color:#fff;' : ''}">-1</button>
            <button class="chip btn-sit-mod" data-val="0" style="cursor:pointer; padding:3px 7px; ${sitMod === 0 ? 'border-color:var(--accent-primary);' : ''}">0</button>
            <button class="chip btn-sit-mod" data-val="1" style="cursor:pointer; padding:3px 7px; ${sitMod === 1 ? 'background:var(--accent-emerald); color:#000;' : ''}">+1</button>
            <button class="chip btn-sit-mod" data-val="2" style="cursor:pointer; padding:3px 7px; ${sitMod === 2 ? 'background:var(--accent-emerald); color:#000;' : ''}">+2</button>
          </div>
        </div>

      </div>

      ${
        woundPenalty > 0 || sustainedPenalty > 0 || sitMod !== 0
          ? `
        <div style="margin-top:8px; font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); display:flex; flex-wrap:wrap; gap:12px;">
          <span>• Wounds: <strong style="color:var(--accent-rose);">${woundPenalty > 0 ? `-${woundPenalty}d6` : '0'}</strong></span>
          <span>• Sustaining: <strong style="color:var(--accent-rose);">${sustainedPenalty > 0 ? `-${sustainedPenalty}d6` : '0'}</strong></span>
          <span>• Situational: <strong style="color:var(--accent-primary);">${sitMod >= 0 ? `+${sitMod}` : sitMod}d6</strong></span>
        </div>
      `
          : ''
      }
    </div>
  `;
}

export function bindModifiersEvents(container: HTMLElement) {
  // Sustaining Dec
  const susDec = container.querySelector('#btn-sustaining-dec');
  if (susDec) {
    susDec.addEventListener('click', () => {
      sound.playClick();
      store.adjustSustainedSpells(-1);
    });
  }

  // Sustaining Inc
  const susInc = container.querySelector('#btn-sustaining-inc');
  if (susInc) {
    susInc.addEventListener('click', () => {
      sound.playClick();
      store.adjustSustainedSpells(1);
    });
  }

  // Situational quick buttons
  container.querySelectorAll('.btn-sit-mod').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const valStr = (e.currentTarget as HTMLElement).getAttribute('data-val');
      if (valStr !== null) {
        sound.playClick();
        store.setSituationalModifier(parseInt(valStr, 10));
      }
    });
  });
}
