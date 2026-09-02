import { store } from '../state/store';
import { sound } from '../utils/audio';

export function renderCombatPanel(): string {
  const char = store.getActiveCharacter();
  const state = store.getActiveState();
  if (!char) return '';

  const weapons = char.weapons || [];
  const armors = char.armors || [];
  const woundPenalty = store.getWoundModifier();

  const weaponsHtml = weapons
    .map((w) => {
      const isMelee = w.is_melee;
      const maxAmmo = store.parseAmmoCapacity(w.ammo);
      const currentAmmo = state.weaponAmmo[w.name] !== undefined ? state.weaponAmmo[w.name] : maxAmmo;

      // Extract firing modes (All ranged weapons can fire SS; listed modes are in addition to SS)
      const rawModes = (
        w.modes_str
          ? w.modes_str.split(/[,/]/).map((m) => m.trim().toUpperCase())
          : (w.modes || []).map((m) => m.toUpperCase())
      ).filter(Boolean);

      const modeList: { name: string; rounds: number }[] = [{ name: 'SS', rounds: 1 }];

      rawModes.forEach((m) => {
        if ((m === 'SA' || m.includes('SEMI')) && !modeList.some((x) => x.name === 'SA')) {
          modeList.push({ name: 'SA', rounds: 2 });
        } else if ((m === 'BF' || m.includes('BURST')) && !modeList.some((x) => x.name === 'BF')) {
          modeList.push({ name: 'BF', rounds: 4 });
        } else if ((m === 'FA' || m.includes('AUTO')) && !modeList.some((x) => x.name === 'FA')) {
          modeList.push({ name: 'FA', rounds: 10 });
        }
      });

      const fireButtonsHtml = !isMelee && maxAmmo > 0
        ? modeList
            .map(({ name: mode, rounds }) => {
              const canFire = currentAmmo >= rounds;
              return `
                <button class="fire-btn" data-weapon="${w.name}" data-rounds="${rounds}" ${
                !canFire ? 'disabled' : ''
              }>
                  🔥 ${mode} (-${rounds})
                </button>
              `;
            })
            .join('')
        : '';

      const reloadBtnHtml = !isMelee && maxAmmo > 0
        ? `<button class="reload-btn" data-weapon="${w.name}" data-max-ammo="${maxAmmo}">RELOAD (${maxAmmo})</button>`
        : '';

      const effectiveAttackPool = store.getEffectiveWeaponPool(w, isMelee);
      const customWeaponOffset = store.getWeaponOffset(w.name);

      return `
      <div class="tactical-card">
        <div class="tactical-card-header">
          <div class="tactical-card-title">${w.name}</div>
          <div class="tactical-card-badge">${w.category.toUpperCase()}</div>
        </div>

        <div class="weapon-stats-row">
          <div>DV: <strong>${w.damage}</strong></div>
          <div>AR: <strong>${w.attack_rating_str || '—'}</strong></div>
          <div>Modes: <strong>${w.modes_str || '—'}</strong></div>
        </div>

        ${
          !isMelee && maxAmmo > 0
            ? `
          <div class="ammo-counter-bar">
            <span>MAGAZINE: <strong style="color:var(--accent-primary); font-size:1.05rem;">${currentAmmo} / ${maxAmmo}</strong> rounds</span>
            <div style="display:flex; gap:6px;">
              ${reloadBtnHtml}
            </div>
          </div>
          <div class="fire-modes-row" style="margin-bottom:12px;">
            ${fireButtonsHtml}
          </div>
        `
            : ''
        }

        <div style="display:flex; justify-content:space-between; align-items:center; padding-top:8px; border-top:1px solid var(--border-subtle);">
          <div>
            <span style="font-size:0.8rem; color:var(--text-secondary);">ATTACK TEST (${isMelee ? 'Close Combat' : 'Firearms'}):</span>
            ${customWeaponOffset !== 0 ? `<div style="font-size:0.75rem; color:var(--accent-gold); font-weight:700;">[Adjusted: ${customWeaponOffset > 0 ? `+${customWeaponOffset}` : customWeaponOffset}d6]</div>` : ''}
          </div>
          
          <div style="display:flex; align-items:center; gap:6px;">
            <div style="display:flex; gap:2px;">
              <button class="icon-btn btn-weapon-step" data-weapon="${w.name}" data-delta="-1" style="width:22px; height:22px; font-size:0.75rem;">-</button>
              <button class="icon-btn btn-weapon-step" data-weapon="${w.name}" data-delta="1" style="width:22px; height:22px; font-size:0.75rem;">+</button>
            </div>

            <button class="pool-btn" data-action="roll-attack" data-weapon-name="${w.name}" data-pool="${effectiveAttackPool}">
              <span>🎯 ${effectiveAttackPool}d6</span>
              <span class="bought-hits">(${Math.floor(effectiveAttackPool / 4)} Hits)</span>
            </button>
          </div>
        </div>

        ${w.notes ? `<div style="font-size:0.75rem; color:var(--text-muted); margin-top:8px;">* ${w.notes}</div>` : ''}
      </div>
    `;
    })
    .join('');

  // Armor list
  const armorHtml = armors
    .map((a: any) => {
      const accBadges = (a.accessories || a.modifications || [])
        .map((acc: string) => `<span class="chip" style="font-size:0.72rem; padding:2px 6px; background:rgba(0, 240, 255, 0.08); border-color:rgba(0, 240, 255, 0.25); color:var(--text-secondary);">${acc}</span>`)
        .join(' ');

      return `
      <div class="tactical-card" style="border-left: 4px solid var(--accent-emerald);">
        <div class="tactical-card-header">
          <div class="tactical-card-title">🛡️ ${a.name}</div>
          <div class="tactical-card-badge" style="color:var(--accent-emerald); font-weight:800;">+${a.defense_rating} DEFENSE RATING</div>
        </div>
        ${accBadges ? `<div style="display:flex; flex-wrap:wrap; gap:4px; margin:6px 0;">${accBadges}</div>` : ''}
        ${a.notes ? `<div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">${a.notes}</div>` : ''}
      </div>
    `;
    })
    .join('');

  return `
    <div class="section-title">
      <h2><span>⚔️</span> ARSENAL & WEAPONS</h2>
    </div>
    <div class="weapon-grid" style="margin-bottom:20px;">
      ${weaponsHtml}
    </div>

    <div class="section-title">
      <h2><span>🛡️</span> ARMOR & BALLISTICS</h2>
    </div>
    <div class="card-stack">
      ${armorHtml}
    </div>
  `;
}

export function bindCombatEvents(container: HTMLElement) {
  // Fire weapon buttons
  container.querySelectorAll('.fire-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const weapon = el.getAttribute('data-weapon');
      const rounds = parseInt(el.getAttribute('data-rounds') || '1', 10);
      if (weapon) {
        sound.playGunshot(rounds);
        store.fireWeapon(weapon, rounds);
      }
    });
  });

  // Reload weapon button
  container.querySelectorAll('.reload-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const weapon = el.getAttribute('data-weapon');
      const maxAmmo = parseInt(el.getAttribute('data-max-ammo') || '10', 10);
      if (weapon) {
        sound.playReload();
        store.reloadWeapon(weapon, maxAmmo);
      }
    });
  });

  // Manual weapon stepper buttons
  container.querySelectorAll('.btn-weapon-step').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const weaponName = el.getAttribute('data-weapon');
      const delta = parseInt(el.getAttribute('data-delta') || '0', 10);
      if (weaponName) {
        sound.playClick();
        store.adjustWeaponOffset(weaponName, delta);
      }
    });
  });

  // Tap-to-roll attack pool
  container.querySelectorAll('[data-action="roll-attack"]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const el = e.currentTarget as HTMLElement;
      const weaponName = el.getAttribute('data-weapon-name') || 'Weapon Attack';
      const pool = parseInt(el.getAttribute('data-pool') || '10', 10);

      sound.playClick();
      // Dispatch custom roll event
      window.dispatchEvent(
        new CustomEvent('sr6-trigger-roll', {
          detail: { pool, actionName: `${weaponName} Attack` },
        })
      );
    });
  });
}
