# Shadowrun 6e Anthroform Drone Chassis & Endgame Build Guide

> **Scope:** Comprehensive evaluation of **Medium** and **Large** anthroform drones across *SR6 Core (Seattle)*, *Double Clutch*, *Deadly Arts*, *Tarnished Star*, *Firing Squad*, *Hack & Slash*, and *SRM Guide v2.4*. Designed for Emergent and Pilot-AI riggers, excluding cyberarm replacements so factory limbs and attachments remain intact. Also relevant to technomancers (a machine sprite can inhabit these drones), conventional riggers, and general players (via upgraded Pilot ratings—note *Double Clutch* treats high-rating pilots as approaching basic AI, making them strong ally RP hooks).

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
* **Upgrading Stock Ratings:** Matching higher-rating mods pay only the **difference** in slots and nuyen (*DC*, p. 120; SRM cyberware upgrade convention applied to nuyen cost).
* **Cross-Category Shifting (`2:1`):** Two unused slots in one category permanently buy `+1` slot in another. Because every shift loses 50% efficiency, match native category capacity before shifting.
* **Hardpoints:** `floor(Unmodified Body / 3)` free Standard Hardpoints (`Body 3` gets `1` Small; `Body 4–5` gets `1` Std; `Body 6–8` gets `2` Std; `Body 9–11` gets `3` Std). `1` Standard Hardpoint splits into **`2` Small Hardpoints** (*DC*, p. 124); adding a `Standard Hardpoint` costs `1` Chassis slot and `1,500¥` (Avail `2`).

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

### E. Chargen Availability Cap & Downtime DIY Assumptions

* **Chargen Availability Cap (*CRB*, p. 66):** Max Avail `6` blocks **`Chameleon Coating 4` (`8I`)**, **`Enhanced Sensors 7–9`**, **`Vector Thrust` (`7L`)**, and **`Realistic Features 4` (`8`)** at chargen. Buy `Wheeled` (Avail `3`), `Passive Stealth` (`1,000¥`, Avail `3`), and an **`Engineering [Industrial Mechanic] Toolkit` (`500¥`, Avail `1`)** upfront.
* **Post-Chargen 50% DIY & Tooling (*DC*, p. 120; *SRMG v2.4*, pp. 19–22):** Book prices cover retail shop installs. We assume the character performs upgrades themselves post-chargen (using a Minor Downtime Action and buying hits on `Engineering + Logic [(slots × 8), (slots × hours)]`), halving mod costs (`50%` off; **not** base drone hulls or weapons). Mods `< 2` slots need a `Toolkit` (`500¥`); mods `2–5` slots require an **`Engineering Shop` (`5,000¥`, Avail `4`, `+1` dice pool)**—which favors cheaper base hulls like `Man-at-Arms` over `Nurse MAID` long term.

### F. *Tarnished Star* Heat Exemption (`Shiawase Silverstar`)

* *SRMG v2.4* (p. 73): *"Any use of gear from Tarnished Star increases the Heat modifier by +1. This effect is cumulative. This does not apply to vehicles with an availability of 6 or less."*
* *Double Clutch* (p. 127): ***"All drones are vehicles, but not all vehicles are drones."***
* **Verdict:** Because `Shiawase Silverstar` is **Availability `4`** ($\le 6$) and drones are explicitly vehicles under RAW, it qualifies for the *SRMG* exemption (**`+0` Heat**). The `Silverstar` is therefore a fully SRM-legal, Heat-free, and valid contender in this analysis.

---

## 3. Master Anthroform Drone Catalog

### Table 1: True Medium Anthroform Drones

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

### Table 2: Large Anthroform Drones

| Chassis (Source) | Cost / Avail | `BOD / ARM / PLT / SEN` | Stock Notable Gear | Base Slots (`C/P/E`) | Hardpoints (`Std`) | Strengths & Weaknesses | Endgame `SEN 9` Verdict |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| **`Nissan Oni`** (*CRB*, p. 300; *DC*, p. 146) | `6,700¥` / `2` | `9 / 10 / 3 / 2` | `2× Std arm mounts (0 cap)`, 4-limb mode (`2×` spd) | `9 / 9 / 9` (`27`) | `3` Std *(arms use 2 Std)* | **(+)** Listed in CRB Medium table (labeled Large); **`Armor 10`** (`23` DR w/ `ISI 4`), twin Std mounts free, `6.7k¥` base.<br>**(-)** `SEN 2->9` (`10` Elec) forces `-2` Pwr shift -> only `VT 5 + 2` Pwr left (`No Top Speed 3`); 4-limb mode disables weapons. | **Viable Budget Heavy Tank** |
| **`Ares Combat MAID Troll`** (*DA*, p. 176) | `55,000¥` / `5I` | `10 / 8 / 4 / 3` | Str 5 limbs, `Milspec 1`, `Medkit 4`, `Biotech 4`, `RF 1` | `10 / 10 / 10` (`30`) | `3` Std | **(+)** Troll-scale `Body 15 / Armor 8`, `3` Hardpoints.<br>**(-)** Burns `3` Cha + `30k¥` on `RF 1->4`; strictly outclassed by `Nurse MAID Troll`. | **Obsolete** (pay `+7.5k¥` for `Nurse MAID Troll`) |
| **`Ares Nurse MAID Troll`** (*DA*, p. 177) | `62,500¥` / `5I` | `10 / 8 / 4 / 3` | Str 5 limbs w/ `Shock Limbs`, `Medkit 3`, `Biotech 6`, `CC 4`, **`RF 4`** | `10 / 10 / 10` (`30`) | `3` Std | **(+)** **`5` free Chassis slots** (`ISI 5 + RF 0`)! Shifts `4` Cha -> **`12` Pwr (`VT 5 + Top 3 + Accel 2 + HFC 2`)**, hits `SEN 9` w/ `1` Elec free, keeps `1` Cha (`Pop-Out Small x2`), `Body 15 / Armor 8`, `3` Hardpoints.<br>**(-)** `62.5k¥` base; Large (Troll) footprint. | **Best Uncompromised Endgame Spec** |
| **`Shiawase Bi-Drone Silverback`** (*DC*, p. 118; *SRMG*, p. 27) | `6,500¥` / `Special` | `10 (14) / 8 / 3 / 3` | Arms `STR 10`, `ISI 4` (base `10`), `Medevac`, `2× Valkyrie` | `10 / 10 / 10` (`30`) | `3` Std | **(+)** Only `1` Cha left to max `ISI 5` (`Body 15`); `6.5k¥` base.<br>**(-)** `3.5m` gorilla fails metahuman disguise (`RF 4`); `Special` availability. | **Niche SAR / Non-Infiltration** |

---

## 4. All Viable Endgame Builds

### Methodology & Minimum Viable `Body`

* **Minimum Endgame Baseline:** `Increased Structural Integrity (½ Body)` + `Realistic Features 4` + `Secondary Propulsion: Vector Thrust` (`5` Pwr) + `Enhanced Sensors 9` (`9 - stock_SEN` Elec) + `Passive Stealth Features` (`1` Elec) + `Chameleon Coating 4` (`2` Elec) + `Small Drone Rack` (`1` Std Hardpoint).
* **Printed `Body` Floor (`Body 8`):** Under `2:1` shifting (whole pairs per donating category), **`Body 7`** is the theoretical minimum with stock `RF 4`, **`Body 8`** with `RF 0–1, SEN 3` (`Silverstar`, `Combat MAID`), and **`Body 9`** with `RF 0–1, SEN 2` (`Nissan Oni`). Since no `Body 7` frame exists in print, **`Body 8` is the hard floor** (`Body <= 6` fails mathematically).
* **Table Conventions:** Every build adds a **`Small Drone Rack`** + **split `1` Std Hardpoint $\rightarrow$ `2× Small Mounts` + `2× Small Pop-Outs` (`1` Cha) + `2× Crimson Wasps`** (`9,000¥` retail / `6,000¥` DIY), then allocates leftover slots to Powertrain speed/fuel mods. Stats show `Vector Thrust` active (*DC*, p. 137) and base `PLT / SEN 9` prior to AI scaling; Session-1 Viable assumes `Wheeled + RF 1+ + Passive Stealth + Toolkit`.

| Metric | **1. `Man-at-Arms`** | **2. `Nurse MAID`** | **3. `Silverstar`** | **4. `Nurse MAID Troll`** | **5. `Nissan Oni`** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Size Class** | Medium | Medium | Medium | Large | Large |
| **Base Chassis** | `4,500¥` (`3L`) | `57,500¥` (`4I`) | `9,000¥` (`4`) | `62,500¥` (`5I`) | `6,700¥` (`2`) |
| **Session-1 Viable (Ret / DIY)** | `26,000¥` / `15,500¥` | `67,000¥` / `62,500¥` | `18,500¥` / `14,000¥` | `74,000¥` / `68,500¥` | `26,200¥` / `16,700¥` |
| **Core Required (Ret / DIY)** | `215.5k¥` / `110.0k¥` | `200.5k¥` / `129.0k¥` | `176.0k¥` / `92.5k¥` | `228.5k¥` / `145.5k¥` | `199.7k¥` / `103.2k¥` |
| **All-In Endgame (Ret / DIY)** | **`278,500¥` / `143,000¥`** | **`233,500¥` / `147,000¥`** | **`185,000¥` / `98,500¥`** | **`306,500¥` / `186,000¥`** | **`235,700¥` / `122,700¥`** |
| **Final `BOD / ARM` (`DR`)** | `15 / 8` (`23`) | `12 / 6` (`18`) | `12 / 4` (`16`) | `15 / 8` (`23`) | `13 / 10` (`23`) |
| **Final `HAN / ACC / SPD / TOP`** | `4/4` / `41` / `50` / `480` | `4/4` / `25` / `50` / `480` | `4/4` / `25` / `50` / `300` | `4/4` / `41` / `50` / `480` | `4/4` / `41` / `50` / `300` |
| **Final `PLT / SEN` (Base)** | `2` / `9` | `4` / `9` | `3` / `9` | `4` / `9` | `3` / `9` |
| **Chassis (`Base -> Final`)** | `10 -> 10` (`ISI 5 + RF 4 + Pop 1`) | `8 -> 6` (`ISI 4 + RF 0 + Pop 1`, `1` free) | `8 -> 8` (`ISI 4 + RF 3 + Pop 1`) | `10 -> 6` (`ISI 5 + RF 0 + Pop 1`) | `9 -> 9` (`ISI 4 + RF 4 + Pop 1`) |
| **Electronics (`Base -> Final`)** | `10 -> 10` (`SEN 7 + PS 1 + Cham 2`) | `8 -> 9` *(+1 Cha)* (`SEN 6 + PS 1 + Cham 2`) | `8 -> 9` *(+1 Pwr)* (`SEN 6 + PS 1 + Cham 2`) | `10 -> 10` (`SEN 6 + PS 1 + Cham 2`, `1` free) | `9 -> 10` *(+1 Pwr)* (`SEN 7 + PS 1 + Cham 2`) |
| **Powertrain (`Final`)** | `10` (`VT 5 + Top 3 + Accel 2`) | `8` (`VT 5 + Top 3`)* | `6` (`VT 5 + 1` free) | `12` *(+2 Cha)* (`VT 5 + Top 3 + Accel 2 + HFC 2`) | `7` (`VT 5 + Accel 2` or `HFC 2`) |
| **Hardpoints** | `Rack + 2× Wasps + 1 Std Free` | `Rack + 2× Wasps` (`0` free) | `Rack + 2× Wasps` (`0` free) | `Rack + 2× Wasps + 1 Std Free` | `Rack + 2× Arm Std Mounts` (`0` free) |
| **Key Differences** | Medium DIY apex | Best Session-1 Medium | Cheapest Medium DIY | Uncompromised Heavy | Budget Armor 10 tank |

*\*`Nurse MAID` option:* Swapping `Pop-Out` (`1` Cha) for `Blow-Away Panels` (`0` slots) frees `2` Chassis slots to shift `2:1 -> +1` Powertrain (`9` Pwr: `VT 5 + Top 3 + Accel 1`, or `VT 5 + Accel 2 + HFC 2`), and keeping `1` Chassis can buy an Extra Hardpoint (`1,500¥`).

### Build 1: `Shiawase Man-at-Arms` — *Medium DIY Apex (`140 cm`)*

* Best all-around Medium endgame chassis at 1.4 to 1.5m tall.
* Avoids any `2:1` slot-shift tax and beats `Nurse MAID` in full-DIY endgame spending because 50% DIY discounts apply to its heavy `RF 4` and `ISI 5` mods rather than a costly base frame.
* **Progression:** Start with `Wheeled`, `Passive Stealth`, `RF 1`, and an `Engineering Toolkit` (plus a handheld gun), buy an `Engineering Shop` early to DIY `Chameleon 4` and step `RF 1->4` and `ISI 1–5`, then drop `Wheeled` once `Vector Thrust` lands. Keep the stock `Standard Weapon Mount` free for a heavy rifle/grenade launcher, or swap it to a `Ram Plate` (`+15` Ram AR, half return damage).

### Build 2: `Ares Nurse MAID` — *Session-1 Medium Benchmark*

* Best out-of-the-box Medium platform: factory `RF 4`, `Shock Limbs`, `Medkit 4`, and `Biotech 6` cover social scenes and medical support from Session 1 while costing noticeably less in retail shop pricing than `Man-at-Arms`.
* **Progression & Trade-Offs:** Starts cleanly out of the box (`Wheeled + Passive Stealth + Toolkit`), then adds an `Engineering Shop` for `Chameleon 4` and stepped `ISI`. At endgame it shifts saved Chassis slots to cover `SEN 9`, retaining `Top Speed 3` and `Pop-Out Wasps` at the cost of `Imp. Accel 2` and a `3rd` hardpoint.

### Build 3: `Shiawase Silverstar` — *Cheapest Medium Endgame Floor*

* Lowest nuyen floor for a legal Medium endgame drone (`+0` Heat under *DC* p. 127's vehicle exemption) and the cheapest Session-1 starter (`RF 1`, `SEN 3`, `PLT 3`, and `Top Speed 30` out of the box with no license required).
* **Progression & Trade-Offs:** Upgrades smoothly from `Wheeled + Passive Stealth + Toolkit` to `Chameleon 4`, `RF 1->4`, and `ISI`. However, spending Chassis slots on `RF 4` forces its `SEN 9` shift out of Powertrain, leaving only `1` spare Powertrain slot (`Improved Handling 1` or `Suncell`, with no room for `Top Speed 3` or `Imp. Accel 2`) alongside lighter armor. *(If `RF 4` is ever dropped, `Top Speed 3` fits immediately.)*

### Build 4: `Ares Nurse MAID Troll` — *Uncompromised Heavy Ceiling*

Note: Average Troll height is 2.5m (8'2") with a range from 2.1m (7'0") to 2.9m (9'6").

* Top pick for characters accepting a Large chassis: pairs Troll-scale slot capacity with factory `RF 4` and `SEN 3`, eliminating the Electronics shift and freeing enough Chassis slots to add `HFC 2` on top.
* **Trade-Offs:** Retains `Shock Limbs`, `Medkit 3`, a `3rd` Hardpoint (`Ram Plate` or extra mount), and `1` spare Electronics slot—trading only its Troll-sized footprint and higher upfront hull price.

### Build 5: `Nissan Oni` — *Budget Armored Tank (Optional)*

* Lowest all-in DIY price while hitting heavy `Armor 10` and supplying twin factory `Standard` cyberarm weapon mounts (`0` capacity, though 4-limb mode disables weapons).
* **Trade-Offs:** Shifting Powertrain slots to cover `SEN 9` caps Powertrain at `Imp. Accel 2` (or `HFC 2`) without `Top Speed 3`, leaves `1` Chassis slot for `Pop-Out`, and consumes its `3rd` Hardpoint on the `Small Drone Rack`.

## 5. Your Drone Rack

This uses a `Small Drone Rack` (`2,000¥`, `1` Std Hardpoint) enclosed behind a factory hatch (no Pop-Out concealment needed). Strong contenders:

1. Federated Boeing Sky Commander: Comes with a satellite link and retrans relay, so fantastic for establishing overwatch over the theater. Can fit a micro/mini drone rack, so store gnats and hornets for your full sensor net. In combat you can use the focused jammer or have it establish target locks.
2. Hawker-Siddley Bats: These can take 3 crimson wasps themselves and some sensor upgrades, unlocking swarm tactics or ally sprite/agent vehicles.
3. Kwonsham Dream Genie: Super cheap way to establish presence in scenes where a militarized drone may not be permitted.
4. Vulcan Systems Utility One: Small repair drone; useful for AI/EI to 'work on themselves' (another option is to rent a drone via lifestyle or a day job).
