import { store } from '../state/store';
import { sound } from '../utils/audio';
import { DiceRollResult } from '../types/sr6';

export function renderDiceTray(): string {
  const isOpen = store.isDiceTrayOpen;
  const history = store.rollHistory;
  const latest = history.length > 0 ? history[0] : null;
  const state = store.getActiveState();
  const char = store.getActiveCharacter();
  const edge = char?.attributes?.edge || 1;
  const edgeAvail = Math.max(0, edge - state.edgeSpent);

  let diceFacesHtml = '<div style="color:var(--text-muted); font-size:0.9rem;">Roll a test or enter dice pool...</div>';
  if (latest) {
    diceFacesHtml = latest.dice
      .map((d) => {
        let cls = '';
        if (d === 6) cls = 'hit-six';
        else if (d === 5) cls = 'hit';
        else if (d === 1) cls = 'glitch-one';
        return `<div class="die-face ${cls}">${d}</div>`;
      })
      .join('');
  }

  let statusHtml = '';
  if (latest) {
    if (latest.isCriticalGlitch) {
      statusHtml = `<span style="color:var(--accent-rose); font-weight:900; animation:pulse-glow 1s infinite;">🚨 CRITICAL GLITCH!</span>`;
    } else if (latest.isGlitch) {
      statusHtml = `<span style="color:var(--accent-gold); font-weight:800;">⚠️ GLITCH OCCURRED!</span>`;
    } else if (latest.hits >= 4) {
      statusHtml = `<span style="color:var(--accent-emerald); font-weight:800;">✨ SPECTACULAR SUCCESS (${latest.hits} Hits)</span>`;
    } else {
      statusHtml = `<span style="color:var(--text-secondary);">${latest.hits} Hits (${latest.ones} ones)</span>`;
    }
  }

  return `
    <div class="dice-tray-modal ${isOpen ? 'open' : ''}" id="dice-tray-container">
      <div class="dice-tray-header">
        <div style="font-family:var(--font-tech); font-size:1.1rem; font-weight:800; color:var(--text-primary); display:flex; align-items:center; gap:8px;">
          <span>🎲 CYBERPUNK DICE RESOLVER</span>
          ${latest ? `<span style="font-size:0.75rem; color:var(--accent-primary); font-family:var(--font-mono);">[${latest.actionName}]</span>` : ''}
        </div>
        <button class="icon-btn" id="btn-close-dice" style="width:32px; height:32px; font-size:0.9rem;">✕</button>
      </div>

      <div class="dice-summary-card">
        <div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">OUTCOME:</div>
          <div style="font-size:0.9rem;">${statusHtml || 'Ready to Roll'}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">AVAILABLE EDGE: <strong>${edgeAvail} / ${edge}</strong></div>
          <div class="dice-hits-count">${latest ? latest.hits : '0'} Hits</div>
        </div>
      </div>

      <div class="dice-results-row">
        ${diceFacesHtml}
      </div>

      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:4px;">
          <input type="number" id="custom-pool-input" min="1" max="40" value="${latest ? latest.pool : 12}"
                 style="width:65px; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:10px; color:var(--text-primary); font-family:var(--font-tech); font-size:1.2rem; font-weight:800; text-align:center;">
          
          <div style="display:flex; gap:3px;">
            <button class="chip btn-dice-pool-adjust" data-delta="-2" style="cursor:pointer; padding:3px 6px;">-2</button>
            <button class="chip btn-dice-pool-adjust" data-delta="-1" style="cursor:pointer; padding:3px 6px;">-1</button>
            <button class="chip btn-dice-pool-adjust" data-delta="1" style="cursor:pointer; padding:3px 6px;">+1</button>
            <button class="chip btn-dice-pool-adjust" data-delta="2" style="cursor:pointer; padding:3px 6px;">+2</button>
          </div>
        </div>
        
        <div style="display:flex; gap:6px; flex:1;">
          <button class="dice-act-btn" id="btn-roll-custom" style="background:var(--accent-primary); color:#040814; font-weight:900; flex:1;">
            🎲 ROLL POOL
          </button>

          <button class="dice-act-btn" id="btn-roll-exploding" style="border-color:var(--accent-gold); color:var(--accent-gold); flex:1;" title="Exploding 6s (Rule of Six)">
            💥 RULE OF SIX
          </button>
        </div>
      </div>


      ${
        latest
          ? `
        <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-bottom:6px; font-weight:700;">
          CANONICAL SR6 EDGE MANEUVERS:
        </div>
        <div class="dice-actions-grid">
          <button class="dice-act-btn" id="btn-edge-reroll-one" ${edgeAvail < 1 ? 'disabled' : ''} title="Spend 1 Edge to reroll one failed die">
            ⚡ Reroll 1 Die (-1 Edge)
          </button>
          <button class="dice-act-btn" id="btn-edge-reroll-all" ${edgeAvail < 4 ? 'disabled' : ''} style="border-color:var(--accent-primary); color:var(--accent-primary);" title="Spend 4 Edge to reroll all failed dice">
            ⚡ Reroll All Failures (-4 Edge)
          </button>
          <button class="dice-act-btn" id="btn-edge-add-four" ${edgeAvail < 4 ? 'disabled' : ''} style="border-color:var(--accent-gold); color:var(--accent-gold);" title="Spend 4 Edge to add Edge dice with exploding 6s">
            💥 Add Edge Pool & Explode (-4 Edge)
          </button>
          <button class="dice-act-btn" id="btn-edge-buy-hit" ${edgeAvail < 3 ? 'disabled' : ''} title="Spend 3 Edge to buy 1 automatic hit">
            🎯 Buy +1 Hit (-3 Edge)
          </button>
          ${
            latest.isGlitch
              ? `
            <button class="dice-act-btn" id="btn-edge-negate-glitch" ${edgeAvail < 5 ? 'disabled' : ''} style="border-color:var(--accent-rose); color:var(--accent-rose);" title="Spend 5 Edge to negate glitch">
              🛡️ Negate Glitch (-5 Edge)
            </button>
          `
              : ''
          }
        </div>
      `
          : ''
      }
    </div>
  `;
}

export function executeRoll(pool: number, actionName: string = 'Action Test', isExploding: boolean = false): DiceRollResult {
  const safePool = Math.max(0, pool);
  const dice: number[] = [];
  let hits = 0;
  let ones = 0;

  if (safePool > 0) {
    sound.playDiceRoll();
  }

  const rollDie = () => Math.floor(Math.random() * 6) + 1;

  for (let i = 0; i < safePool; i++) {
    const val = rollDie();
    dice.push(val);
    if (val >= 5) hits++;
    if (val === 1) ones++;

    // Rule of six exploding dice
    if (isExploding && val === 6) {
      let explodeVal = rollDie();
      while (explodeVal === 6) {
        dice.push(explodeVal);
        hits++;
        explodeVal = rollDie();
      }
      dice.push(explodeVal);
      if (explodeVal >= 5) hits++;
      if (explodeVal === 1) ones++;
    }
  }

  const isGlitch = safePool > 0 && ones > safePool / 2;
  const isCriticalGlitch = safePool > 0 && isGlitch && hits === 0;

  if (isCriticalGlitch || isGlitch) {
    sound.playGlitchAlarm();
  } else if (hits >= 4) {
    sound.playSuccessChime();
  }

  const result: DiceRollResult = {
    id: 'roll_' + Date.now(),
    timestamp: new Date().toLocaleTimeString(),
    pool: safePool,
    dice,
    hits,
    ones,
    isGlitch,
    isCriticalGlitch,
    isExploding,
    actionName,
    woundPenaltyApplied: store.getWoundModifier(),
  };

  store.addRollResult(result);
  store.toggleDiceTray(true);

  return result;
}

export function bindDiceEvents(container: HTMLElement) {
  // Close dice tray
  const closeBtn = container.querySelector('#btn-close-dice');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      sound.playClick();
      store.toggleDiceTray(false);
    });
  }

  // Pool adjustment stepper buttons
  container.querySelectorAll('.btn-dice-pool-adjust').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const delta = parseInt((e.currentTarget as HTMLElement).getAttribute('data-delta') || '0', 10);
      const poolInput = container.querySelector('#custom-pool-input') as HTMLInputElement;
      if (poolInput) {
        sound.playClick();
        const current = parseInt(poolInput.value || '12', 10);
        poolInput.value = String(Math.max(1, Math.min(40, current + delta)));
      }
    });
  });

  // Custom roll
  const rollCustomBtn = container.querySelector('#btn-roll-custom');
  if (rollCustomBtn) {
    rollCustomBtn.addEventListener('click', () => {
      const poolInput = container.querySelector('#custom-pool-input') as HTMLInputElement;
      const pool = poolInput ? parseInt(poolInput.value, 10) : 12;
      executeRoll(Math.max(1, pool), 'Custom Test', false);
    });
  }

  // Exploding roll
  const rollExpBtn = container.querySelector('#btn-roll-exploding');
  if (rollExpBtn) {
    rollExpBtn.addEventListener('click', () => {
      const poolInput = container.querySelector('#custom-pool-input') as HTMLInputElement;
      const pool = poolInput ? parseInt(poolInput.value, 10) : 12;
      executeRoll(Math.max(1, pool), 'Rule of Six Exploding Roll', true);
    });
  }

  // Reroll 1 Die (-1 Edge)
  const rerollOneBtn = container.querySelector('#btn-edge-reroll-one');
  if (rerollOneBtn) {
    rerollOneBtn.addEventListener('click', () => {
      const latest = store.rollHistory[0];
      if (!latest) return;
      store.spendEdge(1);
      sound.playClick();

      // Find first failed die (< 5) and reroll it
      const newDice = [...latest.dice];
      const failIdx = newDice.findIndex((d) => d < 5);
      if (failIdx !== -1) {
        newDice[failIdx] = Math.floor(Math.random() * 6) + 1;
      }

      let newHits = 0;
      let newOnes = 0;
      newDice.forEach((d) => {
        if (d >= 5) newHits++;
        if (d === 1) newOnes++;
      });

      const result: DiceRollResult = {
        ...latest,
        id: 'roll_' + Date.now(),
        dice: newDice,
        hits: newHits,
        ones: newOnes,
        isGlitch: newOnes > latest.pool / 2,
        isCriticalGlitch: newOnes > latest.pool / 2 && newHits === 0,
        actionName: `${latest.actionName} (1 Die Rerolled)`,
      };

      store.addRollResult(result);
    });
  }

  // Reroll All Failures (-4 Edge)
  const rerollAllBtn = container.querySelector('#btn-edge-reroll-all');
  if (rerollAllBtn) {
    rerollAllBtn.addEventListener('click', () => {
      const latest = store.rollHistory[0];
      if (!latest) return;
      store.spendEdge(4);
      sound.playSuccessChime();

      // Reroll all non-hits (< 5)
      const failedCount = latest.dice.filter((d) => d < 5).length;
      const keepDice = latest.dice.filter((d) => d >= 5);
      const newDice = [...keepDice];
      let newHits = keepDice.length;
      let newOnes = 0;

      for (let i = 0; i < failedCount; i++) {
        const val = Math.floor(Math.random() * 6) + 1;
        newDice.push(val);
        if (val >= 5) newHits++;
        if (val === 1) newOnes++;
      }

      const result: DiceRollResult = {
        ...latest,
        id: 'roll_' + Date.now(),
        dice: newDice,
        hits: newHits,
        ones: newOnes,
        isGlitch: newOnes > latest.pool / 2,
        isCriticalGlitch: newOnes > latest.pool / 2 && newHits === 0,
        actionName: `${latest.actionName} (All Failures Rerolled -4 Edge)`,
      };

      store.addRollResult(result);
    });
  }

  // Add Edge Pool with Exploding 6s (-4 Edge)
  const addEdgeBtn = container.querySelector('#btn-edge-add-four');
  if (addEdgeBtn) {
    addEdgeBtn.addEventListener('click', () => {
      const latest = store.rollHistory[0];
      const char = store.getActiveCharacter();
      if (!latest) return;
      const edgeRating = char?.attributes?.edge || 4;
      store.spendEdge(4);
      sound.playSuccessChime();

      const newDice = [...latest.dice];
      let addedHits = 0;
      let newOnes = latest.ones;

      const rollDie = () => Math.floor(Math.random() * 6) + 1;
      for (let i = 0; i < edgeRating; i++) {
        let val = rollDie();
        newDice.push(val);
        if (val >= 5) addedHits++;
        if (val === 1) newOnes++;
        while (val === 6) {
          val = rollDie();
          newDice.push(val);
          if (val >= 5) addedHits++;
          if (val === 1) newOnes++;
        }
      }

      const result: DiceRollResult = {
        ...latest,
        id: 'roll_' + Date.now(),
        dice: newDice,
        hits: latest.hits + addedHits,
        ones: newOnes,
        actionName: `${latest.actionName} (+${edgeRating} Edge Dice Exploded)`,
      };

      store.addRollResult(result);
    });
  }

  // Buy +1 Hit (-3 Edge)
  const buyHitBtn = container.querySelector('#btn-edge-buy-hit');
  if (buyHitBtn) {
    buyHitBtn.addEventListener('click', () => {
      const latest = store.rollHistory[0];
      if (!latest) return;
      store.spendEdge(3);
      sound.playSuccessChime();

      const result: DiceRollResult = {
        ...latest,
        id: 'roll_' + Date.now(),
        hits: latest.hits + 1,
        actionName: `${latest.actionName} (+1 Hit Bought -3 Edge)`,
      };
      store.addRollResult(result);
    });
  }

  // Negate Glitch (-5 Edge)
  const negateBtn = container.querySelector('#btn-edge-negate-glitch');
  if (negateBtn) {
    negateBtn.addEventListener('click', () => {
      const latest = store.rollHistory[0];
      if (!latest) return;
      store.spendEdge(5);
      sound.playSuccessChime();
      const updated: DiceRollResult = {
        ...latest,
        isGlitch: false,
        isCriticalGlitch: false,
        actionName: `${latest.actionName} (Glitch Negated -5 Edge)`,
      };
      store.addRollResult(updated);
    });
  }

  // Listen to window custom trigger event from anywhere in the app
  window.addEventListener('sr6-trigger-roll', (e: any) => {
    const detail = e.detail;
    if (detail && typeof detail.pool === 'number') {
      executeRoll(detail.pool, detail.actionName || 'Action Test', false);
    }
  });
}
