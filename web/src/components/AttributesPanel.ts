import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderAttributesPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const attrList = char.attributes_list || [];
  const isVelvet = char.identity?.is_velvet || store.activeCharId === 'velvet';
  const isMonad = char.identity?.is_monad || store.activeCharId === 'venn' || store.activeCharId === 'union';
  const globalMod = store.getTotalGlobalModifier();

  // Find effective attribute values via store helper
  const bod = store.getEffectiveAttributeVal('BOD').val;
  const rea = store.getEffectiveAttributeVal('REA').val;
  const intVal = store.getEffectiveAttributeVal('INT').val;
  const wil = store.getEffectiveAttributeVal('WIL').val;
  const cha = store.getEffectiveAttributeVal('CHA').val;
  const logVal = store.getEffectiveAttributeVal('LOG').val;

  // Common composite pools
  const defPool = Math.max(0, rea + intVal + globalMod);
  const armorVal = char.armors?.[0]?.defense_rating || 0;
  const soakPool = Math.max(0, bod + armorVal + (isMonad ? 4 : 0) + globalMod);
  const composurePool = Math.max(0, wil + cha + globalMod);
  const memoryPool = Math.max(0, logVal + wil + globalMod);
  const judgePool = Math.max(0, wil + intVal + globalMod);
  const drainPool = Math.max(0, wil + (isVelvet ? cha : logVal) + globalMod);
  const matrixDefObj = store.getEffectiveMatrixDefense('full');
  const matrixDefPool = matrixDefObj.pool;

  const cardsHtml = attrList
    .map((a) => {
      const eff = store.getEffectiveAttributeVal(a.code);
      const isBuffed = eff.isBuffed;
      const val = eff.val;
      const offset = store.getAttributeOffset(a.code);
      const offsetStr = offset !== 0 ? (offset > 0 ? `+${offset}` : `${offset}`) : '';
      const badgeHtml = isBuffed ? `<span class="attr-badge">${offsetStr ? offsetStr : 'AUG'}</span>` : '';

      return `
      <div class="attr-card ${isBuffed ? 'buffed' : ''}" data-attr-code="${a.code}" title="${a.name}: ${eff.breakdown}">
        ${badgeHtml}
        <div class="attr-code">${a.code}</div>
        <div class="attr-val">${val}</div>
      </div>
    `;
    })
    .join('');

  return `
    <div class="attributes-grid" style="margin-bottom: 12px;">
      ${cardsHtml}
    </div>

    <!-- Common Attribute Resists & Tests Bar -->
    <div class="tactical-card" style="margin-bottom: 18px; padding: 10px 14px; background: rgba(8, 14, 28, 0.7); border-color: rgba(0, 229, 255, 0.2);">
      <div style="font-size:0.75rem; color:var(--accent-primary); font-family:var(--font-tech); font-weight:800; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
        <span>🎯 COMMON ATTRIBUTE TESTS & RESISTS</span>
        <span style="font-size:0.65rem; color:var(--text-muted);">TAP TO ROLL</span>
      </div>

      <div style="display:flex; flex-wrap:wrap; gap:8px;">
        <button class="attr-resist-btn btn-common-roll" data-action-name="Defense / Dodge (REA + INT)" data-pool="${defPool}">
          <span>🛡️ Defense</span>
          <span class="pool-highlight">${defPool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Damage Soak (BOD + Armor)" data-pool="${soakPool}">
          <span>🧱 Soak</span>
          <span class="pool-highlight">${soakPool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Composure Test (WIL + CHA)" data-pool="${composurePool}">
          <span>🧠 Composure</span>
          <span class="pool-highlight">${composurePool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Memory Test (LOG + WIL)" data-pool="${memoryPool}">
          <span>💾 Memory</span>
          <span class="pool-highlight">${memoryPool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Judge Intentions (WIL + INT)" data-pool="${judgePool}">
          <span>👁️ Judge Intentions</span>
          <span class="pool-highlight">${judgePool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Drain Resistance (WIL + ${isVelvet ? 'CHA' : 'LOG'})" data-pool="${drainPool}">
          <span>🔮 Drain Soak</span>
          <span class="pool-highlight">${drainPool}d6</span>
        </button>

        <button class="attr-resist-btn btn-common-roll" data-action-name="Matrix Defense" data-pool="${matrixDefPool}" title="${matrixDefObj.breakdown}">
          <span>🌐 Matrix Defense</span>
          <span class="pool-highlight">${matrixDefPool}d6</span>
        </button>
      </div>
    </div>
  `;
}

export function bindAttributesEvents(container: HTMLElement) {
  // Common quick rolls
  container.querySelectorAll('.btn-common-roll').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const actionName = el.getAttribute('data-action-name') || 'Attribute Test';
      const pool = parseInt(el.getAttribute('data-pool') || '6', 10);
      sound.playClick();
      window.dispatchEvent(
        new CustomEvent('sr6-trigger-roll', {
          detail: { pool, actionName },
        })
      );
    });
  });

  // Tap attribute card for drilldown & dual-attribute roll creator & enhancement adjuster
  container.querySelectorAll('.attr-card').forEach((card) => {
    card.addEventListener('click', (e) => {
      const code = (e.currentTarget as HTMLElement).getAttribute('data-attr-code');
      const char = store.getActiveCharacter();
      if (!char || !code) return;

      const attr = char.attributes_list?.find((a) => a.code === code);
      if (!attr) return;

      sound.playClick();
      const eff = store.getEffectiveAttributeVal(code);
      const primaryVal = eff.val;
      const globalMod = store.getTotalGlobalModifier();
      const singlePool = Math.max(0, primaryVal + globalMod);

      let buffsHtml = '';
      if (attr.buffs && attr.buffs.length > 0) {
        buffsHtml = `
          <h4 style="margin: 14px 0 6px; color: var(--accent-primary); font-size:0.85rem;">Active Augmentations & Modifiers:</h4>
          <ul style="font-size:0.8rem; margin-left:14px;">
            ${attr.buffs
              .map(
                (b) => `
              <li style="margin-bottom: 4px;">
                <strong>${b.source}</strong>: +${b.value} ${b.notes ? `<em>(${b.notes})</em>` : ''}
              </li>
            `
              )
              .join('')}
          </ul>
        `;
      }

      // Secondary attribute selector chips
      const otherAttrs = (char.attributes_list || []).filter((a) => a.code !== code);
      const secondaryChipsHtml = otherAttrs
        .map((a) => {
          const aVal = store.getEffectiveAttributeVal(a.code).val;
          return `
          <button class="chip btn-secondary-attr" data-code="${a.code}" data-name="${a.name}" data-val="${aVal}" style="cursor:pointer; padding:4px 8px; font-size:0.8rem;">
            + ${a.code} (${aVal})
          </button>
        `;
        })
        .join('');

      const content = `
        <div style="font-size: 1.05rem; margin-bottom: 8px;">
          <strong>Base:</strong> ${eff.base} | <strong>Current Effective:</strong> <strong style="color:var(--accent-primary); font-size:1.2rem;">${primaryVal}</strong>
        </div>
        <p style="font-size:0.85rem; color:var(--text-secondary);">${eff.breakdown}</p>
        ${buffsHtml}

        <!-- DYNAMIC ATTRIBUTE ENHANCEMENT ADJUSTER -->
        <div style="margin-top: 14px; padding: 12px; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-accent);">
          <div style="font-size:0.8rem; color:var(--accent-primary); font-weight:800; margin-bottom:6px; display:flex; justify-content:space-between;">
            <span>✨ ENHANCE ATTRIBUTE (SPELLS / OVERDRIVE / NANITES)</span>
          </div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:8px;">
            Adjust temporary enhancement level (affects all dependent pools):
          </div>
          <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
            <button class="chip btn-adjust-attr" data-code="${code}" data-delta="-1" style="cursor:pointer; padding:6px 12px; font-weight:800;">-1</button>
            <button class="chip btn-adjust-attr" data-code="${code}" data-delta="1" style="cursor:pointer; padding:6px 12px; font-weight:800;">+1</button>
            <button class="chip btn-adjust-attr" data-code="${code}" data-delta="2" style="cursor:pointer; padding:6px 12px; font-weight:800;">+2</button>
            <button class="chip btn-adjust-attr" data-code="${code}" data-delta="4" style="cursor:pointer; padding:6px 12px; font-weight:800; background:rgba(168, 85, 247, 0.2); border-color:var(--accent-purple); color:var(--text-primary);">+4 (Spell)</button>
            <button class="chip btn-reset-attr" data-code="${code}" style="cursor:pointer; padding:6px 12px; font-weight:800; color:var(--accent-rose);">Reset</button>
          </div>
        </div>

        <div style="margin-top: 14px; padding: 12px; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-subtle);">
          <div style="font-size:0.8rem; color:var(--accent-primary); font-weight:700; margin-bottom:8px;">
            🎲 ROLL SINGLE ATTRIBUTE:
          </div>
          <button class="dice-act-btn" id="btn-roll-single-attr" style="width:100%; background:var(--accent-primary); color:#040814; font-weight:900;">
            🎲 Roll ${attr.name} (${singlePool}d6)
          </button>
        </div>

        <div style="margin-top: 14px; padding: 12px; background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-accent);">
          <div style="font-size:0.8rem; color:var(--accent-gold); font-weight:700; margin-bottom:8px;">
            ➕ COMBINE WITH SECOND ATTRIBUTE (DUAL-ROLL):
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px;">
            ${secondaryChipsHtml}
          </div>
          <div id="dual-roll-preview-container" style="display:none; padding-top:8px; border-top:1px dashed var(--border-subtle);">
            <div style="font-size:0.85rem; margin-bottom:6px;" id="dual-roll-label"></div>
            <button class="dice-act-btn" id="btn-roll-dual-attr" style="width:100%; border-color:var(--accent-gold); color:var(--accent-gold); font-weight:900;">
              🎲 Roll Dual Attribute Pool
            </button>
          </div>
        </div>

        <div style="margin-top: 14px;">
          <button class="dice-act-btn" id="btn-drilldown-lookup" data-query="${attr.name}" style="width:100%; border-color:var(--accent-primary); color:var(--accent-primary); font-size:0.8rem;">
            📖 Lookup "${attr.name}" in Rules Reference
          </button>
        </div>
      `;

      store.openDrawer(`${attr.name} (${attr.code})`, content);

      // Bind dynamic drawer elements
      setTimeout(() => {
        // Adjust enhancement buttons
        document.querySelectorAll('.btn-adjust-attr').forEach((btn) => {
          btn.addEventListener('click', (ev) => {
            const b = ev.currentTarget as HTMLElement;
            const cCode = b.getAttribute('data-code') || '';
            const delta = parseInt(b.getAttribute('data-delta') || '1', 10);
            sound.playClick();
            store.adjustAttributeOffset(cCode, delta);
            store.closeDrawer();
          });
        });

        const resetAttrBtn = document.querySelector('.btn-reset-attr');
        if (resetAttrBtn) {
          resetAttrBtn.addEventListener('click', (ev) => {
            const b = ev.currentTarget as HTMLElement;
            const cCode = b.getAttribute('data-code') || '';
            sound.playClick();
            store.resetAttributeOffset(cCode);
            store.closeDrawer();
          });
        }

        // Single roll
        const singleRollBtn = document.querySelector('#btn-roll-single-attr');
        if (singleRollBtn) {
          singleRollBtn.addEventListener('click', () => {
            sound.playClick();
            store.closeDrawer();
            window.dispatchEvent(
              new CustomEvent('sr6-trigger-roll', {
                detail: { pool: singlePool, actionName: `${attr.name} Test` },
              })
            );
          });
        }

        // Secondary attribute selection
        let selectedSecondary: { code: string; name: string; val: number } | null = null;
        document.querySelectorAll('.btn-secondary-attr').forEach((btn) => {
          btn.addEventListener('click', (ev) => {
            sound.playClick();
            const bEl = ev.currentTarget as HTMLElement;
            const sCode = bEl.getAttribute('data-code') || '';
            const sName = bEl.getAttribute('data-name') || '';
            const sVal = parseInt(bEl.getAttribute('data-val') || '1', 10);

            document.querySelectorAll('.btn-secondary-attr').forEach((b) => b.classList.remove('active'));
            bEl.classList.add('active');

            selectedSecondary = { code: sCode, name: sName, val: sVal };
            const previewContainer = document.querySelector('#dual-roll-preview-container') as HTMLElement;
            const labelEl = document.querySelector('#dual-roll-label') as HTMLElement;
            const dualBtn = document.querySelector('#btn-roll-dual-attr') as HTMLElement;

            const totalPool = Math.max(0, primaryVal + sVal + globalMod);
            if (previewContainer && labelEl && dualBtn) {
              previewContainer.style.display = 'block';
              labelEl.innerHTML = `<strong>${attr.name} (${primaryVal})</strong> + <strong>${sName} (${sVal})</strong> = <strong>${totalPool}d6</strong>`;
              dualBtn.innerText = `🎲 Roll ${attr.code} + ${sCode} (${totalPool}d6)`;
            }
          });
        });

        // Dual roll button
        const dualRollBtn = document.querySelector('#btn-roll-dual-attr');
        if (dualRollBtn) {
          dualRollBtn.addEventListener('click', () => {
            if (!selectedSecondary) return;
            const totalPool = Math.max(0, primaryVal + selectedSecondary.val + globalMod);
            sound.playClick();
            store.closeDrawer();
            window.dispatchEvent(
              new CustomEvent('sr6-trigger-roll', {
                detail: { pool: totalPool, actionName: `${attr.code} + ${selectedSecondary.code} Test` },
              })
            );
          });
        }

        // Lookup in rules
        const lookupBtn = document.querySelector('#btn-drilldown-lookup') as HTMLElement;
        if (lookupBtn) {
          lookupBtn.addEventListener('click', () => {
            sound.playClick();
            store.closeDrawer();
            store.toggleRulesDrawer(true);
            const query = lookupBtn.getAttribute('data-query') || '';
            const searchInput = document.querySelector('#rules-filter-input') as HTMLInputElement;
            if (searchInput) {
              searchInput.value = query;
              searchInput.dispatchEvent(new Event('input'));
            }
          });
        }
      }, 50);
    });
  });
}
