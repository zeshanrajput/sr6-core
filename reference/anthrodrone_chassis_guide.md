# Shadowrun 6e Anthroform Drone Chassis & Endgame Build Guide

> **Scope:** Comprehensive evaluation of **Medium** and **Large** anthroform drones across *SR6 Core (Seattle)*, *Double Clutch*, *Deadly Arts*, *Tarnished Star*, *Firing Squad*, *Hack & Slash*, and *SRM Guide v2.4*. Designed for Emergent/Pilot-AI riggers ([`sparks_template.md`](file:///c:/GitHub/sr6-core/characters/lab/sparks_template.md), [`ouro`](file:///c:/GitHub/sr6-core/characters/lab/ouro/character_build.qmd), [`reiko`](file:///c:/GitHub/sr6-core/characters/reiko/rules/rules_and_downtime.qmd)), excluding cyberarm replacements so factory limbs/attachments remain intact. Also relevant to most technomancers (a machine sprite can inhabit these drones), regular riggers, and any player (by just increasing the pilot rating of the device). Double Clutch notes that at high levels of pilot devices approach basic AI, so I would RP them as allies at that point.

---

## 1. Design Doctrine: Session-1 Viability vs. Endgame Ceiling

### Session-1 Viability Floor

To operate as a functional metahuman-passing runner body from Session 1:

1. **Anthroform silhouette:** Human/metahuman scale (`Medium`, or `Large` for Troll/heavy frames) able to wear standard metahuman armor and wield handheld weapons (`0` mod slots, `0` hardpoints per *SRMG v2.4*, p. 28). Justification: Not all of SR6 is combat scenes. An anthroform drone will be able to participate in other scene types (social, legwork, etc.) far more reliably than an obvious combat drone or a toy. The ability to use weapons and wear armor unlocks many cheaper gear options in early game, as well as scavenging gear.
2. **Round-1 metahuman speed:** `Secondary Propulsion: Wheeled` (`Body × 1,000¥`, Avail `3`, `2` Powertrain slots -> `Accel 10`, `Spd Int 15`, `Top Speed 120`). Justification: you need to maneuver around combat maps, even if you're a ranged combatant. Basic accelerations of 5 means you move 2 meters in the first round, which is untenable.
3. **Basic disguise:** `Realistic Features 1+` (`1–4` Perception threshold to recognize as artificial). Same justification as #1.

### Endgame Target Spec (Strict In-Category Priority Order)

In-category priorities are ordered **before** invoking any `2:1` cross-category slot shifting:

| Category | Priority Order | Endgame Target & Slot Cost |
| :--- | :---: | :--- |
| **Chassis** | 1 (Req)<br>2 (Req)<br>3 (Nice) | • **Increased Structural Integrity (Max = `½ Body`)**: `½ Body` slots (`5,000¥ × Rating`, Avail `4`)<br>• **Realistic Features 4**: `4 - stock_RF` slots (`(4 - stock_RF) × Body × 1,000¥`, Avail `8`)<br>• **Pop-Out Concealment**: `0.5` slots (`Small`, `1,500¥`, `2I`) or `1` slot (`Standard`, `3,000¥`, `3I`) per mount |
| **Powertrain** | 1 (Req)<br>2 (Nice)<br>3 (Nice)<br>4 (Nice)<br>5 (Nice) | • **Secondary Propulsion: Vector Thrust**: `5` slots (`Body × 9,000¥`, Avail `7L`)<br>• **Improved Top Speed (R3)**: `3` slots (`24,000¥`, Avail `3`)<br>• **Improved Acceleration (R2)**: `2` slots (`30,000¥`, Avail `3`)<br>• **Hydrocarbon Fuel Converter**: `2` slots (`Body × 1,500¥`, Avail `5`)<br>• **Nitro Boost**: `2` slots (`5,000¥`, Avail `3I`) *(Full wish-list = `14` Powertrain slots; no hull fits all 5)* |
| **Electronics** | 1 (Req)<br>2 (Req)<br>3 (Req) | • **Enhanced Sensors 9**: `9 - stock_SEN` slots (`(9 - stock_SEN) × 5,000¥`, Avail `9`)<br>• **Passive Stealth Features**: `1` slot (`1,000¥`, Avail `3`)<br>• **Chameleon Coating 4**: `2` slots (`18,000¥`, Avail `8I`) |
| **Hardpoints** | 1 (Req)<br>2 (Nice)<br>3 (Nice) | • **Small Drone Rack**: `1` Standard Hardpoint (`2,000¥`, Avail `3`, enclosed hatch — no Pop-Out needed)<br>• **Concealed Heavy Weapon**: Twin `Crimson Wasps` on `1` split Standard Hardpoint (or Ramming / `Ram Plate`)<br>• **Concealed AoE Stun**: Point-blank `Stun Grenade` (`0` hardpoints; immune at `Body >= 10`) |

---

## 2. Core Rules & Optimization Mechanics

### A. Mod Slots, Shifting & Hardpoints (*Double Clutch*, pp. 120, 123–124)

* **Base Slots:** Unmodified `Body` slots in **each** of Chassis, Powertrain, and Electronics (`3 × Body` total).
* **Upgrading Stock Ratings:** Matching higher-rating mods pay only the **difference** in slots and nuyen (*DC*, p. 120. While this only explicitly says Mod slots, SRM generally offers this for cyberware, etc. so we use the same for nuyen costs as well.).
* **Cross-Category Shifting (`2:1`):** Two unused slots in one category permanently buy `+1` slot in another. Because every shift loses 50% efficiency, match native category capacity before shifting.
* **Hardpoints:** `floor(Unmodified Body / 3)` free Standard Hardpoints (`Body 3` gets `1` Small; `Body 4–5` gets `1` Std; `Body 6–8` gets `2` Std; `Body 9–11` gets `3` Std).
  * `1` Standard Hardpoint splits cleanly into **`2` Small Hardpoints** (*DC*, p. 124).
  * Adding a `Standard Hardpoint` costs `1` Chassis slot and `1,500¥` (Avail `2`).
* **DIY Pricing:** Book listed availability and costs are for shop install. We assume the character is capable of doing work themselves (has access to a facility, sufficient engineering skill/autosoft, etc.) As a result, this analysis may skew towards a cheaper initial (chargen) build as parts become 50% cheaper post-chargen when you can do the work yourself. Note that this does incur a cost of a minor downtime action, but as a rigger we assume you'll take this often enough.

### B. Why Base Sensor `9` Uncaps Endgame Scaling

* **`Enhanced Sensors` (*DC*, p. 142):** Raises the drone's `Sensor` attribute up to **`9`** (`1` slot & `5,000¥` per rating above stock).
* **CRB Housing Cap vs. Drone Attribute:** The *Sensor Packages* table (*CRB*, p. 277: Medium Drone max `4`, Large Drone max `5`) caps **individual gear sensors installed in a housing**, *not* the drone's `Sensor` attribute.
* **Stacking Ceiling:** Pushing base Hardware Sensor to **`9`** stacks cleanly with *Sensor Upgrade* (`+1`), *Home Device* (`+1`), and *Enlighten Automaton* (*Hack & Slash*, p. 130: up to **double** original Sensor = up to **`+9`**!). You would enlighten the automaton at the beginning of your play session, then jump back in while sustaining the form.

### C. Anthroform Armor, Stun Immunity & `Realistic Features` Economics

* **Worn Armor (*SRMG v2.4*, p. 28):** Anthroforms use `max(base Armor, worn Armor)`, so buying Chassis armor mods (`Ceramic`/`Milspec`) wastes slots; throw metahuman armor over a disguised chassis instead (`0` mod slots). This guide generally devalues armor for drones as most SRM tables I've played at have ruled that drones cannot use the 'Armor Lessens Physical Damage' optional rule (as they only have a single condition monitor, there's nothing to shift from or to). If you're under the same restriction, you might actually value **removing** armor to increase acceleration / top speed; this would actually make a combat frame viable without secondary propulsion.
* **`Realistic Features 4` Tax:** Because `RF 4` costs `(4 - stock_RF) × Body × 1,000¥` and `1` Chassis slot per level, **factory `RF 4` on `Nurse MAID` / `Nurse MAID Troll` saves `4` Chassis slots (and `32k¥–40k¥` retail)**—the core reason a `Body 8` Nurse MAID comes within 1–2 raw slots of a `Body 10` Man-at-Arms.
* **Point-Blank Stun Grenade Immunity (*CRB*, pp. 197, 263):** Vehicles are immune to non-electrical Stun damage `<= Body`. At **`Body >= 10`** (all `Body 8–10` frames after `ISI`), dropping a **`Stun Grenade`** (`10S` GZ / `8S` Close / `6S` Near, `15m` blast + `Blinded I, Deafened I, Dazed`, `100¥`, `4L`) deals **zero damage** to your chassis (`Body 12–15` even shrugs off `2–5` net attack hits).

### D. Hardpoint Weapon Winner: Split-Mount Twin **`Crimson Wasps`**

For hardpoint and pop-out concealment efficiency, so far I haven't found a better weapon than Crimson Wasps.

* **Weapon:** **`rEVOlution Arms Crimson Wasp`** (*Firing Squad*, p. 44) — `5P*` (`3P` at Medium), `SA`, AR `16/14/11/6/-`, `15(c)`, `6(I)`, **`1,500¥`**, uses Wild Die (`100¥` non-rechargeable batteries).
* **Hardpoint Split (0¥) + Weapon Mounts:** Split **`1` free stock Standard Hardpoint** into **`2` Small Hardpoints** (**`0¥`, `0` slots**; *DC*, p. 124). Onto those two free hardpoints, install `2× Small Weapon Mounts` (`1,500¥ × 2` retail / `750¥ × 2` DIY, `0` slots, `3I`; *DC*, p. 142) + `2× Pop-Out Concealment (Small)` (**`0.5` Chassis slots × 2 = `1` slot total**, `1,500¥ × 2` retail / `750¥ × 2` DIY, `2I`; *DC*, p. 144). *(Note: Hardpoints are free structural sockets; Weapon Mounts are the powered gimbals/ammo feeds bolted onto them).*
* **Link-Firing Payload (*DC*, p. 143):** Because `Crimson Wasp` base DV is `5P >= 5`, Link-Firing both (`1` Minor Action) adds **`+2 DV` (`7P`)** and **`+1 AR`**, stacking with Weapon Mount **`+2 AR`** (*DC*, p. 142) and Smartlink **`+2 AR`** (*CRB*, p. 260, if smartgun-equipped) for **`7P`, AR `21/19/16/11/-`**—all concealed inside **`1` free split Standard Hardpoint** (`0¥`) and **`1` Chassis slot** (`0.5 × 2`) for **`9,000¥` retail** (`3,000¥` mounts + `3,000¥` Pop-Outs + `3,000¥` guns) or **`6,000¥` DIY** (`1,500¥` for `2× Small Mounts` + `1,500¥` for `2× Small Pop-Outs` + `3,000¥` guns).

### E. Chargen CP vs. Downtime DIY Reality

* **Chargen Availability Cap (*CRB*, p. 66):** Max Avail `6` blocks **`Chameleon Coating 4` (`8I`)**, **`Enhanced Sensors 7–9`**, **`Vector Thrust` (`7L`)**, and **`Realistic Features 4` (`8`)** at chargen. Buy `Wheeled` (`8,000¥`, Avail `3`), `Passive Stealth` (`1,000¥`, Avail `3`), and an **`Engineering [Industrial Mechanic] Toolkit` (`500¥`, Avail `1`)** upfront.
* **Downtime DIY Tooling (*DC*, p. 120; *SRMG v2.4*, pp. 19–22):**
  * Mods `>= 2` slots require an **`Engineering Shop` (`5,000¥`, Avail `4`, `+1` dice pool)** and **50% cost**; *SRMG* mandates **buying hits** (`pool / 4`) on `Engineering + Logic [(slots × 8), (slots × hours)]` as a Minor Downtime Action.

### F. *Tarnished Star* Heat Exemption (`Shiawase Silverstar`)

* *SRMG v2.4* (p. 73): *"Any use of gear from Tarnished Star increases the Heat modifier by +1. This effect is cumulative. This does not apply to vehicles with an availability of 6 or less."*
* *Double Clutch* (p. 127): ***"All drones are vehicles, but not all vehicles are drones."***
* **Verdict:** Because `Shiawase Silverstar` is **Availability `4`** ($\le 6$) and drones are explicitly vehicles under RAW, it qualifies for the *SRMG* exemption (**`+0` Heat**). The `Silverstar` is therefore a fully SRM-legal, Heat-free, and valid contender in this analysis.

---

## 3. Master Anthroform Drone Catalog

### Table 1: True Medium Anthroform Drones (`Reiko`, `Cleo`, `Étaín`, `Aisling`)

| Chassis (Source) | Cost / Avail | `BOD / ARM / PLT / SEN` | Stock Notable Gear | Base Slots (`C/P/E`) | Hardpoints (`Std`) | Strengths & Weaknesses | Endgame `SEN 9` Verdict |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| **`Renraku Attendant (RA)`** (*DA*, p. 177) | `3,500¥` / `2` | `3 / 0 / 2 / 3` | Str 2 limbs, `Passive Stealth`, `Powered Breakdown 2` | `3 / 3 / 3` (`9`) | `1` Small | **(+)** Dirt cheap, folds into briefcase.<br>**(-)** `9` slots; slow (`Top 3`); zero armor. | **Ineligible** (cannot fit `VT + RF 4 + SEN 9`) |
| **`Shiawase Bi-Drone Butler`** (*DC*, p. 117) | `3,000¥` / `2` | `4 / 0 / 2 / 3` | Str 2 limbs, `RF 1` | `4 / 4 / 4` (`12`) | `1` Std | **(+)** Cheapest starter (`7,000¥` w/ `Wheeled`), `SEN 3` stock.<br>**(-)** `Armor 0`; `12` slots chokes in mid-game. | **Ineligible** (`19` req slots > `12`) |
| **`Evo Orderly`** (*DA*, p. 176) | `5,500¥` / `4` | `4 / 2 / 3 / 2` | Str 3 limbs, `Medkit 4`, `RF 1`, Tactile (`+2` Biotech) | `4 / 4 / 4` (`12`) | `1` Std | **(+)** Built-in Medkit 4 + medical cover.<br>**(-)** Expensive for `Body 4`; `SEN 2`. | **Ineligible** (`12` slots) |
| **`Nissan Samurai`** (*CRB*, p. 300; *DC*, p. 146) | `4,500¥` / `2` | `6 / 6 / 3 / 2` | `2× Small arm mounts (0 cap)`, 4-limb mode (`2×` spd) | `6 / 6 / 6` (`18`) | `2` Std *(arms use 2 Small)* | **(+)** Fast starter (`Top 30`), `Armor 6`, `2` free Small mounts.<br>**(-)** `ISI 3 + RF 4 = 7` Cha forces `2:1` shift neither `Pwr` (`5/6` for VT) nor `Elec` (`5/6`) can pay; `Body 9` fails Stun `10S` immunity. | **Ineligible** (`18` slots mathematically chokes) |
| **`Shiawase Silverstar`** (*TS*, p. 158) | `9,000¥` / `4` | `8 / 4 / 3 / 3` | `RF 1`, `Know: Law` soft | `8 / 8 / 8` (`24`) | `2` Std | **(+)** Cheapest `Body 8` DIY hull (`92.5k¥` core DIY); `SEN 3`; `+0` Heat (`Avail 4` vehicle exemption via *DC* p. 127).<br>**(-)** `Armor 4`; `RF 1->4` (`3` Cha) forces `2` Pwr -> `1` Elec shift (`VT 5 + 1` Pwr only!). | **Valid / Tight Fit** (Cheapest Medium `SEN 9` DIY; `Top Speed` starved) |
| **`Ares Combat MAID`** (*DA*, p. 176) | `50,000¥` / `4I` | `8 / 6 / 4 / 3` | Str 3 limbs, `Milspec 1`, `Medkit 4`, `Biotech 4`, `RF 1` | `8 / 8 / 8` (`24`) | `2` Std | **(+)** `Armor 6`, `Pilot 4`, `Medkit 4`.<br>**(-)** Pays `50k¥` yet still needs `3` Cha (`24k¥`) for `RF 4`; strictly dominated by `Nurse MAID`. | **Obsolete** (pay `+7.5k¥` for `Nurse MAID`) |
| **`Ares Nurse MAID`** (*DA*, p. 177) | `57,500¥` / `4I` | `8 / 6 / 4 / 3` | Str 3 limbs w/ `Shock Limbs`, `Medkit 4`, `Biotech 6`, `CC 4`, **`RF 4`** | `8 / 8 / 8` (`24`) | `2` Std | **(+)** Free **`RF 4`** (`4` Cha saved!), `Shock Limbs`, `SEN 3`; shifts `2` Cha -> `SEN 9`, still leaving **`2` Cha + `3` Pwr** (`Pop-Out Small x2` + `Top Speed 3`!).<br>**(-)** High base price (`57.5k¥`, not 50% DIY); `Body 12 / Armor 6`. | **Top Tier (Covert/Medical)** |
| **`Shiawase Man-at-Arms`** (*DC*, p. 117) | `4,500¥` / `3L` | `10 / 8 / 2 / 2` | Str 3 limbs, `1× Standard Weapon Mount` | `10 / 10 / 10` (`30`) | `3` Std *(1 stock)* | **(+)** `30` slots (`0` shift tax for `SEN 9`!), **`Body 15 / Armor 8` (`23` DR)**, `3` Hardpoints, `VT 5 + Top 3 + Accel 2 + Pop-Out Small x2`, cheapest 50% DIY endgame.<br>**(-)** `40k¥` (`20k¥` DIY) `RF 4` bill; slow starter (`Top 10` w/o `Wheeled`). | **Top Tier (Apex Chassis)** |

*Non-standard Medium notes:* **`SpinGlobal SOTA Prototype Anthrodrone`** (*Whisper Nets*, p. 145: `Body 8 (12)`, `Armor 12`, `Pilot 5`, `Sensor 5`, `RF 4`, `Passive Stealth`, `HFC`, `Imp. Economy 3`, `Nano-Repair 4`, `4` cyberlimbs) is an unpriced NPC Monad chassis; **`Fire Protector`** (`de_feuerlaeufer`, `Body 8`, `Armor 8`, `Sensor 3`, `30k¥`) and **`Sony X Reliable4`** (`de_other`, `Body 6`, `Armor 6`, `13.5k¥`) are German-only releases.

---

### Table 2: Large Anthroform Drones (`Ouro`, `Percy` / Heavy Platforms)

| Chassis (Source) | Cost / Avail | `BOD / ARM / PLT / SEN` | Stock Notable Gear | Base Slots (`C/P/E`) | Hardpoints (`Std`) | Strengths & Weaknesses | Endgame `SEN 9` Verdict |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| **`Nissan Oni`** (*CRB*, p. 300; *DC*, p. 146) | `6,700¥` / `2` | `9 / 10 / 3 / 2` | `2× Std arm mounts (0 cap)`, 4-limb mode (`2×` spd) | `9 / 9 / 9` (`27`) | `3` Std *(arms use 2 Std)* | **(+)** Listed in CRB Medium table (labeled Large); **`Armor 10`** (`23` DR w/ `ISI 4`), twin Std mounts free, `6.7k¥` base.<br>**(-)** `SEN 2->9` (`10` Elec) forces `-2` Pwr shift -> only `VT 5 + 2` Pwr left (`No Top Speed 3`); 4-limb mode disables weapons. | **Viable Budget Heavy Tank** |
| **`Ares Combat MAID Troll`** (*DA*, p. 176) | `55,000¥` / `5I` | `10 / 8 / 4 / 3` | Str 5 limbs, `Milspec 1`, `Medkit 4`, `Biotech 4`, `RF 1` | `10 / 10 / 10` (`30`) | `3` Std | **(+)** Troll-scale `Body 15 / Armor 8`, `3` Hardpoints.<br>**(-)** Burns `3` Cha + `30k¥` on `RF 1->4`; strictly outclassed by `Nurse MAID Troll`. | **Obsolete** (pay `+7.5k¥` for `Nurse MAID Troll`) |
| **`Ares Nurse MAID Troll`** (*DA*, p. 177) | `62,500¥` / `5I` | `10 / 8 / 4 / 3` | Str 5 limbs w/ `Shock Limbs`, `Medkit 3`, `Biotech 6`, `CC 4`, **`RF 4`** | `10 / 10 / 10` (`30`) | `3` Std | **(+)** **`5` free Chassis slots** (`ISI 5 + RF 0`)! Shifts `4` Cha -> **`12` Pwr (`VT 5 + Top 3 + Accel 2 + HFC 2`)**, hits `SEN 9` w/ `1` Elec free, keeps `1` Cha (`Pop-Out Small x2`), `Body 15 / Armor 8`, `3` Hardpoints.<br>**(-)** `62.5k¥` base; Large (Troll) footprint. | **Best Uncompromised Endgame Spec** |
| **`Shiawase Bi-Drone Silverback`** (*DC*, p. 118; *SRMG*, p. 27) | `6,500¥` / `Special` | `10 (14) / 8 / 3 / 3` | Arms `STR 10`, `ISI 4` (base `10`), `Medevac`, `2× Valkyrie` | `10 / 10 / 10` (`30`) | `3` Std | **(+)** Only `1` Cha left to max `ISI 5` (`Body 15`); `6.5k¥` base.<br>**(-)** `3.5m` gorilla fails metahuman disguise (`RF 4`); `Special` availability. | **Niche SAR / Non-Infiltration** |

---

## 4. Endgame Slot & Nuyen Math (`Base Sensor 9` + `Vector Thrust` + `ISI Max` + `RF 4`)

All builds below include **`Small Drone Rack` (`2,000¥`, `1` Std Hardpoint)** + **split `1` Std Hardpoint $\rightarrow$ `2× Small Mounts` (`3,000¥`) + `2× Small Pop-Outs` (`3,000¥`, `1` Cha slot) + `2× Crimson Wasps` (`3,000¥`)**.

| Metric | **`Man-at-Arms`** *(Medium)* | **`Nurse MAID`** *(Medium)* | **`Silverstar`** *(Medium)* | **`Nurse MAID Troll`** *(Large)* | **`Nissan Oni`** *(Large)* |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Endgame `BOD / ARM` (DR)** | `15 / 8` (`23`) | `12 / 6` (`18`) | `12 / 4` (`16`) | `15 / 8` (`23`) | `13 / 10` (`23`) |
| **Chassis (`Base -> Final`)** | `10 -> 10` (`ISI 5 + RF 4 + Pop 1`) | `8 -> 6` (`ISI 4 + RF 0 + Pop 1`, `1` free) | `8 -> 8` (`ISI 4 + RF 3 + Pop 1`) | `10 -> 6` (`ISI 5 + RF 0 + Pop 1`) | `9 -> 9` (`ISI 4 + RF 4 + Pop 1`) |
| **Electronics (`Base -> Final`)** | `10 -> 10` (`SEN 7 + PS 1 + Cham 2`) | `8 -> 9` *(+1 from Cha)* (`SEN 6 + PS 1 + Cham 2`) | `8 -> 9` *(+1 from Pwr)* (`SEN 6 + PS 1 + Cham 2`) | `10 -> 10` (`SEN 6 + PS 1 + Cham 2`, `1` free) | `9 -> 10` *(+1 from Pwr)* (`SEN 7 + PS 1 + Cham 2`) |
| **Powertrain (`Final`)** | **`10`** (`VT 5 + Top 3 + Accel 2`) | **`8`** (`VT 5 + Top 3`)* | **`6`** (`VT 5 + 1` free) | **`12`** *(+2 from Cha)* (`VT 5 + Top 3 + Accel 2 + HFC 2`) | **`7`** (`VT 5 + Accel 2` or `HFC 2`) |
| **Free Std Hardpoints Left** | **`1`** *(after Rack + Wasps)* | **`0`** | **`0`** | **`1`** | **`0`** *(2 arms + Rack)* |
| **Core Endgame (Retail / DIY)** | `215.5k¥` / `110.0k¥` | `200.5k¥` / `129.0k¥` | `176.0k¥` / `92.5k¥` | `228.5k¥` / `145.5k¥` | `199.7k¥` / `103.2k¥` |
| **Full Listed Build (Retail / DIY)** | **`278.5k¥`** / **`143.0k¥`** | **`233.5k¥`** / **`147.0k¥`** | **`185.0k¥`** / **`98.5k¥`** | **`306.5k¥`** / **`186.0k¥`** | **`235.7k¥`** / **`122.7k¥`** *(w/ Accel 2 + Pop-Out)* |

*\*`Nurse MAID` note:* Dropping `Pop-Out Small x2` in favor of `Blow-Away Panels` (`0` slots) frees `2` Chassis slots to shift `2:1 -> +1` Powertrain (`9` Powertrain: `VT 5 + Top Speed 3 + Imp. Accel 1` or `VT 5 + Accel 2 + HFC 2`), and keeping `1` Chassis can still buy an Extra Hardpoint (`1,500¥`).
*DIY math note:* 50% DIY applies to *Double Clutch* vehicle modifications only (per *DC*, p. 120), **not** the base drone hull or the `2× Crimson Wasps` (`3,000¥`). That is why **`Man-at-Arms` (`4.5k¥` base) actually beats `Nurse MAID` (`57.5k¥` base) by `4,000¥` in full DIY endgame spending (`143k¥` vs `147k¥`) while packing higher `Body`, `Armor`, `Accel 2`, and a `3rd` Hardpoint**—whereas `Nurse MAID` wins in retail cash (`45k¥` cheaper) and Session-1 readiness.

---

## 5. Recommended Reference Builds

### Build 1: The Street-to-Apex Workhorse — `Shiawase Man-at-Arms` *(Medium)*

*Best overall Medium endgame frame (`Reiko`, `Étaín`, `Aisling`, `Cleo`) and cheapest 50%-DIY apex chassis.*

* **Phase 1 (Chargen / Session 1 — `~13.5k¥` + Toolkit):** Base `Man-at-Arms` (`4,500¥`) + `Wheeled` (`10,000¥`, Avail `3`, `2` Pwr) + `Passive Stealth` (`1,000¥`, Avail `3`, `1` Elec) + `Engineering [Ind. Mech.] Toolkit` (`500¥`) + `RF 1` (`10,000¥`, `1` Cha, Avail `2`) + worn metahuman armor + handheld weapon.
* **Phase 2 (Early Downtime — Shop + Disguise):** Buy `Engineering [Ind. Mech.] Shop` (`5,000¥`), DIY `Chameleon Coating 4` (`9,000¥`, `2` Elec), step `RF 1->4` (`15,000¥` DIY, `3` Cha) and `ISI 1–5` (`12,500¥` DIY, `5` Cha -> `Body 15`, immune to point-blank `10S` Stun Grenades).
* **Phase 3 (Endgame Loadout — `143,000¥` DIY total):**
  * `Chassis (10/10)`: `ISI 5` (`5`), `RF 4` (`4`), `Pop-Out Concealment (Small) x2` (`1`)
  * `Powertrain (10/10)`: `Vector Thrust` (`5`), `Top Speed 3` (`3`), `Imp. Accel 2` (`2`) *(drop `Wheeled` once `VT` is installed)*
  * `Electronics (10/10)`: `Enhanced Sensors 2->9` (`7`), `Passive Stealth` (`1`), `Chameleon Coating 4` (`2`)
  * `Hardpoints (3/3)`: `Small Drone Rack` (`1`), Split Std -> `2× Small Mounts` w/ `Crimson Wasps` (`1`), plus the `1×` factory `Standard Weapon Mount` free for a heavy rifle/grenade launcher (or swapped for a `Ram Plate` @ `2,500¥`).

### Build 2: The Covert Medic / Slot-Efficient Starter — `Ares Nurse MAID` *(Medium)*

*Best out-of-the-box Session-1 Medium platform (`Ouro`'s active build in [`character_build.qmd`](file:///c:/GitHub/sr6-core/characters/lab/ouro/character_build.qmd)), saving `45,000¥` retail (`4` Chassis slots) via stock `RF 4`.*

* **Phase 1 (Chargen Route A — `67,000¥`):** `Nurse MAID` (`57,500¥`, stock `RF 4`, `SEN 3`, `Shock Limbs`, `Medkit 4`) + `Wheeled` (`8,000¥`) + `Passive Stealth` (`1,000¥`) + `Engineering [Ind. Mech.] Toolkit` (`500¥`).
* **Phase 2 (Early Downtime):** Buy `Engineering Shop` (`5,000¥`), DIY `Chameleon Coating 4` (`9,000¥`), step `ISI 1–4` (`10,000¥` DIY -> `Body 12`).
* **Phase 3 (Endgame Loadout — `147,000¥` DIY total):**
  * `Chassis (6/8 -> +1 Elec)`: `ISI 4` (`4`), `Pop-Out (Small) x2` (`1`), shift `2` Chassis -> `+1` Electronics (`1` Chassis spare).
  * `Powertrain (8/8)`: `Vector Thrust` (`5`), `Top Speed 3` (`3`). *(Trade `Pop-Out` for `Blow-Away Panels` to shift `2` Cha -> `9` Pwr if prioritizing `Accel 1` or `HFC 2`).*
  * `Electronics (9/9)`: `Enhanced Sensors 3->9` (`6`), `Passive Stealth` (`1`), `Chameleon Coating 4` (`2`).
  * `Hardpoints (2/2)`: `Small Drone Rack` (`1`), Split Std -> `2× Small Mounts` w/ `Crimson Wasps` (`1`).

### Build 3: The Uncompromised Heavy Frame — `Ares Nurse MAID Troll` *(Large)*

*Best absolute endgame ceiling for characters who accept a **Large** (Troll-sized) chassis (`Ouro`, `Percy`), fitting **`HFC` + `Top Speed 3` + `Imp. Accel 2` + `SEN 9` + `Pop-Out` + `3` Hardpoints**.*

* **Endgame Loadout (`186,000¥` DIY / `306,500¥` retail):**
  * `Chassis (6/10 -> +2 Pwr)`: `ISI 5` (`5`), `RF 4` (`0` stock!), `Pop-Out (Small) x2` (`1`), shift `4` Chassis `2:1 -> +2` Powertrain.
  * `Powertrain (12/12)`: `Vector Thrust` (`5`), `Top Speed 3` (`3`), `Imp. Accel 2` (`2`), `Hydrocarbon Fuel Converter` (`2`).
  * `Electronics (9/10)`: `Enhanced Sensors 3->9` (`6`), `Passive Stealth` (`1`), `Chameleon Coating 4` (`2`) (`1` slot spare!).
  * `Hardpoints (3/3)`: `Small Drone Rack` (`1`), Split Std -> `2× Small Mounts` w/ `Crimson Wasps` (`1`), `Ram Plate` (`2,500¥` / `1`).

### Build 4: The Budget Armored Tank — `Nissan Oni` *(Large, Optional)*

*Lowest nuyen floor (`122,700¥` DIY w/ `Accel 2 + Pop-Out + 2× Wasps`) for `Armor 10` (`23` Phys DR) and `2×` factory Standard arm mounts (`6,700¥` base), ideal if speed mods (`Top Speed 3`) are secondary to armor and melee/gun arms.*

* **Endgame Loadout (`9/9/9` shifted to `9/7/10`):** `ISI 4` (`4`) + `RF 4` (`4`) + `Pop-Out` (`1`); `SEN 2->9` (`7`) + `PS` (`1`) + `Cham 4` (`2`); `Vector Thrust` (`5`) + `Imp. Accel 2` (`2`, or `HFC 2`); `2×` factory Standard arm mounts + `Small Drone Rack` (`3/3` Hardpoints).

## Your Drone Rack

This is a small drone rack and comes with its own pop-out concealment. Some strong contenders:

1. Federated Boeing Sky Commander: Comes with a satellite link and retrans relay, so fantastic for establishing overwatch over the theater. Can fit a micro/mini drone rack, so store gnats and hornets for your full sensor net. In combat you can use the focused jammer or have it establish target locks.
2. Hawker-Siddley Bats: These can take 3 crimson wasps themselves and some sensor upgrades, unlocking swarm tactics or ally sprite/agent vehicles.
3. Kwonsham Dream Genie: Super cheap way to establish presence in scenes where a militarized drone may not be permitted.
4. Vulcan Systems Utility One: Small repair drone; useful for AI/EI to 'work on themselves' (another option is to rent a drone via lifestyle or a day job).
