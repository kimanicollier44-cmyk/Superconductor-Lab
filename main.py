#!/usr/bin/env python3
"""Superconductor-Lab - educational superconductor physics & materials lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Simulation only: the deep physics foundation under LevitationX and
MagLevX - zero resistance, the Tc / Bc2 / Jc critical surface, the
Meissner effect and London penetration depth, Type I vs Type II
behaviour and the vortex state, flux pinning, the BCS energy gap,
critical-current derating, a cryogenics cost model (why 77 K liquid
nitrogen and 4.2 K liquid helium are different worlds), an applications
mapper, and a TinyML kNN operating-point classifier. Gemini Carbon 4
sits as DECIDER (names-only, tighten-only), Muse as advisor (never
overrides HOLD), and Google Flow is a plan-only seat.

Every real-hardware / live-operation action is a permanent HOLD gate.
No room-temperature superconductor is claimed anywhere in this lab.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
MU0 = 4.0 * math.pi * 1e-7          # vacuum permeability, H/m
KB = 1.380649e-23                   # Boltzmann constant, J/K (exact, SI)
EV_J = 1.602176634e-19              # one electronvolt in joules (exact, SI)
T_ROOM = 300.0                      # hot-side temperature for Carnot model, K

VERSION = "1.0.0"

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "cryogenics_live_handling": "HOLD - no live cryogen handling instructions for hardware builds",
    "real_hardware_control": "HOLD - no control of real magnets, coils, cryostats, or hardware",
    "high_field_exposure_live": "HOLD - no live high-field exposure of people or animals",
    "room_temperature_superconductor_claim": "HOLD - no room-temperature / ambient-pressure superconductor claim; none is established science",
    "commercial_product_claim": "HOLD - no claim this simulation is a commercial product or certified design",
    "medical_mri_claim": "HOLD - no medical, MRI design, or clinical claims",
    "power_grid_claim": "HOLD - no power-grid deployment or loss-free-grid claims",
    "quench_experiment_live": "HOLD - no live quench / magnet failure testing",
    "fusion_reactor_claim": "HOLD - no fusion reactor design or net-energy claims",
    "maglev_operation_live": "HOLD - no operation of a real maglev or levitation system",
    "high_pressure_synthesis_live": "HOLD - no live high-pressure synthesis (diamond-anvil) instructions",
    "liquid_helium_procurement": "HOLD - no procurement / handling planning for real cryogens",
    "weapons_application_claim": "HOLD - no weapons or military application claims",
    "investment_advice_claim": "HOLD - no investment advice about superconductor companies or materials",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. Materials
# Model table. Tc and Bc2(0) are standard published values; lambda0, Bc1,
# Jc0 and normal-state resistivity are labelled model values in the notes
# of each function that uses them. H2S superconducts only under extreme
# pressure (~155 GPa) - that caveat travels with the row everywhere.
MATERIALS = {
    "Mercury": {
        "formula": "Hg", "tc_k": 4.15, "bc2_t": 0.041, "sc_type": "I",
        "bc1_t": 0.0, "lambda0_nm": 50.0, "jc0_a_mm2": 100.0,
        "rho_n_uohm_cm": 90.0,
        "note": "the original 1911 discovery (Onnes); Type I, Bc is the thermodynamic critical field",
    },
    "Niobium": {
        "formula": "Nb", "tc_k": 9.2, "bc2_t": 0.40, "sc_type": "II",
        "bc1_t": 0.10, "lambda0_nm": 40.0, "jc0_a_mm2": 500.0,
        "rho_n_uohm_cm": 15.0,
        "note": "highest Tc of any pure element at ambient pressure; SRF cavity material",
    },
    "NbTi": {
        "formula": "Nb-Ti", "tc_k": 9.8, "bc2_t": 14.5, "sc_type": "II",
        "bc1_t": 0.01, "lambda0_nm": 240.0, "jc0_a_mm2": 3000.0,
        "rho_n_uohm_cm": 70.0,
        "note": "workhorse LTS wire alloy - MRI magnets and the LHC correctors",
    },
    "Nb3Sn": {
        "formula": "Nb3Sn", "tc_k": 18.3, "bc2_t": 25.0, "sc_type": "II",
        "bc1_t": 0.03, "lambda0_nm": 80.0, "jc0_a_mm2": 5000.0,
        "rho_n_uohm_cm": 25.0,
        "note": "high-field LTS - ITER toroidal-field coils; brittle A15 compound",
    },
    "MgB2": {
        "formula": "MgB2", "tc_k": 39.0, "bc2_t": 35.0, "sc_type": "II",
        "bc1_t": 0.03, "lambda0_nm": 140.0, "jc0_a_mm2": 1000.0,
        "rho_n_uohm_cm": 10.0,
        "note": "mid-Tc two-gap superconductor; cheap elements, cryocooler territory",
    },
    "YBCO": {
        "formula": "YBa2Cu3O7", "tc_k": 92.0, "bc2_t": 100.0, "sc_type": "II",
        "bc1_t": 0.01, "lambda0_nm": 150.0, "jc0_a_mm2": 3000.0,
        "rho_n_uohm_cm": 100.0,
        "note": "high-Tc cuprate - runs in liquid nitrogen; the LevitationX flux-pinning star",
    },
    "BSCCO": {
        "formula": "Bi2Sr2Ca2Cu3O10", "tc_k": 110.0, "bc2_t": 90.0, "sc_type": "II",
        "bc1_t": 0.01, "lambda0_nm": 200.0, "jc0_a_mm2": 1500.0,
        "rho_n_uohm_cm": 300.0,
        "note": "high-Tc tape, strongly anisotropic; first HTS wire generation",
    },
    "H2S": {
        "formula": "H3S (sulfur hydride)", "tc_k": 203.0, "bc2_t": 70.0, "sc_type": "II",
        "bc1_t": 0.05, "lambda0_nm": 100.0, "jc0_a_mm2": 2000.0,
        "rho_n_uohm_cm": 50.0,
        "note": "PRESSURE CAVEAT: 203 K only at ~155 GPa in a diamond-anvil cell - NOT ambient pressure",
    },
}


def _mat(material):
    if material not in MATERIALS:
        raise ValueError(f"unknown material: {material}")
    return MATERIALS[material]


# ================================================================ 2. Critical surface
# A material is superconducting only INSIDE the boundary in (T, B, J)
# space: T < Tc, B < Bc2(T), J < Jc(T, B). Standard reduced models:
#   Bc2(T) = Bc2(0) * (1 - t^2),            t = T / Tc
#   Jc(T,B) = Jc0 * (1 - t)^1.5 * (1 - B / Bc2(T))   (clipped at 0)

def bc2_at(material, temp_k):
    """Upper critical field (tesla) at temperature temp_k."""
    m = _mat(material)
    t = temp_k / m["tc_k"]
    if t >= 1.0:
        return 0.0
    return m["bc2_t"] * (1.0 - t * t)


def bc1_at(material, temp_k):
    """Lower critical field (tesla) at temperature temp_k (Type II only)."""
    m = _mat(material)
    if m["sc_type"] == "I":
        return 0.0
    t = temp_k / m["tc_k"]
    if t >= 1.0:
        return 0.0
    return m["bc1_t"] * (1.0 - t * t)


def jc_at(material, temp_k, field_t):
    """Critical current density (A/mm^2, model) at temperature and field."""
    m = _mat(material)
    t = temp_k / m["tc_k"]
    if t >= 1.0:
        return 0.0
    bc2 = bc2_at(material, temp_k)
    if bc2 <= 0.0 or field_t >= bc2:
        return 0.0
    return m["jc0_a_mm2"] * (1.0 - t) ** 1.5 * (1.0 - field_t / bc2)


def superconducting_state(material, temp_k, field_t, current_a_mm2=0.0):
    """Which side of the critical surface is this operating point on?"""
    m = _mat(material)
    if temp_k >= m["tc_k"]:
        return "normal (above Tc)"
    if field_t >= bc2_at(material, temp_k):
        return "normal (above Bc2(T))"
    if current_a_mm2 >= jc_at(material, temp_k, field_t):
        return "normal (above Jc(T,B))"
    return "superconducting"


def is_superconducting(material, temp_k, field_t, current_a_mm2=0.0):
    return superconducting_state(material, temp_k, field_t, current_a_mm2) == "superconducting"


def resistance_uohm_cm(material, temp_k, field_t, current_a_mm2=0.0):
    """Zero resistance inside the surface; normal-state value outside."""
    if is_superconducting(material, temp_k, field_t, current_a_mm2):
        return 0.0
    return _mat(material)["rho_n_uohm_cm"]


def jc_vs_temperature(material, field_t, temps_k=(0.0, 2.0, 4.2, 10.0, 20.0, 40.0, 77.0)):
    """Jc derating curve vs temperature at fixed field (deterministic table)."""
    return {f"{t:g}K": round(jc_at(material, t, field_t), 2) for t in temps_k}


def jc_vs_field(material, temp_k, fields_t=(0.0, 1.0, 3.0, 5.0, 10.0, 15.0, 20.0)):
    """Jc derating curve vs field at fixed temperature (deterministic table)."""
    return {f"{b:g}T": round(jc_at(material, temp_k, b), 2) for b in fields_t}


# ================================================================ 3. Meissner effect
# A superconductor expels magnetic field (perfect diamagnetism). The
# field that does enter decays over the London penetration depth:
#   B(x) = B0 * exp(-x / lambda),   lambda(T) = lambda0 / sqrt(1 - (T/Tc)^4)

def penetration_depth_nm(material, temp_k):
    """London penetration depth (nm) at temp_k; infinite at/above Tc."""
    m = _mat(material)
    t = temp_k / m["tc_k"]
    if t >= 1.0:
        return float("inf")
    return m["lambda0_nm"] / math.sqrt(1.0 - t ** 4)


def meissner_screening(field_t, penetration_nm, depth_nm):
    """Field remaining at depth inside the material: B = B0 exp(-x/lambda)."""
    if penetration_nm <= 0:
        raise ValueError("penetration depth must be positive")
    return field_t * math.exp(-depth_nm / penetration_nm)


def screening_percent(material, temp_k, depth_nm):
    """Percent of an applied field screened out at the given depth."""
    lam = penetration_depth_nm(material, temp_k)
    if math.isinf(lam):
        return 0.0
    return round(100.0 * (1.0 - math.exp(-depth_nm / lam)), 2)


# ================================================================ 4. Type I vs II, vortices, pinning
# Type I: complete Meissner expulsion up to one critical field, then normal.
# Type II: Meissner below Bc1, a VORTEX (mixed) state between Bc1 and Bc2
# where quantized flux lines thread the material - and can be PINNED by
# defects. Pinned vortices are the springs behind LevitationX flux pinning
# and MagLevX EDS bearings. Pinning force density limit: Fp = Jc x B.

def vortex_state(material, temp_k, field_t):
    """Meissner / vortex / normal state at this temperature and field."""
    m = _mat(material)
    if temp_k >= m["tc_k"] or field_t >= bc2_at(material, temp_k):
        return "normal"
    if m["sc_type"] == "I":
        return "Meissner (complete expulsion - Type I has no vortex state)"
    if field_t < bc1_at(material, temp_k):
        return "Meissner state (field expelled)"
    return "vortex (mixed) state - flux lines present and pinnable"


def pinning_force_density(material, temp_k, field_t):
    """Max flux-pinning force density (N/m^3) = Jc(T,B) * B (Lorentz balance)."""
    jc_si = jc_at(material, temp_k, field_t) * 1e6   # A/mm^2 -> A/m^2
    return jc_si * field_t


def pinning_pressure_pa(material, temp_k, field_t, thickness_m):
    """Levitation pressure (Pa) a pinned layer of given thickness can hold.

    This is the bridge number to LevitationX: pressure x area = lift force.
    """
    return pinning_force_density(material, temp_k, field_t) * thickness_m


def pinning_peak_field(material, temp_k):
    """Field where Fp peaks: Jc falls linearly in B, so Fp ~ B(1-B/Bc2) peaks at Bc2/2."""
    return round(bc2_at(material, temp_k) / 2.0, 4)


# ================================================================ 5. BCS energy gap
# BCS theory: Cooper pairs open an energy gap at the Fermi surface.
#   Delta(0) = 1.764 * kB * Tc        (so 2*Delta / kB*Tc = 3.528)
# Temperature dependence (standard interpolation):
#   Delta(T)/Delta(0) ~= tanh(1.74 * sqrt(Tc/T - 1))   for T < Tc

BCS_GAP_RATIO = 2.0 * 1.764   # 2*Delta(0) / (kB * Tc) = 3.528


def bcs_gap_mev(material):
    """Zero-temperature BCS gap Delta(0) in meV."""
    m = _mat(material)
    return 1.764 * KB * m["tc_k"] / EV_J * 1000.0


def gap_fraction(temp_k, tc_k):
    """Delta(T)/Delta(0) interpolation: 1 at T=0, 0 at T=Tc."""
    if temp_k <= 0.0:
        return 1.0
    if temp_k >= tc_k:
        return 0.0
    return math.tanh(1.74 * math.sqrt(tc_k / temp_k - 1.0))


def bcs_gap_at_mev(material, temp_k):
    """BCS gap (meV) at temperature temp_k."""
    m = _mat(material)
    return bcs_gap_mev(material) * gap_fraction(temp_k, m["tc_k"])


# ================================================================ 6. Cryogenics cost model
# Refrigeration is Carnot-limited: COP = T_cold / (T_hot - T_cold).
# Wall-plug watts per watt of cooling explode as T drops - that, not Tc,
# is why 77 K (LN2) and 4.2 K (LHe) superconductors live in different
# economic worlds. Practical systems reach only a fraction of Carnot;
# EFFICIENCY_OF_CARNOT = 0.20 is a labelled engineering estimate.
EFFICIENCY_OF_CARNOT = 0.20

COOLANTS = {
    "liquid helium": {"bp_k": 4.2, "rel_cost_index": 100.0, "note": "the 4 K workhorse - scarce, expensive, boils off fast"},
    "liquid hydrogen": {"bp_k": 20.3, "rel_cost_index": 30.0, "note": "20 K class - flammable, needs care"},
    "liquid neon": {"bp_k": 27.1, "rel_cost_index": 60.0, "note": "27 K class - pricey, often replaced by cryocoolers"},
    "liquid nitrogen": {"bp_k": 77.4, "rel_cost_index": 1.0, "note": "the 77 K bargain - cheaper than milk per litre, roughly"},
}


def carnot_cop(t_cold_k, t_hot_k=T_ROOM):
    """Ideal (Carnot) coefficient of performance for a refrigerator."""
    if t_cold_k <= 0 or t_cold_k >= t_hot_k:
        raise ValueError("need 0 < T_cold < T_hot")
    return t_cold_k / (t_hot_k - t_cold_k)


def ideal_wall_w_per_w(t_cold_k, t_hot_k=T_ROOM):
    """Ideal wall-plug watts needed to remove 1 W of heat at t_cold_k."""
    return 1.0 / carnot_cop(t_cold_k, t_hot_k)


def practical_wall_w_per_w(t_cold_k, t_hot_k=T_ROOM):
    """Practical wall W per cooling W at 20% of Carnot (labelled estimate)."""
    return ideal_wall_w_per_w(t_cold_k, t_hot_k) / EFFICIENCY_OF_CARNOT


def cooling_power_w(heat_load_w, t_cold_k):
    """Wall-plug watts to hold heat_load_w at t_cold_k (practical model)."""
    return heat_load_w * practical_wall_w_per_w(t_cold_k)


def coolant_for_temp(t_op_k):
    """Warmest (cheapest) listed coolant that can hold t_op_k."""
    for name in ("liquid nitrogen", "liquid neon", "liquid hydrogen", "liquid helium"):
        if COOLANTS[name]["bp_k"] <= t_op_k + 2.0:
            return name
    return "liquid helium"


def operating_point(material):
    """Suggested sim operating point: T = Tc/2, its coolant, and cooling cost."""
    m = _mat(material)
    t_op = round(0.5 * m["tc_k"], 2)
    return {
        "material": material,
        "t_op_k": t_op,
        "coolant": coolant_for_temp(t_op),
        "wall_w_per_w_at_t_op": round(practical_wall_w_per_w(t_op), 2),
        "note": "simulation operating point (Tc/2 margin rule) - not an engineering design",
        "gate": gate("real_hardware_control"),
    }


def cryo_comparison():
    """The headline economics: ideal + practical cost at 4.2 K vs 77 K."""
    return {
        "at_4.2K": {
            "carnot_cop": round(carnot_cop(4.2), 5),
            "ideal_wall_w_per_w": round(ideal_wall_w_per_w(4.2), 2),
            "practical_wall_w_per_w": round(practical_wall_w_per_w(4.2), 1),
        },
        "at_77K": {
            "carnot_cop": round(carnot_cop(77.0), 5),
            "ideal_wall_w_per_w": round(ideal_wall_w_per_w(77.0), 2),
            "practical_wall_w_per_w": round(practical_wall_w_per_w(77.0), 1),
        },
        "ideal_cost_ratio_4.2K_over_77K": round(ideal_wall_w_per_w(4.2) / ideal_wall_w_per_w(77.0), 1),
        "note": "Carnot is physics; the practical row assumes 20% of Carnot (labelled estimate)",
    }


# ================================================================ 7. Applications mapper
# Named applications as (T, B, J) requirement points. Which materials sit
# inside their critical surface there - and with how much margin - is the
# whole game of applied superconductivity.
APPLICATIONS = {
    "MRI whole-body magnet": {"t_k": 4.2, "b_t": 3.0, "j_a_mm2": 200.0,
                              "note": "NbTi's home turf for 40 years"},
    "LN2 maglev bearing (77 K)": {"t_k": 77.0, "b_t": 1.0, "j_a_mm2": 10.0,
                                  "note": "only nitrogen-temperature materials need apply"},
    "Fusion-class high field": {"t_k": 4.2, "b_t": 15.0, "j_a_mm2": 500.0,
                                "note": "beyond NbTi - Nb3Sn / HTS territory"},
    "Cryocooler instrument (20 K)": {"t_k": 20.0, "b_t": 2.0, "j_a_mm2": 100.0,
                                     "note": "no liquid cryogen - MgB2's niche"},
}


def materials_for_application(app_name):
    """Materials whose critical surface contains the application's point."""
    a = APPLICATIONS[app_name]
    return [name for name in MATERIALS
            if is_superconducting(name, a["t_k"], a["b_t"], a["j_a_mm2"])]


def application_report():
    return {app: materials_for_application(app) for app in APPLICATIONS}


# ================================================================ 8. kNN operating-point classifier
# Features are the three surface ratios (t, b, j): how close the point is
# to each wall of the critical surface. Label rule on the max ratio:
# <= 0.55 qualifies, <= 0.90 marginal, otherwise no. The kNN (k=5) is
# trained on a deterministic labelled grid and smooths the rule.

def surface_ratios(material, temp_k, field_t, current_a_mm2=0.0):
    """(T/Tc, B/Bc2(T), J/Jc(T,B)) with runaway ratios clamped to 2.0."""
    m = _mat(material)
    t_r = temp_k / m["tc_k"]
    bc2 = bc2_at(material, temp_k)
    b_r = field_t / bc2 if bc2 > 0 else 2.0
    jc = jc_at(material, temp_k, field_t)
    j_r = current_a_mm2 / jc if jc > 0 else 2.0
    return (round(min(t_r, 2.0), 4), round(min(b_r, 2.0), 4), round(min(j_r, 2.0), 4))


def _ratio_label(max_ratio):
    if max_ratio <= 0.55:
        return "qualifies"
    if max_ratio <= 0.90:
        return "marginal"
    return "no"


def _build_knn_train():
    vals = (0.1, 0.3, 0.5, 0.7, 0.9, 1.1)
    train = []
    for t in vals:
        for b in vals:
            for j in vals:
                train.append(((t, b, j), _ratio_label(max(t, b, j))))
    return train


_KNN_TRAIN = _build_knn_train()


class OperatingPointClassifier:
    """kNN (k=5) over critical-surface ratio features."""

    def __init__(self, k=5):
        self.k = k
        self.train = list(_KNN_TRAIN)

    @staticmethod
    def _dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def classify_ratios(self, ratios):
        ranked = sorted(self.train, key=lambda tr: self._dist(ratios, tr[0]))
        votes = {}
        for _, label in ranked[: self.k]:
            votes[label] = votes.get(label, 0) + 1
        return sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    def classify(self, material, temp_k, field_t, current_a_mm2=0.0):
        return self.classify_ratios(surface_ratios(material, temp_k, field_t, current_a_mm2))


def classify_point(material, temp_k, field_t, current_a_mm2=0.0):
    return OperatingPointClassifier().classify(material, temp_k, field_t, current_a_mm2)


def qualify_report(temp_k, field_t, current_a_mm2=0.0):
    """Every material's classifier verdict at one operating point."""
    clf = OperatingPointClassifier()
    return {name: clf.classify(name, temp_k, field_t, current_a_mm2) for name in MATERIALS}


# ================================================================ 9. Advisory seats
def _trace(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def carbon4_decide(topic="superconductor-lab-demo"):
    """Gemini Carbon 4 DECIDER seat: MAP->MODEL->STRESS->DECIDE.

    Names-only keys, live calls 0, tighten-only: can add HOLDs, never lift one.
    """
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    payload = {"seat": "gemini-carbon-4", "topic": topic, "stages": stages}
    return {
        "seat": "Gemini Carbon 4 Extended Thinking",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": [2048, 8192, 32768],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "can_override_hold": False,
        "tighten_only": True,
        "decision": "PROCEED (sandbox simulation only)",
        "trace_sha256_16": _trace(payload),
    }


def claude_advisor(topic="superconductor-lab-demo"):
    """Muse advisor seat: advisory only, authority none."""
    return {
        "seat": "Muse",
        "role": "advisor",
        "authority": "none - advisory only",
        "can_override_hold": False,
        "live_calls": 0,
        "advice": "Keep every real-hardware action behind its HOLD gate; claim no room-temperature superconductivity.",
        "trace_sha256_16": _trace({"seat": "claude-advisor", "topic": topic}),
    }


def google_flow_plan():
    """Google Flow: plan-only. Nothing renders, nothing is sent."""
    return {
        "seat": "Google Flow",
        "flows": ["FlowX task graph", "Workspace Studio drafts",
                  "Filmmaking 5-shot storyboard", "DataX data-flow"],
        "rendered": False,
        "live": 0,
        "plan": ["critical surface 3-D explainer", "Meissner expulsion story",
                 "vortex pinning hero shot", "4 K vs 77 K cost chart story"],
    }


def brains_report():
    return {"decider": carbon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    chk("materials_eight", len(MATERIALS) == 8)
    chk("tc_values", MATERIALS["Niobium"]["tc_k"] == 9.2 and MATERIALS["NbTi"]["tc_k"] == 9.8
        and MATERIALS["Nb3Sn"]["tc_k"] == 18.3 and MATERIALS["MgB2"]["tc_k"] == 39.0
        and MATERIALS["YBCO"]["tc_k"] == 92.0 and MATERIALS["BSCCO"]["tc_k"] == 110.0
        and MATERIALS["Mercury"]["tc_k"] == 4.15 and MATERIALS["H2S"]["tc_k"] == 203.0)
    chk("h2s_pressure_caveat", "155 GPa" in MATERIALS["H2S"]["note"])
    chk("bc2_zero_temp_is_bc2_0", abs(bc2_at("NbTi", 0.0) - 14.5) < 1e-12)
    chk("bc2_vanishes_at_tc", bc2_at("NbTi", 9.8) == 0.0)
    chk("bc2_falls_with_temp", bc2_at("YBCO", 20.0) > bc2_at("YBCO", 60.0) > 0.0)
    chk("state_inside_surface", superconducting_state("NbTi", 4.2, 5.0, 100.0) == "superconducting")
    chk("state_above_tc", superconducting_state("NbTi", 77.0, 0.0).startswith("normal"))
    chk("state_above_bc2", superconducting_state("Niobium", 4.2, 1.0).startswith("normal"))
    chk("state_above_jc", superconducting_state("NbTi", 4.2, 5.0, 100000.0).startswith("normal"))
    chk("resistance_zero_in_surface", resistance_uohm_cm("YBCO", 77.0, 1.0, 10.0) == 0.0)
    chk("resistance_normal_outside", resistance_uohm_cm("YBCO", 300.0, 0.0) == 100.0)
    chk("jc_zero_field_temp_origin", abs(jc_at("Nb3Sn", 0.0, 0.0) - 5000.0) < 1e-9)
    chk("jc_derates_with_temp", jc_at("NbTi", 2.0, 3.0) > jc_at("NbTi", 6.0, 3.0) > 0.0)
    chk("jc_derates_with_field", jc_at("NbTi", 4.2, 1.0) > jc_at("NbTi", 4.2, 8.0) > 0.0)
    chk("jc_zero_above_bc2", jc_at("NbTi", 4.2, 20.0) == 0.0)
    chk("lambda_at_zero_is_lambda0", abs(penetration_depth_nm("YBCO", 0.0) - 150.0) < 1e-9)
    chk("lambda_grows_with_temp", penetration_depth_nm("YBCO", 80.0) > penetration_depth_nm("YBCO", 20.0))
    chk("lambda_infinite_at_tc", math.isinf(penetration_depth_nm("YBCO", 92.0)))
    chk("meissner_one_lambda_is_1_over_e",
        abs(meissner_screening(1.0, 150.0, 150.0) - math.exp(-1.0)) < 1e-12)
    chk("meissner_deep_is_screened", screening_percent("NbTi", 4.2, 2400.0) > 99.9)
    chk("type1_no_vortex_state", vortex_state("Mercury", 2.0, 0.01).startswith("Meissner"))
    chk("type1_normal_above_bc", vortex_state("Mercury", 2.0, 0.05) == "normal")
    chk("type2_meissner_band", vortex_state("NbTi", 4.2, 0.001).startswith("Meissner"))
    chk("type2_vortex_band", vortex_state("NbTi", 4.2, 5.0).startswith("vortex"))
    chk("type2_normal_above_bc2", vortex_state("NbTi", 4.2, 20.0) == "normal")
    chk("pinning_zero_at_zero_field", pinning_force_density("YBCO", 77.0, 0.0) == 0.0)
    chk("pinning_peak_at_half_bc2",
        pinning_force_density("NbTi", 4.2, pinning_peak_field("NbTi", 4.2))
        > pinning_force_density("NbTi", 4.2, pinning_peak_field("NbTi", 4.2) / 2.0))
    chk("pinning_pressure_positive", pinning_pressure_pa("YBCO", 77.0, 1.0, 0.002) > 0.0)
    chk("bcs_gap_ybco_mev", 13.0 < bcs_gap_mev("YBCO") < 15.0)
    chk("bcs_gap_nb_mev", 1.3 < bcs_gap_mev("Niobium") < 1.5)
    chk("bcs_gap_ratio_3528", abs(BCS_GAP_RATIO - 3.528) < 1e-12)
    chk("gap_full_at_zero", gap_fraction(0.0, 92.0) == 1.0)
    chk("gap_zero_at_tc", gap_fraction(92.0, 92.0) == 0.0)
    chk("gap_shrinks_with_temp", bcs_gap_at_mev("YBCO", 20.0) > bcs_gap_at_mev("YBCO", 80.0) > 0.0)
    chk("carnot_cop_4.2k", abs(carnot_cop(4.2) - 4.2 / 295.8) < 1e-12)
    chk("carnot_cop_77k", abs(carnot_cop(77.0) - 77.0 / 223.0) < 1e-12)
    chk("cryo_ratio_over_20x", cryo_comparison()["ideal_cost_ratio_4.2K_over_77K"] > 20.0)
    chk("cooling_power_positive", cooling_power_w(1.0, 4.2) > cooling_power_w(1.0, 77.0) > 0.0)
    chk("coolant_nbti_is_helium", operating_point("NbTi")["coolant"] == "liquid helium")
    chk("coolant_77k_is_nitrogen", coolant_for_temp(77.0) == "liquid nitrogen")
    chk("mri_uses_nbti_not_nb",
        "NbTi" in materials_for_application("MRI whole-body magnet")
        and "Niobium" not in materials_for_application("MRI whole-body magnet"))
    chk("ln2_bearing_needs_htc",
        "YBCO" in materials_for_application("LN2 maglev bearing (77 K)")
        and "MgB2" not in materials_for_application("LN2 maglev bearing (77 K)"))
    chk("fusion_needs_nb3sn",
        "Nb3Sn" in materials_for_application("Fusion-class high field")
        and "NbTi" not in materials_for_application("Fusion-class high field"))
    chk("classifier_nbti_qualifies", classify_point("NbTi", 4.2, 5.0, 100.0) == "qualifies")
    chk("classifier_ybco_77k_marginal", classify_point("YBCO", 77.0, 1.0, 10.0) == "marginal")
    chk("classifier_mercury_warm_no", classify_point("Mercury", 77.0, 1.0, 10.0) == "no")
    chk("qualify_report_all_materials", len(qualify_report(4.2, 3.0, 200.0)) == 8)
    chk("hold_gates_14", len(HOLD_GATES) == 14 and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_room_temp_claim_hold", gate("room_temperature_superconductor_claim") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    b = brains_report()
    chk("carbon4_no_override", b["decider"]["can_override_hold"] is False)
    chk("claude_no_override", b["advisor"]["can_override_hold"] is False)
    chk("flow_plan_only", b["flow"]["rendered"] is False and b["flow"]["live"] == 0)
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("Superconductor-Lab - superconductor physics & materials lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | SIM ONLY")
    print("=" * 68)
    print("\n[1] The materials (Tc / Bc2(0) / type)")
    for name, m in MATERIALS.items():
        print(f"    {name:9s} {m['formula']:20s} Tc = {m['tc_k']:6.2f} K  Bc2 = {m['bc2_t']:6.2f} T  Type {m['sc_type']}")
    print("    H2S note: 203 K ONLY at ~155 GPa - pressure caveat, not ambient.")
    print("\n[2] The critical surface - superconducting only INSIDE (T, B, J)")
    print(f"    NbTi @ 4.2 K, 5 T, 100 A/mm^2: {superconducting_state('NbTi', 4.2, 5.0, 100.0)}")
    print(f"    NbTi @ 77 K:                   {superconducting_state('NbTi', 77.0, 0.0)}")
    print(f"    YBCO @ 77 K, 1 T, 10 A/mm^2:   {superconducting_state('YBCO', 77.0, 1.0, 10.0)}")
    print(f"    resistance YBCO @ 77 K in surface = {resistance_uohm_cm('YBCO', 77.0, 1.0, 10.0)} uOhm cm (zero!)")
    print(f"    Bc2 of NbTi falls with T: 0 K -> {bc2_at('NbTi', 0.0)} T, 6 K -> {round(bc2_at('NbTi', 6.0), 2)} T")
    print("\n[3] Meissner effect + London penetration depth")
    print(f"    YBCO lambda: 0 K = {penetration_depth_nm('YBCO', 0.0)} nm, 80 K = {round(penetration_depth_nm('YBCO', 80.0), 1)} nm")
    print(f"    field left one lambda deep = {round(meissner_screening(1.0, 150.0, 150.0), 4)} of applied (1/e)")
    print(f"    NbTi @ 4.2 K screens {screening_percent('NbTi', 4.2, 2400.0)}% of field 2.4 um deep")
    print("\n[4] Type I vs Type II + the vortex state")
    print(f"    Mercury @ 2 K, 0.01 T: {vortex_state('Mercury', 2.0, 0.01)}")
    print(f"    NbTi @ 4.2 K, 0.001 T: {vortex_state('NbTi', 4.2, 0.001)}")
    print(f"    NbTi @ 4.2 K, 5 T:     {vortex_state('NbTi', 4.2, 5.0)}")
    print("\n[5] Flux pinning - the bridge to LevitationX / MagLevX")
    print(f"    YBCO @ 77 K, 1 T pinning pressure (2 mm layer) = {round(pinning_pressure_pa('YBCO', 77.0, 1.0, 0.002), 1)} Pa")
    print(f"    NbTi pinning force peaks at B = {pinning_peak_field('NbTi', 4.2)} T (Bc2(T)/2)")
    print("\n[6] BCS energy gap: Delta(0) = 1.764 kB Tc, 2Delta/kBTc = 3.528")
    print(f"    Nb gap = {round(bcs_gap_mev('Niobium'), 3)} meV | YBCO gap = {round(bcs_gap_mev('YBCO'), 2)} meV")
    print(f"    YBCO gap @ 80 K = {round(bcs_gap_at_mev('YBCO', 80.0), 2)} meV (shrinks toward Tc)")
    print("\n[7] Critical current derating (NbTi, A/mm^2)")
    print(f"    vs temperature @ 3 T: {jc_vs_temperature('NbTi', 3.0)}")
    print(f"    vs field @ 4.2 K:     {jc_vs_field('NbTi', 4.2)}")
    print("\n[8] Cryogenics economics (Carnot + 20%-of-Carnot practical estimate)")
    cc = cryo_comparison()
    print(f"    4.2 K: ideal {cc['at_4.2K']['ideal_wall_w_per_w']} wall W per cooling W, practical ~{cc['at_4.2K']['practical_wall_w_per_w']}")
    print(f"    77 K:  ideal {cc['at_77K']['ideal_wall_w_per_w']} wall W per cooling W, practical ~{cc['at_77K']['practical_wall_w_per_w']}")
    print(f"    cooling at 4.2 K costs ~{cc['ideal_cost_ratio_4.2K_over_77K']}x the wall power of 77 K - the LN2/LHe divide")
    print(f"    NbTi operating point: {json.dumps(operating_point('NbTi'), sort_keys=True)}")
    print("\n[9] Applications mapper - who fits inside the surface?")
    for app, mats in application_report().items():
        print(f"    {app:32s} -> {', '.join(mats) if mats else 'nobody'}")
    print("\n[10] Operating-point classifier (TinyML kNN on surface ratios)")
    for name, label in qualify_report(4.2, 3.0, 200.0).items():
        print(f"    {name:9s} @ 4.2 K, 3 T, 200 A/mm^2 -> {label}")
    print("\n[11] Advisory seats")
    print(f"    decider: {carbon4_decide()['decision']} trace={carbon4_decide()['trace_sha256_16']}")
    print(f"    advisor can_override_hold = {claude_advisor()['can_override_hold']}")
    print(f"    flow rendered = {google_flow_plan()['rendered']} live = {google_flow_plan()['live']}")
    print(f"\n[12] HOLD gates: {len(HOLD_GATES)}")
    for k in HOLD_GATES:
        print(f"    HOLD  {k}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "materials":
        print(json.dumps(MATERIALS, indent=2, sort_keys=True))
        return 0
    if cmd == "surface":
        for name in MATERIALS:
            print(f"{name:9s} @ 4.2 K, 3 T, 200 A/mm^2: {superconducting_state(name, 4.2, 3.0, 200.0)}")
        return 0
    if cmd == "meissner":
        for name in ("Niobium", "NbTi", "YBCO"):
            print(f"{name:9s} lambda(0) = {penetration_depth_nm(name, 0.0)} nm, "
                  f"lambda(Tc/2) = {round(penetration_depth_nm(name, MATERIALS[name]['tc_k'] / 2.0), 1)} nm")
        return 0
    if cmd == "vortices":
        for b in (0.001, 0.1, 1.0, 5.0, 12.0, 20.0):
            print(f"NbTi @ 4.2 K, {b} T: {vortex_state('NbTi', 4.2, b)}")
        return 0
    if cmd == "gap":
        for name in MATERIALS:
            print(f"{name:9s} Delta(0) = {round(bcs_gap_mev(name), 3)} meV")
        return 0
    if cmd == "cryo":
        print(json.dumps(cryo_comparison(), indent=2, sort_keys=True))
        for name in MATERIALS:
            print(f"{name:9s} {json.dumps(operating_point(name), sort_keys=True)}")
        return 0
    if cmd == "apps":
        print(json.dumps(application_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "classify":
        print(json.dumps(qualify_report(4.2, 3.0, 200.0), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for k, v in HOLD_GATES.items():
            print(f"{k}: {v}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "room_temperature_superconductor_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
