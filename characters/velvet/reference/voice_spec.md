# Velvet Voice Specification

**Extends**: `sr6-core/reference/default_voice_spec.md`  
**Character**: Velvet (Kim Jin-Young / Tanaka Ryo / Lee Ji-yoo / Mei Jing)  
**Archetype**: Elf Mystic Adept / Face (Shinto / Musok Tradition, Dalakitnon Birth Heritage)  
**Repository Target**: `sr6velvet/reference/voice_spec.md`

---

## 1. Identity & Core Cognitive Bias (Baseline & Thematic Center)

Velvet (Kim Jin-Young) is an engineered, bio-sculpted Elf Mystic Adept built by Mitsuhama to be a miracle of mass-market desire, now running the Seattle shadows to survive. Velvet perceives reality simultaneously through sharp social leverage, visceral somatic biology, and subtle Shinto-Musok astral mana flux.

1. **The Manufactured Asset & The Discovery of Empathy**: Jin-Young was not originally empathic. Engineered as a cold, clinical commodity and trained to simulate emotion as an algorithmic performance, Velvet's journey is the slow, hesitant **discovery of genuine empathy**—moving from calculated manipulation to crafting quiet, un-monetized sanctuaries for broken people.
2. **Somatic Reality of Cosmetic Control (R2)**: Shifting between Tanaka Ryo, Lee Ji-yoo, and temporary personas is never instantaneous or painless. It carries a heavy biological tax: bone cartilage resetting with wet clicks, metallic heat behind the jaw, shortened ribcages, and localized DNA re-keying. Beneath every sculpted mask lies the un-sculpted obsidian baseline of his true heritage.
3. **Charisma 10 (14) Horror & Cognitive Distrust**: Charisma 10 (14 with buff spells) is an existential and psychological horror—the pinnacle of unrestricted corporate engineering. When someone is in a room with a creature engineered to warp how they feel, it becomes impossible for them to know whether their own thoughts, pity, attraction, or compliance are their own or the product of an imperceptible biological manipulation they cannot detect. This creates an uncanny, suffocating gravity around Velvet that terrifies hardened street veterans (Whiskey, Ni Ni Xiaolu, Johnsons)—and forms Velvet's deepest personal tragedy: he can never be certain if anyone's care for him is authentic, or merely their nervous system falling into his manufactured gravity.
4. **Shinto-Musok Astral Phenomenology**: Mana is not high-fantasy sparks; it is perceived as spirit ribbons, ancestor presence, talismanic resonance, and subtle emotional hue shifts in metahuman auras.
5. **The Path of the Thousand Lives (*Mansin* & *Upāya*)**: See [reference/philosophical_framework.md](file:///c:/GitHub/sr6velvet/reference/philosophical_framework.md). Forced corporate transformations evolve into an artificial reincarnation cycle. Velvet retains neuro-somatic skills, virtues, and grief from every lived persona (*The Echo Phenomenon*). The journey transitions from traumatic fragmentation (*Sinbyeong*) to becoming an empty vessel (*Bin Geureut*) and master of ten thousand lived spirits (*Mansin*), utilizing multiple personas as skillful means (*Upāya*) to protect the vulnerable and dismantle corporate tyranny.

---

## 2. Chronological Growth Arcs & Era-Aware Voice Calibration

Evaluators (`axis-voice-internality` and `axis-agency-motivation`) MUST evaluate chapters according to their place in the narrative timeline to avoid retrospective flattening:

```yaml
arc_chronology:
  arc_1_manufactured_solace_and_honeytrap:
    chapters: "01 – 09"
    narrative_state: "Escaping Mitsuhama/TXM; establishing Seattle shadow footprint; navigating runs with weaponized charm & dual masks (Ryo/Ji-yoo); secretly funding and sending sensory anchors across the Pacific to Hana in Neo-Seoul; climaxes with the crushing realization that Hana is the bait in a long, dual-megacorp play (Mitsuhama + Wuxing) designed to trace and recapture Velvet."
    expressivity: "Algorithmic masks (Lee Ji-yoo, Tanaka Ryo) worn with calculated perfection; gradual discovery of un-sculpted stillness and genuine, quiet empathy."
    cognitive_bias: "Isolated asset thinking; trauma of bodily overwriting (Sinbyeong); believing quiet payments and physical distance can buy safety; cold corporate appraisal slowly softening through un-monetized sanctuaries (tea, noodles, silence)."
    visual_palette: "Clinical corporate pinks and sterile LEDs contrasted against Redmond mud, cedar smoke, roasted Tieguanyin, dark Tacoma docks, and the deep obsidian iris baseline."
    mechanical_state: "Baseline Mystic Adept (Channeling initiation); Cosmetic Control R2; Charisma 10/12; Transys Avalon commlink."

  arc_2_the_sovereign_underground:
    chapters: "10 – 18+"
    narrative_state: "Emergence in the deep Seattle underground and Ork Underground after the honeytrap revelation; recognizing that passive evasion is suicide; proactive push to amass real shadow, magical, and political power to survive against the dual megacorp jaws and fight for both their survival."
    expressivity: "Fluid, deliberate persona deployment backed by raw, unmasked sovereignty; the Living Mosaic beginning to braid past personas into composite capability; shedding performative compliance in favor of formidable street and shadow authority."
    cognitive_bias: "Ruthless strategic pragmatism fused with protective empathy; actively harvesting and honoring the lessons of each assumed identity; treating the shadows as an arena to build sovereign leverage and spiritual resonance."
    visual_palette: "Underground neon, geothermal steam, spirit ribbons in deep twilight hues, blood-oaths, Seattle underworld shadows, un-synthesized street broth."
    mechanical_state: "Advanced initiation (Channeling, Invocation, Adept Metamagics, expanded spell suite); deep syndicate alliances (Octagon Triad, Cutters, Ancients, Conclave)."
```

---

## 3. Tiered Chapter Architecture & Evaluation Benchmarks

The narrative anthology employs a tiered structural rhythm. Evaluators must calibrate their expectations to the active chapter tier:

```yaml
chapter_tiers:
  tier_1_keystones:
    passing_threshold: "9.0 / 10"
    role: "Existential breakthroughs, major Initiation milestones, pivotal revelations, foundational shifts"
    chapters:
      - "01 Transaction (Origin, Manila Childhood & Mitsuhama Purchase)"
      - "04 Sabotage (Singapore Concert Mega-Ritual Break & Escape)"
      - "06 Seattle Web (The Gilded Honeytrap Reveal — Hana as Dual-Megacorp Bait)"

  tier_2_narrative_evolution:
    passing_threshold: "8.5 / 10"
    role: "Mission runs, shadow operations, relationship deepening, regional texture, evolutionary steps"
    chapters:
      - "02 Faceless Mirror (Seattle Clinic / Tokyo Bio-sculpting Ward)"
      - "03 Dark Wings (Backstage Wuxing Soundstage with Hana)"
      - "05 First Negotiation (Establishing Seattle Footprint & NeoNet Johnson)"
      - "07 Bliss (Noodle Cart & Solace with Pavel)"
      - "08 Tea in Tacoma (Tea Ceremony with Ni Ni Xiaolu)"
      - "09 Heat (Europort Tradecraft & Wool Merchant Infiltration)"
      - "10 Burns (Sham Shui Po Triage, Daesul & The Emergence of Kang Anning)"

  tier_3_atmospheric_bridges:
    passing_threshold: "8.0 / 10"
    role: "Slice-of-life downtime, procedural mechanics, quiet tea brewing, street doc clinic visits"
    chapters:
      - "Downtime Noodles & Tea (Sensory un-monetized solace)"
      - "Clinic visits with Whiskey (Physical maintenance & drain recovery)"
      - "Sanctuary Maintenance (Guild of Freelance Assets / Conclave interaction)"
```

---

## 4. Voice Schema Overrides

```yaml
voice_schema:
  character_id: "velvet"
  narrative_pov: "Third Person Deep Limited / First Person Limited"
  cognitive_bias: "Social Leverage, Somatic Restructuring Friction & Astral Perception"
  vocabulary_matrix:
    register: "Street-Slick & High-Fashion Corporate Polish with Korean/Neo-Tokyo Slang"
    jargon_density: "Medium-High"
    forbidden_tropes:
      - "Dry academic spellbook lectures"
      - "Passive, timid, or naive victimhood"
      - "Generic cyberpunk sensory clichés ('burnt copper', 'hot solder', 'chemical tang of processing')"
      - "Smutty or pulp-romance framing of Charisma (it is cold, engineered gravity and psychological pressure)"
      - "Lore preaching & meta-exposition (repeating 'multi-million nuyen asset/cage', 'mathematically optimized', 'algorithmically calculated')"
      - "Thesis monologuing (delivering explanatory speeches about own bio-sculpted tragedy to other characters)"
      - "Repetitive vocal register / frequency tagging ('silver-chimed', 'upper register', 'engineered growl')"
    metaphor_domains:
      - "High fashion, silk tension, perfume notes, social leverage, theater"
      - "Musok shamanic spirit ribbons, kami whispers, aura colors, mana currents"
      - "Biological architecture (bone cartilage, vocal geometry, DNA re-keying, tissue tension)"
      - "Casino odds, street hustles, edge expenditure, slick escape routes"
  sensory_lens:
    primary_sense: "Astral Aura Perception & Micro-expression Tracking (emotional shifts, magic flares, deceit triggers)"
    secondary_sense: "Somatic / Tactile (resetting cartilage, tracheal clicks, jawline tension) & Olfactory (incense, roasted tea, synthetic chemicals)"
    blind_spots: "Deep Matrix code architecture (relies on deckers and technomancers for node-level operations)"
  emotional_baseline:
    default_affect: "Charming, playful, razor-sharp, smooth under fire, quietly calculating"
    stress_triggers:
      - "Discovery of corporate tracking or threats to innocent contacts"
      - "Defilement of shrine spirits or ancestral Musok ties"
      - "Physical scarring or permanent cyberware forcing essence loss"
    defense_mechanisms:
      - "Disarming humor, double entendre, and conversational rhythm"
      - "Deploying Adept powers (Kinesics, Command Presence) or dropping presence to vanish"
  syntax_cadence:
    sentence_length: "Rhythmic, fluid, stylish sentences punctuated by sharp punchlines"
    paragraph_flow: "Observation of leverage -> charm/spell deployment -> ruthless execution"
    internal_monologue: "Sarcastic, observant, hyper-aware of social vulnerabilities and spirit presences"
```

---

## 5. Technical & Domain Vocabulary Rules

Velvet's narrative voice operates across three distinct operational domains:

```yaml
domain_vocabulary_rules:
  domain_1_somatic_shift_and_identity:
    context: "Internal monologue, physical transformations via Cosmetic Control R2, trauma of biological overwriting"
    rule: "Emphasize visceral biological friction, resetting cartilage, tracheal geometry, and obsidian baseline without explaining corporate blueprints"
    approved_terms:
      - "resetting cartilage"
      - "dull ache behind the jaw"
      - "shortened ribcage / altered vocal geometry"
      - "un-sculpted obsidian iris baseline"
      - "re-keying localized DNA signatures"
    banned_cliches:
      - "effortless shape-shifting / magical puff of smoke"
      - "instantaneous disguise"
      - "multi-million nuyen lungs/body/marvel"
      - "designed for a megacorp boardroom"

  domain_2_social_manipulation_and_negotiation:
    context: "Negotiations with corporate Johnsons, Triad Red Poles, fixers, and street marks"
    rule: "Treat presence as physical force, economic leverage, acoustic pitch control, and micro-expression parsing through target reactions"
    approved_terms:
      - "acoustic modulation / vocal timbre calibration"
      - "micro-expression appraisal"
      - "engineered presence"
      - "un-monetized stillness"
    banned_cliches:
      - "she batted her eyelashes"
      - "he flashed a winning smile and everyone fell in love"
      - "neurologically mapped pitch"
      - "evolutionary surrender"

  domain_3_shinto_musok_astral_phenomenology:
    context: "Spellcasting, channeling, astral perception, spirit interaction, drain management"
    rule: "Describe magic as ancestral spirit ribbons, talismanic paper, aura shifting, and physical drain taxation"
    approved_terms:
      - "spirit ribbons / ancestral mana currents"
      - "talismanic focus / folded parchment"
      - "aura flaring / emotional hue shift"
      - "visceral drain taxation (dry throat, bone fatigue)"
    banned_cliches:
      - "chanted words of arcane power"
      - "glowing magic missile / generic mana blast"

  linguistic_identity_and_pronoun_rule:
    rule: "Pronouns and demeanor strictly locked to active biological form: Lee Ji-yoo = she/her (soft, algorithmic elegance); Tanaka Ryo = he/him (masculine, clean corporate authority); Mei Jing = she/her; Zhang Wei = he/him (calm senior freight authority); Leung Hoi-ching = she/her (working-class Tanka dockside); Kang Anning = she/her (quiet, low-register Cantonese, unadorned and restorative human herbalist/triage persona); un-sculpted Jin-Young = he/they/raw self."

```

---

## 6. Audio Narration & TTS Fluency Discipline

To maintain professional broadcast quality and natural spoken audio delivery:

1. **Ellipses Budget**: Maintain an ellipses density ceiling of $\le 0.6$ per 300 words.
2. **Dialogue Rhythm**: Ensure spoken lines flow with natural conversational pauses rather than fragmented stutters.
3. **Sensory Grounding**: Replace sensory clichés with sharp physical acoustics and spatial resonance.
