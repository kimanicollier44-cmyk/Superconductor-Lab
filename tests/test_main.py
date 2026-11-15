import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main as sc


def test_materials_eight(): assert len(sc.MATERIALS) == 8
def test_tc_table():
    assert sc.MATERIALS["Niobium"]["tc_k"] == 9.2 and sc.MATERIALS["NbTi"]["tc_k"] == 9.8
    assert sc.MATERIALS["Nb3Sn"]["tc_k"] == 18.3 and sc.MATERIALS["MgB2"]["tc_k"] == 39.0
    assert sc.MATERIALS["YBCO"]["tc_k"] == 92.0 and sc.MATERIALS["BSCCO"]["tc_k"] == 110.0
    assert sc.MATERIALS["Mercury"]["tc_k"] == 4.15 and sc.MATERIALS["H2S"]["tc_k"] == 203.0
def test_h2s_pressure_caveat(): assert "155 GPa" in sc.MATERIALS["H2S"]["note"]
def test_bc2_at_zero(): assert abs(sc.bc2_at("NbTi", 0.0) - 14.5) < 1e-12
def test_bc2_at_tc_zero(): assert sc.bc2_at("NbTi", 9.8) == 0.0
def test_bc2_falls_with_temp(): assert sc.bc2_at("YBCO", 20.0) > sc.bc2_at("YBCO", 60.0) > 0.0
def test_bc2_quadratic_form(): assert abs(sc.bc2_at("NbTi", 4.9) - 14.5 * (1 - 0.25)) < 1e-9
def test_state_inside(): assert sc.superconducting_state("NbTi", 4.2, 5.0, 100.0) == "superconducting"
def test_state_above_tc(): assert sc.superconducting_state("NbTi", 77.0, 0.0).startswith("normal")
def test_state_above_bc2(): assert sc.superconducting_state("Niobium", 4.2, 1.0).startswith("normal")
def test_state_above_jc(): assert sc.superconducting_state("NbTi", 4.2, 5.0, 100000.0).startswith("normal")
def test_is_superconducting_bool(): assert sc.is_superconducting("YBCO", 77.0, 1.0, 10.0) is True
def test_resistance_zero(): assert sc.resistance_uohm_cm("YBCO", 77.0, 1.0, 10.0) == 0.0
def test_resistance_normal(): assert sc.resistance_uohm_cm("YBCO", 300.0, 0.0) == 100.0
def test_jc_origin(): assert abs(sc.jc_at("Nb3Sn", 0.0, 0.0) - 5000.0) < 1e-9
def test_jc_derates_temp(): assert sc.jc_at("NbTi", 2.0, 3.0) > sc.jc_at("NbTi", 6.0, 3.0) > 0.0
def test_jc_derates_field(): assert sc.jc_at("NbTi", 4.2, 1.0) > sc.jc_at("NbTi", 4.2, 8.0) > 0.0
def test_jc_zero_above_bc2(): assert sc.jc_at("NbTi", 4.2, 20.0) == 0.0
def test_jc_curves_shape():
    ct = sc.jc_vs_temperature("NbTi", 3.0); cf = sc.jc_vs_field("NbTi", 4.2)
    assert len(ct) == 7 and len(cf) == 7 and ct["0K"] > ct["4.2K"] and cf["0T"] > cf["20T"]
def test_lambda_zero(): assert abs(sc.penetration_depth_nm("YBCO", 0.0) - 150.0) < 1e-9
def test_lambda_grows(): assert sc.penetration_depth_nm("YBCO", 80.0) > sc.penetration_depth_nm("YBCO", 20.0)
def test_lambda_half_tc():
    assert abs(sc.penetration_depth_nm("YBCO", 46.0) - 150.0 / math.sqrt(1 - 0.0625)) < 1e-9
def test_lambda_inf_at_tc(): assert math.isinf(sc.penetration_depth_nm("YBCO", 92.0))
def test_meissner_exp(): assert abs(sc.meissner_screening(1.0, 150.0, 150.0) - math.exp(-1)) < 1e-12
def test_meissner_surface_full(): assert sc.meissner_screening(2.0, 150.0, 0.0) == 2.0
def test_screening_percent(): assert sc.screening_percent("NbTi", 4.2, 2400.0) > 99.9
def test_screening_normal_zero(): assert sc.screening_percent("NbTi", 300.0, 100.0) == 0.0
def test_type1_meissner(): assert sc.vortex_state("Mercury", 2.0, 0.01).startswith("Meissner")
def test_type1_normal(): assert sc.vortex_state("Mercury", 2.0, 0.05) == "normal"
def test_type2_meissner(): assert sc.vortex_state("NbTi", 4.2, 0.001).startswith("Meissner")
def test_type2_vortex(): assert sc.vortex_state("NbTi", 4.2, 5.0).startswith("vortex")
def test_type2_normal(): assert sc.vortex_state("NbTi", 4.2, 20.0) == "normal"
def test_bc1_type1_zero(): assert sc.bc1_at("Mercury", 2.0) == 0.0
def test_pinning_zero_field(): assert sc.pinning_force_density("YBCO", 77.0, 0.0) == 0.0
def test_pinning_peak():
    pk = sc.pinning_peak_field("NbTi", 4.2)
    assert sc.pinning_force_density("NbTi", 4.2, pk) > sc.pinning_force_density("NbTi", 4.2, pk / 2.0)
def test_pinning_pressure(): assert sc.pinning_pressure_pa("YBCO", 77.0, 1.0, 0.002) > 0.0
def test_gap_ybco(): assert 13.0 < sc.bcs_gap_mev("YBCO") < 15.0
def test_gap_nb(): assert 1.3 < sc.bcs_gap_mev("Niobium") < 1.5
def test_gap_scales_with_tc():
    assert abs(sc.bcs_gap_mev("YBCO") / sc.bcs_gap_mev("Niobium") - 92.0 / 9.2) < 1e-9
def test_gap_ratio(): assert abs(sc.BCS_GAP_RATIO - 3.528) < 1e-12
def test_gap_fraction_ends(): assert sc.gap_fraction(0.0, 92.0) == 1.0 and sc.gap_fraction(92.0, 92.0) == 0.0
def test_gap_at_temp(): assert sc.bcs_gap_at_mev("YBCO", 20.0) > sc.bcs_gap_at_mev("YBCO", 80.0) > 0.0
def test_carnot_4k(): assert abs(sc.carnot_cop(4.2) - 4.2 / 295.8) < 1e-12
def test_carnot_77k(): assert abs(sc.carnot_cop(77.0) - 77.0 / 223.0) < 1e-12
def test_cryo_ratio(): assert sc.cryo_comparison()["ideal_cost_ratio_4.2K_over_77K"] > 20.0
def test_cooling_power_order(): assert sc.cooling_power_w(1.0, 4.2) > sc.cooling_power_w(1.0, 77.0) > 0.0
def test_coolant_helium(): assert sc.operating_point("NbTi")["coolant"] == "liquid helium"
def test_coolant_nitrogen(): assert sc.coolant_for_temp(77.0) == "liquid nitrogen"
def test_coolant_neon_band(): assert sc.coolant_for_temp(30.0) == "liquid neon"
def test_app_mri():
    mats = sc.materials_for_application("MRI whole-body magnet")
    assert "NbTi" in mats and "Niobium" not in mats and "Mercury" not in mats
def test_app_ln2():
    mats = sc.materials_for_application("LN2 maglev bearing (77 K)")
    assert "YBCO" in mats and "BSCCO" in mats and "MgB2" not in mats
def test_app_fusion():
    mats = sc.materials_for_application("Fusion-class high field")
    assert "Nb3Sn" in mats and "NbTi" not in mats
def test_app_cryocooler():
    mats = sc.materials_for_application("Cryocooler instrument (20 K)")
    assert "MgB2" in mats and "Nb3Sn" not in mats
def test_classifier_qualifies(): assert sc.classify_point("NbTi", 4.2, 5.0, 100.0) == "qualifies"
def test_classifier_marginal(): assert sc.classify_point("YBCO", 77.0, 1.0, 10.0) == "marginal"
def test_classifier_no(): assert sc.classify_point("Mercury", 77.0, 1.0, 10.0) == "no"
def test_surface_ratios_clamped():
    r = sc.surface_ratios("Mercury", 300.0, 5.0, 10.0)
    assert r[0] == 2.0 and all(0.0 <= x <= 2.0 for x in r)
def test_qualify_report(): assert len(sc.qualify_report(4.2, 3.0, 200.0)) == 8
def test_holds_count(): assert len(sc.HOLD_GATES) == 14
def test_holds_all_hold(): assert all(v.startswith("HOLD") for v in sc.HOLD_GATES.values())
def test_gate():
    assert sc.gate("room_temperature_superconductor_claim") == "HOLD"
    assert sc.gate("run_simulation") == "PROCEED"
def test_hold_demo_exit_code(): assert sc.main(["hold-demo", "quench_experiment_live"]) == 2
def test_hold_demo_ungated(): assert sc.main(["hold-demo", "run_simulation"]) == 0
def test_carbon4():
    d = sc.carbon4_decide()
    assert d["can_override_hold"] is False and d["live_calls"] == 0 and len(d["trace_sha256_16"]) == 16
    assert d["pipeline"] == ["MAP", "MODEL", "STRESS", "DECIDE"] and d["tighten_only"] is True
def test_claude(): assert sc.claude_advisor()["can_override_hold"] is False
def test_flow():
    f = sc.google_flow_plan(); assert f["rendered"] is False and f["live"] == 0
def test_checks_all_pass():
    checks = sc.run_checks(); assert all(ok for _, ok in checks), [n for n, ok in checks if not ok]
def test_checks_count(): assert len(sc.run_checks()) == 54
def test_deterministic_jc(): assert sc.jc_vs_field("NbTi", 4.2) == sc.jc_vs_field("NbTi", 4.2)
def test_deterministic_classifier():
    assert sc.qualify_report(4.2, 3.0, 200.0) == sc.qualify_report(4.2, 3.0, 200.0)
def test_demo_exit_zero(capsys):
    assert sc.main([]) == 0
    out = capsys.readouterr().out
    assert "CHECKS 54/54" in out and "VERDICT PROCEED" in out
