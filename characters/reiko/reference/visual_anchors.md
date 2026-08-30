# Reiko (r31-K0 / Yuriko Star) Master Visual Anchors

> [!IMPORTANT]
> **Master Visual Reference Specification**
> This document details the visual identity, chassis specifications, world-specific shaders, clothing rules, hero assets, and prompt templates for Reiko (r31-K0 / Yuriko Star).

---

## 1. Key Visual Reference Images

The three foundational visual anchors defining Reiko across her core operational modes:

* **[Reiko attending a meet virtually (Dante's Image)](../images/r31-K0_Dantes.png)**
  * **File:** [`r31-K0_Dantes.png`](../images/r31-K0_Dantes.png)
  * **Description:** Establishes Reiko's core appearance in the Matrix and Resonance Realms—glowing ethereal digital persona with neon-indigo bioluminescent circuitry against virtual data architecture. (Note: This image reflects her base digital geometry; canonical circuit colors follow the Neon-Indigo [Emotion] and Gold [Logic] state system).
  
* **[Reiko in the Seattle Rain (SEA Rain Image)](../images/r31k0%20-%20SEA%20rain.png)**
  * **File:** [`r31k0 - SEA rain.png`](../images/r31k0%20-%20SEA%20rain.png)
  * **Description:** Establishes the core physical appearance for Reiko's anthroform drone bodies in the real world, including facial features, cybernetic wing structure, porcelain skin, and rain-swept field attire.
  * **Variant:** [`r31k0 - SEA rain light wings.jpg`](../images/r31k0%20-%20SEA%20rain%20light%20wings.jpg) — Variant depicting subtle bioluminescent light emitting from her cybernetic wing membranes through real-world rain.

* **[Reiko at Desert Wars (Desert Wars Image)](../images/r31ko_desert-wars.jpg)**
  * **File:** [`r31ko_desert-wars.jpg`](../images/r31ko_desert-wars.jpg)
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
* **Heads 3.5 to 6.5 (3.0 Heads total):** Crotch to foot soles. Legs are slightly elongated (1:1.2 torso-to-leg ratio) to grant a graceful, agile silhouette for aerial traversal and inline skating while keeping overall height capped at 140 cm.

Backless Garment Clearance Zone: Upper back cutout on halter/kimono tops extends from the C7 vertebra down to L1, providing a 10 cm radial clearance around the thoracic wing hinges to prevent fabric collision during extension or rotation.

Foot & Sole Geometry: Proportional human feet with porcelain skin finish. Sole surfaces feature a central longitudinal seam where two skin panels split outward to reveal the internal wheel carriage chassis.

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

* **Resonance Pathways:** Bioluminescent neon-indigo and tactical gold circuit lines tracing seamlessly across her skin. Circuits are never fully absent, though they may be muted. Dual-channel self-illuminating pathways mapped via vector displacement and emissive masks across forearms, wrists, neck, and torso.
* **Circuit Luminescence & Color Sync Rules:**
  * **Baseline / Resting:** Soft, muted violet/indigo pulse.
  * **High Emotion / Empathy:** Broad, flaring neon-indigo pathways across forearms, wrists, neck, and cheeks.
  * **Active Processing / Hacking / Combat:** Sharp, geometric gold lines along her wrists, temples, and torso.
  * **Harmonized / Peak State:** Both neon-indigo and geometric gold circuit lines appear simultaneously.

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

### Integrated Mobility Systems

* **Retractable Inline Wheels (Cybernetic Legs):** When active, her feet remain bare/unshod porcelain skin with mechanical sole panels hinged open along the bottom, allowing 3-4 small inline rollerblade wheels to extend directly from the interior chassis of each foot.
* **Retractable Wheel Assembly Cutaway Description:**
  * **Plantar Portal & Longitudinal Hinges:** Underside of each foot features a precision-machined bilateral seam with twin micro-hinges allowing sole panels to swing outward by 90 degrees.
  * **Internal Chassis & Deployment:** High-torque linear screw actuator and titanium four-bar linkage drop 3 to 4 polyurethane micro-inline wheels vertically into place along the plantar arch for high-speed urban street traversal.

### Physical World Negative Prompt Anchors

* **Excluded Elements:** Full robot body, mechanical robot face, metallic/gray skin, android ball-joints, exposed internal wiring, green olive-drab bomber jacket, Western facial features, blonde hair, short hair, organic feather/bird wings, organic demon wings, wings clipping through closed jackets.

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

### Digital Attire & Companion Sprite

* **Attire:** Blue-tinted full-length kimono or short yukata top (sleeveless with traditional undergarments and obi).
* **Companion Sprite (Taz):** Small, translucent 8-bit Tasmanian devil sprite glowing with a pixelated blue/indigo aura (scampering on her shoulder, hanging from her outfit, or floating nearby).

### Technology World Negative Prompt Anchors

* **Excluded Elements:** Opaque human skin, biological texture, mechanical wings, succubus wings, physical furniture, real-world outdoor lighting, metallic robot faceplate, heavy armor.

---

## 6. Updated Master Prompt Templates

### Template A: Flight / Combat Mode (Physical World - Wings Extended)

**Prompt:** Photorealistic cyberpunk portrait of a petite 4'7" Pan-Asian woman in her early 20s with delicate expressive facial features, dark almond-shaped eyes, fair porcelain skin, and jet-black hair in a bun secured by two crossed silver hairpins with loose strands framing her cheeks. Bioluminescent [neon-indigo / golden] circuit lines trace seamlessly across her forearms, neck, and chest. She wears a backless black futuristic halter top and fitted utilitarian black leather pants. Two articulated cybernetic succubus wings extend from her upper back, constructed of black titanium skeletal bones and dark grey carbon fiber netting. She holds her cropped white and red Shiawase jacket draped over one arm. [INSERT SETTING & LIGHTING]. 8k resolution, cinematic lighting, photorealistic.

**Negative Prompt:** full robot body, mechanical robot faceplate, featureless face, metallic skin, gray skin, android joints, green bomber jacket, Western facial features, blonde hair, short hair, feather wings, bird wings, wings clipping through clothes, extra limbs.

### Template B: Casual / Ground Operations (Physical World - Wings Retracted & Jacket Worn)

**Prompt:** Photorealistic cyberpunk portrait of a petite 4'7" Pan-Asian woman in her early 20s with delicate expressive facial features, dark almond-shaped eyes, fair porcelain skin, and shoulder-length straight jet-black hair with soft bangs framing her face. Bioluminescent [neon-indigo / golden] circuit lines glow subtly on her hands, wrists, and neck. Her wings are completely absent. She wears a cropped white and red Shiawase corporate jacket with a standing high collar, long sleeves, and the Shiawase logo on the chest, paired with fitted utilitarian black leather pants. [INSERT SETTING & LIGHTING]. 8k resolution, cinematic lighting, photorealistic.

**Negative Prompt:** wings, mechanical wings, devil wings, full robot body, mechanical faceplate, featureless face, metallic skin, gray skin, android joints, green bomber jacket, Western facial features, blonde hair, extra limbs.

### Template C: Matrix / Resonance Realm Persona (Digital Construct Mode)

**Prompt:** Photorealistic cyberpunk digital portrait of a petite 4'7" Pan-Asian woman in her early 20s manifesting as an ethereal holographic digital construct inside the Matrix. She features semi-translucent cyan-blue skin with internal light projection at 75% opacity, framed by electric cyan rim lighting. Her hair is semi-translucent electric cyan-blue (`#00BFFF` to `#00FFFF`), shoulder-length straight with bangs, worn loose. Bioluminescent [`neon-indigo` / golden] circuit lines trace seamlessly across her translucent forearms, neck, and torso. She wears a blue-tinted sleeveless yukata top with traditional undergarments and an obi. Her back is completely smooth with NO WINGS. Surrounding her are floating holographic UI diagnostic panels, data graphs, and wireframe schematics glowing in neon green and teal. Next to her is Taz, a small translucent 8-bit Tasmanian devil sprite glowing with a pixelated blue-indigo aura. [INSERT VIRTUAL SETTING & DIGITAL LIGHTING]. 8k resolution, cinematic digital lighting, cyberspace construct aesthetic.

**Negative Prompt:** opaque human skin, biological texture, flesh, mechanical wings, succubus wings, feather wings, bird wings, physical furniture, real-world outdoor lighting, physical environment, metallic robot faceplate, heavy armor, extra limbs.
