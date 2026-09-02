export interface AttributeData {
  name: string;
  code: string;
  base: number;
  buffed: number;
  is_buffed: boolean;
  buffs: Array<{ source: string; value: number; notes?: string; type?: string; target?: string }>;
  breakdown: string;
  doc_link?: string;
}

export interface SkillBuff {
  source: string;
  type: string;
  value: number;
  target?: string;
  active?: boolean;
}

export interface SkillData {
  name: string;
  id: string;
  rating: number;
  attribute: string;
  specialization?: string;
  base_pool: number;
  buffed_pool: number;
  bought_hits: number;
  specialized_pool: number;
  specialized_hits: number;
  effective_attribute?: string;
  is_attribute_overridden?: boolean;
  breakdown_text: string;
  buffs: SkillBuff[];
  doc_link?: string;
  is_activesoft?: boolean;
  base_rating?: number;
}

export interface WeaponData {
  name: string;
  category: string;
  damage: string;
  attack_rating: number[];
  attack_rating_str: string;
  base_attack_rating_str?: string;
  modes: string[];
  modes_str: string;
  ammo: string;
  current_ammo?: number;
  max_ammo?: number;
  ammo_feed?: string;
  is_melee: boolean;
  accessories?: string[];
  notes?: string;
  source_ref?: string;
}

export interface ArmorData {
  name: string;
  defense_rating: number;
  notes?: string;
  features?: string[];
}

export interface VehicleData {
  name: string;
  category: string;
  handling: number;
  handling_offroad?: number;
  accel: number;
  speed: number;
  body: number;
  armor: number;
  pilot: number;
  sensor: number;
  rigged_pools?: Record<string, { pool: number; hits: number; notes: string }>;
  weapons?: any[];
  notes?: string;
}

export interface ContactData {
  name: string;
  archetype?: string;
  connection: number;
  loyalty: number;
  favors?: number;
  region?: string;
  types?: string[];
  description?: string;
  notes?: string;
}

export interface SpellData {
  name: string;
  category: string;
  type: string;
  range: string;
  damage?: string;
  duration: string;
  drain: number;
  description?: string;
  notes?: string;
}

export interface ComplexFormData {
  name: string;
  fading: number;
  duration: string;
  target?: string;
  description?: string;
  notes?: string;
}

export interface AdeptPowerData {
  name: string;
  cost?: number;
  level?: number;
  activation?: string;
  description?: string;
  notes?: string;
}

export interface QualityData {
  name: string;
  rating?: number;
  type?: string;
  notes?: string;
  summary?: string;
}

export interface SinData {
  name: string;
  rating: number;
  quality?: string;
  licenses?: string[];
}

export interface LifestyleData {
  name: string;
  comfort?: string;
  entertainment?: string;
  necessities?: string;
  neighborhood?: string;
  security?: string;
}

export interface IdentityData {
  name?: string;
  handle: string;
  real_name: string;
  metatype: string;
  role: string;
  stream?: string;
  tradition?: string;
  mortype?: string;
  gender?: string;
  age?: string | number;
  nuyen: number;
  karma_avail: number;
  karma_life: number;
  is_ai?: boolean;
  is_monad?: boolean;
  is_velvet?: boolean;
}

export interface CharacterBundleItem {
  identity: IdentityData;
  attributes: Record<string, number>;
  attributes_list: AttributeData[];
  skills: SkillData[];
  weapons: WeaponData[];
  armors: ArmorData[];
  vehicles: VehicleData[];
  drones: VehicleData[];
  contacts: ContactData[];
  sins?: SinData[];
  lifestyles?: LifestyleData[];
  spells?: SpellData[];
  complex_forms?: ComplexFormData[];
  adept_powers?: AdeptPowerData[];
  qualities: {
    positive?: QualityData[];
    negative?: QualityData[];
  };
  gear?: any[];
  inventory?: any;
  cyberware?: any[];
  bioware?: any[];
  living_persona?: any;
  monad_abilities?: any[];
  martial_arts?: any[];
  notes?: any[];
}

export interface CharacterDataBundle {
  characters?: Record<string, CharacterBundleItem>;
  [key: string]: any;
}

export interface DiceRollResult {
  id: string;
  timestamp: string;
  pool: number;
  dice: number[];
  hits: number;
  ones: number;
  isGlitch: boolean;
  isCriticalGlitch: boolean;
  isExploding: boolean;
  actionName: string;
  woundPenaltyApplied: number;
}
