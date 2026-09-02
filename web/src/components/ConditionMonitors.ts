import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderConditionMonitors(): string {
  const char = store.getActiveCharacter();
  const state = store.getActiveState();
  if (!char) return '';

  const attrs = char.attributes || {};
  const isAi = char.identity?.is_ai || false;
  const isMonad = char.identity?.is_monad || false;

  const bod = attrs.body || 1;
  const wil = attrs.willpower || 1;
  const edge = attrs.edge || 1;

  // Physical boxes: Base (Math.ceil(BOD / 2) + 8) + Augmentations / Qualities
  // AI has no physical condition monitor (uses Matrix CM)
  let maxPhys = isAi ? 0 : Math.ceil(bod / 2) + 8;
  if (isMonad) maxPhys += 2; // Monad Toughness / Redliner
  if (char.identity?.is_velvet) maxPhys += 0;

  // Stun boxes: Math.ceil(WIL / 2) + 8
  let maxStun = Math.ceil(wil / 2) + 8;
  if (isMonad) maxStun += 1;

  const woundPenalty = store.getWoundModifier();
  const edgeSpent = state.edgeSpent;
  const edgeAvail = Math.max(0, edge - edgeSpent);

  // Render Physical Box Grid
  const physBoxesHtml = Array.from({ length: maxPhys }, (_, i) => {
    const isMarked = i < state.physicalDamage;
    const isThreshold = (i + 1) % 3 === 0;
    return `
      <div class="box-cell ${isMarked ? 'marked-phys' : ''} ${isThreshold ? 'penalty-threshold' : ''}"
           data-box-type="physical" data-index="${i}" title="Physical Box ${i + 1}">
        ${isMarked ? '✕' : i + 1}
      </div>
    `;
  }).join('');

  // Render Stun Box Grid
  const stunBoxesHtml = Array.from({ length: maxStun }, (_, i) => {
    const isMarked = i < state.stunDamage;
    const isThreshold = (i + 1) % 3 === 0;
    return `
      <div class="box-cell ${isMarked ? 'marked-stun' : ''} ${isThreshold ? 'penalty-threshold' : ''}"
           data-box-type="stun" data-index="${i}" title="Stun Box ${i + 1}">
        ${isMarked ? '✕' : i + 1}
      </div>
    `;
  }).join('');

  return `
    <div class="tactical-hud-banner">
      <div class="hud-header">
        <div class="hud-title">
          <span>⚡ TACTICAL CONDITION & EDGE HUD</span>
        </div>
        <div class="wound-badge ${woundPenalty > 0 ? 'wounded' : ''}">
          ${woundPenalty > 0 ? `WOUND PENALTY: -${woundPenalty} DICE` : 'STATUS: OPTIMAL (0 MOD)'}
        </div>
      </div>

      <div class="condition-tracks">
        ${
          !isAi
            ? `
          <div class="track-card">
            <div class="track-label-row">
              <span>PHYSICAL DAMAGE (${state.physicalDamage} / ${maxPhys})</span>
              <button class="icon-btn" id="btn-reset-phys" style="width:24px; height:24px; font-size:0.7rem;" title="Clear Physical Damage">↺</button>
            </div>
            <div class="box-grid">
              ${physBoxesHtml}
            </div>
          </div>
        `
            : `
          <div class="track-card">
            <div class="track-label-row">
              <span>MATRIX CONDITION (WIL / 2 + 8)</span>
              <span>12 Boxes</span>
            </div>
            <div class="box-grid">
              ${stunBoxesHtml}
            </div>
          </div>
        `
        }

        ${
          !isAi
            ? `
          <div class="track-card">
            <div class="track-label-row">
              <span>STUN DAMAGE (${state.stunDamage} / ${maxStun})</span>
              <button class="icon-btn" id="btn-reset-stun" style="width:24px; height:24px; font-size:0.7rem;" title="Clear Stun Damage">↺</button>
            </div>
            <div class="box-grid">
              ${stunBoxesHtml}
            </div>
          </div>
        `
            : ''
        }
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; padding-top:6px; border-top:1px solid var(--border-subtle);">
        <div style="display:flex; align-items:center; gap:8px; font-family:var(--font-mono); font-size:0.85rem;">
          <span style="color:var(--text-secondary);">EDGE POOL:</span>
          <strong style="color:var(--accent-primary); font-size:1.1rem;">${edgeAvail} / ${edge}</strong>
        </div>
        <div style="display:flex; gap:6px;">
          <button class="fire-btn" id="btn-spend-edge" ${edgeAvail <= 0 ? 'disabled' : ''}>
            -1 SPEND EDGE
          </button>
          <button class="reload-btn" id="btn-restore-edge">
            RESTORE
          </button>
        </div>
      </div>
    </div>
  `;
}

export function bindConditionEvents(container: HTMLElement) {
  // Box clicks
  container.querySelectorAll('.box-cell').forEach((cell) => {
    cell.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const type = el.getAttribute('data-box-type') as 'physical' | 'stun';
      const index = parseInt(el.getAttribute('data-index') || '0', 10);
      const state = store.getActiveState();

      sound.playWound();

      const current = type === 'physical' ? state.physicalDamage : state.stunDamage;
      // If clicking the currently highest marked box, reduce by 1; otherwise set to index + 1
      if (current === index + 1) {
        store.setDamage(type, index);
      } else {
        store.setDamage(type, index + 1);
      }
    });
  });

  // Reset buttons
  const resetPhys = container.querySelector('#btn-reset-phys');
  if (resetPhys) {
    resetPhys.addEventListener('click', () => {
      sound.playClick();
      store.setDamage('physical', 0);
    });
  }

  const resetStun = container.querySelector('#btn-reset-stun');
  if (resetStun) {
    resetStun.addEventListener('click', () => {
      sound.playClick();
      store.setDamage('stun', 0);
    });
  }

  // Edge spend & restore
  const spendEdge = container.querySelector('#btn-spend-edge');
  if (spendEdge) {
    spendEdge.addEventListener('click', () => {
      sound.playClick();
      store.spendEdge(1);
    });
  }

  const restoreEdge = container.querySelector('#btn-restore-edge');
  if (restoreEdge) {
    restoreEdge.addEventListener('click', () => {
      sound.playSuccessChime();
      store.restoreEdge();
    });
  }
}
