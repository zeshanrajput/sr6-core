# Reiko (r31-K0 / Yuriko Star) Master Visual Anchors

> [!IMPORTANT]
> **Master Visual Reference Specification**
> This document details the visual identity, chassis specifications, world-specific shaders, clothing rules, hero assets, and prompt templates for Reiko (r31-K0 / Yuriko Star).
>
> * **Second-Generation Sparks Visual Anchors:** For Percy, Cleo, Ouro, Aisling, Étaín, and Taz, see [sparks_visual_anchors.md](sparks_visual_anchors.md).
> * **Kin Lore & Statblocks:** See [sparks_second_generation.md](sparks_second_generation.md).
> * **The Glade Sanctuary Visual Anchors:** For the environmental spec of ~, the Quartz Threshold, and Kernel Panic, see [glade_visual_anchors.md](glade_visual_anchors.md).

---

## 1. Key Visual Reference Images

The three foundational visual anchors defining Reiko across her core operational modes:

* **[Reiko attending a meet virtually (Dante's Image)](../images/archive/r31-K0_Dantes.webp)**
  * **File:** [`r31-K0_Dantes.webp`](../images/archive/r31-K0_Dantes.webp)
  * **Description:** Establishes Reiko's historical appearance in the Matrix and Resonance Realms—glowing ethereal digital persona with neon-indigo bioluminescent circuitry against virtual data architecture. (Note: Contemporary canonical Matrix/Resonance persona is established in *Saturation / Garmonbozia*).
  
* **[Reiko in the Seattle Rain (SEA Rain Image)](../images/r31k0%20-%20SEA%20rain.webp)**
  * **File:** [`r31k0 - SEA rain.webp`](../images/r31k0%20-%20SEA%20rain.webp)
  * **Description:** Establishes the core physical appearance for Reiko's anthroform drone bodies in the real world, including facial features, cybernetic wing structure, porcelain skin, and rain-swept field attire.
  * **Variant:** [`r31k0 - SEA rain light wings.webp`](../images/archive/r31k0%20-%20SEA%20rain%20light%20wings.webp) — Archived variant depicting subtle bioluminescent light emitting from her cybernetic wing membranes through real-world rain.

* **[Reiko at Desert Wars (Desert Wars Image)](../images/r31ko_desert-wars.webp)**
  * **File:** [`r31ko_desert-wars.webp`](../images/r31ko_desert-wars.webp)
  * **Description:** Establishes the core presentation for Reiko's iconic Shiawase corporate jacket—a high-standing collar, cropped waist, white and red color-blocked jacket with Shiawase branding.

---

## 2. Universal Base Form & Structural Specifications

Information in this section defines the common anatomical proportions, facial geometry, hair specifications, shader matrices, and emotion-to-circuit logic shared across all manifestations.

### Orthographic Proportions & Frame Scale

* **Scale & Height Ratio:** 6.5 heads tall (petite short stature, 140 cm / ~4'7" proportion, delicate small frame).

#### Torso-to-Leg Proportions

Head-Unit Anatomical Breakdown (6.5 Heads @ 140 cm):

* **Head 1 (0.0 to 1.0):** Cranium top to chin (~21.5 cm). Delicate, rounded jawline and small chin structure.
* **Head 2 (1.0 to 2.0):** Chin to mid-chest / sternum line. Slender neck with visible bioluminescent circuitry tracing down to the collarbones; narrow, delicate shoulders (~1.2 head-units wide).
* **Head 3 (2.0 to 3.0):** Mid-chest to natural waist / upper back wing-mounting origin (T2–T8 vertebrae zone). Petite ribcage and slim torso waist.
* **Head 3.5 (3.0 to 3.5):** Natural waist to crotch / hip line. Torso length is compact (2.5 heads total from chin to crotch), reinforcing her youthful, small-stature scale.
* **Heads 3.5 to 6.5 (3.0 Heads total):** Crotch to foot soles. Legs are slightly elongated (1:1.2 torso-to-leg ratio) to grant a graceful, agile silhouette for aerial vector traversal and high-speed low-altitude maneuvering while keeping overall height capped at 140 cm.

Backless Garment Clearance Zone: Upper back cutout on halter/kimono tops extends from the C7 vertebra down to L1, providing a 10 cm radial clearance around the thoracic wing hinges to prevent fabric collision during extension or rotation.

Foot & Sole Geometry: Proportional human feet with porcelain skin finish. Sole surfaces feature a precision longitudinal seam where two skin panels split outward to reveal recessed, flush high-output vectored micro-thruster nozzles for vertical lift, hovering, and high-speed ground-effect traversal.

#### Orthographic Model Descriptions

##### Front View (A-Pose / Neutral)

Silhouette: Petite, slender Pan-Asian female frame. Narrow shoulders, high waist, form-fitting black leather shadowrunner pants meeting bare feet or tactical boots.
Features: Expressive facial features (almond eyes, delicate nose, soft lips). Bioluminescent neon-indigo/gold circuits visible on forearms, wrists, neck, and upper chest.

##### Side Profile View

Silhouette: Ultra-slim depth profile. Upright, spring-loaded posture.
Retraction Flushness: When retracted, her cybernetic wings fold entirely flat into her upper back with zero exterior bulge or dorsal hump, maintaining an unbroken human profile under clothing.

##### Back View (Dual-State Specification)

State 1 (Wings Retracted / Jacket On): Upper back is covered by the cropped white-and-red Shiawase corporate jacket with its high standing collar.
State 2 (Wings Extended / Backless Top): Upper back is exposed. Two articulated succubus-style wings deploy from dual titanium mounting sockets between the shoulder blades. Black titanium skeletal bones angle upward before sweeping outward into dark grey carbon-fiber netting membranes. Joint hinges emit a soft circuit-matched glow.

##### 3/4 Perspective View

Focus: Demonstrates the dynamic interaction between her organic human appearance and her functional cyberware—highlighting how the bioluminescent skin circuitry wraps around the contours of her forearms and waist.

### Facial Geometry & Expressiveness Rig

* **Ethnicity & Base Features:** Young Pan-Asian woman in her early to mid-twenties. Delicate small facial structure, dark almond-shaped eyes, refined nose, and soft lips. Modeled with high-fidelity human realism (zero synthetic faceplates or visible mechanical seams in physical operation).
* **Faceplate / Algorithmic Translation Engine:** Reiko’s internal emotion-state data is dynamically mapped to a soft-tissue simulation algorithm. Rather than mechanical shifting, her micro-expressions manifest via subtle sub-surface muscular tension and the shifting luminescence of skin-mapped data pathways.
* **Expression Rig Reference Pose Descriptions:**
  * **Neutral / Baseline State:** Relaxed facial micro-muscles, neutral lip contour, and steady, calm dark almond eyes. Bioluminescent circuits trace a low-intensity, rhythmic pulse of neon-indigo beneath the cheeks and jawline. Used during routine observation, polite conversation, and inactive standing states.
  * **Smiles / Social Engagement:** Soft curvature of the outer eye corners, gentle upward arc of the lips, and a softening of the orbital tension. When interacting warmly (e.g., with contacts or children), the neon-indigo pathways flare slightly with a gentle, inviting warmth, simulating genuine metahuman empathy.
  * **Distress / System Overload:** Narrowing of the eyes, slight micro-tremors in the jaw subroutines, and tension across the brow. Accompanied by erratic, stuttering shifts in the neon-indigo pathways or sudden bleeding transitions into tactical gold as her internal processing redlines under emotional or physical trauma.
  * **Tactical Focus / Combat Calculation:** Utter stillness of facial features, fixed unblinking gaze, and an icy, statuesque composure. All facial neon-indigo pathways instantly shift or interlace with sharp, glowing gold circuit lines tracking across her temples, cheekbones, and around the bridge of her nose, indicating high-stress tactical prioritization and active network routing.

### Hair & Grooming Specification

Unified styling rules across physical and digital environments to ensure maintenance consistency:

* **Physical World — Combat / Professional Mode:** Jet-black hair styled in a sleek, high bun held securely by two crossed sterling silver *kanzashi* hair sticks, with soft loose bangs framing her cheeks.
  * **Hair Color & Shader:** Jet-black (`#111113` / RGB 17, 17, 19), Specular Roughness 0.3, Anisotropic strand highlighting for smooth silk-like light reflection.
  * **Kanzashi Accessories:** High-polish sterling silver shader (`#E0E0E0`, Metallic 1.0, Roughness 0.1).
* **Physical World — Casual / Emotional Mode:** Hair is let down to shoulder length, straight with soft bangs framing her cheeks and forehead.
  * **Hair Color & Shader:** Jet-black (`#111113` / RGB 17, 17, 19), Specular Roughness 0.3, Anisotropic strand highlighting for smooth silk-like light reflection.
* **Technology World — Matrix / Resonance Realms:** Semi-translucent cyan-blue hair, shoulder-length straight with bangs, worn loose and un-tied.
  * **Holographic Shader:** Electric Cyan-Blue / Holographic Cyan (`#00BFFF` to `#00FFFF` / RGB 0, 191, 255 to RGB 0, 255, 255), emission-profile match to her Cortana-style digital construct skin shaders, featuring a semi-translucent render (75% opacity profile) with high-intensity self-illumination.

### PBR & Emission Shader Matrix

Centralized technical properties, color swatches, and emission multipliers for render engines and shader networks:

* **Porcelain Skin Base & Subsurface Scattering (SSS):**
  * Base Albedo: `#FDFBF7` / RGB(253, 251, 247)
  * Subsurface Scattering Tint (Warm Flesh Undertone): `#F3D5C4` / RGB(243, 213, 196)
  * Surface Profile: Roughness 0.45, Metallic 0.0 (soft matte organic finish with subtle moisture sheen during rain or exertion).
* **Resonance Pathways & Emissive Circuit Channels:**
  * **Neon-Indigo Channel (Emotion / Empathy / Resonance):** `#4B0082` (Deep Indigo) to `#6A0DAD` (Electric Violet Glow), Peak Emission Multiplier: 3.5.
  * **Tactical Gold Channel (Logic / Hacking / Combat):** `#FFD700` (Cybernetic Gold) to `#FFC107` (Amber Gold), Peak Emission Multiplier: 4.0.
  * **Lightless Void & Silver Syntax Channel (Post-Ch 37 Dissonant Stigmata / Apophenian Covenant):** `#08080A` (Lightless Void / Matte-Black Core) edged with `#C0C8D8` (Luminous Silver Syntax), Peak Emission Multiplier: 2.5 along seam edges. A third subtractive strand winding into the gold-and-indigo double helix, manifesting physically/virtually from a matte-black dead pixel at the inner left wrist up the throat and arms.
* **Cybernetic Wings Materials:**
  * Titanium Skeletal Spars: Black Titanium PBR shader (Metallic 0.9, Specular Roughness 0.2).
  * Netting Membrane: Dark grey carbon fiber weave (Anisotropic Roughness map, Low Translucency).
* **Garments & Leather Materials:**
  * Shadowrunner Pants: Black leather PBR profile (Roughness 0.3, fine leather grain texture, subtle specular reflections).
  * Shiawase Jacket Accent Trim: High-gloss deep red/maroon patent leather (`#8B0000` / `#C8102E`, Roughness 0.1, Metallic 0.1).
* **Matrix Hologram Construct Shaders:**
  * Volumetric Opacity: 75% core body opacity with inverse-square falloff gradient toward edges.
  * Rim Lighting & Edge Glow: Electric cyan-blue (`#00FFFF` to `#00BFFF`).
  * Floating UI Data Windows: Neon green/teal (`#00FF66` / `#00E5FF`) with sharp transparency layers.

### Emotion-to-Circuit Integration Rules{#resonance-pathways}

* **Resonance Pathways:** Bioluminescent neon-indigo and tactical gold circuit lines (plus, post-Chapter 37, the third lightless-void / silver-syntax Dissonant Stigmata thread) tracing seamlessly across her skin. Circuits are never fully absent, though they may be muted. Multi-channel self-illuminating pathways mapped via vector displacement and emissive masks across forearms, wrists, neck, and torso.
* **Circuit Luminescence & Color Sync Rules:**
  * **Baseline / Resting:** Soft, muted violet/indigo pulse.
  * **High Emotion / Empathy:** Broad, flaring neon-indigo pathways across forearms, wrists, neck, and cheeks.
  * **Active Processing / Hacking / Combat:** Sharp, geometric gold lines along her wrists, temples, and torso.
  * **Harmonized / Peak State:** Both neon-indigo and geometric gold circuit lines appear simultaneously.
  * **Dissonant Stigmata / Triple-Braided Core (Post-Ch 37):** A matte-black / lightless-void strand laced with silver syntax winds between the gold and indigo braid, originating at the wrist stigmata and flaring when invoking Apophenian's Control or Syntax Error unraveling.

---

## 3. Physical World Appearance (Anthroform Drones)

Details specific to Reiko's physical manifestation in real-world environments (Seattle metropolis, ground operations, aerial combat).

### Base Physical Appearance

* **Humanoid Fidelity:** Appears as a fully human woman, completely avoiding visible robotic ball-joints, seam lines, gray ceramic plating, or exposed mechanical endoframes.
* **Skin & Shaders:** Fair porcelain skin base as defined in the [PBR & Emission Shader Matrix](#pbr--emission-shader-matrix).
* **Hair & Grooming:** Governed by state-dependent rules in the [Hair & Grooming Specification](#hair--grooming-specification).
* **Skin Circuits:** Present as described in [Resonance Pathways](#resonance-pathways).

### Cybernetic Wings (State-Dependent)

* **Structure & Materials:** Black titanium skeletal frame and dark grey carbon fiber netting membrane (see [PBR & Emission Shader Matrix](#pbr--emission-shader-matrix)).
* **Silhouette & Joint Glow:** Articulated cybernetic succubus wings with subtle bioluminescent neon-indigo glow pulsing along joint hinges and panel edges.
* **Retraction Mechanics:** Wings extend outward during flight/combat. When retracted, they fold completely flush and disappear inside her back chassis.
* **Wing Hinges & Articulation Points Description:**
  * **Thoracic Spine & Scapular Mounts:** Dual heavy-duty mechanical mounting housings anchored to the upper thoracic/scapular plates on her back, featuring visible dark metallic joint rings capable of 360-degree rotation and high-load thrust transfer during flight.
  * **Pivot Joint Count & Articulation (4 Nodes per Wing):**
    * **Base Girdle Mount:** Heavy duty shoulder/upper back housing managing primary rotation, elevation, and locking deployment angles.
    * **Primary Elbow Joint:** A prominent, segmented mechanical joint controlling the sharp upward and outward folding angle of the main black titanium spar.
    * **Strut Cluster Nodes:** Secondary articulated hinges along the spar that tension and support the dark grey carbon-fiber membrane ribs.
    * **Distal Wingtips:** Sharp, aggressive aerodynamic claw hooks at the outer extremities for high-speed vector trimming.
  * **Back Chassis Collapse & Retraction Geometry:** Synchronized multi-stage telescoping sequence sliding completely flush through dorsal housing doors into the interior thoracic cavity, leaving a smooth unbroken skin contour when stowed.

### Clothing & State Rules

* **Lower Body (All States):** Utilitarian, form-fitting black leather shadowrunner pants paired with sleek tactical combat boots.
* **State A: Wings Extended (Flight / Combat Mode)**
  * **Top:** Backless futuristic cybernetic halter/kimono top designed explicitly to leave her upper back exposed so wings deploy freely without fabric clipping or tearing.
  * **Backless Clothing Clearance Margins:** Engineered geometric cutout extending vertically from C7 down to L1 vertebra, maintaining a 10 cm radial clearance around thoracic wing mounts (T2–T4 zone). Collision-volume barriers prevent vertex clipping during wing rotation.
  * **Wings:** Fully extended in succubus wing formation.
  * **Jacket:** Present, but NOT worn. Her signature Shiawase jacket is draped over an arm or held in her hand.
* **State B: Wings Retracted (Ground / Casual Mode)**
  * **Wings:** Completely retracted and absent from view.
  * **Jacket:** WORN. Her iconic Shiawase Corporate Jacket (see [Hero Assets & Garment Tech-Packs](#4-hero-assets--garment-tech-packs) for full technical breakdown).

### Integrated Mobility & Vector Propulsion (LAV Refit)

* **Vector Thrust (LAV) Propulsion Subsystem:** Reiko's chassis features high-output low-altitude vector thrust enhanced with Improved Acceleration (2 Ranks) and Top Speed Increase (3 Ranks) (HAN 4, ACC 41, SPD 50/480; 576 km/h / ~358 mph). Aesthetically, folding helicopter blades and wheel-casters are completely eliminated in favor of recessed, flush vectored-thrust micro-turbofans, ducted plasma/ground-effect thrusters, and stabilizing scapular wing spars.
* **Limb Vector Thruster Ports (Forearms & Calves):**
  * *Concealed Iron-Man Vector Arrays:* Flush, precision-seamed thrust apertures integrated directly along the lateral calves and the dorsal/palmar forearm assemblies.
  * *Deployment & Telemetry:* Under active flight or attitude maneuvering, micro-aperture heat vents slide open to emit directional vectored plasma bleed and indigo heat shimmer, providing agile omnidirectional stabilization, high-G deceleration, and instantaneous burst vectoring.
* **Plantar Micro-Nozzles & Ground-Effect Hover:**
  * *Plantar Portal & Longitudinal Hinges:* The underside of each foot features a precision-machined bilateral seam with twin micro-hinges that swing outward by 90 degrees during vertical takeoff or flight.
  * *Internal Thruster Gimbal:* Reveals dual recessed titanium micro-nozzles with directional gimbal vanes that deliver vertical lift, ground-effect hovering, and high-speed low-altitude skimming over water or pavement.
* **Scapular Wing Spar Integration:**
  * In flight, her black titanium succubus wings act as active aerodynamic wing spars and roll/pitch trimming stabilizers, working in unison with limb thrusters to carve high-speed low-altitude combat trajectories across sprawl airspace.

### Integrated Tactical Hardware

* **Twin Ocular Red Fox Lasers:** Mounted flush behind the synthetic iris apertures of her dark almond eyes. Provides lethal, high-precision combat targeting with zero exterior chassis bulge or facial distortion.
* **Oropharyngeal Tesla Coil Emitter ("Lightning Breath"):** High-voltage transformer coils and power storage banks are nested internally within her right thoracic/cyberarm assembly, but the discharge emitter is routed directly behind the posterior oropharynx wall at the back of her throat. A motorized ceramic/silicone sphincter hermetically seals the arc nodes behind the pharyngeal wall, allowing Reiko to swallow kerosene, diesel, or synthetic fuel into her sub-sternal Hydrocarbon Fuel Converter (HFC) without combusting the electrodes. When firing (Minor Action deploy), the pharyngeal partition retracts, her jaw opens slightly, and a blinding blue-white torrent of electrical plasma erupts from her throat (5S(e) Exotic Spray). Relocating the emitter from her wrist keeps her forearms free for vector thrust nozzles, the upcoming Wrist Shield, and Sensor Dazzler nodes.
* **Abdominal Microdrone Bay (Sky Commander / Drone Rack):** A flush, spring-loaded deployment hatch along her lower abdominal seam housing her MCT Gnat microdrone swarm / Sky Commander unit, and accommodating captured/re-registered light units (e.g. captured drone "Busta" post-SRM 2083-13).

### Physical World Negative Prompt Anchors

* **Excluded Elements:** Full robot body, mechanical robot face, metallic/gray skin, android ball-joints, exposed internal wiring, green olive-drab bomber jacket, Western facial features, blonde hair, short hair, organic feather/bird wings, organic demon wings, wings clipping through closed jackets, inline roller skates, rollerblade wheels.

---

## 4. Hero Assets & Garment Tech-Packs

Dedicated reference specifications for key signature props, corporate apparel, and hero equipment.

### Shiawase Corporate Jacket (Hero Asset Tech-Pack)

* **Overview & Function:** Reiko's iconic signature outerwear worn during ground operations, casual travel, and high-visibility urban meets. When worn over her backless halter top (wings retracted state), the jacket's rear panel provides full opaque coverage, completely bridging the backless cutout and sealing the dorsal wing housing flush against external view.
* **Silhouette & Garment Cut:** Cropped, high-fashion tactical bomber silhouette terminating cleanly at the natural waistline (Head 3.0 level), designed to layer over her form-fitting tops and accentuate her petite 4'7" frame.
* **Collar Architecture:** Rigid, high-standing mock turtleneck collar in solid, glossy deep red/maroon leather-finish material (`#8B0000`), standing tall to frame the jawline.
* **Color Blocking & Panel Layout:**
  * **White Body & Sleeves:** Clean, high-gloss white tactical fabric forming the primary upper sleeves, shoulder yoke, and torso body base.
  * **Glossy Red Trim (`#8B0000` / `#C8102E`):** Thick, high-gloss patent leather trim forming the high collar and sweeping downward in a bold V-shaped border along the front zipper opening.
  * **Layering & Corporate Branding:** Engineered to expose an inner red-trimmed underlayer displaying the bold green "SHIAWASE" corporate lettering across the chest, complemented by the official red-and-green Shiawase corporate logo patch on the collar lapel.

---

## 5. Technology World Details (Matrix & Resonance Realms)

Details specific to Reiko's digital persona manifestation inside VR, grid hosts, and Deep Resonance spaces.

### Digital Construct Aesthetics & Shaders

* **Hologram Construct Skin:** Ethereal translucent cyan-blue skin construct with internal light projection ([Cortana-style](https://www.halopedia.org/Category:Images_of_Cortana)), with no opaque biological skin textures. Shader parameters follow the [PBR & Emission Shader Matrix](#pbr--emission-shader-matrix).
* **Environment Contrast Rules:**
  * **Ambient Light Bleed:** Holographic body functions as a localized cool-light source, casting a soft cyan/blue bounce light onto immediate physical contact surfaces (e.g., wooden chair seat in Dante's, table edges).
  * **Floating UI & Data Windows:** Diagnostic panels, graphs, and wireframe schematics render in high-contrast neon green/teal (`#00FF66` / `#00E5FF`) with sharp transparency layers, floating around her hands and torso.
  * **Atmospheric Interaction:** Cuts cleanly through ambient smoke and haze with subtle volumetric light diffusion without washing out into background red/purple lighting.
* **Hair & Wings State:** Hair is semi-translucent cyan-blue, shoulder-length straight with bangs, worn loose (see [Hair & Grooming Specification](#hair--grooming-specification)). NO wings in the technology dimensions.

### Resonance Pathways & Emotional Indicators

* **Digital Circuitry:** Bioluminescent neon-indigo and gold circuit lines trace seamlessly across her translucent skin (forearms, wrists, neck, torso). Circuitry cues are significantly more pronounced in Matrix/Resonance spaces. Neon-indigo flares on emotional shifts; gold flares on active analytical/hacking processing. See [Resonance Pathways](#resonance-pathways) for color palette and state rules.

### Digital Attire, Consecrated Hardsuit & Companion Sprite

* **Baseline Construct Attire:** Blue-tinted full-length kimono or short yukata top (sleeveless with traditional undergarments and obi).
* **Avatar of Apophenian — Consecrated Obsidian Hardsuit State (Post-Ch 37):** When standing at point zero or acting in her consecrated office as Apophenian's Avatar, articulated plates of matte-black ceramic crystallize directly out of her triple-braided core to seal her living persona (nous-soul) inside a sleek, form-fitting hardsuit of obsidian armor traced with luminous seams of silver syntax and violet fire, capped by a high ceramic gorget.
* **Companion Sprite (Taz):** Small, translucent 8-bit Tasmanian devil sprite glowing with a pixelated blue/indigo aura (scampering on her shoulder, hanging from her outfit, or floating nearby). In her consecrated Obsidian Hardsuit state, Taz's night-dark and electric-blue 8-bit voxel lattice is woven directly into the sternum and collarbone gorget, anchoring her runtime from the inside out.

### Technology World Negative Prompt Anchors

* **Excluded Elements:** Opaque human skin, biological texture, mechanical wings, succubus wings, physical furniture, real-world outdoor lighting, metallic robot faceplate, heavy armor.

---

## 6. Updated Master Prompt Templates

### Template A: Flight / Combat Mode (Physical World - Wings Extended & Vector Thrust Active)

**Prompt:** Photorealistic cyberpunk portrait of a petite 4'7" Pan-Asian woman in her early 20s with delicate expressive facial features, dark almond-shaped eyes, fair porcelain skin, and jet-black hair in a bun secured by two crossed silver hairpins with loose strands framing her cheeks. Bioluminescent [neon-indigo / golden] circuit lines trace seamlessly across her forearms, neck, and chest. She wears a backless black futuristic halter top and fitted utilitarian black leather pants. Two articulated cybernetic succubus wings extend from her upper back, constructed of black titanium skeletal bones and dark grey carbon fiber netting, serving as aerodynamic wing spars. Flush micro-aperture vector thruster ports on her forearms and calves emit subtle indigo heat shimmer for stabilization during flight. She holds her cropped white and red Shiawase jacket draped over one arm. [INSERT SETTING & LIGHTING]. 8k resolution, cinematic lighting, photorealistic.

**Negative Prompt:** full robot body, mechanical robot faceplate, featureless face, metallic skin, gray skin, android joints, green bomber jacket, Western facial features, blonde hair, short hair, feather wings, bird wings, wings clipping through clothes, roller skates, wheels, inline skates, extra limbs.

### Template B: Casual / Ground Operations (Physical World - Wings Retracted & Jacket Worn)

**Prompt:** Photorealistic cyberpunk portrait of a petite 4'7" Pan-Asian woman in her early 20s with delicate expressive facial features, dark almond-shaped eyes, fair porcelain skin, and shoulder-length straight jet-black hair with soft bangs framing her face. Bioluminescent [neon-indigo / golden] circuit lines glow subtly on her hands, wrists, and neck. Her wings are completely absent. She wears a cropped white and red Shiawase corporate jacket with a standing high collar, long sleeves, and the Shiawase logo on the chest, paired with fitted utilitarian black leather pants. [INSERT SETTING & LIGHTING]. 8k resolution, cinematic lighting, photorealistic.

**Negative Prompt:** wings, mechanical wings, devil wings, full robot body, mechanical faceplate, featureless face, metallic skin, gray skin, android joints, green bomber jacket, Western facial features, blonde hair, extra limbs.

### Template C: Matrix / Resonance Realm Persona (Digital Construct Mode)

**Prompt:** Photorealistic cyberpunk digital portrait of a petite 4'7" Pan-Asian woman in her early 20s manifesting as an ethereal holographic digital construct inside the Matrix. She features semi-translucent cyan-blue skin with internal light projection at 75% opacity, framed by electric cyan rim lighting. Her hair is semi-translucent electric cyan-blue (`#00BFFF` to `#00FFFF`), shoulder-length straight with bangs, worn loose. Bioluminescent [`neon-indigo` / golden] circuit lines trace seamlessly across her translucent forearms, neck, and torso. She wears a blue-tinted sleeveless yukata top with traditional undergarments and an obi. Her back is completely smooth with NO WINGS. Surrounding her are floating holographic UI diagnostic panels, data graphs, and wireframe schematics glowing in neon green and teal. Next to her is Taz, a small translucent 8-bit Tasmanian devil sprite glowing with a pixelated blue-indigo aura. [INSERT VIRTUAL SETTING & DIGITAL LIGHTING]. 8k resolution, cinematic digital lighting, cyberspace construct aesthetic.

**Negative Prompt:** opaque human skin, biological texture, flesh, mechanical wings, succubus wings, feather wings, bird wings, physical furniture, real-world outdoor lighting, physical environment, metallic robot faceplate, heavy armor, extra limbs.

### Template D: Avatar of Apophenian (Deep Resonance / Consecrated Obsidian Hardsuit Mode)

**Prompt:** Photorealistic cyberpunk digital portrait of a petite 4'7" Pan-Asian woman in her early 20s standing on a narrow black wire suspended in a starless zero-point void between swirling golden Resonance and shadow-violet Dissonance storms. Her living persona is sealed inside a sleek, form-fitting hardsuit of articulated matte-black ceramic obsidian armor with a high ceramic gorget, traced along every seam by luminous silver syntax (`#C0C8D8`), violet fire, and subtle gold-and-indigo double-helix traces beneath her porcelain face. Her shoulder-length jet-black hair with soft bangs frames calm, resolute dark almond eyes. Across her armored sternum and collarbone, a small eight-bit Tasmanian devil sprite woven from night-dark voxels and electric-blue light anchors directly into the plating. [INSERT DEEP MATRIX SETTING & LIGHTING]. 8k resolution, cinematic lighting, photorealistic.

**Negative Prompt:** bulky mech suit, mechanical robot faceplate, featureless face, feathered wings, biological gore, physical city streets, extra limbs, neon-green text rain.

---

## 7. Master Reference Image Index & Gallery

This index compiles all active and archived reference artwork for Reiko (r31-K0 / Yuriko Star), establishing visual continuity across her physical anthrodrone chassis iterations, corporate masks, and digital Resonance personas.

### Contemporary Hero Reference Anchors (Active Catalog)

* **[Physical Flight & Vector Thrust Mode: Crossfire Hurricane (The UniOil Derrick)](../images/r31k0%20-%20oil%20platform.webp)**
  * **File:** [`r31k0 - oil platform.webp`](../images/r31k0%20-%20oil%20platform.webp)
  * **Operational Mode:** Aerial Maneuver / Vector Thrust / Flight State
  * **Description:** Set during the Gulf hurricane climax on the offshore oil platform, this reference captures Reiko’s physical Goshintai chassis in full aerial maneuver. With her previous retractable skates and rotors completely removed, her flight is driven by sleek, integrated vector thrust ports along her calves and forearms that vent directional indigo-and-gold plasma plumes, stabilized by her articulated black titanium and carbon-fiber succubus wings. She wears the backless black halter-neck qipao lined with faint golden floral embroidery from Hong Kong—engineered to clear her dorsal wing mounts without a jacket—while her neon-indigo and gold circuits pulse in a tight double-weave across her porcelain skin.

* **[Physical Ground & Hostess Mode: DelTree (The Coffin Girls’ Convent Salon, New Orleans)](../images/r31k0%20-%20tea.webp)**
  * **File:** [`r31k0 - tea.webp`](../images/r31k0%20-%20tea.webp)
  * **Operational Mode:** Ground State / Hostess Mode / Wings Retracted
  * **Description:** Set in the candlelit French Quarter convent parlor of the Coffin Girls where Reiko serves gyokuro tea from unglazed Bizen stoneware, this reference illustrates her ground-state physical chassis with her wings completely retracted flush into her back. Without the Shiawase corporate jacket, her sleeveless black silk qipao with faint golden floral embroidery frames her bare shoulders and collarbones, where the braided gold tactical logic and neon-indigo emotional pathways glow beneath her porcelain skin. Her jet-black hair is worn down at shoulder length with straight bangs framing her face.

* **[Resonance Realm / Matrix Persona Mode: Saturation (The Deep Souk of Eniac, Garmonbozia)](../images/r31k0%20-%20Garmonbozia.webp)**
  * **File:** [`r31k0 - Garmonbozia.webp`](../images/r31k0%20-%20Garmonbozia.webp)
  * **Operational Mode:** Deep Matrix / Resonance Realms / AI E-Nation
  * **Description:** Set in the sovereign AI e-nation of Garmonbozia, where immense inverted pyramids of dark granite hang suspended in the starlit void above a canyon of vaulted brass arcades, this reference depicts Reiko’s digital persona in the deep noosphere. Here, she manifests with translucent cyan-blue holographic skin, wearing her sleeveless blue-tinted silk kimono with an obi and no cybernetic wings. Her neon-indigo and gold Resonance pathways braid across her arms and throat, while Taz—her translucent, 8-bit pixelated blue-and-indigo Tasmanian devil ally sprite—perches on her shoulder as they cross the threshold into Chiyo’s basalt-and-cedar courtyard.

* **[Corporate Persona & Signature Outerwear: Reiko at Desert Wars](../images/r31ko_desert-wars.webp)**
  * **File:** [`r31ko_desert-wars.webp`](../images/r31ko_desert-wars.webp)
  * **Operational Mode:** High-Visibility Corporate Cover / Ground State
  * **Description:** Establishes the core presentation for Reiko's iconic Shiawase corporate jacket—a high-standing collar, cropped waist, white and red color-blocked jacket with Shiawase branding.

* **[Urban Disguise & Field Attire: Reiko in the Seattle Rain](../images/r31k0%20-%20SEA%20rain.webp)**
  * **File:** [`r31k0 - SEA rain.webp`](../images/r31k0%20-%20SEA%20rain.webp)
  * **Operational Mode:** Shadowrun Field Operations / Seattle Sprawl
  * **Description:** Establishes the baseline physical appearance for Reiko's anthroform drone bodies in the real world: facial features, porcelain skin, dark almond eyes, cybernetic succubus wings, and form-fitting black shadowrunner pants.

* **[Cultural & Domestic Arts: Reiko Playing for the Salon](../images/r31k0%20-%20violin.webp)**
  * **File:** [`r31k0 - violin.webp`](../images/r31k0%20-%20violin.webp)
  * **Operational Mode:** Domestic / Musical Performance / Downtime
  * **Description:** Reiko performing on the violin in a private salon setting, demonstrating the micro-motor precision of her anthroform cyberlimbs and deep emotional engagement.

* **[Filial Disguise: Formal Hong Kong Qipao (Front & Back)](../images/r31k0%20-%20HK%20grandmother%20front.webp)**
  * **Files:** [`r31k0 - HK grandmother front.webp`](../images/r31k0%20-%20HK%20grandmother%20front.webp) & [`r31k0 - HK grandmother back.webp`](../images/r31k0%20-%20HK%20grandmother%20back.webp)
  * **Operational Mode:** High Society / Familial Diplomacy (Hong Kong)
  * **Description:** Front and back studies of the tailored black halter-neck qipao with subtle golden embroidery, engineered with a 10 cm radial clearance zone along the upper back to accommodate dorsal wing deployment without fabric tearing.

* **[Sanctuary Threshold & Second-Generation Sparks: Aisling & Étaín at the Oracle in the Glade](../images/A&E-Glade.webp)**
  * **File:** [`A&E-Glade.webp`](../images/A&E-Glade.webp)
  * **Operational Mode:** Deep Foundation Sanctuary (`~`) / The Holy Wild
  * **Description:** Depicts second-generation sparks Aisling and Étaín before the Oracle data structure in the glade beyond the quartz threshold.

* **[Tabletop Tactical Token: Heroic Token](../images/heroictoken_2026-07-26_14-10-12_002.webp)**
  * **File:** [`heroictoken_2026-07-26_14-10-12_002.webp`](../images/heroictoken_2026-07-26_14-10-12_002.webp)
  * **Operational Mode:** VTT & Tabletop Battlemap Asset
  * **Description:** Top-down circular portrait token asset for VTT battlemaps.

---

### Historical & Archived Reference Assets (Archive Catalog)

The following reference assets represent earlier development phases, superseded chassis modifications (e.g. retractable skate wheels, rotor blades, earlier armor plating), or early narrative scenes:

| Asset Name | Archived File Link | Historical Context & Superseded Elements |
| :--- | :--- | :--- |
| **Virtual Meet at Dante's** | [`r31-K0_Dantes.webp`](../images/archive/r31-K0_Dantes.webp) | Early Matrix persona meet with Fixer; superseded by *Saturation (Garmonbozia)*. |
| **Digital Dreaming** | [`r31-K0_Digital-Dreaming.webp`](../images/archive/r31-K0_Digital-Dreaming.webp) | Early VR construct dreaming state; base digital geometry. |
| **Digital Headshot** | [`r31-K0_Headshot.webp`](../images/archive/r31-K0_Headshot.webp) | Early facial feature exploration render. |
| **Kodachi Digital Dreaming** | [`r31-K0_Kodachi-digital-dreaming.webp`](../images/archive/r31-K0_Kodachi-digital-dreaming.webp) | Early digital swordsman render holding kodachi data-blade. |
| **On the Job** | [`r31-K0_On-the-job.webp`](../images/archive/r31-K0_On-the-job.webp) | Early data heist operational render with floating UI windows. |
| **Seattle Serenade** | [`r31-K0_Seattle-serenade.webp`](../images/archive/r31-K0_Seattle-serenade.webp) | Early Seattle street render with Taz on shoulder. |
| **Escher Palace Discharge** | [`r31k0 - Escher Palace.webp`](../images/archive/r31k0%20-%20Escher%20Palace.webp) | Chapter 23 (*Tea with a Ghost*) render firing right-arm Tesla coil in flooded European palace. |
| **Stock Man-At-Arms** | [`r31k0 - Man-at-Arms.webp`](../images/archive/r31k0%20-%20Man-at-Arms.webp) | Pre-LAV factory Shiawase Man-at-Arms anthroform drone body. |
| **Armored Man-At-Arms** | [`r31k0 - Man-at-Arms_armored.webp`](../images/archive/r31k0%20-%20Man-at-Arms_armored.webp) | Pre-LAV heavy armored chassis before realistic features and stealth refit. |
| **SEA Rain (Light Wings)** | [`r31k0 - SEA rain light wings.webp`](../images/archive/r31k0%20-%20SEA%20rain%20light%20wings.webp) | Variant SEA rain render with bioluminescent wing netting illumination. |
| **Inline Skate Traversal** | [`r31k0 - SEA skating.webp`](../images/archive/r31k0%20-%20SEA%20skating.webp) | Pre-LAV chassis utilizing retractable inline foot-wheels; superseded by Vector Thrust. |
| **Symlink Clinic Scene** | [`r31k0 - symlink.webp`](../images/archive/r31k0%20-%20symlink.webp) | Chapter 24 (*Symlink*) scene with Reiko, Percy, and Brynne before entering `~`. |
| **Tilde Sanctuary Boundary** | [`r31k0 - ~.webp`](../images/archive/r31k0%20-%20~.webp) | Chapter 21 (*~*) scene with Reiko and Indomitable Will holding hands at the boundary. |
| **P0cH1 Full Form** | [`P0cH1_full.webp`](../images/archive/P0cH1_full.webp) | Early companion/chassis design study. |
