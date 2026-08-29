"""
Declarative Synergy & Modifier Engine for Shadowrun 6e / Missions (SRM).

Handles:
  - Multi-Component Pool Optimizations (Attributes, Skills, Autosofts, Action-added components)
  - SRMG Augmentation Limits (+4 per Attribute, +4 per Skill/Autosoft; multi-component tests up to +12)
  - Focus Non-Splitting Rules (untyped/power/resonance foci assigned to single component)
  - Teamwork Caps (clamped to leader's skill/autosoft rating)
  - Attribute Overrides (e.g. Natural Hacker substituting Resonance for Mental attributes)
  - Companion & Sprite Symbiosis (evaluates companion's skills, autosofts, and powers such as Taz the Assassin Sprite)
  - Living Persona ASDF, Matrix Initiative, Full Matrix Defense, and Drone Action Pools
"""

from typing import Dict, Any, List, Optional, Tuple, Set


class PoolModifier:
    """Represents an atomic modifier to a pool component or whole test."""
    def __init__(
        self,
        target: str,
        type_: str,  # 'augmentation', 'focus', 'symbiosis', 'specialization', 'teamwork', 'tactical', 'action', 'diagnosis'
        source: str,
        value: int,
        is_srm_capped: bool = False,
        condition: Optional[str] = None
    ):
        self.target = target
        self.type = type_
        self.source = source
        self.value = value
        self.is_srm_capped = is_srm_capped
        self.condition = condition

    def __repr__(self) -> str:
        return f"<PoolModifier {self.target} +{self.value} ({self.source}) [{self.type}]>"


# Backwards compatibility alias
Modifier = PoolModifier


class PoolComponent:
    """
    Represents a test component (Attribute, Skill, Autosoft, or Action Attribute).
    Enforces the SRMG +4 augmentation maximum per component.
    """
    def __init__(
        self,
        name: str,
        base_value: int,
        component_type: str = "attribute",  # 'attribute', 'skill', 'autosoft', 'action_attribute'
        modifiers: Optional[List[PoolModifier]] = None,
        aug_cap: int = 4
    ):
        self.name = name
        self.base_value = base_value
        self.component_type = component_type
        self.modifiers = modifiers or []
        self.aug_cap = aug_cap

    @property
    def raw_aug_bonus(self) -> int:
        return sum(
            m.value for m in self.modifiers
            if m.is_srm_capped or m.type in ["augmentation", "symbiosis", "focus", "boost"]
        )

    @property
    def uncapped_bonus(self) -> int:
        return sum(
            m.value for m in self.modifiers
            if not (m.is_srm_capped or m.type in ["augmentation", "symbiosis", "focus", "boost"])
        )

    @property
    def clamped_aug_bonus(self) -> int:
        return min(self.raw_aug_bonus, self.aug_cap)

    @property
    def effective_value(self) -> int:
        return self.base_value + self.clamped_aug_bonus + self.uncapped_bonus

    @property
    def is_at_aug_cap(self) -> bool:
        return self.raw_aug_bonus >= self.aug_cap

    def get_breakdown(self) -> str:
        if not self.modifiers:
            return f"{self.name} {self.base_value}"
        mods_str = " + ".join([f"+{m.value} {m.source}" for m in self.modifiers])
        return f"{self.name} {self.base_value} ({mods_str})"


class PoolOptimization:
    """
    Encapsulates a fully calculated and audited dice pool with multi-component breakdowns,
    exempt modifiers (Specializations, Teamwork, Tactical software, Action modifiers),
    bought hits, and transparent mathematical derivations.
    """
    def __init__(
        self,
        name: str,
        components: List[PoolComponent],
        specialization: Optional[PoolModifier] = None,
        teamwork: Optional[PoolModifier] = None,
        tactical_modifiers: Optional[List[PoolModifier]] = None,
        action_modifiers: Optional[List[PoolModifier]] = None,
        notes: Optional[str] = None,
        wild_dice: int = 0
    ):
        self.name = name
        self.components = components
        self.specialization = specialization
        self.teamwork = teamwork
        self.tactical_modifiers = tactical_modifiers or []
        self.action_modifiers = action_modifiers or []
        self.notes = notes
        self.wild_dice = wild_dice

    @property
    def base_pool(self) -> int:
        return sum(c.base_value for c in self.components)

    @property
    def total_pool(self) -> int:
        comp_total = sum(c.effective_value for c in self.components)
        spec_val = self.specialization.value if self.specialization else 0
        tw_val = self.teamwork.value if self.teamwork else 0
        tact_val = sum(m.value for m in self.tactical_modifiers)
        act_val = sum(m.value for m in self.action_modifiers)
        return comp_total + spec_val + tw_val + tact_val + act_val

    @property
    def bought_hits(self) -> int:
        return self.total_pool // 4

    @property
    def total_augmentations(self) -> int:
        return sum(c.clamped_aug_bonus for c in self.components)

    @property
    def max_possible_augmentations(self) -> int:
        return len(self.components) * 4

    def get_base_stat_skill_string(self) -> str:
        attr_abbrevs = {
            "resonance": "RES", "firewall": "FW", "data_processing": "DP",
            "attack": "ATT", "sleaze": "SLZ", "willpower": "WIL",
            "logic": "LOG", "intuition": "INT", "charisma": "CHA",
            "body": "BOD", "agility": "AGI", "reaction": "REA",
            "strength": "STR", "edge": "EDG"
        }
        parts = []
        for c in self.components:
            if c.component_type == "skill":
                parts.append(f"{c.name} ({c.base_value})")
            elif c.component_type == "attribute":
                short_n = attr_abbrevs.get(c.name.lower(), c.name[:3].upper() if len(c.name) > 3 else c.name.upper())
                parts.append(f"{short_n} ({c.base_value})")
            else:
                parts.append(f"{c.name} ({c.base_value})")
        return f"{' + '.join(parts)} = **{self.base_pool}d6**"

    def get_modifiers_breakdown_string(self) -> str:
        parts = [f"Base ({self.base_pool})"]
        for c in self.components:
            for m in c.modifiers:
                parts.append(f"{m.source} (+{m.value})")
        if self.specialization:
            parts.append(f"{self.specialization.source} (+{self.specialization.value})")
        if self.teamwork:
            parts.append(f"{self.teamwork.source} (+{self.teamwork.value})")
        for m in self.tactical_modifiers:
            wild_note = f", {self.wild_dice} wild" if self.wild_dice and "Overclock" in m.source else ""
            parts.append(f"{m.source} (+{m.value}{wild_note})")
        for m in self.action_modifiers:
            parts.append(f"{m.source} (+{m.value})")
        return " + ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "total_pool": self.total_pool,
            "bought_hits": self.bought_hits,
            "wild_dice": self.wild_dice,
            "base_stat_skill": self.get_base_stat_skill_string(),
            "modifiers_math": self.get_modifiers_breakdown_string(),
            "components": [
                {
                    "name": c.name,
                    "base": c.base_value,
                    "type": c.component_type,
                    "aug_bonus": c.clamped_aug_bonus,
                    "effective": c.effective_value,
                    "modifiers": [{"source": m.source, "value": m.value, "type": m.type} for m in c.modifiers]
                } for c in self.components
            ],
            "total_augmentations": self.total_augmentations,
            "max_augmentations": self.max_possible_augmentations,
            "breakdown": f"{self.get_modifiers_breakdown_string()} = {self.total_pool}d6" + (f" ({self.wild_dice} wild)" if self.wild_dice else "")
        }


class ModifierEngine:
    """
    Core calculation and audit engine for character synergies and modifiers.
    Enforces SRMG multi-component +4 augmentation caps, teamwork limits, and focus non-splitting rules.
    """

    @staticmethod
    def get_attribute_substitutions(char_data: Dict[str, Any], domain: str = "matrix") -> Dict[str, str]:
        """Determines attribute overrides (e.g. Natural Hacker)."""
        overrides = {}
        synergies = char_data.get("synergies", {})
        substitutions = synergies.get("attribute_substitutions", [])
        
        for sub in substitutions:
            if isinstance(sub, dict) and sub.get("domain") == domain:
                target_attr = sub.get("target_attribute", "all_mental")
                sub_attr = sub.get("substitute_attribute", "resonance")
                overrides[target_attr] = sub_attr

        if not overrides:
            qualities = char_data.get("qualities", {})
            pos_qualities = qualities.get("positive", []) if isinstance(qualities, dict) else []
            pos_names = [q.get("name", "").lower() if isinstance(q, dict) else str(q).lower() for q in pos_qualities]
            if any("natural hacker" in qn or "natural_hacker" in qn for qn in pos_names):
                overrides["all_mental"] = "resonance"

        return overrides

    @staticmethod
    def get_companion_modifiers(char_data: Dict[str, Any], target_skill: str) -> List[PoolModifier]:
        """Evaluates companion sprite/spirit contributions (e.g. Taz the Assassin Sprite)."""
        modifiers = []
        target_norm = target_skill.lower().strip()
        synergies = char_data.get("synergies", {})
        companions = synergies.get("companions", [])

        if not companions:
            meta_echoes = char_data.get("meta_echoes", [])
            echo_names = [e.get("name", "").lower() if isinstance(e, dict) else str(e).lower() for e in meta_echoes]
            if any("symbiosis" in en for en in echo_names):
                companions = [{
                    "name": "Taz",
                    "type": "Assassin Sprite",
                    "level": 7,
                    "skills": ["cracking", "electronics"],
                    "autosofts": ["targeting", "stealth", "clearsight"],
                    "powers": ["diagnosis"],
                    "symbiosis_bonus": 4,
                    "diagnosis_bonus": 3
                }]

        for comp in companions:
            if not isinstance(comp, dict):
                continue
            name = comp.get("name", "Taz")
            symb_bonus = comp.get("symbiosis_bonus", 4)
            diag_bonus = comp.get("diagnosis_bonus", 3)
            skills = [s.lower() for s in comp.get("skills", [])]
            autosofts = [a.lower() for a in comp.get("autosofts", [])]
            powers = [p.lower() for p in comp.get("powers", [])]

            if target_norm in skills:
                modifiers.append(PoolModifier(
                    target=f"skill:{target_norm}",
                    type_="symbiosis",
                    source=f"{name}",
                    value=symb_bonus,
                    is_srm_capped=True
                ))

            if target_norm in autosofts or any(a in target_norm for a in autosofts):
                modifiers.append(PoolModifier(
                    target=f"skill:{target_norm}",
                    type_="symbiosis",
                    source=f"{name}",
                    value=symb_bonus,
                    is_srm_capped=True
                ))

            if ("diagnosis" in powers) and (target_norm in ["piloting", "maneuvering", "engineering", "drone_piloting"]):
                modifiers.append(PoolModifier(
                    target=f"skill:{target_norm}",
                    type_="diagnosis",
                    source=f"{name}",
                    value=diag_bonus,
                    is_srm_capped=True
                ))

        return modifiers

    @staticmethod
    def get_focus_modifiers(char_data: Dict[str, Any], target_attribute: str) -> List[PoolModifier]:
        """Evaluates focus bonuses (e.g. Resonance Focus). Focuses apply to a single component."""
        modifiers = []
        synergies = char_data.get("synergies", {})
        foci = synergies.get("foci", [])

        if not foci:
            res = char_data.get("attributes", {}).get("resonance", 0)
            if res > 0:
                foci = [{"name": "Focus", "rating": 4, "applies_to": "resonance"}]

        for f in foci:
            if not isinstance(f, dict):
                continue
            applies_to = f.get("applies_to", "").lower()
            if applies_to == target_attribute.lower():
                modifiers.append(PoolModifier(
                    target=f"attribute:{applies_to}",
                    type_="focus",
                    source=f"Focus",
                    value=int(f.get("rating", 4)),
                    is_srm_capped=True
                ))

        return modifiers

    @classmethod
    def calculate_skill_pool(
        cls,
        char_data: Dict[str, Any],
        skill_name: str,
        skill_rating: int,
        linked_attribute: str,
        specialization: Optional[str] = None,
        is_matrix_test: bool = False
    ) -> Dict[str, Any]:
        """
        Computes the effective dice pool for an active skill.
        Breakdown format is concise: RES 8 + 5 Rtg + 4 Focus 4 + 4 Taz
        """
        attrs = char_data.get("attributes", {})
        base_attr_val = int(attrs.get(linked_attribute.lower(), 1))
        
        effective_attr_name = linked_attribute.lower()
        effective_attr_val = base_attr_val
        is_overridden = False

        if is_matrix_test or skill_name.lower() in ["cracking", "electronics", "tasking"]:
            substitutions = cls.get_attribute_substitutions(char_data, domain="matrix")
            if "all_mental" in substitutions or linked_attribute.lower() in substitutions:
                override_attr = substitutions.get(linked_attribute.lower(), substitutions.get("all_mental", "resonance"))
                if override_attr in attrs:
                    effective_attr_name = override_attr
                    effective_attr_val = int(attrs.get(override_attr, base_attr_val))
                    is_overridden = True

        short_attr = "RES" if effective_attr_name.lower() == "resonance" else effective_attr_name[:3].upper()
        running_pool = effective_attr_val + skill_rating
        breakdown_parts = [f"{short_attr} {effective_attr_val}", f"{skill_rating} Rtg"]
        applied_modifiers: List[PoolModifier] = []

        focus_mods = cls.get_focus_modifiers(char_data, effective_attr_name)
        for fm in focus_mods:
            running_pool += fm.value
            applied_modifiers.append(fm)
            breakdown_parts.append(f"+{fm.value} {fm.source}")

        comp_mods = cls.get_companion_modifiers(char_data, skill_name)
        aug_total = 0
        for cm in comp_mods:
            if cm.is_srm_capped:
                if aug_total + cm.value > 4:
                    clamped_val = max(0, 4 - aug_total)
                    if clamped_val > 0:
                        running_pool += clamped_val
                        aug_total = 4
                        applied_modifiers.append(cm)
                        breakdown_parts.append(f"+{clamped_val} {cm.source}")
                else:
                    running_pool += cm.value
                    aug_total += cm.value
                    applied_modifiers.append(cm)
                    breakdown_parts.append(f"+{cm.value} {cm.source}")
            else:
                running_pool += cm.value
                applied_modifiers.append(cm)
                breakdown_parts.append(f"+{cm.value} {cm.source}")

        return {
            "skill_name": skill_name,
            "specialization": specialization,
            "effective_pool": running_pool,
            "base_pool": base_attr_val + skill_rating,
            "effective_attribute": effective_attr_name,
            "is_attribute_overridden": is_overridden,
            "breakdown": " + ".join(breakdown_parts),
            "applied_modifiers": applied_modifiers
        }

    @staticmethod
    def get_living_persona_asdf(char_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculates active ASDF ratings.
        For Technomancers: base ASDF + tuning (Attack: 7, Sleaze: 9, DP: 7, Firewall: 9).
        For Monads (Whisper Nets p. 149): Attack=CHA, Sleaze=INT, DP=LOG, Firewall=WIL, boosted by Nanite Volume (NV).
        """
        attrs = char_data.get("attributes", {})
        res = int(attrs.get("resonance", 0))
        identity = char_data.get("identity", {})
        mortype = str(identity.get("mortype", "")).lower()

        persona = char_data.get("living_persona", {})
        base_asdf = persona.get("asdf_bonuses", {}) if isinstance(persona, dict) else {}

        if "monad" in mortype or res == 0:
            # Monad Living Persona (Whisper Nets p. 149 & Collapsing Now p. 160)
            cha = int(attrs.get("charisma", 3))
            int_val = int(attrs.get("intuition", 4))
            log_val = int(attrs.get("logic", 7))
            wil = int(attrs.get("willpower", 5))

            nv_att = base_asdf.get("attack", 0)
            nv_slz = base_asdf.get("sleaze", 2)
            nv_dp = base_asdf.get("data_processing", 1)
            nv_fw = base_asdf.get("firewall", 3)

            return {
                "attack": cha + nv_att,
                "sleaze": int_val + nv_slz,
                "data_processing": log_val + nv_dp,
                "firewall": wil + nv_fw
            }

        synergies = char_data.get("synergies", {})
        tuning = synergies.get("living_persona_network_tuning", {}).get("asdf_bonuses", {})
        if not tuning:
            tuning = {"attack": 4, "sleaze": 8, "data_processing": 6, "firewall": 6}

        return {
            "attack": base_asdf.get("attack", 0) + tuning.get("attack", 0),
            "sleaze": base_asdf.get("sleaze", 0) + tuning.get("sleaze", 0),
            "data_processing": base_asdf.get("data_processing", 0) + tuning.get("data_processing", 0),
            "firewall": base_asdf.get("firewall", 0) + tuning.get("firewall", 0)
        }

    @classmethod
    def get_full_matrix_defense(cls, char_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Full Matrix Defense.
        For Monads: Willpower + Firewall (cannot run personal assistant apps on living persona).
        For Technomancers: RES + FW + PA + DP + Focus.
        """
        attrs = char_data.get("attributes", {})
        res = int(attrs.get("resonance", 0))
        wil = int(attrs.get("willpower", 5))
        identity = char_data.get("identity", {})
        mortype = str(identity.get("mortype", "")).lower()
        asdf = cls.get_living_persona_asdf(char_data)
        fw = asdf.get("firewall", 8)

        if "monad" in mortype or res == 0:
            total_pool = wil + fw
            effective_hits = total_pool // 4
            breakdown = f"WIL {wil} + FW {fw} = {total_pool}d6"
            return {
                "pool": total_pool,
                "effective_hits": effective_hits,
                "breakdown": breakdown
            }

        dp = asdf.get("data_processing", 7)
        pa_rating = 6
        focus_bonus = 4 if res > 0 else 0

        total_pool = res + fw + pa_rating + dp + focus_bonus
        effective_hits = total_pool // 4
        breakdown = f"RES {res} + FW {fw} + PA {pa_rating} + DP {dp} + Focus {focus_bonus} = {total_pool}d6"
        return {
            "pool": total_pool,
            "effective_hits": effective_hits,
            "breakdown": breakdown
        }

    @classmethod
    def get_matrix_initiative(cls, char_data: Dict[str, Any]) -> str:
        """
        Matrix Initiative string.
        """
        attrs = char_data.get("attributes", {})
        res = int(attrs.get("resonance", 0))
        identity = char_data.get("identity", {})
        mortype = str(identity.get("mortype", "")).lower()

        if "monad" in mortype or res == 0:
            rea = int(attrs.get("reaction", 4)) + 2  # Synaptic Booster R2
            int_val = int(attrs.get("intuition", 4))
            asdf = cls.get_living_persona_asdf(char_data)
            dp = asdf.get("data_processing", 9)
            return f"{rea + int_val} + 3D6 (AR) / {dp + int_val} + 3D6 (Hot-Sim VR)"

        return "10 + 4D6 (Hot-Sim VR / Overclock)"

    @classmethod
    def get_matrix_action_pools(cls, char_data: Dict[str, Any]) -> Dict[str, PoolOptimization]:
        """
        Calculates the full set of standardized Matrix Action Pools with SRMG multi-component rules.
        """
        attrs = char_data.get("attributes", {})
        res = int(attrs.get("resonance", 0))
        identity = char_data.get("identity", {})
        mortype = str(identity.get("mortype", "")).lower()

        asdf = cls.get_living_persona_asdf(char_data)
        fw = asdf.get("firewall", 6)
        dp = asdf.get("data_processing", 7)
        log_val = int(attrs.get("logic", 4))
        int_val = int(attrs.get("intuition", 4))
        wil = int(attrs.get("willpower", 5))

        if "monad" in mortype or res == 0:
            # Monad Living Persona Matrix Pools (No Resonance, Focus, Overclock, or Sprite Allies)
            # 1. Offensive Cracking: Hacking
            c_skill = PoolComponent("Cracking", 5, "skill")
            c_attr = PoolComponent("Logic", log_val, "attribute")
            hacking_opt = PoolOptimization(
                name="Offensive Cracking: Hacking",
                components=[c_skill, c_attr],
                notes="Matrix Brute Force, Probe & Backdoor Exploits (Logic 7 + Cracking 5 = 12d6 -> 3 Hits)"
            )

            # 2. Offensive Cracking: Other
            cracking_other_opt = PoolOptimization(
                name="Offensive Cracking",
                components=[c_skill, c_attr],
                notes="Cybercombat & Electronic Warfare Tests (Data Spike, Erase Mark, Jamming)"
            )

            # 3. Full Matrix Defense Test
            c_def_wil = PoolComponent("Willpower", wil, "attribute")
            c_def_fw = PoolComponent("Firewall", fw, "attribute")
            mdef_opt = PoolOptimization(
                name="Full Matrix Defense Test",
                components=[c_def_wil, c_def_fw],
                notes="Monad Living Persona defense (WIL 5 + FW 6/7 = 11-12d6 -> 3 Hits)"
            )

            # 4. Electronics: Software Tests
            e_skill_soft = PoolComponent("Electronics", 6, "skill")
            e_attr_soft = PoolComponent("Logic", log_val, "attribute")
            electronics_soft_opt = PoolOptimization(
                name="Electronics: Software Tests",
                components=[e_skill_soft, e_attr_soft],
                notes="Format Device, Edit File, Data Extraction (Logic 7 + Electronics 6 = 13d6 -> 3 Hits)"
            )

            # 5. Electronics: Matrix Perception
            e_skill_perc = PoolComponent("Electronics", 6, "skill")
            e_attr_perc = PoolComponent("Intuition", int_val, "attribute")
            electronics_other_opt = PoolOptimization(
                name="Electronics: Matrix Perception",
                components=[e_skill_perc, e_attr_perc],
                notes="Matrix Spotting & Grid Analytics (Intuition 4 + Electronics 6 = 10d6 -> 2 Hits)"
            )

            # 6. Downtime Buying Gear Test
            buy_gear_opt = PoolOptimization(
                name="Downtime Buying Gear Test",
                components=[e_skill_perc, e_attr_perc],
                notes="Matrix Search & Legwork (Intuition 4 + Electronics 6 = 10d6 -> 2 Hits)"
            )

            # 7. Programming / Coding Tests
            programming_opt = PoolOptimization(
                name="Programming / Coding Tests",
                components=[e_skill_soft, e_attr_soft],
                notes="Custom Scripting & Data Architecture (Logic 7 + Electronics 6 = 13d6 -> 3 Hits)"
            )

            return {
                "cracking_hacking": hacking_opt,
                "cracking_other": cracking_other_opt,
                "full_matrix_defense": mdef_opt,
                "electronics_software": electronics_soft_opt,
                "electronics_other": electronics_other_opt,
                "buy_gear": buy_gear_opt,
                "programming": programming_opt
            }

        # Technomancer Pools (Yuriko)
        focus_bonus = 4 if res > 0 else 0
        c_skill = PoolComponent("Cracking", 5, "skill")
        c_attr = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        hacking_opt = PoolOptimization(
            name="Offensive Cracking: Hacking",
            components=[c_skill, c_attr],
            specialization=PoolModifier("skill:cracking", "specialization", "Hacking", 2),
            teamwork=PoolModifier("skill:cracking", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2),
                PoolModifier("test:matrix", "tactical", "ECM Warrior II", 2)
            ],
            wild_dice=1
        )

        c_skill_other = PoolComponent("Cracking", 5, "skill")
        c_attr_other = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        cracking_other_opt = PoolOptimization(
            name="Offensive Cracking",
            components=[c_skill_other, c_attr_other],
            teamwork=PoolModifier("skill:cracking", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2),
                PoolModifier("test:matrix", "tactical", "ECM Warrior II", 2)
            ],
            wild_dice=1,
            notes="Cybercombat & Electronic Warfare Tests"
        )

        c_def_res = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        c_def_fw = PoolComponent("Firewall", fw, "attribute")
        mdef_opt = PoolOptimization(
            name="Full Matrix Defense Test",
            components=[c_def_res, c_def_fw],
            action_modifiers=[
                PoolModifier("action:defense", "action", "Personal Assistant App R6", 6),
                PoolModifier("action:defense", "action", "Directional Shield (Active DP)", dp)
            ]
        )

        e_skill_soft = PoolComponent("Electronics", 5, "skill")
        e_attr_soft = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        electronics_soft_opt = PoolOptimization(
            name="Electronics: Software Tests",
            components=[e_skill_soft, e_attr_soft],
            specialization=PoolModifier("skill:electronics", "specialization", "Software", 2),
            teamwork=PoolModifier("skill:electronics", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2)
            ],
            wild_dice=1
        )

        e_skill_other = PoolComponent("Electronics", 5, "skill")
        e_attr_other = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        electronics_other_opt = PoolOptimization(
            name="Electronics",
            components=[e_skill_other, e_attr_other],
            teamwork=PoolModifier("skill:electronics", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2)
            ],
            wild_dice=1,
            notes="Computer, Hardware & Complex Forms"
        )

        e_skill_buy = PoolComponent("Electronics", 5, "skill")
        e_attr_buy = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        buy_gear_opt = PoolOptimization(
            name="Downtime Buying Gear Test",
            components=[e_skill_buy, e_attr_buy],
            teamwork=PoolModifier("skill:electronics", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2),
                PoolModifier("test:matrix", "tactical", "Shopsoft", 1)
            ],
            wild_dice=1
        )

        e_skill_prog = PoolComponent("Electronics", 5, "skill")
        e_attr_prog = PoolComponent("Resonance", res, "attribute", [
            PoolModifier("attribute:resonance", "focus", "Focus", focus_bonus, is_srm_capped=True)
        ])
        programming_opt = PoolOptimization(
            name="Programming / Coding Tests",
            components=[e_skill_prog, e_attr_prog],
            specialization=PoolModifier("skill:electronics", "specialization", "Software", 2),
            teamwork=PoolModifier("skill:electronics", "teamwork", "Ally Teamwork", 4),
            tactical_modifiers=[
                PoolModifier("test:matrix", "tactical", "Overclock", 2)
            ],
            wild_dice=1
        )

        return {
            "cracking_hacking": hacking_opt,
            "cracking_other": cracking_other_opt,
            "full_matrix_defense": mdef_opt,
            "electronics_software": electronics_soft_opt,
            "electronics_other": electronics_other_opt,
            "buy_gear": buy_gear_opt,
            "programming": programming_opt
        }


    @classmethod
    def get_sprite_downtime_pools(cls, char_data: Dict[str, Any], sprite_level: int = 7) -> Dict[str, Any]:
        """
        Calculates downtime sprite compiling, registering, and fading pools.
        """
        attrs = char_data.get("attributes", {})
        res = int(attrs.get("resonance", 8))
        wil = int(attrs.get("willpower", 6))
        cha = int(attrs.get("charisma", 4))
        log_val = int(attrs.get("logic", 4))
        focus_bonus = 4 if res > 0 else 0

        # Tasking: Compiling (Base 6) + RES 8 + Focus 4 = 18d6 -> 4 Hits
        compiling_pool = 6 + res + focus_bonus
        compiling_hits = compiling_pool // 4

        # Sprite Defense: Level * 2
        sprite_def_pool = sprite_level * 2
        sprite_def_hits = sprite_def_pool // 4

        # Net Compiling Hits
        net_compiling_hits = max(0, compiling_hits - sprite_def_hits)
        compiling_fade_fv = sprite_def_hits

        # Fade Resistance: WIL + CHA + Submersion (assumed 7)
        fade_res_pool = wil + cha + 7
        fade_res_hits = fade_res_pool // 4

        # Registering: Tasking 6 + Spec 2 = 8 + RES 8 + Focus 4 = 20d6 -> 5 Hits
        registering_pool = 8 + res + focus_bonus
        registering_hits = registering_pool // 4
        registering_fade_fv = sprite_def_hits * 2
        net_registering_hits = max(0, registering_hits - sprite_def_hits)
        total_services = net_compiling_hits + 1 + net_registering_hits
        registering_damage = max(0, registering_fade_fv - fade_res_hits)

        # Focus Fading: FV = Focus / 2 = 2. Resistance: WIL + LOG = 10d6 -> 2 Hits.
        focus_fade_fv = focus_bonus // 2
        focus_fade_res_pool = wil + log_val
        focus_fade_res_hits = focus_fade_res_pool // 4
        focus_fade_damage = max(0, focus_fade_fv - focus_fade_res_hits)

        return {
            "compiling_pool": compiling_pool,
            "compiling_hits": compiling_hits,
            "sprite_def_pool": sprite_def_pool,
            "sprite_def_hits": sprite_def_hits,
            "net_compiling_hits": net_compiling_hits,
            "compiling_fade_fv": compiling_fade_fv,
            "fade_res_pool": fade_res_pool,
            "fade_res_hits": fade_res_hits,
            "registering_pool": registering_pool,
            "registering_hits": registering_hits,
            "registering_fade_fv": registering_fade_fv,
            "net_registering_hits": net_registering_hits,
            "total_services": total_services,
            "registering_damage": registering_damage,
            "focus_fade_fv": focus_fade_fv,
            "focus_fade_res_pool": focus_fade_res_pool,
            "focus_fade_res_hits": focus_fade_res_hits,
            "focus_fade_damage": focus_fade_damage
        }

    @classmethod
    def get_magic_action_pools(cls, char_data: Dict[str, Any], enhanced: bool = True) -> Dict[str, PoolOptimization]:
        """
        Calculates optimal dice pools and bonus strategies for Magic actions
        (Spellcasting, Conjuring, Drain Resistance, Dispelling).
        Supports +4 Increase Attribute sustained configurations (Focused Concentration R3).
        """
        attrs = char_data.get("attributes", {})
        mag = int(attrs.get("magic", 0))
        wil = int(attrs.get("willpower", 1))
        cha = int(attrs.get("charisma", 1))

        # Skills
        skills = {s.get("name", ""): s for s in char_data.get("skills", []) if isinstance(s, dict)}
        sorc_r = int(skills.get("Sorcery", {}).get("rating", 0))
        conj_r = int(skills.get("Conjuring", {}).get("rating", 0))

        # Adept powers
        adept_powers = {p.get("name", ""): p for p in char_data.get("adept_powers", []) if isinstance(p, dict)}
        sorc_impr = int(adept_powers.get("Improved Ability (Sorcery)", {}).get("rating", 0))

        # Focus modifiers
        focus_mods = cls.get_focus_modifiers(char_data, "magic")

        # Attribute Enhancement Modifiers (Focused Concentration R3: CHA +4, WIL +4)
        cha_mods = [PoolModifier("attribute:charisma", "spell", "Increase Attribute (+4 Sustained)", 4, is_srm_capped=True)] if enhanced else []
        wil_mods = [PoolModifier("attribute:willpower", "spell", "Increase Attribute (+4 Sustained)", 4, is_srm_capped=True)] if enhanced else []

        # 1. Spellcasting (Sorcery)
        s_skill = PoolComponent("Sorcery", sorc_r, "skill")
        s_attr = PoolComponent("Magic", mag, "attribute", focus_mods)
        tact_mods = []
        if sorc_impr:
            tact_mods.append(PoolModifier("skill:sorcery", "adept_power", f"Improved Ability (Sorcery R{sorc_impr})", sorc_impr))

        spec_name = skills.get("Sorcery", {}).get("specialization")
        spec_mod = PoolModifier("skill:sorcery", "specialization", f"Specialization: {spec_name}", 2) if spec_name else None

        spell_opt = PoolOptimization(
            name="Spellcasting (Sorcery)",
            components=[s_skill, s_attr],
            specialization=spec_mod,
            tactical_modifiers=tact_mods,
            notes="Health, Manipulation, Combat Spells"
        )

        # 2. Shinto-Musok Drain Resistance
        d_wil = PoolComponent("Willpower", wil, "attribute", wil_mods)
        d_cha = PoolComponent("Charisma", cha, "attribute", cha_mods)
        drain_opt = PoolOptimization(
            name="Drain Resistance (Shinto / Musok)",
            components=[d_wil, d_cha],
            notes="Tradition: Willpower + Charisma (Enhanced: 23d6 -> 5 Hits)" if enhanced else "Tradition: Willpower + Charisma (Baseline)"
        )

        # 3. Conjuring & Summoning
        c_skill = PoolComponent("Conjuring", conj_r, "skill")
        c_attr = PoolComponent("Magic", mag, "attribute", focus_mods)
        conj_opt = PoolOptimization(
            name="Conjuring & Spirit Summoning",
            components=[c_skill, c_attr],
            notes="Summoning & Binding Spirits (Conjuring + MAG = 11d6 -> 2 Hits)"
        )

        # 4. Spirit Channeling (if Channeling metamagic is unlocked)
        meta_echoes = char_data.get("meta_echoes", [])
        init_grade = len(meta_echoes) if isinstance(meta_echoes, list) else 0
        has_channeling = any((isinstance(e, dict) and e.get("name") == "Channeling") or str(e) == "Channeling" for e in meta_echoes)

        chan_opt = None
        if has_channeling:
            chan_skill = PoolComponent("Conjuring", conj_r, "skill")
            chan_attr = PoolComponent("Magic", mag, "attribute", focus_mods)
            chan_opt = PoolOptimization(
                name="Spirit Channeling (Inhabitation)",
                components=[chan_skill, chan_attr],
                action_modifiers=[
                    PoolModifier("action:channeling", "metamagic", f"Initiate Grade ({init_grade})", init_grade)
                ],
                notes="Channeling spirits into physical vessel (Dual Natured, +Physical Attributes, Critter Powers)"
            )

        # 5. Counterspelling / Dispelling
        disp_skill = PoolComponent("Sorcery", sorc_r, "skill")
        disp_attr = PoolComponent("Magic", mag, "attribute", focus_mods)
        disp_opt = PoolOptimization(
            name="Counterspelling & Dispelling",
            components=[disp_skill, disp_attr],
            tactical_modifiers=tact_mods,
            notes="Dispelling active magical spells & magical defense"
        )

        res_pools = {
            "spellcasting": spell_opt,
            "drain_resistance": drain_opt,
            "conjuring": conj_opt,
        }
        if chan_opt:
            res_pools["channeling"] = chan_opt
        res_pools["dispelling"] = disp_opt

        return res_pools

    @classmethod
    def get_social_action_pools(cls, char_data: Dict[str, Any], scene_mode: str = "social_enhanced") -> Dict[str, PoolOptimization]:
        """
        Calculates optimal dice pools and bonus strategies for Social / Face actions
        (Influence, Negotiation, Disguise, Inspire Competence, Composure, Judge Intentions).
        Supports 'baseline', 'social_enhanced' (CHA +4, WIL +4, INT +4), and 'combat_enhanced' (CHA +4, WIL +4, REA/BOD +4).
        """
        attrs = char_data.get("attributes", {})
        cha = int(attrs.get("charisma", 1))
        wil = int(attrs.get("willpower", 1))
        int_val = int(attrs.get("intuition", 1))

        is_enhanced = "enhanced" in scene_mode

        # Skills
        skills = {s.get("name", ""): s for s in char_data.get("skills", []) if isinstance(s, dict)}
        infl_r = int(skills.get("Influence", {}).get("rating", 0))
        con_r = int(skills.get("Con", {}).get("rating", 0))

        # Adept powers
        adept_powers = {p.get("name", ""): p for p in char_data.get("adept_powers", []) if isinstance(p, dict)}
        cosmetic_r = int(adept_powers.get("Cosmetic Control", {}).get("rating", 0))

        # Attribute Enhancement Modifiers
        cha_mods = [PoolModifier("attribute:charisma", "spell", "Increase Attribute (+4 Sustained)", 4, is_srm_capped=True)] if is_enhanced else []
        wil_mods = [PoolModifier("attribute:willpower", "spell", "Increase Attribute (+4 Sustained)", 4, is_srm_capped=True)] if is_enhanced else []
        int_mods = [PoolModifier("attribute:intuition", "spell", "Increase Attribute (+4 Sustained)", 4, is_srm_capped=True)] if (is_enhanced and "social" in scene_mode) else []

        # 1. Influence & Social Negotiation
        i_skill = PoolComponent("Influence", infl_r, "skill")
        i_attr = PoolComponent("Charisma", cha, "attribute", cha_mods)
        infl_opt = PoolOptimization(
            name="Social Negotiation & Face Actions (Influence)",
            components=[i_skill, i_attr],
            action_modifiers=[
                PoolModifier("test:social", "gear", "Ares Skinshield (Très Chic x2: +4 Social Rating)", 0)
            ],
            notes="Negotiating with marks, Johnsons, contacts & fixers (Enhanced: 19d6 -> 4 Hits)" if is_enhanced else "Negotiating with marks, Johnsons & fixers (Baseline)"
        )

        # 2. Inspire Competence (Teamwork Buff)
        insp_skill = PoolComponent("Influence", infl_r, "skill")
        insp_attr = PoolComponent("Charisma", cha, "attribute", cha_mods)
        insp_opt = PoolOptimization(
            name="Inspire Competence (Ally Teamwork Buff)",
            components=[insp_skill, insp_attr],
            notes="Teamwork test assists ally test + grants 1 free Edge (Enhanced: 19d6 -> 4 Hits)" if is_enhanced else "Teamwork test assists ally test + grants 1 free Edge (Baseline)"
        )

        # 3. Deception & Impersonation (Con)
        con_skill = PoolComponent("Con", con_r, "skill")
        con_attr = PoolComponent("Charisma", cha, "attribute", cha_mods)
        con_opt = PoolOptimization(
            name="Deception & Impersonation (Con)",
            components=[con_skill, con_attr],
            notes="Fast-talk, deep-cover impersonation, blending personas (Enhanced: 18d6 -> 4 Hits)" if is_enhanced else "Fast-talk, deep-cover impersonation, blending personas (Baseline: 14d6 -> 3 Hits)"
        )

        # 4. Disguise & Persona Shift (Cosmetic Control)
        c_skill = PoolComponent("Con / Disguise", con_r if con_r else 1, "skill")
        c_attr = PoolComponent("Intuition", int_val, "attribute", int_mods)
        c_mods = []
        if cosmetic_r:
            c_mods.append(PoolModifier("skill:disguise", "adept_power", f"Cosmetic Control (R{cosmetic_r})", cosmetic_r))
        c_mods.append(PoolModifier("test:disguise", "gear", "Nanopaste Disguise / Nanocosmetics (+1 Edge)", 0))

        disguise_opt = PoolOptimization(
            name="Disguise & Persona Shift (Cosmetic Control)",
            components=[c_skill, c_attr],
            tactical_modifiers=c_mods,
            notes="Shifting between Lee Ji-yoo, Tanaka Ryo, and custom identities (Enhanced: 13d6 -> 3 Hits)" if is_enhanced else "Shifting between Lee Ji-yoo, Tanaka Ryo, and custom identities (Baseline)"
        )

        # 5. Composure Test
        comp_wil = PoolComponent("Willpower", wil, "attribute", wil_mods)
        comp_cha = PoolComponent("Charisma", cha, "attribute", cha_mods)
        comp_opt = PoolOptimization(
            name="Composure (Social & Psychological Resistance)",
            components=[comp_wil, comp_cha],
            notes="Resisting intimidation, manipulation, pressure (Enhanced: 23d6 -> 5 Hits)" if is_enhanced else "Resisting intimidation, manipulation, pressure (Baseline)"
        )

        # 6. Judge Intentions Test
        judge_int = PoolComponent("Intuition", int_val, "attribute", int_mods)
        judge_wil = PoolComponent("Willpower", wil, "attribute", wil_mods)
        judge_opt = PoolOptimization(
            name="Judge Intentions (Micro-Expression Reading)",
            components=[judge_int, judge_wil],
            notes="Parsing mark deception, aura shifts, stress signals (Enhanced: 16d6 -> 4 Hits)" if is_enhanced else "Parsing mark deception, aura shifts, stress signals (Baseline)"
        )

        return {
            "influence": infl_opt,
            "inspire_competence": insp_opt,
            "con": con_opt,
            "disguise": disguise_opt,
            "composure": comp_opt,
            "judge_intentions": judge_opt
        }

    @classmethod
    def get_tactical_action_pools(cls, char_data: Dict[str, Any], scene_mode: str = "baseline") -> Dict[str, PoolOptimization]:
        """
        Calculates optimal dice pools and tactical actions for cybered operatives / street samurais
        (Firearms, Close Combat, Physical Defense, Damage Soak, Initiative, Perception, Stealth, Engineering).
        Enforces SRMG +4 augmentation caps, Wireless-ON Skillwires Activesoft streaming,
        and SRMG Adrenaline Pump drug stacking rules.
        """
        attrs = char_data.get("attributes", {})
        bod = int(attrs.get("body", 1))
        agi = int(attrs.get("agility", 1))
        rea = int(attrs.get("reaction", 1))
        str_val = int(attrs.get("strength", 1))
        wil = int(attrs.get("willpower", 1))
        log_val = int(attrs.get("logic", 1))
        int_val = int(attrs.get("intuition", 1))

        is_adrenaline = "adrenaline" in scene_mode.lower() or scene_mode.lower() == "pump_active"

        # Cyberware / Bioware detection & modifiers
        # Muscle Toner R2 (+2 AGI)
        agi_mods = [PoolModifier("attribute:agility", "augmentation", "Muscle Toner (Used R2)", 2, is_srm_capped=True)]
        # Muscle Augmentation R2 (+2 STR)
        str_mods = [PoolModifier("attribute:strength", "augmentation", "Muscle Augmentation (Used R2)", 2, is_srm_capped=True)]
        # Synaptic Booster R2 (+2 REA)
        rea_mods = [PoolModifier("attribute:reaction", "augmentation", "Synaptic Booster (Used R2)", 2, is_srm_capped=True)]
        # Willpower baseline
        wil_mods = []

        # SRMG Adrenaline Pump Drug Stacking (+2 AGI, +2 REA, +2 STR, +2 WIL)
        if is_adrenaline:
            agi_mods.append(PoolModifier("attribute:agility", "drug", "Adrenaline Pump Drug Surge (Omega R2)", 2, is_srm_capped=True))
            rea_mods.append(PoolModifier("attribute:reaction", "drug", "Adrenaline Pump Drug Surge (Omega R2)", 2, is_srm_capped=True))
            str_mods.append(PoolModifier("attribute:strength", "drug", "Adrenaline Pump Drug Surge (Omega R2)", 2, is_srm_capped=True))
            wil_mods.append(PoolModifier("attribute:willpower", "drug", "Adrenaline Pump Drug Surge (Omega R2)", 2, is_srm_capped=True))

        # 1. Firearms Attack (FN P93 Praetor / Colt Manhunter w/ Smartlink)
        # Activesoft R6 (Streamed via Wireless-ON Skillwires R6: +1) + Reflex Recorder (Firearms: +1) = 8 skill dice
        # AGI (4 + Aug 2 = 6) + Smartlink (+2) = 16d6 (4 Hits)
        # With Adrenaline Pump: AGI (4 + Aug 4 = 8) + Skill 8 + Smartlink 2 = 18d6 (4 Hits)
        f_skill = PoolComponent("Firearms (Activesoft R6)", 6, "skill", [
            PoolModifier("skill:firearms", "gear", "Skillwires Wireless ON", 1),
            PoolModifier("skill:firearms", "augmentation", "Reflex Recorder (Firearms)", 1)
        ])
        f_attr = PoolComponent("Agility", agi, "attribute", agi_mods)
        firearms_opt = PoolOptimization(
            name="Firearms Attack (Smartlink Active)",
            components=[f_skill, f_attr],
            tactical_modifiers=[
                PoolModifier("test:ranged_combat", "gear", "Smartlink (Wireless ON)", 2)
            ],
            notes="Streamed Activesoft R6 (+1 Wires, +1 Reflex Recorder) via Wireless-ON Used Skillwires (Adrenaline Surge: 18d6 -> 4 Hits)" if is_adrenaline else "Streamed Activesoft R6 (+1 Wires, +1 Reflex Recorder) via Wireless-ON Used Skillwires (Baseline: 16d6 -> 4 Hits)"
        )

        # 2. Close Combat / Unarmed Strike (Bone Density Augmentation R4)
        # Activesoft R6 (+1 Wireless-ON) + AGI (Augmented: 6) = 13d6 (3 Hits, 3P/4P DV)
        # With Adrenaline Pump: AGI (Augmented: 8) + Activesoft 7 = 15d6 (3 Hits, 3P/4P DV)
        cc_skill = PoolComponent("Close Combat (Activesoft R6)", 6, "skill", [
            PoolModifier("skill:close_combat", "gear", "Skillwires Wireless ON", 1)
        ])
        cc_attr = PoolComponent("Agility", agi, "attribute", agi_mods)
        unarmed_opt = PoolOptimization(
            name="Close Combat / Unarmed Strike",
            components=[cc_skill, cc_attr],
            notes="Bone Density R4 (3P DV) / Monofilament Whip (4P DV). Wireless-ON Skillwires (Adrenaline Surge: 14d6 -> 3 Hits)" if is_adrenaline else "Bone Density R4 (3P DV) / Monofilament Whip (4P DV). Wireless-ON Skillwires (Baseline: 12d6 -> 3 Hits)"
        )

        # 3. Physical Defense Test (Evasion)
        # REA (2 + Aug 2 = 4) + INT (4) = 8d6 (2 Hits)
        # With Adrenaline Pump: REA (2 + Aug 4 = 6) + INT (4) = 10d6 (2 Hits)
        d_rea = PoolComponent("Reaction", rea, "attribute", rea_mods)
        d_int = PoolComponent("Intuition", int_val, "attribute")
        defense_opt = PoolOptimization(
            name="Physical Defense (Ranged/Melee Evasion)",
            components=[d_rea, d_int],
            notes="Synaptic Booster R2 (+2 REA). Resisting ranged & melee attacks (Adrenaline Surge: 10d6 -> 2 Hits)" if is_adrenaline else "Synaptic Booster R2 (+2 REA). Resisting ranged & melee attacks (Baseline: 8d6 -> 2 Hits)"
        )

        # 4. Damage Resistance / Soak Test
        # BOD (4 + Bone Density +4 = 8) = 8d6 (2 Hits)
        soak_bod = PoolComponent("Body", bod, "attribute", [
            PoolModifier("attribute:body", "augmentation", "Bone Density Augmentation (Used R4)", 4, is_srm_capped=True)
        ])
        soak_opt = PoolOptimization(
            name="Damage Resistance / Soak Test",
            components=[soak_bod],
            notes="Bone Density Augmentation R4 (+4 Soak unarmored base: 8 Soak). Platelet Factories reduces incoming Physical damage by 1 box (min 1). Armor (Lined Coat DR 3, Helmet DR 1, SkinShield DR 3) provides Defense Rating."
        )

        # 5. Physical Initiative
        # REA (2 + 2 Synaptic Booster = 4) + INT (4) = 8 + 3D6 (Synaptic Booster R2 provides +2D6 Initiative)
        # With Adrenaline Pump: REA (6) + INT (4) = 10 + 3D6 (Per SRMG, Initiative Dice do not stack and uses highest: 3D6)
        init_rea = rea + (4 if is_adrenaline else 2)
        init_val = init_rea + int_val
        init_opt = PoolOptimization(
            name="Physical Initiative",
            components=[d_rea, d_int],
            notes=f"{init_val} + 3D6 Physical Initiative (Synaptic Booster R2: +2D6 Init Dice; Adrenaline Pump stacks REA but not Init Dice per SRMG)"
        )

        # 6. Physical Perception Test
        # Perception Activesoft R6 (+1 Wireless-ON) + INT 4 + Smartlink 1 = 12d6 (3 Hits)
        p_skill = PoolComponent("Perception (Activesoft R6)", 6, "skill", [
            PoolModifier("skill:perception", "gear", "Skillwires Wireless ON", 1)
        ])
        p_attr = PoolComponent("Intuition", int_val, "attribute")
        perception_opt = PoolOptimization(
            name="Perception & Visual Scanning",
            components=[p_skill, p_attr],
            tactical_modifiers=[
                PoolModifier("test:perception", "gear", "Image Link / Smartlink Visuals", 1)
            ],
            notes="Streamed Perception Activesoft R6 via Wireless-ON Used Skillwires"
        )

        # 7. Stealth & Infiltration Test
        # Stealth Activesoft R6 (+1 Wireless-ON) + AGI (Augmented: 6) = 13d6 (3 Hits)
        # With Adrenaline Pump: Stealth R6 (+1 Wires) + AGI (Augmented: 8) = 15d6 (3 Hits)
        st_skill = PoolComponent("Stealth (Activesoft R6)", 6, "skill", [
            PoolModifier("skill:stealth", "gear", "Skillwires Wireless ON", 1)
        ])
        st_attr = PoolComponent("Agility", agi, "attribute", agi_mods)
        stealth_opt = PoolOptimization(
            name="Stealth & Infiltration",
            components=[st_skill, st_attr],
            notes="Streamed Stealth Activesoft R6 via Wireless-ON Used Skillwires"
        )

        # 8. Technical Engineering & Cyber Repair Test
        # Engineering 1 + LOG 7 + Math SPU 1 = 9d6 (2 Hits)
        eng_skill = PoolComponent("Engineering", 1, "skill")
        eng_attr = PoolComponent("Logic", log_val, "attribute")
        engineering_opt = PoolOptimization(
            name="Engineering & Cybernetic Repair",
            components=[eng_skill, eng_attr],
            tactical_modifiers=[
                PoolModifier("test:engineering", "augmentation", "Math SPU (Used)", 1)
            ],
            notes="Hardware maintenance, cyberware tuning & electronics diagnostics"
        )

        return {
            "firearms": firearms_opt,
            "close_combat": unarmed_opt,
            "defense": defense_opt,
            "soak": soak_opt,
            "initiative": init_opt,
            "perception": perception_opt,
            "stealth": stealth_opt,
            "engineering": engineering_opt
        }

