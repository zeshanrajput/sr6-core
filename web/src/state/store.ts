import { CharacterBundleItem, CharacterDataBundle, DiceRollResult, SkillData, WeaponData } from '../types/sr6';

export interface CharacterState {
  charId: string;
  physicalDamage: number;
  stunDamage: number;
  overflowDamage: number;
  edgeSpent: number;
  weaponAmmo: Record<string, number>;
  // Dynamic Modifiers & Adjustments
  sustainedSpellsCount: number; // e.g. 0, 1, 2, 3 (-2 penalty per spell sustained without focus)
  situationalModifier: number; // Global situational modifier (+/- dice)
  skillOffsets: Record<string, number>; // per-skill custom dice adjustments
  weaponOffsets: Record<string, number>; // per-weapon custom dice adjustments
  disabledBuffs: Record<string, boolean>; // e.g. "Smartlink": true (if disabled)
}

export type StoreListener = () => void;

class TacticalStore {
  private bundle: Record<string, CharacterBundleItem> = {};
  public activeCharId: string = 'reiko';
  private states: Record<string, CharacterState> = {};
  public rollHistory: DiceRollResult[] = [];
  public activeTab: string = 'dashboard';
  public drawerContent: { title: string; html: string } | null = null;
  public isRulesDrawerOpen: boolean = false;
  public isDiceTrayOpen: boolean = false;
  public isModifiersHudOpen: boolean = true;
  public contactFilter = {
    search: '',
    region: 'ALL',
    type: 'ALL',
    hasFavorsOnly: false,
    sortBy: 'name', // 'name' | 'conn_desc' | 'loy_desc' | 'favors_desc'
  };
  private listeners: Set<StoreListener> = new Set();

  public setContactFilter(filter: Partial<{ search: string; region: string; type: string; hasFavorsOnly: boolean; sortBy: string }>) {
    this.contactFilter = { ...this.contactFilter, ...filter };
    this.notify();
  }

  constructor() {
    this.loadPersistedState();
  }

  public initBundle(rawBundle: CharacterDataBundle, initialId?: string) {
    if (rawBundle.characters) {
      this.bundle = rawBundle.characters;
    } else {
      this.bundle = rawBundle as Record<string, CharacterBundleItem>;
    }

    const availableIds = Object.keys(this.bundle);
    if (availableIds.length > 0) {
      if (initialId && availableIds.includes(initialId)) {
        this.activeCharId = initialId;
      } else if (!availableIds.includes(this.activeCharId)) {
        this.activeCharId = availableIds[0];
      }
    }

    // Ensure state entry exists for each character
    availableIds.forEach((id) => {
      if (!this.states[id]) {
        this.states[id] = {
          charId: id,
          physicalDamage: 0,
          stunDamage: 0,
          overflowDamage: 0,
          edgeSpent: 0,
          weaponAmmo: {},
          sustainedSpellsCount: 0,
          situationalModifier: 0,
          skillOffsets: {},
          weaponOffsets: {},
          disabledBuffs: {},
        };
      } else {
        // Ensure new fields exist on restored states
        if (this.states[id].sustainedSpellsCount === undefined) this.states[id].sustainedSpellsCount = 0;
        if (this.states[id].situationalModifier === undefined) this.states[id].situationalModifier = 0;
        if (!this.states[id].skillOffsets) this.states[id].skillOffsets = {};
        if (!this.states[id].weaponOffsets) this.states[id].weaponOffsets = {};
        if (!this.states[id].disabledBuffs) this.states[id].disabledBuffs = {};
      }

      // Initialize weapon ammo defaults
      const char = this.bundle[id];
      if (char && char.weapons) {
        char.weapons.forEach((w) => {
          if (this.states[id].weaponAmmo[w.name] === undefined) {
            const cap = this.parseAmmoCapacity(w.ammo);
            this.states[id].weaponAmmo[w.name] = cap;
          }
        });
      }
    });

    this.notify();
  }

  public parseAmmoCapacity(ammoStr: string): number {
    if (!ammoStr || ammoStr === '—' || ammoStr === '-') return 0;
    const match = ammoStr.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }

  public getCharacterList(): Array<{ id: string; name: string; role: string; theme: string }> {
    return Object.keys(this.bundle).map((id) => {
      const c = this.bundle[id];
      const handle = c.identity?.handle || id;
      const role = c.identity?.role || 'Shadowrunner';
      let theme = 'reiko';
      if (c.identity?.is_velvet || id === 'velvet') theme = 'velvet';
      else if (c.identity?.is_monad || id === 'venn' || id === 'union') theme = 'venn';
      return { id, name: handle, role, theme };
    });
  }

  public getActiveCharacter(): CharacterBundleItem | null {
    return this.bundle[this.activeCharId] || null;
  }

  public getActiveState(): CharacterState {
    if (!this.states[this.activeCharId]) {
      this.states[this.activeCharId] = {
        charId: this.activeCharId,
        physicalDamage: 0,
        stunDamage: 0,
        overflowDamage: 0,
        edgeSpent: 0,
        weaponAmmo: {},
        sustainedSpellsCount: 0,
        situationalModifier: 0,
        skillOffsets: {},
        weaponOffsets: {},
        disabledBuffs: {},
      };
    }
    return this.states[this.activeCharId];
  }

  public getTheme(): string {
    const char = this.getActiveCharacter();
    if (!char) return 'reiko';
    if (char.identity?.is_velvet || this.activeCharId === 'velvet') return 'velvet';
    if (char.identity?.is_monad || this.activeCharId === 'venn' || this.activeCharId === 'union') return 'venn';
    return 'reiko';
  }

  /**
   * Calculates SR6 Wound Modifier: -1 per 3 full damage boxes.
   * Monad Toughness shifts wound threshold where applicable.
   */
  public getWoundModifier(): number {
    const state = this.getActiveState();
    const char = this.getActiveCharacter();
    const totalBoxes = state.physicalDamage + state.stunDamage;
    if (totalBoxes <= 0) return 0;

    const isMonad = char?.identity?.is_monad || false;
    const rawPenalty = Math.floor(totalBoxes / 3);
    if (isMonad && rawPenalty > 0) {
      return Math.max(0, rawPenalty - 1);
    }
    return rawPenalty;
  }

  /**
   * Calculates penalty for sustained spells without focus: -2 per sustained spell.
   */
  public getSustainedSpellsPenalty(): number {
    const state = this.getActiveState();
    return Math.max(0, (state.sustainedSpellsCount || 0) * 2);
  }

  public getSituationalModifier(): number {
    const state = this.getActiveState();
    return state.situationalModifier || 0;
  }

  /**
   * Net global dice pool modifier = Situational - Wounds - Sustained Spells.
   */
  public getTotalGlobalModifier(): number {
    return this.getSituationalModifier() - this.getWoundModifier() - this.getSustainedSpellsPenalty();
  }

  public isBuffActive(buffKey: string, defaultActive: boolean = true): boolean {
    const state = this.getActiveState();
    if (state.disabledBuffs?.[buffKey] !== undefined) {
      return !state.disabledBuffs[buffKey];
    }
    return defaultActive;
  }

  public isBuffDisabled(buffKey: string): boolean {
    return !this.isBuffActive(buffKey, true);
  }

  public toggleBuff(buffKey: string, enabled?: boolean) {
    const state = this.getActiveState();
    if (!state.disabledBuffs) state.disabledBuffs = {};
    if (enabled !== undefined) {
      state.disabledBuffs[buffKey] = !enabled;
    } else {
      const currentlyActive = this.isBuffActive(buffKey, true);
      state.disabledBuffs[buffKey] = currentlyActive;
    }
    this.persistState();
    this.notify();
  }

  public setSustainedSpells(count: number) {
    const state = this.getActiveState();
    state.sustainedSpellsCount = Math.max(0, count);
    this.persistState();
    this.notify();
  }

  public adjustSustainedSpells(delta: number) {
    const state = this.getActiveState();
    state.sustainedSpellsCount = Math.max(0, (state.sustainedSpellsCount || 0) + delta);
    this.persistState();
    this.notify();
  }

  public setSituationalModifier(val: number) {
    const state = this.getActiveState();
    state.situationalModifier = val;
    this.persistState();
    this.notify();
  }

  public adjustSituationalModifier(delta: number) {
    const state = this.getActiveState();
    state.situationalModifier = (state.situationalModifier || 0) + delta;
    this.persistState();
    this.notify();
  }

  public getSkillOffset(skillName: string): number {
    const state = this.getActiveState();
    return state.skillOffsets?.[skillName] || 0;
  }

  public adjustSkillOffset(skillName: string, delta: number) {
    const state = this.getActiveState();
    if (!state.skillOffsets) state.skillOffsets = {};
    state.skillOffsets[skillName] = (state.skillOffsets[skillName] || 0) + delta;
    this.persistState();
    this.notify();
  }

  public resetSkillOffset(skillName: string) {
    const state = this.getActiveState();
    if (state.skillOffsets && state.skillOffsets[skillName] !== undefined) {
      delete state.skillOffsets[skillName];
      this.persistState();
      this.notify();
    }
  }

  public getWeaponOffset(weaponName: string): number {
    const state = this.getActiveState();
    return state.weaponOffsets?.[weaponName] || 0;
  }

  public adjustWeaponOffset(weaponName: string, delta: number) {
    const state = this.getActiveState();
    if (!state.weaponOffsets) state.weaponOffsets = {};
    state.weaponOffsets[weaponName] = (state.weaponOffsets[weaponName] || 0) + delta;
    this.persistState();
    this.notify();
  }

  public getAttributeOffset(attrCode: string): number {
    const state = this.getActiveState();
    const codeUpper = attrCode.toUpperCase();
    return state.attributeOffsets?.[codeUpper] || 0;
  }

  public adjustAttributeOffset(attrCode: string, delta: number) {
    const state = this.getActiveState();
    if (!state.attributeOffsets) state.attributeOffsets = {};
    const codeUpper = attrCode.toUpperCase();
    state.attributeOffsets[codeUpper] = (state.attributeOffsets[codeUpper] || 0) + delta;
    this.persistState();
    this.notify();
  }

  public resetAttributeOffset(attrCode: string) {
    const state = this.getActiveState();
    const codeUpper = attrCode.toUpperCase();
    if (state.attributeOffsets && state.attributeOffsets[codeUpper] !== undefined) {
      delete state.attributeOffsets[codeUpper];
      this.persistState();
      this.notify();
    }
  }

  public getEffectiveAttributeVal(attrCode: string): { val: number; base: number; isBuffed: boolean; breakdown: string } {
    const char = this.getActiveCharacter();
    if (!char) return { val: 1, base: 1, isBuffed: false, breakdown: '1' };
    const codeUpper = attrCode.toUpperCase();
    const codeLower = attrCode.toLowerCase();
    const attrItem = char.attributes_list?.find((a) => a.code.toUpperCase() === codeUpper);
    const base = attrItem ? attrItem.base : (char.attributes?.[codeLower] || 1);
    const defaultBuffed = attrItem ? (attrItem.buffed ?? attrItem.base) : base;
    const offset = this.getAttributeOffset(codeUpper);
    const total = Math.max(1, defaultBuffed + offset);
    const isBuffed = total !== base;
    return {
      val: total,
      base,
      isBuffed,
      breakdown: isBuffed ? `Base ${base} + Enhancements ${total - base}` : `Base ${base}`,
    };
  }

  /**
   * Computes the final effective pool for a skill including active buffs,
   * specialization (when checked), wounds, sustaining penalties, situational adjustments, and custom offsets.
   */
  public getEffectiveSkillPool(skill: SkillData, useSpecialization: boolean = false): number {
    let pool = skill.base_pool || skill.rating || 0;

    // Add buffs if active
    if (skill.buffs && skill.buffs.length > 0) {
      skill.buffs.forEach((b) => {
        const buffKey = `${skill.name}_${b.source}`;
        const defaultActive = b.type !== 'specialization';
        if (this.isBuffActive(buffKey, defaultActive)) {
          pool += b.value || 0;
        }
      });
    }

    if (useSpecialization && skill.specialization) {
      pool += 2;
    }

    // Add attribute offset if enhanced
    const attrCode = skill.effective_attribute || skill.attribute;
    if (attrCode) {
      pool += this.getAttributeOffset(attrCode);
    }

    // Add per-skill offset
    pool += this.getSkillOffset(skill.name);

    // Apply global modifiers (situational - wounds - sustaining)
    pool += this.getTotalGlobalModifier();

    return Math.max(0, pool);
  }

  public getSkillEffectivePool(skill: SkillData, useSpecialization: boolean = false): number {
    return this.getEffectiveSkillPool(skill, useSpecialization);
  }

  /**
   * Computes effective weapon attack pool.
   */
  public getEffectiveWeaponPool(w: WeaponData, isMelee: boolean): number {
    const char = this.getActiveCharacter();
    if (!char) return 8;

    const skill = char.skills?.find(
      (s) =>
        (isMelee && (s.name.toLowerCase().includes('close combat') || s.name.toLowerCase().includes('unarmed') || s.name.toLowerCase().includes('athletics'))) ||
        (!isMelee && s.name.toLowerCase().includes('firearms'))
    );

    let pool = skill ? skill.base_pool : (isMelee ? 8 : 10);

    // Include skill buffs if active
    if (skill && skill.buffs) {
      skill.buffs.forEach((b) => {
        const buffKey = `${skill.name}_${b.source}`;
        if (!this.isBuffDisabled(buffKey)) {
          pool += b.value || 0;
        }
      });
    }

    // Add weapon-specific offset
    pool += this.getWeaponOffset(w.name);

    // Apply global modifiers
    pool += this.getTotalGlobalModifier();

    return Math.max(0, pool);
  }

  public getDroneMode(droneName: string): 'inhabited' | 'sprite' | 'autopilot' {
    const state = this.getActiveState();
    if (state.droneModes?.[droneName]) {
      return state.droneModes[droneName];
    }
    const isHome = droneName.toLowerCase().includes('man-at-arms') || droneName.toLowerCase().includes('butler');
    return isHome ? 'inhabited' : 'autopilot';
  }

  public setDroneMode(droneName: string, mode: 'inhabited' | 'sprite' | 'autopilot') {
    const state = this.getActiveState();
    if (!state.droneModes) state.droneModes = {};
    state.droneModes[droneName] = mode;
    this.persistState();
    this.notify();
  }

  public getDroneOffset(droneName: string, actionKey: string): number {
    const state = this.getActiveState();
    return state.droneOffsets?.[droneName]?.[actionKey] || 0;
  }

  public adjustDroneOffset(droneName: string, actionKey: string, delta: number) {
    const state = this.getActiveState();
    if (!state.droneOffsets) state.droneOffsets = {};
    if (!state.droneOffsets[droneName]) state.droneOffsets[droneName] = {};
    state.droneOffsets[droneName][actionKey] = (state.droneOffsets[droneName][actionKey] || 0) + delta;
    this.persistState();
    this.notify();
  }

  public getEffectiveDronePool(
    drone: any,
    actionKey: string
  ): { pool: number; hits: number; breakdown: string } {
    const mode = this.getDroneMode(drone.name);
    const char = this.getActiveCharacter();
    const isHome = drone.name.toLowerCase().includes('man-at-arms') || drone.name.toLowerCase().includes('butler');
    const asdf = char?.matrix?.asdf || {};
    const dataProc = asdf.data_processing || 7;
    const res = char?.attributes?.resonance || 8;
    const globalMod = this.getTotalGlobalModifier();
    const customOffset = this.getDroneOffset(drone.name, actionKey);

    let pilotVal = drone.base_pilot || 2;
    let focusBonus = 0;
    let diagBonus = 0;
    let symbBonus = 0;

    const tazDiagActive = this.isBuffActive(`${drone.name}_TazDiag`, true);
    const tazSymbActive = this.isBuffActive(`${drone.name}_TazSymb`, true);
    const focusActive = this.isBuffActive(`${drone.name}_Focus`, true);

    if (mode === 'inhabited') {
      pilotVal = res + (isHome ? 1 : 0); // Reiko RES + Designer bonus on Home Device
      if (focusActive) focusBonus = 4;
      if (tazDiagActive) diagBonus = 3;
      if (tazSymbActive) symbBonus = 4;
    } else if (mode === 'sprite') {
      pilotVal = 7; // Level 7 Sprite Override
      if (tazDiagActive) diagBonus = 3;
      if (tazSymbActive) symbBonus = 4;
    } else {
      // Autopilot
      pilotVal = drone.base_pilot || 1;
    }

    const sensorVal = drone.sensor || drone.base_sensor || 1;
    let basePool = 0;
    let breakdown = '';

    const key = actionKey.toLowerCase();
    if (key.includes('target') || key.includes('gun') || key.includes('attack')) {
      basePool = dataProc + sensorVal + (mode !== 'autopilot' ? symbBonus : 0);
      breakdown = `Targeting ${dataProc} + Sensor ${sensorVal}${symbBonus && mode !== 'autopilot' ? ` + Taz Symb ${symbBonus}` : ''}`;
    } else if (key.includes('defense') || key.includes('evasion')) {
      basePool = dataProc + pilotVal + focusBonus + (mode !== 'autopilot' ? symbBonus : 0);
      breakdown = `Evasion ${dataProc} + Pilot ${pilotVal}${focusBonus ? ` + Focus ${focusBonus}` : ''}${symbBonus && mode !== 'autopilot' ? ` + Taz Symb ${symbBonus}` : ''}`;
    } else if (key.includes('percept') || key.includes('clear')) {
      basePool = dataProc + sensorVal + (mode !== 'autopilot' ? symbBonus : 0);
      breakdown = `Clearsight ${dataProc} + Sensor ${sensorVal}${symbBonus && mode !== 'autopilot' ? ` + Taz Symb ${symbBonus}` : ''}`;
    } else if (key.includes('stealth')) {
      basePool = dataProc + pilotVal + focusBonus + (mode !== 'autopilot' ? symbBonus : 0) + (isHome ? 2 : 0);
      breakdown = `Stealth ${dataProc} + Pilot ${pilotVal}${focusBonus ? ` + Focus ${focusBonus}` : ''}${symbBonus && mode !== 'autopilot' ? ` + Taz Symb ${symbBonus}` : ''}${isHome ? ' + SneakSoft 2' : ''}`;
    } else if (key.includes('pilot') || key.includes('maneuver')) {
      basePool = dataProc + pilotVal + focusBonus + (mode !== 'autopilot' ? diagBonus : 0);
      breakdown = `Maneuvering ${dataProc} + Pilot ${pilotVal}${focusBonus ? ` + Focus ${focusBonus}` : ''}${diagBonus && mode !== 'autopilot' ? ` + Taz Diag ${diagBonus}` : ''}`;
    } else {
      basePool = dataProc + pilotVal;
      breakdown = `Autosoft ${dataProc} + Pilot ${pilotVal}`;
    }

    const finalPool = Math.max(0, basePool + customOffset + globalMod);
    return {
      pool: finalPool,
      hits: Math.floor(finalPool / 4),
      breakdown: `${breakdown}${customOffset ? ` [Adjusted: ${customOffset > 0 ? `+${customOffset}` : customOffset}]` : ''} = ${finalPool}d6`,
    };
  }

  public getMatrixDefenseOffset(defenseType: string): number {
    const state = this.getActiveState();
    return state.matrixDefenseOffsets?.[defenseType] || 0;
  }

  public adjustMatrixDefenseOffset(defenseType: string, delta: number) {
    const state = this.getActiveState();
    if (!state.matrixDefenseOffsets) state.matrixDefenseOffsets = {};
    state.matrixDefenseOffsets[defenseType] = (state.matrixDefenseOffsets[defenseType] || 0) + delta;
    this.persistState();
    this.notify();
  }

  public getEffectiveMatrixDefense(defenseType: 'full' | 'standard' = 'full'): { pool: number; hits: number; breakdown: string } {
    const char = this.getActiveCharacter();
    const isAi = char?.identity?.is_ai || false;
    const res = char?.attributes?.resonance || 0;
    const wil = char?.attributes?.willpower || 6;
    const asdf = char?.matrix?.asdf || char?.living_persona?.asdf_bonuses || {};
    const firewall = asdf.firewall || (isAi ? 9 : 5);
    const dataProc = asdf.data_processing || (isAi ? 7 : 3);
    const globalMod = this.getTotalGlobalModifier();
    const customOffset = this.getMatrixDefenseOffset(defenseType);

    const isTechnoOrAi = isAi || res > 0;
    const primaryAttr = isTechnoOrAi ? (res || 8) : wil;
    const primaryName = isTechnoOrAi ? 'RES' : 'WIL';

    const focusActive = isTechnoOrAi && this.isBuffActive('MatrixDef_Focus', true);
    const paActive = isTechnoOrAi && this.isBuffActive('MatrixDef_PA_App', true);
    const shieldActive = isTechnoOrAi && this.isBuffActive('MatrixDef_Directional_Shield', true);
    const spriteShieldActive = this.isBuffActive('MatrixDef_Sprite_Shield', false);

    let basePool = firewall + primaryAttr;
    let parts = [`FW ${firewall}`, `${primaryName} ${primaryAttr}`];

    if (focusActive) {
      basePool += 4;
      parts.push('Focus +4');
    }

    if (defenseType === 'full') {
      if (paActive) {
        basePool += 6;
        parts.push('PA App R6 +6');
      }
      if (shieldActive) {
        basePool += dataProc;
        parts.push(`Directional Shield +${dataProc}`);
      }
    }

    if (spriteShieldActive) {
      basePool += 7;
      parts.push('Sprite Shield +7');
    }

    const finalPool = Math.max(0, basePool + customOffset + globalMod);
    return {
      pool: finalPool,
      hits: Math.floor(finalPool / 4),
      breakdown: `${parts.join(' + ')}${customOffset ? ` [Adjusted: ${customOffset > 0 ? `+${customOffset}` : customOffset}]` : ''} = ${finalPool}d6`,
    };
  }

  public setActiveCharacter(charId: string) {
    if (this.bundle[charId]) {
      this.activeCharId = charId;
      this.persistState();
      this.notify();
    }
  }

  public setDamage(type: 'physical' | 'stun' | 'overflow', value: number) {
    const state = this.getActiveState();
    if (type === 'physical') state.physicalDamage = Math.max(0, value);
    else if (type === 'stun') state.stunDamage = Math.max(0, value);
    else if (type === 'overflow') state.overflowDamage = Math.max(0, value);
    this.persistState();
    this.notify();
  }

  public resetDamage() {
    const state = this.getActiveState();
    state.physicalDamage = 0;
    state.stunDamage = 0;
    state.overflowDamage = 0;
    this.persistState();
    this.notify();
  }

  public fireWeapon(weaponName: string, rounds: number) {
    const state = this.getActiveState();
    const current = state.weaponAmmo[weaponName] || 0;
    state.weaponAmmo[weaponName] = Math.max(0, current - rounds);
    this.persistState();
    this.notify();
  }

  public reloadWeapon(weaponName: string, maxAmmo: number) {
    const state = this.getActiveState();
    state.weaponAmmo[weaponName] = maxAmmo;
    this.persistState();
    this.notify();
  }

  public spendEdge(amount: number = 1) {
    const state = this.getActiveState();
    state.edgeSpent = Math.max(0, state.edgeSpent + amount);
    this.persistState();
    this.notify();
  }

  public restoreEdge(amount?: number) {
    const state = this.getActiveState();
    if (amount === undefined) {
      state.edgeSpent = 0;
    } else {
      state.edgeSpent = Math.max(0, state.edgeSpent - amount);
    }
    this.persistState();
    this.notify();
  }

  public addRollResult(result: DiceRollResult) {
    this.rollHistory.unshift(result);
    if (this.rollHistory.length > 30) {
      this.rollHistory.pop();
    }
    this.notify();
  }

  public clearRollHistory() {
    this.rollHistory = [];
    this.notify();
  }

  public setActiveTab(tab: string) {
    this.activeTab = tab;
    this.notify();
  }

  public openDrawer(title: string, html: string) {
    this.drawerContent = { title, html };
    this.notify();
  }

  public closeDrawer() {
    this.drawerContent = null;
    this.notify();
  }

  public toggleRulesDrawer(open?: boolean) {
    this.isRulesDrawerOpen = open !== undefined ? open : !this.isRulesDrawerOpen;
    this.notify();
  }

  public toggleDiceTray(open?: boolean) {
    this.isDiceTrayOpen = open !== undefined ? open : !this.isDiceTrayOpen;
    this.notify();
  }

  public toggleModifiersHud(open?: boolean) {
    this.isModifiersHudOpen = open !== undefined ? open : !this.isModifiersHudOpen;
    this.notify();
  }

  public subscribe(listener: StoreListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((fn) => fn());
  }

  private persistState() {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('sr6_active_char', this.activeCharId);
        localStorage.setItem('sr6_char_states', JSON.stringify(this.states));
      }
    } catch {}
  }

  private loadPersistedState() {
    try {
      if (typeof localStorage !== 'undefined') {
        const savedChar = localStorage.getItem('sr6_active_char');
        if (savedChar) this.activeCharId = savedChar;
        const savedStates = localStorage.getItem('sr6_char_states');
        if (savedStates) {
          this.states = JSON.parse(savedStates);
        }
      }
    } catch {}
  }
}

export const store = new TacticalStore();
