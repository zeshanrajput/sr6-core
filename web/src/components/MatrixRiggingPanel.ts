import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderMatrixRiggingPanel(): string {
  const char = store.getActiveCharacter();
  if (!char) return '';

  const isAi = char.identity?.is_ai || false;
  const rawFleet = [...(char.drones || []), ...(char.vehicles || [])];
  // Deduplicate by name
  const seen = new Set<string>();
  const allFleet = rawFleet.filter((item) => {
    if (!item || !item.name || seen.has(item.name)) return false;
    seen.add(item.name);
    return true;
  });
  const globalMod = store.getTotalGlobalModifier();

  // Living Persona ASDF calculation
  const lp = char.living_persona || {};
  const asdf = lp.asdf_bonuses || {};

  const attack = asdf.attack ?? (isAi ? 7 : 0);
  const sleaze = asdf.sleaze ?? (isAi ? 9 : 0);
  const dataProc = asdf.data_processing ?? (isAi ? 7 : 0);
  const firewall = asdf.firewall ?? (isAi ? 9 : 0);

  // Matrix Defenses from store
  const fullDef = store.getEffectiveMatrixDefense('full');

  const focusActive = store.isBuffActive('MatrixDef_Focus', true);
  const paActive = store.isBuffActive('MatrixDef_PA_App', true);
  const shieldActive = store.isBuffActive('MatrixDef_Directional_Shield', true);
  const spriteShieldActive = store.isBuffActive('MatrixDef_Sprite_Shield', false);

  const intVal = char.attributes?.intuition || 2;
  const matrixInitPool = Math.max(0, dataProc + intVal + globalMod);

  // Fleet cards HTML
  const fleetHtml = allFleet
    .map((item) => {
      const isDrone = item.category === 'drone' || !item.seats || item.seats === '-';
      const badgeText = isDrone ? 'TACTICAL DRONE' : 'VEHICLE';
      const badgeColor = isDrone ? 'var(--accent-primary)' : 'var(--accent-gold)';

      const currentMode = store.getDroneMode(item.name);
      const isHome = item.name.toLowerCase().includes('man-at-arms') || item.name.toLowerCase().includes('butler');

      // Standard Action Pools with Sensor vs Pilot clarification
      const actionKeys = ['Piloting (Pilot)', 'Targeting (Sensor)', 'Evasion (Pilot)', 'Perception (Sensor)', 'Stealth (Pilot)'];
      const poolsHtml = `
        <div style="margin-top:12px; padding-top:10px; border-top:1px solid var(--border-subtle);">
          <div style="font-size:0.75rem; color:var(--accent-primary); font-family:var(--font-tech); font-weight:800; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <span>⚡ RIGGED & INHABITED ACTION POOLS</span>
            <span style="font-size:0.68rem; color:var(--text-muted);">DYNAMIC MODIFIERS ACTIVE</span>
          </div>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:6px;">
            ${actionKeys
              .map((k) => {
                const poolData = store.getEffectiveDronePool(item, k);
                const effP = poolData.pool;
                const hits = poolData.hits;
                const icon = k.includes('Pilot')
                  ? '🕹️'
                  : k.includes('Target')
                  ? '🎯'
                  : k.includes('Evasion')
                  ? '🛡️'
                  : k.includes('Percept')
                  ? '👁️'
                  : '👻';

                return `
                <div class="attr-resist-btn" style="justify-content:space-between; padding:5px 8px; width:100%;">
                  <div style="display:flex; align-items:center; gap:4px;">
                    <!-- Fine-grained stepper -->
                    <div style="display:flex; gap:2px;">
                      <button class="icon-btn btn-drone-step" data-drone="${item.name}" data-action-key="${k}" data-delta="-1" style="width:20px; height:20px; font-size:0.7rem; padding:0;">-</button>
                      <button class="icon-btn btn-drone-step" data-drone="${item.name}" data-action-key="${k}" data-delta="1" style="width:20px; height:20px; font-size:0.7rem; padding:0;">+</button>
                    </div>
                    <span style="font-size:0.78rem; font-weight:700;">${icon} ${k}</span>
                  </div>

                  <button class="pool-btn" data-action="roll-drone" data-name="${item.name} (${k})" data-pool="${effP}" style="padding:2px 8px; font-size:0.8rem; margin:0;" title="${poolData.breakdown}">
                    <span>🎲 ${effP}d6</span>
                    <span class="bought-hits">(${hits}h)</span>
                  </button>
                </div>
              `;
              })
              .join('')}
          </div>
        </div>
      `;

      // Operational mode selector chips
      const modesHtml = isDrone
        ? `
        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin: 10px 0 6px;">
          <span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); font-weight:700;">CONTROL MODE:</span>
          <button class="chip btn-drone-mode ${currentMode === 'inhabited' ? 'active' : ''}" data-drone="${item.name}" data-mode="inhabited" style="cursor:pointer; font-size:0.75rem; ${
            currentMode === 'inhabited' ? 'border-color:var(--accent-primary); background:rgba(0,229,255,0.15); color:var(--accent-primary); font-weight:800;' : ''
          }">
            ✨ Reiko Inhabited (${isHome ? 'RES 9' : 'RES 8'})
          </button>
          <button class="chip btn-drone-mode ${currentMode === 'sprite' ? 'active' : ''}" data-drone="${item.name}" data-mode="sprite" style="cursor:pointer; font-size:0.75rem; ${
            currentMode === 'sprite' ? 'border-color:var(--accent-gold); background:rgba(255,215,0,0.15); color:var(--accent-gold); font-weight:800;' : ''
          }">
            👾 Sprite Override (L7)
          </button>
          <button class="chip btn-drone-mode ${currentMode === 'autopilot' ? 'active' : ''}" data-drone="${item.name}" data-mode="autopilot" style="cursor:pointer; font-size:0.75rem; ${
            currentMode === 'autopilot' ? 'border-color:var(--text-secondary); background:rgba(255,255,255,0.08); font-weight:800;' : ''
          }">
            🤖 Autopilot (Pilot ${item.base_pilot || item.pilot || 2})
          </button>
        </div>
      `
        : '';

      // Synergy & Companion Buff Checkboxes
      const tazDiagKey = `${item.name}_TazDiag`;
      const tazSymbKey = `${item.name}_TazSymb`;
      const focusKey = `${item.name}_Focus`;

      const tazDiagActive = store.isBuffActive(tazDiagKey, true);
      const tazSymbActive = store.isBuffActive(tazSymbKey, true);
      const focusDroneActive = store.isBuffActive(focusKey, true);

      const buffsHtml = isDrone
        ? `
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px;">
          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${
            tazDiagActive ? 'border-color:var(--accent-primary); background:rgba(0,229,255,0.08);' : 'opacity:0.6;'
          }">
            <input type="checkbox" class="drone-buff-cb" data-buff-key="${tazDiagKey}" ${
            tazDiagActive ? 'checked' : ''
          } style="cursor:pointer; accent-color:var(--accent-primary);">
            <span>🐉 Taz Diag (+3 Pilot)</span>
          </label>

          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${
            tazSymbActive ? 'border-color:var(--accent-primary); background:rgba(0,229,255,0.08);' : 'opacity:0.6;'
          }">
            <input type="checkbox" class="drone-buff-cb" data-buff-key="${tazSymbKey}" ${
            tazSymbActive ? 'checked' : ''
          } style="cursor:pointer; accent-color:var(--accent-primary);">
            <span>🐉 Taz Symb (+4 Action)</span>
          </label>

          ${
            currentMode === 'inhabited'
              ? `
            <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${
              focusDroneActive ? 'border-color:var(--accent-gold); background:rgba(255,215,0,0.08);' : 'opacity:0.6;'
            }">
              <input type="checkbox" class="drone-buff-cb" data-buff-key="${focusKey}" ${
                  focusDroneActive ? 'checked' : ''
                } style="cursor:pointer; accent-color:var(--accent-gold);">
              <span>🔮 Resonance Focus (+4 Pilot)</span>
            </label>
          `
              : ''
          }
        </div>
      `
        : '';

      // Modifications badges
      let modsHtml = '';
      if (item.modifications && item.modifications.length > 0) {
        modsHtml = `
          <div style="margin-top:10px; display:flex; flex-wrap:wrap; gap:4px;">
            ${item.modifications
              .map(
                (m: string) => `
              <span class="chip" style="font-size:0.7rem; padding:2px 6px; background:rgba(0, 229, 255, 0.05);">
                🔧 ${m}
              </span>
            `
              )
              .join('')}
          </div>
        `;
      }

      // Notes / Mobility
      let notesHtml = '';
      if (item.mobility_str || (item.profile_notes && item.profile_notes.length > 0)) {
        notesHtml = `
          <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:8px; font-family:var(--font-mono);">
            ${item.mobility_str ? `<div>🚀 <strong>Mobility:</strong> ${item.mobility_str}</div>` : ''}
            ${
              item.profile_notes && item.profile_notes.length > 0
                ? `<div>📝 ${item.profile_notes.join(' • ')}</div>`
                : ''
            }
          </div>
        `;
      }

      return `
        <div class="tactical-card" style="margin-bottom:14px; border-color:rgba(0, 229, 255, 0.25);">
          <div class="tactical-card-header">
            <div>
              <div class="tactical-card-title">${item.name}</div>
              ${item.role ? `<div style="font-size:0.75rem; color:var(--text-muted);">${item.role}</div>` : ''}
            </div>
            <div class="chip" style="font-size:0.7rem; font-weight:800; border-color:${badgeColor}; color:${badgeColor};">
              ${badgeText}
            </div>
          </div>

          <div class="weapon-stats-row" style="margin-top:8px;">
            <div>HAN: <strong>${item.handling}</strong></div>
            <div>SPD: <strong>${item.speed}</strong></div>
            <div>ACC: <strong>${item.accel}</strong></div>
            <div>BOD: <strong>${item.body}</strong></div>
            <div>ARM: <strong>${item.armor}</strong></div>
            <div>PLT: <strong>${currentMode === 'inhabited' ? (isHome ? '9 (Override)' : '8 (Override)') : currentMode === 'sprite' ? '7 (Sprite)' : item.pilot}</strong></div>
            <div>SEN: <strong>${item.sensor}</strong></div>
          </div>

          ${modesHtml}
          ${buffsHtml}
          ${notesHtml}
          ${modsHtml}
          ${poolsHtml}
        </div>
      `;
    })
    .join('');

  // Decking & Matrix Tests (Electronics + RES, Cracking + RES)
  const electronicsSkill = char.skills?.find((s) => s.name.toLowerCase() === 'electronics');
  const crackingSkill = char.skills?.find((s) => s.name.toLowerCase() === 'cracking');

  const elecSoftwarePool = store.getEffectiveSkillPool(electronicsSkill || { name: 'Electronics', base_pool: 13, specialized_pool: 28, specialization: 'Software' }, true);
  const elecOtherPool = store.getEffectiveSkillPool(electronicsSkill || { name: 'Electronics', base_pool: 13, buffed_pool: 26 }, false);

  const crackHackingPool = store.getEffectiveSkillPool(crackingSkill || { name: 'Cracking', base_pool: 13, specialized_pool: 30, specialization: 'Hacking' }, true);
  const crackOtherPool = store.getEffectiveSkillPool(crackingSkill || { name: 'Cracking', base_pool: 13, buffed_pool: 28 }, false);

  const deckingTestsHtml = `
    <div class="section-title" style="margin-top:20px;">
      <h2><span>💻</span> NATURAL HACKER DECKING TESTS (SKILL + RES)</h2>
    </div>

    <div class="tactical-card" style="margin-bottom:20px; border-color:rgba(0, 229, 255, 0.25); background:rgba(8, 14, 28, 0.75);">
      <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:12px; font-family:var(--font-mono);">
        Applies <strong>Natural Hacker</strong> (RES Substitution), <strong>Resonance Focus (+4)</strong>, <strong>Taz Teamwork (+4)</strong>, <strong>Overclocking (+2, 1 wild die)</strong>, and <strong>ECM Warrior II (+2)</strong>.
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:10px;">
        <!-- Electronics (Software) -->
        <div class="tactical-card" style="padding:10px; border-color:rgba(0, 229, 255, 0.2);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div style="font-size:0.85rem; font-weight:800; color:var(--accent-primary);">⚡ Electronics + RES (Software)</div>
            <button class="pool-btn" data-action="roll-matrix" data-name="Electronics + RES (Software Spec)" data-pool="${elecSoftwarePool}" style="padding:3px 8px; font-size:0.85rem; margin:0;" title="Base Electronics 8 + RES 8 + Focus 4 + Taz 4 + Overclock 2 + Spec 2 = 28d6 (1 wild)">
              <span>🎲 ${elecSoftwarePool}d6</span>
              <span class="bought-hits">(${Math.floor(elecSoftwarePool / 4)}h)</span>
            </button>
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted);">
            Control Device, Format Device, Jack Out, Jump into Rigged Device, Reboot Device, Set Data Bomb, Trace Icon.
          </div>
        </div>

        <!-- Electronics (Other) -->
        <div class="tactical-card" style="padding:10px; border-color:rgba(0, 229, 255, 0.2);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div style="font-size:0.85rem; font-weight:800; color:var(--accent-primary);">⚡ Electronics + RES (Other / Hardware)</div>
            <button class="pool-btn" data-action="roll-matrix" data-name="Electronics + RES (Computer / Hardware)" data-pool="${elecOtherPool}" style="padding:3px 8px; font-size:0.85rem; margin:0;" title="Base Electronics 8 + RES 8 + Focus 4 + Taz 4 + Overclock 2 = 26d6 (1 wild)">
              <span>🎲 ${elecOtherPool}d6</span>
              <span class="bought-hits">(${Math.floor(elecOtherPool / 4)}h)</span>
            </button>
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted);">
            Edit File, Encrypt File, Erase Matrix Signature, Hash Check, Matrix Perception, Matrix Search, Modify Icon, Threat Analysis.
          </div>
        </div>

        <!-- Cracking (Hacking) -->
        <div class="tactical-card" style="padding:10px; border-color:rgba(255, 215, 0, 0.2);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div style="font-size:0.85rem; font-weight:800; color:var(--accent-gold);">⚡ Cracking + RES (Hacking)</div>
            <button class="pool-btn" data-action="roll-matrix" data-name="Cracking + RES (Hacking Spec)" data-pool="${crackHackingPool}" style="padding:3px 8px; font-size:0.85rem; margin:0;" title="Base Cracking 8 + RES 8 + Focus 4 + Taz 4 + Overclock 2 + ECM Warrior 2 + Spec 2 = 30d6 (1 wild)">
              <span>🎲 ${crackHackingPool}d6</span>
              <span class="bought-hits">(${Math.floor(crackHackingPool / 4)}h)</span>
            </button>
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted);">
            Backdoor Entry, Crack File, Delayed Command, Garbage In/Out, Known Exploit, Metahuman in Middle, Probe, Puppet Cyberware, Spoof Command.
          </div>
        </div>

        <!-- Cracking (Cybercombat / EW) -->
        <div class="tactical-card" style="padding:10px; border-color:rgba(255, 215, 0, 0.2);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div style="font-size:0.85rem; font-weight:800; color:var(--accent-gold);">⚡ Cracking + RES (Cybercombat / EW)</div>
            <button class="pool-btn" data-action="roll-matrix" data-name="Cracking + RES (Cybercombat / EW)" data-pool="${crackOtherPool}" style="padding:3px 8px; font-size:0.85rem; margin:0;" title="Base Cracking 8 + RES 8 + Focus 4 + Taz 4 + Overclock 2 + ECM Warrior 2 = 28d6 (1 wild)">
              <span>🎲 ${crackOtherPool}d6</span>
              <span class="bought-hits">(${Math.floor(crackOtherPool / 4)}h)</span>
            </button>
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted);">
            Brute Force, Crash Program, Data Spike, Device Lock, Disarm Data Bomb, Resonance Spike, Tar Pit, Jam Signals, Masquerade, Snoop, Watchdog.
          </div>
        </div>
      </div>
    </div>
  `;

  // Submersion Echoes & Complex Forms
  const echoes = char.powers?.echoes || [];
  const complexForms = char.complex_forms || char.powers?.complex_forms || [];

  let echoesHtml = '';
  if (echoes.length > 0) {
    echoesHtml = `
      <div class="section-title" style="margin-top:20px;">
        <h2><span>⚡</span> SUBMERSION ECHOES & NETWORK CAPABILITIES</h2>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:18px;">
        ${echoes
          .map(
            (e: any) => `
          <div class="chip" style="font-size:0.8rem; padding:6px 12px; border-color:var(--accent-primary); background:rgba(0, 229, 255, 0.08); font-weight:700;">
            ✨ ${e.name || e}
          </div>
        `
          )
          .join('')}
      </div>
    `;
  }

  let complexFormsHtml = '';
  if (complexForms.length > 0) {
    complexFormsHtml = `
      <div class="section-title" style="margin-top:20px;">
        <h2><span>🔮</span> COMPLEX FORMS & THREADING ARRAYS</h2>
      </div>
      <div class="card-stack" style="margin-bottom:20px;">
        ${complexForms
          .map(
            (cf: any) => `
          <div class="tactical-card" style="padding:10px 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="font-family:var(--font-tech); font-weight:800; font-size:0.95rem; color:var(--text-primary);">
                ${cf.name}
              </div>
              <div class="chip" style="font-size:0.75rem; border-color:var(--accent-gold); color:var(--accent-gold); font-weight:800;">
                FV: ${cf.fading || 'L'} | ${cf.duration || 'I'}
              </div>
            </div>
            ${
              cf.notes
                ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">${cf.notes}</div>`
                : ''
            }
          </div>
        `
          )
          .join('')}
      </div>
    `;
  }

  return `
    <div class="section-title">
      <h2><span>🌐</span> LIVING PERSONA & MATRIX SUITE</h2>
    </div>

    <div class="tactical-card" style="margin-bottom:20px; border-color:rgba(0, 229, 255, 0.3); background:rgba(8, 14, 28, 0.85);">
      <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; text-align:center; margin-bottom:14px;">
        <div style="background:var(--bg-surface); padding:8px 4px; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">ATTACK</div>
          <div style="font-size:1.4rem; font-family:var(--font-tech); font-weight:800; color:var(--accent-rose);">${attack}</div>
        </div>
        <div style="background:var(--bg-surface); padding:8px 4px; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">SLEAZE</div>
          <div style="font-size:1.4rem; font-family:var(--font-tech); font-weight:800; color:var(--accent-primary);">${sleaze}</div>
        </div>
        <div style="background:var(--bg-surface); padding:8px 4px; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">DATA PROC</div>
          <div style="font-size:1.4rem; font-family:var(--font-tech); font-weight:800; color:var(--accent-gold);">${dataProc}</div>
        </div>
        <div style="background:var(--bg-surface); padding:8px 4px; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">FIREWALL</div>
          <div style="font-size:1.4rem; font-family:var(--font-tech); font-weight:800; color:var(--accent-emerald);">${firewall}</div>
        </div>
      </div>

      <!-- Matrix Defense Protocols Suite -->
      <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle);">
        <div style="font-size:0.8rem; color:var(--accent-primary); font-family:var(--font-tech); font-weight:800; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
          <span>🛡️ MATRIX DEFENSE PROTOCOLS (NATURAL HACKER)</span>
          <span style="font-size:0.68rem; color:var(--text-muted);">SR6 MATRIX RULES p. 198</span>
        </div>

        <!-- Defense Buff Toggles -->
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px;">
          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${focusActive ? 'border-color:var(--accent-gold); background:rgba(255,215,0,0.08);' : 'opacity:0.6;'}">
            <input type="checkbox" class="matrix-def-cb" data-buff-key="MatrixDef_Focus" ${focusActive ? 'checked' : ''} style="cursor:pointer; accent-color:var(--accent-gold);">
            <span>🔮 RES Focus (+4)</span>
          </label>

          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${paActive ? 'border-color:var(--accent-primary); background:rgba(0,229,255,0.08);' : 'opacity:0.6;'}">
            <input type="checkbox" class="matrix-def-cb" data-buff-key="MatrixDef_PA_App" ${paActive ? 'checked' : ''} style="cursor:pointer; accent-color:var(--accent-primary);">
            <span>📱 PA App R6 (+6 Full Def)</span>
          </label>

          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${shieldActive ? 'border-color:var(--accent-primary); background:rgba(0,229,255,0.08);' : 'opacity:0.6;'}">
            <input type="checkbox" class="matrix-def-cb" data-buff-key="MatrixDef_Directional_Shield" ${shieldActive ? 'checked' : ''} style="cursor:pointer; accent-color:var(--accent-primary);">
            <span>🛡️ Directional Shield (+${dataProc} Full Def)</span>
          </label>

          <label class="chip" style="font-size:0.72rem; cursor:pointer; display:flex; align-items:center; gap:4px; ${spriteShieldActive ? 'border-color:var(--accent-emerald); background:rgba(0,255,136,0.1);' : 'opacity:0.6;'}">
            <input type="checkbox" class="matrix-def-cb" data-buff-key="MatrixDef_Sprite_Shield" ${spriteShieldActive ? 'checked' : ''} style="cursor:pointer; accent-color:var(--accent-emerald);">
            <span>👾 Sprite Shield (+7 All Defenses)</span>
          </label>
        </div>

        <!-- Defense Buttons Grid -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:8px;">
          <!-- Matrix Defense (Continuous PA-Managed) -->
          <div class="attr-resist-btn" style="justify-content:space-between; padding:6px 10px;">
            <div style="display:flex; align-items:center; gap:4px;">
              <div style="display:flex; gap:2px;">
                <button class="icon-btn btn-mdef-step" data-def="full" data-delta="-1" style="width:20px; height:20px; font-size:0.7rem;">-</button>
                <button class="icon-btn btn-mdef-step" data-def="full" data-delta="1" style="width:20px; height:20px; font-size:0.7rem;">+</button>
              </div>
              <span style="font-size:0.8rem; font-weight:700;">🛡️ Matrix Defense</span>
            </div>
            <button class="pool-btn" data-action="roll-matrix" data-name="Matrix Defense" data-pool="${fullDef.pool}" style="padding:2px 8px; font-size:0.8rem; margin:0;" title="${fullDef.breakdown}">
              <span>🎲 ${fullDef.pool}d6</span>
              <span class="bought-hits">(${fullDef.hits}h)</span>
            </button>
          </div>

          <!-- Matrix Initiative -->
          <div class="attr-resist-btn" style="justify-content:space-between; padding:6px 10px;">
            <span style="font-size:0.8rem; font-weight:700;">⚡ Matrix Initiative (Hot-Sim)</span>
            <button class="pool-btn" data-action="roll-matrix" data-name="Matrix Initiative (DP + INT + 3d6)" data-pool="${matrixInitPool}" style="padding:2px 8px; font-size:0.8rem; margin:0;">
              <span>🎲 ${matrixInitPool}d6 + 3d6</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="section-title">
      <h2><span>🤖</span> TACTICAL DRONES & SWARM FLEET (${allFleet.length})</h2>
    </div>

    <div class="card-stack">
      ${fleetHtml || `<div class="tactical-card" style="text-align:center; color:var(--text-muted); padding:20px;">No registered tactical drones found in character registry.</div>`}
    </div>

    ${deckingTestsHtml}
    ${echoesHtml}
    ${complexFormsHtml}
  `;
}

export function bindMatrixEvents(container: HTMLElement) {
  // Mode switcher
  container.querySelectorAll('.btn-drone-mode').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const droneName = el.getAttribute('data-drone');
      const mode = el.getAttribute('data-mode') as 'inhabited' | 'sprite' | 'autopilot';
      if (droneName && mode) {
        sound.playClick();
        store.setDroneMode(droneName, mode);
      }
    });
  });

  // Drone buff toggles
  container.querySelectorAll('.drone-buff-cb').forEach((cb) => {
    cb.addEventListener('change', (e) => {
      const el = e.target as HTMLInputElement;
      const buffKey = el.getAttribute('data-buff-key');
      if (buffKey) {
        sound.playClick();
        store.toggleBuff(buffKey, el.checked);
      }
    });
  });

  // Matrix defense buff toggles
  container.querySelectorAll('.matrix-def-cb').forEach((cb) => {
    cb.addEventListener('change', (e) => {
      const el = e.target as HTMLInputElement;
      const buffKey = el.getAttribute('data-buff-key');
      if (buffKey) {
        sound.playClick();
        store.toggleBuff(buffKey, el.checked);
      }
    });
  });

  // Matrix defense fine-grained steppers
  container.querySelectorAll('.btn-mdef-step').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const defType = el.getAttribute('data-def') || 'full';
      const delta = parseInt(el.getAttribute('data-delta') || '0', 10);
      sound.playClick();
      store.adjustMatrixDefenseOffset(defType, delta);
    });
  });

  // Drone fine-grained pool steppers
  container.querySelectorAll('.btn-drone-step').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const droneName = el.getAttribute('data-drone');
      const actionKey = el.getAttribute('data-action-key');
      const delta = parseInt(el.getAttribute('data-delta') || '0', 10);
      if (droneName && actionKey) {
        sound.playClick();
        store.adjustDroneOffset(droneName, actionKey, delta);
      }
    });
  });

  // Tap-to-roll drone actions, decking tests & matrix defenses
  container.querySelectorAll('[data-action="roll-matrix"], [data-action="roll-drone"]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const name = el.getAttribute('data-name') || 'Matrix Test';
      const pool = parseInt(el.getAttribute('data-pool') || '6', 10);

      sound.playClick();
      window.dispatchEvent(
        new CustomEvent('sr6-trigger-roll', {
          detail: { pool, actionName: name },
        })
      );
    });
  });
}
