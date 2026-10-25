# 🗺️ CODE_MAP — RGON shin-agent 코드 지도

<!-- [RGON-STATUS-V25-START] -->
> **RGON 상태:** v11.39-AON-NEURAL-SYNAPSE · 항체 R1~R40 · 정식 스킬 36개 · 제16기관 신경망 시냅스 검증기 개통
<!-- [RGON-STATUS-V25-END] -->

> 자동 생성: `step16_karpathy_codemap_and_eod.py` · 2026-10-23 22:29:07 KST · 손으로 수정하지 말고 스크립트를 다시 실행할 것
> 스캔 제외: `.git`, `node_modules`, `__pycache__`, `_rgon_backups`, 백업 폴더, `*.bak*` 파일

## 🧭 새 AI 세션 30초 가이드
1. `CLAUDE.md` — 코딩 헌법(4대 원칙) 먼저 읽기
2. 이 파일 — 아래 **마커 인덱스**로 어떤 스크립트가 어떤 HTML 구간을 관리하는지 확인
3. `rgon_brain_snapshot.json` — 현재 버전·항체·오늘 성과
4. `RGON_EVOLUTION_LOG.md` — 최신 진화 기록
5. 수정 대상 파일만 실제로 열어서 확인한 뒤 작업 (전체 파일을 다 읽을 필요 없음)

## 📊 요약
| 구분 | 파일 수 |
|---|---|
| Python (.py) | 551 |
| HTML | 6 |
| JavaScript (.js) | 3 |
| JSON | 40 |
| **합계** | **600 (5.0MB)** |

## 🌳 트리
```
shin-agent/
├── .temp_s_0.js  (769B)
├── a4_a5_snapshot_output.json  (8.5KB)
├── activate_brain_and_push.py  (51.2KB)
├── active_design_theme.json  (412B)
├── active_external_tunnel.json  (348B)
├── add_error_event_test.py  (2.6KB)
├── add_test_node.py  (3.5KB)
├── agency_stage_gate_master.json  (12.4KB)
├── agency_stage_gate_scheduler.py  (5.9KB)
├── agent_swarm_cloner.py  (12.5KB)
├── amend_design1.py  (1.6KB)
├── analyze_feed_all.py  (2.7KB)
├── analyze_scratch_logs.py  (902B)
├── anchongri_exec_queue.json  (3B)
├── apply_50c_doc.py  (1.1KB)
├── apply_52c_doc.py  (1.1KB)
├── apply_account_state_optimization.py  (3.3KB)
├── apply_all_fixes.py  (7.3KB)
├── apply_backlog19_fix.py  (6.8KB)
├── apply_backlog2_core.py  (7.4KB)
├── apply_backlog50.py  (879B)
├── apply_blocker_fixes.py  (8.9KB)
├── apply_closing_fixes.py  (5.2KB)
├── apply_combined_docs.py  (2.0KB)
├── apply_commit1.py  (4.8KB)
├── apply_commit2.py  (3.0KB)
├── apply_commit4.py  (4.2KB)
├── apply_commit5.py  (748B)
├── apply_d3_and_b1.py  (12.9KB)
├── apply_deduplication_updates.py  (11.5KB)
├── apply_defect14_fix.py  (6.7KB)
├── apply_defect47_fail_closed.py  (4.4KB)
├── apply_defect51.py  (1.5KB)
├── apply_defect54_null_guard.py  (1.8KB)
├── apply_defects_27_28.py  (3.4KB)
├── apply_defects_28_29_30.py  (6.3KB)
├── apply_defects_35_40.py  (2.9KB)
├── apply_defects_52_53.py  (5.3KB)
├── apply_defects_71_75.py  (14.5KB)
├── apply_design1_and_defect15.py  (6.0KB)
├── apply_design3_and_defect43.py  (5.5KB)
├── apply_design3_full.py  (3.8KB)
├── apply_dry_run_accepted_patch.py  (2.4KB)
├── apply_exact_scheduler_patch.py  (9.0KB)
├── apply_final_refinements.py  (4.8KB)
├── apply_full_fixes_turn19.py  (10.1KB)
├── apply_hourly_scan_fix.py  (751B)
├── apply_listener_followups.py  (5.2KB)
├── apply_m4_b_prime.py  (10.7KB)
├── apply_m5_clean.py  (8.3KB)
├── apply_m5_gate.py  (3.0KB)
├── apply_mute_removal_only.py  (7.2KB)
├── apply_n1.py  (897B)
├── apply_null_defaults.py  (6.3KB)
├── apply_opatch1_ms.py  (6.3KB)
├── apply_opatch1_safe.py  (3.7KB)
├── apply_p34_fixes.py  (3.8KB)
├── apply_part_a_patch.py  (3.0KB)
├── apply_patch_56.py  (654B)
├── apply_patch_57a.py  (3.5KB)
├── apply_patch_57b.py  (2.3KB)
├── apply_patch_57c.py  (1.6KB)
├── apply_patches_and_benchmark.py  (7.4KB)
├── apply_rebalance_patch.py  (2.1KB)
├── apply_round3j_doc_updates.py  (9.9KB)
├── apply_scheduler_clean.py  (3.3KB)
├── apply_scheduler_enhancements.py  (10.8KB)
├── apply_scheduler_patch.py  (6.0KB)
├── apply_scheduler_timeout.py  (2.3KB)
├── apply_sd_to_stock.py  (3.8KB)
├── apply_telegram_patch.py  (3.2KB)
├── apply_turn18_fixes.py  (8.3KB)
├── apply_turn22_fixes.py  (7.3KB)
├── apply_turn23_fixes.py  (8.1KB)
├── apply_turn24_fixes.py  (4.9KB)
├── apply_turn25_fixes.py  (3.1KB)
├── apply_turn26_fixes.py  (2.7KB)
├── apply_turn27_fixes.py  (5.1KB)
├── apply_turn28_fixes.py  (2.6KB)
├── apply_turn29_fixes.py  (9.6KB)
├── apply_turn30_fixes.py  (7.1KB)
├── apply_turn31_fixes.py  (8.1KB)
├── apply_turn32_fixes.py  (7.0KB)
├── apply_turn33_fixes.py  (14.4KB)
├── apply_turn34_fixes.py  (4.4KB)
├── apply_turn35_fixes.py  (6.4KB)
├── apply_turn36_fixes.py  (6.9KB)
├── apply_turn37_fixes.py  (5.0KB)
├── apply_turn38_fixes.py  (9.3KB)
├── apply_turn38_full.py  (9.1KB)
├── apply_v605_fix.py  (8.4KB)
├── apply_v606_lock.py  (12.1KB)
├── aside_drawer.js  (24.3KB)
├── aside_local_memory.json  (24.9KB)
├── audit_a12_all.py  (5.5KB)
├── audit_a13_all.py  (10.5KB)
├── audit_a14_all.py  (12.2KB)
├── audit_a15_all.py  (16.6KB)
├── audit_turn8.py  (3.2KB)
├── audit_turn9.py  (4.7KB)
├── auto_company_loop.py  (8.5KB)
├── auto_exec_latest.py  (45.4KB)
├── auto_production_queue.json  (4.9KB)
├── auto_write_to_5_google_sheets.py  (12.4KB)
├── benchmark_n3.py  (2.8KB)
├── benchmark_n3_ext.py  (2.7KB)
├── benchmark_r2.py  (2.1KB)
├── build_omni_link_communicator.py  (82.6KB)
├── build_real_aside_ext.py  (5.9KB)
├── capture_pytest_complete.py  (801B)
├── channel_agent.py  (32.3KB)
├── check_analysis.py  (391B)
├── check_apscheduler.py  (214B)
├── check_bb_values.py  (791B)
├── check_broker_client.py  (268B)
├── check_defect14_sources.py  (1.4KB)
├── check_empty_err.py  (390B)
├── check_err_card.py  (812B)
├── check_fallbacks.py  (561B)
├── check_final_state.py  (1.5KB)
├── check_fn.py  (592B)
├── check_fresh_live.py  (2.5KB)
├── check_imports.py  (649B)
├── check_indent.py  (360B)
├── check_jpm_price.py  (481B)
├── check_k.py  (1.3KB)
├── check_ms_test.py  (298B)
├── check_n1c_inst.py  (516B)
├── check_pytest_output.py  (536B)
├── check_risk_route.py  (278B)
├── check_routes.py  (1.0KB)
├── check_signal.py  (907B)
├── check_stock_route.py  (282B)
├── check_task_logs.py  (595B)
├── check_verify_a32.py  (455B)
├── check_verify_output.py  (443B)
├── check_보정62.py  (873B)
├── cheongwadae_comm_engine.py  (23.5KB)
├── cheongwadae_comm_log.json  (21.8KB)
├── cheongwadae_golden_hashes.json  (3.5KB)
├── cheongwadae_guard.py  (10.0KB)
├── clean_base_weights.py  (1.5KB)
├── clean_conf_maps.py  (891B)
├── clean_func_safe.py  (1.0KB)
├── clean_isolated_metrics.json  (8.9KB)
├── clean_master_signal.py  (3.8KB)
├── clean_slashes.py  (332B)
├── clean_ui.py  (19.9KB)
├── cleanup_and_docs.py  (2.4KB)
├── collect_f_items.py  (3.0KB)
├── collect_top1_ingredients.py  (6.3KB)
├── commit_p34_fixes.py  (1.5KB)
├── compare_p26_p27.py  (1.9KB)
├── connect_ai_cloud_corps.py  (24.6KB)
├── control_tower_bot.py  (12.5KB)
├── copy_telegram.py  (231B)
├── create_desktop_shortcut.py  (1.5KB)
├── create_migration_package.py  (8.5KB)
├── create_new_tests.py  (4.0KB)
├── create_regression_tests.py  (3.6KB)
├── create_test_alert.py  (2.6KB)
├── create_test_counter.py  (1.8KB)
├── cross_dept_synergy_engine.py  (26.3KB)
├── deep_duplicate_scan.py  (2.3KB)
├── deep_sweep_final_purger.py  (16.6KB)
├── delete_todo_sheet.py  (1.5KB)
├── department_work_queue.json  (12.6KB)
├── dept_mission_backlog.py  (18.4KB)
├── dept_sub_agents_corps.py  (17.1KB)
├── dept_sub_agents_state.json  (7.2KB)
├── diagnose_fail.py  (945B)
├── dump_0939.py  (379B)
├── dump_4193.py  (346B)
├── dump_account_state.py  (193B)
├── dump_client.py  (270B)
├── dump_exact.py  (327B)
├── dump_listener.py  (300B)
├── dump_p40_artifacts.py  (1.1KB)
├── dump_p42_details.py  (877B)
├── dump_p43_details.py  (979B)
├── dump_p44_all.py  (1.4KB)
├── dump_pod.py  (310B)
├── dump_pod_def.py  (307B)
├── dump_scan_result.py  (271B)
├── dump_scanner_methods.py  (277B)
├── dump_sched_709.py  (269B)
├── dump_sched_run.py  (470B)
├── dump_sched_throttle.py  (397B)
├── dump_stop_loss_code.py  (269B)
├── dump_target_lines.py  (707B)
├── dump_task_logs.py  (585B)
├── dump_telegram.py  (287B)
├── dump_verify_ps1.py  (206B)
├── ecc_pipeline_engine.py  (5.9KB)
├── ecc_skills_vault.json  (2.2KB)
├── evolution_memory.json  (7.0KB)
├── export_secrets_helper.py  (3.1KB)
├── external_kitchen_worker.py  (25.7KB)
├── extract_and_check.py  (571B)
├── extract_literals_p30.py  (2.2KB)
├── extract_live_pod.py  (2.3KB)
├── extract_live_pod_accurate.py  (2.5KB)
├── extract_n1_bodies.py  (558B)
├── fast_patch_1.py  (1.6KB)
├── fast_patch_3.py  (4.5KB)
├── fast_patch_5.py  (5.6KB)
├── fast_patch_6.py  (4.2KB)
├── fast_patch_7.py  (6.7KB)
├── fast_patch_8.py  (4.3KB)
├── fetch_raw_posts.py  (1.2KB)
├── fetch_route_signals.py  (1.3KB)
├── final_round_check.py  (1.6KB)
├── find_broker_loop.py  (381B)
├── find_canvas_positions.py  (427B)
├── find_listener.py  (324B)
├── find_logs.py  (776B)
├── find_nvda_paths.py  (1.3KB)
├── find_order_routes.py  (1.1KB)
├── find_pod_classes.py  (343B)
├── find_scheduler_bits.py  (365B)
├── find_scheduler_lines.py  (396B)
├── find_sl_mutations.py  (743B)
├── find_throttle.py  (365B)
├── find_trading_files.py  (691B)
├── finish_boot.py  (1.6KB)
├── fix_17_and_locate_01_02.py  (2.2KB)
├── fix_accepted_live_guard.py  (2.3KB)
├── fix_ad_host.py  (3.8KB)
├── fix_ad_popup_studio.py  (5.2KB)
├── fix_and_generate_p44.py  (3.5KB)
├── fix_and_verify_d3.py  (5.4KB)
├── fix_app_null_guards.py  (1.8KB)
├── fix_app_residual_fallbacks.py  (1.9KB)
├── fix_auto_sync_master.py  (44.2KB)
├── fix_backtester_weights.py  (1.2KB)
├── fix_bb_syntax.py  (1.1KB)
├── fix_boot_now.py  (2.2KB)
├── fix_comp_name.py  (731B)
├── fix_component_score_sig.py  (2.9KB)
├── fix_components_exact.py  (5.2KB)
├── fix_components_grid.py  (7.9KB)
├── fix_conf_65.py  (2.7KB)
├── fix_conf_var.py  (1.3KB)
├── fix_corr_and_api.py  (2.3KB)
├── fix_cs_ms.py  (1.5KB)
├── fix_datetime_patch.py  (1001B)
├── fix_debt.py  (1.9KB)
├── fix_defect48_returns.py  (3.5KB)
├── fix_defect59_pkg.py  (1.6KB)
├── fix_err_test_import.py  (753B)
├── fix_event_msg.py  (2.8KB)
├── fix_final_corr.py  (1.1KB)
├── fix_flush_indent.py  (628B)
├── fix_function_injection.py  (3.3KB)
├── fix_grid_and_kelly.py  (13.5KB)
├── fix_inv_caller.py  (1.7KB)
├── fix_inv_def.py  (1.4KB)
├── fix_inv_exact.py  (1.4KB)
├── fix_inv_score.py  (841B)
├── fix_kc.py  (429B)
├── fix_kc_defaults.py  (2.1KB)
├── fix_kc_insert.py  (1.4KB)
├── fix_kelly_calls.py  (2.6KB)
├── fix_kelly_ceiling.py  (1.6KB)
├── fix_kelly_dataclass.py  (1.1KB)
├── fix_kelly_final.py  (1.6KB)
├── fix_kelly_identity.py  (2.3KB)
├── fix_kelly_sig.py  (1.3KB)
├── fix_leaders_clean.py  (966B)
├── fix_llm_conf_field.py  (1.5KB)
├── fix_lock.py  (759B)
├── fix_main_import.py  (1.3KB)
├── fix_mock_trader.py  (531B)
├── fix_mock_trader_exact.py  (1.3KB)
├── fix_ms_dataclass.py  (945B)
├── fix_ms_dc_avail.py  (1.4KB)
├── fix_ms_imports.py  (891B)
├── fix_ms_indent.py  (1.2KB)
├── fix_opt_unavail.py  (1.1KB)
├── fix_pm_5returns.py  (993B)
├── fix_pod_and_route.py  (3.0KB)
├── fix_pod_division.py  (1.3KB)
├── fix_pod_manager_avail.py  (942B)
├── fix_post_17_margin_and_verify.py  (2.6KB)
├── fix_rebal_clean.py  (1.1KB)
├── fix_rebal_perfect.py  (1.5KB)
├── fix_rebal_typing.py  (657B)
├── fix_rebal_typing_all.py  (665B)
├── fix_rebalance.py  (281B)
├── fix_route_imports.py  (1.8KB)
├── fix_scanner_bb.py  (1.2KB)
├── fix_scanner_change_pct.py  (1.1KB)
├── fix_sched_clean.py  (4.2KB)
├── fix_sched_exact.py  (985B)
├── fix_sched_indent.py  (618B)
├── fix_scheduler_import.py  (926B)
├── fix_scheduler_syntax.py  (1.3KB)
├── fix_score_to_signal.py  (1.2KB)
├── fix_sec9_conf.py  (2.8KB)
├── fix_services_init.py  (811B)
├── fix_sizing_clean.py  (2.9KB)
├── fix_sizing_safe.py  (2.9KB)
├── fix_stock_order.py  (1.4KB)
├── fix_stock_pod_block.py  (1.8KB)
├── fix_stock_price_param.py  (742B)
├── fix_stock_route_param.py  (1.2KB)
├── fix_stock_settings.py  (664B)
├── fix_strict_pod_and_conf.py  (5.8KB)
├── fix_tech_avail.py  (1.2KB)
├── fix_tech_conf.py  (2.2KB)
├── fix_tech_conf_clean.py  (1.4KB)
├── fix_test_endpoint_gate.py  (1.4KB)
├── fix_test_jobstore.py  (697B)
├── fix_trader_exact.py  (1.2KB)
├── fix_trader_sig.py  (1.1KB)
├── fix_v604_full_autowiring.py  (16.9KB)
├── fix_v607_claude_master.py  (35.9KB)
├── fix_voice_close_and_tabs.py  (5.2KB)
├── fix_weights_and_dataclasses.py  (4.2KB)
├── gen_apply_round3k.py  (6.9KB)
├── gen_apply_round3l.py  (12.9KB)
├── gen_audit_ledger_logs.py  (7.0KB)
├── gen_audit_ledger_logs_k.py  (8.3KB)
├── gen_audit_ledger_logs_l.py  (8.7KB)
├── gen_compare_ram_metrics.py  (1.7KB)
├── gen_evaluate_filtered.py  (2.5KB)
├── gen_inspect_transcript_window.py  (1.7KB)
├── gen_p44_git_proof.py  (1.4KB)
├── gen_parse_task123.py  (3.0KB)
├── gen_run_verify_gate.py  (916B)
├── gen_verify_line_history.py  (1.0KB)
├── gen_verify_line_history_k.py  (1.1KB)
├── general_affairs_treasury.py  (11.1KB)
├── generate_p40_artifacts.py  (6.6KB)
├── generate_p41_artifacts.py  (7.4KB)
├── generate_p42_artifacts.py  (7.3KB)
├── generate_p42_part2.py  (3.4KB)
├── get_p41_hashes.py  (524B)
├── get_p42_hashes.py  (524B)
├── get_p43_hashes.py  (748B)
├── get_p43_hashes_final.py  (751B)
├── get_paths_from_transcript.py  (608B)
├── github_scout_adapter.py  (25.0KB)
├── google_sheets_archaeologist.py  (16.6KB)
├── google_sheets_history_report.json  (145.3KB)
├── google_sheets_sync_queue.json  (28.1KB)
├── grep_master_calls.py  (616B)
├── grep_of_empty.py  (325B)
├── grok_viral_master_plan.json  (4.4KB)
├── grok_viral_schedule_engine.py  (6.4KB)
├── healing_music_producer.py  (17.0KB)
├── immortal_tunnel_daemon.py  (13.5KB)
├── index.html  (205.2KB · 마커 2)
├── inject_v39_canvas_blocks.py  (4.4KB)
├── insert_showroom_index.py  (793B)
├── inspect_all_empty.py  (806B)
├── inspect_audit_exact.py  (1.9KB)
├── inspect_audit_items.py  (2.8KB)
├── inspect_avatar_code.py  (408B)
├── inspect_base_promises.py  (297B)
├── inspect_cards_l.py  (297B)
├── inspect_collector_hist.py  (372B)
├── inspect_components_list.py  (300B)
├── inspect_components_tail.py  (300B)
├── inspect_converters.py  (300B)
├── inspect_corrupt_test.py  (600B)
├── inspect_def_lines.py  (999B)
├── inspect_details_p30.py  (2.2KB)
├── inspect_effects.py  (714B)
├── inspect_empty_lines.py  (738B)
├── inspect_err_jsx.py  (343B)
├── inspect_kis_and_portfolio.py  (3.3KB)
├── inspect_kis_broker.py  (675B)
├── inspect_kis_raw.py  (2.8KB)
├── inspect_l2.py  (523B)
├── inspect_l3_blocks.py  (616B)
├── inspect_l3_l4_safe.py  (1.1KB)
├── inspect_l3_l4_status.py  (974B)
├── inspect_l3_l4_supersafe.py  (1.2KB)
├── inspect_l3_precheck.py  (1.5KB)
├── inspect_l3_safe.py  (1.3KB)
├── inspect_l_blocks.py  (523B)
├── inspect_master_calc.py  (432B)
├── inspect_master_signal.py  (453B)
├── inspect_middle_area.py  (403B)
├── inspect_ms_calc.py  (572B)
├── inspect_ms_calc_lines.py  (514B)
├── inspect_ms_weights.py  (570B)
├── inspect_n1b.py  (2.2KB)
├── inspect_nyda_trace.py  (397B)
├── inspect_o1.py  (348B)
├── inspect_opatch1_pre.py  (2.7KB)
├── inspect_p1.py  (988B)
├── inspect_p1_details.py  (636B)
├── inspect_p1_rem.py  (840B)
├── inspect_p1_scope.py  (708B)
├── inspect_p1_types.py  (740B)
├── inspect_paragraphs.py  (1.5KB)
├── inspect_pod_calc.py  (895B)
├── inspect_post_routes.py  (997B)
├── inspect_q2.py  (428B)
├── inspect_q2_details.py  (523B)
├── inspect_q2_patch.py  (523B)
├── inspect_q2_verif.py  (1.0KB)
├── inspect_q_n1b.py  (2.5KB)
├── inspect_real_5_google_sheets.py  (12.5KB)
├── inspect_rebalance_bytes.py  (517B)
├── inspect_remaining.py  (2.4KB)
├── inspect_risk_reb.py  (735B)
├── inspect_risk_reb_safety.py  (1.4KB)
├── inspect_scanner_and_adj.py  (1.5KB)
├── inspect_scanner_and_stats.py  (1.2KB)
├── inspect_scanner_jsx.py  (366B)
├── inspect_sched_init.py  (359B)
├── inspect_sig_details.py  (736B)
├── inspect_signal_tail.py  (334B)
├── inspect_signals.py  (1.3KB)
├── inspect_signatures_and_hunks.py  (2.4KB)
├── inspect_sl_tests.py  (1.0KB)
├── inspect_slices.py  (327B)
├── inspect_sources_p30.py  (1.8KB)
├── inspect_step_i.py  (746B)
├── inspect_step_r.py  (2.0KB)
├── inspect_step_s.py  (1.2KB)
├── inspect_step_s_4items.py  (1.3KB)
├── inspect_step_s_details.py  (1.9KB)
├── inspect_step_t.py  (1.1KB)
├── inspect_tabs.py  (444B)
├── inspect_tech_components.py  (801B)
├── inspect_turn11.py  (2.8KB)
├── inspect_turn12.py  (2.2KB)
├── inspect_turn13.py  (1.7KB)
├── inspect_turn15.py  (2.4KB)
├── inspect_turn16.py  (2.2KB)
├── inspect_turn18.py  (1.5KB)
├── inspect_u_and_pod.py  (2.7KB)
├── inspect_verification_all.py  (2.5KB)
├── inspect_volume_samples.py  (1.4KB)
├── investigate_b2_and_d3.py  (2.1KB)
├── investigate_p0_3.py  (2.5KB)
├── investigate_p43_routes.py  (2.7KB)
├── latest_tunnel_info.json  (328B)
├── launch_tunnel_and_send_telegram.py  (6.4KB)
├── legal_compliance_engine.py  (6.0KB)
├── legal_security_guardian.py  (7.8KB)
├── list_scheduler_jobs.py  (337B)
├── master_analyze_response.json  (3.3KB)
├── master_clean_fix.py  (8.2KB)
├── measure_snapshot.py  (576B)
├── measure_stop_loss_performance.py  (841B)
├── measure_stop_loss_speed.py  (1.0KB)
├── measure_thread_stop_loss.py  (662B)
├── memory_vault.json  (20.9KB)
├── morning_briefing_report.json  (1.4KB)
├── multi_agent_orchestrator.py  (12.1KB)
├── night_autonomous_daemon.py  (4.4KB)
├── night_seal_v607.py  (9.1KB)
├── nvda_analysis_verification.json  (3.3KB)
├── nvda_trading_auditor.py  (8.3KB)
├── nvda_trading_diagnosis_report.json  (5.6KB)
├── nvda_trading_manager.py  (11.3KB)
├── offline.html  (3.5KB)
├── omni_agent_bus.json  (39.3KB)
├── omni_claude_20261022_225837.py  (21.1KB)
├── omni_claude_20261022_231830.py  (17.7KB)
├── omni_dispatch_queue.json  (2.6KB)
├── omni_shared_clipboard.json  (52B)
├── one_touch_auto_executor.py  (28.9KB)
├── p1.htm  (703B)
├── p2.htm  (610B)
├── package-lock.json  (16.7KB)
├── package.json  (323B)
├── patch_249.py  (3.0KB)
├── patch_249_analyzer.py  (749B)
├── patch_500.py  (1.2KB)
├── patch_aside_v603.py  (10.1KB)
├── patch_d43.py  (0B)
├── patch_detect_all.py  (2.8KB)
├── patch_detect_safe.py  (2.5KB)
├── patch_early_ret.py  (2.2KB)
├── patch_full_ms.py  (10.2KB)
├── patch_ms_kelly_and_inv.py  (3.5KB)
├── patch_ms_warn.py  (1.2KB)
├── patch_none_check.py  (523B)
├── patch_nvda_analysis_return.py  (1.8KB)
├── patch_nvda_price_attr.py  (550B)
├── patch_omni_agent_bus_backend.py  (6.3KB)
├── patch_omni_agent_bus_frontend.py  (21.6KB)
├── patch_opatch2.py  (6.0KB)
├── patch_reb.py  (549B)
├── patch_rebal.py  (1.5KB)
├── patch_risk.py  (623B)
├── patch_run_dashboard_signals.py  (4.5KB)
├── patch_step1.py  (1.1KB)
├── patch_step2.py  (913B)
├── patch_step3.py  (1.2KB)
├── patch_step_c.py  (4.9KB)
├── patch_step_d1.py  (2.1KB)
├── patch_step_d2.py  (8.6KB)
├── patch_step_e.py  (2.0KB)
├── patch_step_f1.py  (3.7KB)
├── patch_step_f2.py  (891B)
├── patch_step_h.py  (7.6KB)
├── patch_step_l.py  (4.2KB)
├── patch_step_l2.py  (3.9KB)
├── patch_step_l3.py  (6.3KB)
├── patch_step_l3_correct.py  (6.2KB)
├── patch_step_l4.py  (677B)
├── patch_step_n2.py  (851B)
├── patch_step_p1.py  (2.2KB)
├── patch_step_q2.py  (1.9KB)
├── patch_step_s.py  (1.9KB)
├── patch_step_u.py  (1.4KB)
├── patch_stock_841.py  (1009B)
├── patch_stock_coverage.py  (617B)
├── patch_timeout_fail_count.py  (3.2KB)
├── patch_v360_3d_master.py  (32.5KB)
├── patch_v360_signal_sync.py  (14.6KB)
├── patch_v38_master_upgrade.py  (21.8KB)
├── patch_v39_remote_autotype.py  (5.7KB)
├── patch_v39_wardrobe_pro.py  (43.3KB)
├── phase1625_isolated_metrics.json  (9.7KB)
├── post_pinned_comment_hunters_dawn.py  (3.1KB)
├── posts_raw_content.json  (126.7KB)
├── prep_and_trim_ingredients.py  (44.9KB)
├── prepend_import.py  (541B)
├── print_send_telegram.py  (727B)
├── print_snapshot_keys.py  (620B)
├── profile_modules.py  (6.3KB)
├── publish_post_17.py  (10.6KB)
├── pwa_bootstrap.js  (9.3KB)
├── pwa_install_patch.py  (4.5KB)
├── qa_50x_stress_inspector.py  (11.7KB)
├── qa_button_inspector_agent.py  (11.4KB)
├── quant_risk_engine.py  (12.3KB)
├── query_enabled_test_ep.py  (933B)
├── query_live_endpoints.py  (1.1KB)
├── query_normal_live_final.py  (354B)
├── query_turn23_endpoints.py  (1.1KB)
├── query_turn30_live.py  (1.2KB)
├── r2.py  (1.4KB)
├── read_conftest.py  (323B)
├── read_verify_fail.py  (217B)
├── record_evolution_and_sync.py  (7.5KB)
├── register_final_out.py  (1.2KB)
├── reissue_channel_tokens.py  (4.9KB)
├── remaining_11_wrapped_report.json  (2.5KB)
├── remove_obsolete_func.py  (1.0KB)
├── remove_second_method.py  (1.5KB)
├── repair_bus.py  (1022B)
├── reproduce_growthpod.py  (321B)
├── restore_secrets.py  (2.9KB)
├── restore_slices.py  (7.0KB)
├── rewrite_master_signal.py  (11.7KB)
├── rgon_alpha_audience.html  (586.9KB · 마커 3)
├── rgon_alpha_button_audit_report.json  (3.7KB)
├── rgon_alpha_chat.html  (592.5KB · 마커 3)
├── rgon_alpha_chat_history.json  (107.6KB)
├── rgon_alpha_clone_engine.py  (51.0KB)
├── rgon_alpha_deep_button_auditor.py  (11.5KB)
├── rgon_alpha_patrol_log.json  (33.6KB)
├── rgon_alpha_persona_constitution.json  (2.2KB)
├── rgon_aside_browser_agent.py  (38.3KB)
├── rgon_auto_evolve_brain.py  (62.4KB)
├── rgon_auto_sync_daemon.py  (5.4KB)
├── rgon_auto_watcher.py  (21.8KB)
├── rgon_brain_snapshot.json  (39.9KB)
├── rgon_bridge_8765.py  (3.5KB)
├── rgon_constitution.json  (1.8KB)
├── rgon_full_agency_live_audit.py  (18.1KB)
├── rgon_master_scheduler.py  (8.9KB)
├── rgon_morning_routine.py  (2.1KB)
├── rgon_real_browser_inspector.py  (74.7KB)
├── rgon_runner.py  (10.0KB)
├── rgon_schedule_roadmap.json  (5.6KB)
├── rgon_skill_radar.json  (80.5KB)
├── rgon_watcher_state.json  (108B)
├── rgon_youtube_skill_scout.py  (45.0KB)
├── run_atomic_and_gather.py  (5.5KB)
├── run_benchmark_and_fault.py  (4.1KB)
├── run_clean_patch.py  (5.1KB)
├── run_comprehensive_audit.py  (7.8KB)
├── run_dashboard.py  (217.2KB)
├── run_deep_inspection.py  (4.0KB)
├── run_deep_profiling.py  (5.9KB)
├── run_full_e_inspection.py  (3.9KB)
├── run_full_verification.py  (4.5KB)
├── run_master_audit_v2.py  (6.3KB)
├── run_p14_probe.py  (645B)
├── run_p30_1_checks.py  (3.1KB)
├── run_p30_investigation.py  (2.5KB)
├── run_p30_tests.py  (5.2KB)
├── run_p31_exact_measurements.py  (3.0KB)
├── run_p31_investigation.py  (3.3KB)
├── run_p32_cleanup.py  (2.7KB)
├── run_p32_investigation.py  (2.7KB)
├── run_p33_raw_measurements.py  (6.3KB)
├── run_p35_part1.py  (2.2KB)
├── run_p35_part2.py  (3.8KB)
└── run_p36_part2_diff.py  (4.6KB)
```

## 🏷️ 패치 마커 인덱스 (마커 → HTML 위치 / 관리 스크립트)
| 마커 | 삽입된 HTML | 관리(생성) 스크립트 | JS |
|---|---|---|---|
| `RGON-STEP11` | rgon_alpha_audience.html, rgon_alpha_chat.html | - | - |
| `RGON-YT-SCOUT-V13` | index.html, rgon_alpha_audience.html, rgon_alpha_chat.html | - | - |
| `RGYT-PLACE-ONCE-V15` | index.html, rgon_alpha_audience.html, rgon_alpha_chat.html | - | - |

## 🐍 Python
| 경로 | 크기 | 수정 | 요약(docstring) | def / class |
|---|---|---|---|---|
| `activate_brain_and_push.py` | 51.2KB | 2026-10-20 15:39 | activate_brain_and_push.py | `log()`, `step()`, `ok()`, `warn()`, `fail()`, `now_kst()`, `stamp()`, `rel()`, `sha256()`, `read_json()`, `write_json()`, `run_cap()`, `run_stream()`, `ensure_pkg()`, `find_ffmpeg()`, `_lerp()`, `_font()`, `cover()`, `_overlay()`, `fetch_pollinations()`, `draw_paper_cup()`, `r1_replace_sample()`, `_walk_dicts()`, `_first()`, `_texts()` …(+27) |
| `add_error_event_test.py` | 2.6KB | 2026-09-07 19:27 | - | - |
| `add_test_node.py` | 3.5KB | 2026-09-14 09:00 | - | - |
| `agency_stage_gate_scheduler.py` | 5.9KB | 2026-10-19 19:00 | [v11.26-CREATOR-FORGE] | `load_stage_gate_master()`, `save_stage_gate_master()`, `get_stage_gate_schedule()`, `evaluate_stage_gate_status()` |
| `agent_swarm_cloner.py` | 12.5KB | 2026-10-17 17:58 | 안실장 무한 복제 클론 스웜 & 외부 샌드박스 자가치유 엔진 (agent_swarm_cloner.py) | `prepare_sandbox()`, `class DOMHealer [audit_and_heal]`, `class SwarmOrchestrator [run_clone_1_command, run_clone_2_suno, run_clone_3_chat, run_clone_4_daughters, run_clone_5_qa_guardian, execute_swarm]` |
| `amend_design1.py` | 1.6KB | 2026-08-21 15:53 | - | - |
| `analyze_feed_all.py` | 2.7KB | 2026-08-18 13:28 | - | - |
| `analyze_scratch_logs.py` | 902B | 2026-08-30 18:52 | - | - |
| `apply_50c_doc.py` | 1.1KB | 2026-09-16 06:34 | - | - |
| `apply_52c_doc.py` | 1.1KB | 2026-09-16 06:13 | - | - |
| `apply_account_state_optimization.py` | 3.3KB | 2026-09-25 10:48 | - | - |
| `apply_all_fixes.py` | 7.3KB | 2026-09-07 18:49 | - | - |
| `apply_backlog19_fix.py` | 6.8KB | 2026-09-12 11:30 | - | - |
| `apply_backlog2_core.py` | 7.4KB | 2026-09-08 07:08 | - | - |
| `apply_backlog50.py` | 879B | 2026-09-16 06:19 | - | - |
| `apply_blocker_fixes.py` | 8.9KB | 2026-09-07 18:34 | - | - |
| `apply_closing_fixes.py` | 5.2KB | 2026-09-12 11:13 | - | - |
| `apply_combined_docs.py` | 2.0KB | 2026-09-16 17:17 | - | - |
| `apply_commit1.py` | 4.8KB | 2026-08-30 18:14 | - | - |
| `apply_commit2.py` | 3.0KB | 2026-08-30 18:15 | - | - |
| `apply_commit4.py` | 4.2KB | 2026-08-30 18:18 | - | - |
| `apply_commit5.py` | 748B | 2026-08-30 18:18 | - | - |
| `apply_d3_and_b1.py` | 12.9KB | 2026-08-21 14:25 | - | `run_cmd()` |
| `apply_deduplication_updates.py` | 11.5KB | 2026-08-18 13:30 | - | - |
| `apply_defect14_fix.py` | 6.7KB | 2026-08-21 14:57 | - | - |
| `apply_defect47_fail_closed.py` | 4.4KB | 2026-08-21 16:26 | - | - |
| `apply_defect51.py` | 1.5KB | 2026-08-21 16:59 | - | - |
| `apply_defect54_null_guard.py` | 1.8KB | 2026-08-21 17:10 | - | - |
| `apply_defects_27_28.py` | 3.4KB | 2026-08-21 14:43 | - | - |
| `apply_defects_28_29_30.py` | 6.3KB | 2026-08-21 14:50 | - | - |
| `apply_defects_35_40.py` | 2.9KB | 2026-08-21 16:02 | - | - |
| `apply_defects_52_53.py` | 5.3KB | 2026-08-21 17:15 | - | - |
| `apply_defects_71_75.py` | 14.5KB | 2026-08-21 21:56 | - | - |
| `apply_design1_and_defect15.py` | 6.0KB | 2026-08-21 15:52 | - | - |
| `apply_design3_and_defect43.py` | 5.5KB | 2026-08-21 16:10 | - | - |
| `apply_design3_full.py` | 3.8KB | 2026-08-21 16:11 | - | - |
| `apply_dry_run_accepted_patch.py` | 2.4KB | 2026-08-31 03:57 | - | - |
| `apply_exact_scheduler_patch.py` | 9.0KB | 2026-09-25 10:50 | - | - |
| `apply_final_refinements.py` | 4.8KB | 2026-09-07 19:13 | - | - |
| `apply_full_fixes_turn19.py` | 10.1KB | 2026-08-21 21:39 | - | - |
| `apply_hourly_scan_fix.py` | 751B | 2026-09-30 20:10 | - | - |
| `apply_listener_followups.py` | 5.2KB | 2026-09-07 19:26 | - | - |
| `apply_m4_b_prime.py` | 10.7KB | 2026-09-14 08:44 | - | - |
| `apply_m5_clean.py` | 8.3KB | 2026-09-14 09:07 | - | - |
| `apply_m5_gate.py` | 3.0KB | 2026-09-14 09:01 | - | - |
| `apply_mute_removal_only.py` | 7.2KB | 2026-09-25 10:51 | - | - |
| `apply_n1.py` | 897B | 2026-09-07 18:21 | - | - |
| `apply_null_defaults.py` | 6.3KB | 2026-09-25 09:52 | - | - |
| `apply_opatch1_ms.py` | 6.3KB | 2026-08-20 18:44 | - | - |
| `apply_opatch1_safe.py` | 3.7KB | 2026-08-20 18:45 | - | - |
| `apply_p34_fixes.py` | 3.8KB | 2026-08-30 22:03 | - | - |
| `apply_part_a_patch.py` | 3.0KB | 2026-09-25 10:18 | - | - |
| `apply_patch_56.py` | 654B | 2026-09-16 17:06 | - | - |
| `apply_patch_57a.py` | 3.5KB | 2026-09-16 10:09 | - | - |
| `apply_patch_57b.py` | 2.3KB | 2026-09-16 12:22 | - | - |
| `apply_patch_57c.py` | 1.6KB | 2026-09-16 15:06 | - | - |
| `apply_patches_and_benchmark.py` | 7.4KB | 2026-08-21 14:19 | - | `run_cmd()`, `verify_d1()`, `benchmark_3runs()` |
| `apply_rebalance_patch.py` | 2.1KB | 2026-09-25 09:53 | - | - |
| `apply_round3j_doc_updates.py` | 9.9KB | 2026-09-23 23:22 | - | - |
| `apply_scheduler_clean.py` | 3.3KB | 2026-09-07 18:51 | - | - |
| `apply_scheduler_enhancements.py` | 10.8KB | 2026-09-25 10:49 | - | - |
| `apply_scheduler_patch.py` | 6.0KB | 2026-09-25 10:18 | - | - |
| `apply_scheduler_timeout.py` | 2.3KB | 2026-09-25 10:51 | - | - |
| `apply_sd_to_stock.py` | 3.8KB | 2026-08-21 14:50 | - | - |
| `apply_telegram_patch.py` | 3.2KB | 2026-09-25 10:18 | - | - |
| `apply_turn18_fixes.py` | 8.3KB | 2026-08-21 21:18 | - | - |
| `apply_turn22_fixes.py` | 7.3KB | 2026-08-21 22:05 | - | - |
| `apply_turn23_fixes.py` | 8.1KB | 2026-08-21 22:17 | - | - |
| `apply_turn24_fixes.py` | 4.9KB | 2026-08-21 22:25 | - | - |
| `apply_turn25_fixes.py` | 3.1KB | 2026-08-21 22:33 | - | - |
| `apply_turn26_fixes.py` | 2.7KB | 2026-08-21 22:50 | - | - |
| `apply_turn27_fixes.py` | 5.1KB | 2026-08-21 22:57 | - | - |
| `apply_turn28_fixes.py` | 2.6KB | 2026-08-21 23:38 | - | - |
| `apply_turn29_fixes.py` | 9.6KB | 2026-08-21 23:50 | - | - |
| `apply_turn30_fixes.py` | 7.1KB | 2026-08-22 00:07 | - | - |
| `apply_turn31_fixes.py` | 8.1KB | 2026-08-22 21:48 | - | - |
| `apply_turn32_fixes.py` | 7.0KB | 2026-08-22 22:02 | - | - |
| `apply_turn33_fixes.py` | 14.4KB | 2026-08-22 22:21 | - | - |
| `apply_turn34_fixes.py` | 4.4KB | 2026-08-23 22:09 | - | - |
| `apply_turn35_fixes.py` | 6.4KB | 2026-08-23 22:31 | - | - |
| `apply_turn36_fixes.py` | 6.9KB | 2026-08-23 23:00 | - | - |
| `apply_turn37_fixes.py` | 5.0KB | 2026-08-23 23:13 | - | - |
| `apply_turn38_fixes.py` | 9.3KB | 2026-08-23 23:20 | - | - |
| `apply_turn38_full.py` | 9.1KB | 2026-08-23 23:21 | - | - |
| `apply_v605_fix.py` | 8.4KB | 2026-10-20 22:23 | RGON Omni-Link Hub v6.0.5 업그레이드 | `say()`, `update_manifest()`, `update_background()`, `update_content()`, `check_js_syntax()`, `main()` |
| `apply_v606_lock.py` | 12.1KB | 2026-10-20 22:34 | RGON Omni-Link Hub v6.0.6 체크박스 리셋 원천 봉쇄 패치 | `say()`, `update_manifest()`, `update_background()`, `update_content()`, `check_js_syntax()`, `main()` |
| `audit_a12_all.py` | 5.5KB | 2026-08-25 23:44 | - | - |
| `audit_a13_all.py` | 10.5KB | 2026-08-25 23:56 | - | - |
| `audit_a14_all.py` | 12.2KB | 2026-08-26 00:11 | - | `dump_window()` |
| `audit_a15_all.py` | 16.6KB | 2026-08-26 08:12 | - | `dump_anchor_window()` |
| `audit_turn8.py` | 3.2KB | 2026-08-21 14:41 | - | `run_cmd()` |
| `audit_turn9.py` | 4.7KB | 2026-08-21 14:49 | - | `run_cmd()`, `run_blocking_removal_poc()` |
| `auto_company_loop.py` | 8.5KB | 2026-10-18 10:30 | auto_company_loop.py [청와대 24시간 무인 자율 오토파일럿 & 합의 기억 엔진] | `get_morning_brief_agenda()`, `approve_ceo_agenda()`, `append_to_consensus_ledger()`, `run_autonomous_company_cycle()`, `get_auto_loop_status()` |
| `auto_exec_latest.py` | 45.4KB | 2026-10-21 06:04 | RGON dashboard zero-click auto-sync patcher (Python standard library only) | `info()`, `kst_now_str()`, `P()`, `read_bytes()`, `read_text()`, `write_text()`, `ascii_escape()`, `node_check_text()`, `default_antibodies()`, `default_ledger()`, `plan_ledgers()`, `find_first()`, `_name_of()`, `extract_antibodies()`, `extract_offices()`, `extract_treasury()`, `extract_tunnel()`, `build_snapshot()`, `build_js()`, `find_insert_index()`, `inject_html()`, `main()` |
| `auto_write_to_5_google_sheets.py` | 12.4KB | 2026-10-20 00:02 | - | `find_token()`, `get_sheets_service()`, `ensure_tab_exists()`, `append_rows_to_tab()`, `update_local_records()`, `main()` |
| `benchmark_n3.py` | 2.8KB | 2026-08-20 15:41 | - | `fetch_one()`, `run_scenario2()` |
| `benchmark_n3_ext.py` | 2.7KB | 2026-08-20 16:25 | - | `fetch_one()`, `run_scenario2()` |
| `benchmark_r2.py` | 2.1KB | 2026-08-20 17:06 | - | `fetch_one()` |
| `build_omni_link_communicator.py` | 82.6KB | 2026-10-20 17:31 | - | `resolve_base()`, `log()`, `atomic_write()`, `render()`, `backup_file()`, `validate_js()`, `patch_html()`, `main()` |
| `build_real_aside_ext.py` | 5.9KB | 2026-10-19 19:37 | - | - |
| `capture_pytest_complete.py` | 801B | 2026-08-30 19:30 | - | - |
| `channel_agent.py` | 32.3KB | 2026-10-16 10:07 | - | `_load_telegram_config()`, `send_telegram()`, `get_creds()`, `get_sheets()`, `get_youtube()`, `get_gemini()`, `log()`, `cmd_produce()`, `cmd_analytics()`, `cmd_status()`, `cmd_strategy()`, `cmd_schedule()`, `cmd_grade()`, `self_diagnose_api()`, `main()` |
| `check_analysis.py` | 391B | 2026-08-17 21:41 | - | - |
| `check_apscheduler.py` | 214B | 2026-09-25 10:09 | - | - |
| `check_bb_values.py` | 791B | 2026-08-19 11:58 | - | - |
| `check_broker_client.py` | 268B | 2026-09-25 10:16 | - | - |
| `check_defect14_sources.py` | 1.4KB | 2026-08-21 14:55 | - | - |
| `check_empty_err.py` | 390B | 2026-08-20 16:51 | - | - |
| `check_err_card.py` | 812B | 2026-08-20 16:21 | - | - |
| `check_fallbacks.py` | 561B | 2026-08-20 15:16 | - | - |
| `check_final_state.py` | 1.5KB | 2026-08-30 22:05 | - | - |
| `check_fn.py` | 592B | 2026-08-20 18:59 | - | - |
| `check_fresh_live.py` | 2.5KB | 2026-08-21 16:01 | - | - |
| `check_imports.py` | 649B | 2026-09-25 09:54 | - | - |
| `check_indent.py` | 360B | 2026-08-30 18:14 | - | - |
| `check_jpm_price.py` | 481B | 2026-09-25 11:23 | - | - |
| `check_k.py` | 1.3KB | 2026-08-20 15:50 | - | - |
| `check_ms_test.py` | 298B | 2026-09-25 09:58 | - | - |
| `check_n1c_inst.py` | 516B | 2026-08-20 16:22 | - | - |
| `check_pytest_output.py` | 536B | 2026-09-25 09:57 | - | - |
| `check_risk_route.py` | 278B | 2026-09-25 09:54 | - | - |
| `check_routes.py` | 1.0KB | 2026-08-23 22:30 | - | `print_all_fastapi_routes()` |
| `check_signal.py` | 907B | 2026-08-17 21:42 | - | - |
| `check_stock_route.py` | 282B | 2026-09-25 09:55 | - | - |
| `check_task_logs.py` | 595B | 2026-09-25 09:56 | - | `get_sha256()` |
| `check_verify_a32.py` | 455B | 2026-09-25 10:22 | - | - |
| `check_verify_output.py` | 443B | 2026-09-25 10:04 | - | - |
| `check_보정62.py` | 873B | 2026-09-16 12:22 | - | - |
| `cheongwadae_comm_engine.py` | 23.5KB | 2026-10-19 10:26 | cheongwadae_comm_engine.py [v11.26-CREATOR-FORGE: 대표님 ⇄ 르곤·안총리·6대 청사 실시간 양방향 지능형 소통 사령부 엔진] | `get_engine_secrets()`, `load_comm_log()`, `record_commander_inbox()`, `send_real_telegram_message()`, `gather_realtime_system_metrics()`, `call_gemini_ai()`, `process_direct_communication()`, `append_comm_message()` |
| `cheongwadae_guard.py` | 10.0KB | 2026-10-18 21:26 | cheongwadae_guard.py [청와대 경호처 - 부서 간 침범 원천 차단 & 차곡차곡 누적 보호 엔진] | `compute_file_hash()`, `get_cheongwadae_status()`, `save_golden_hashes()`, `verify_all_departments()` |
| `clean_base_weights.py` | 1.5KB | 2026-08-21 16:20 | - | - |
| `clean_conf_maps.py` | 891B | 2026-08-22 00:18 | - | - |
| `clean_func_safe.py` | 1.0KB | 2026-08-21 16:31 | - | - |
| `clean_master_signal.py` | 3.8KB | 2026-08-22 00:14 | - | - |
| `clean_slashes.py` | 332B | 2026-09-16 17:18 | - | - |
| `clean_ui.py` | 19.9KB | 2026-10-19 20:54 | - | `_skip_template()`, `match_brace()`, `strip_defs()`, `only_comments()`, `backup()`, `write()`, `patch_html()`, `main()` |
| `cleanup_and_docs.py` | 2.4KB | 2026-08-30 18:18 | - | - |
| `collect_f_items.py` | 3.0KB | 2026-08-21 14:17 | - | `run_cmd()` |
| `collect_top1_ingredients.py` | 6.3KB | 2026-10-20 10:06 | - | `test_voice()` |
| `commit_p34_fixes.py` | 1.5KB | 2026-08-30 22:04 | - | - |
| `compare_p26_p27.py` | 1.9KB | 2026-08-30 17:56 | - | - |
| `connect_ai_cloud_corps.py` | 24.6KB | 2026-10-18 09:56 | connect_ai_cloud_corps.py [Connect AI 8대 정예 팀원 외부 클라우드 오프로딩 & 지식 엔진] | `ensure_stitch_design_system()`, `ensure_knowledge_engine()`, `sync_brain_to_wiki()`, `record_knowledge_and_reinforce()`, `dispatch_agent_task()`, `get_connect_ai_status()` |
| `control_tower_bot.py` | 12.5KB | 2026-10-16 10:02 | ══════════════════════════════════════════════════════════════════ | `get_env_or_connect_ai()`, `mask_secret()`, `log()`, `send_briefing()`, `trigger_github_workflow()`, `main()` |
| `copy_telegram.py` | 231B | 2026-09-25 10:17 | - | - |
| `create_desktop_shortcut.py` | 1.5KB | 2026-10-16 17:30 | - | - |
| `create_migration_package.py` | 8.5KB | 2026-10-14 17:48 | - | - |
| `create_new_tests.py` | 4.0KB | 2026-09-25 10:18 | - | - |
| `create_regression_tests.py` | 3.6KB | 2026-09-25 09:55 | - | - |
| `create_test_alert.py` | 2.6KB | 2026-08-30 18:14 | - | - |
| `create_test_counter.py` | 1.8KB | 2026-08-30 18:16 | - | - |
| `cross_dept_synergy_engine.py` | 26.3KB | 2026-10-19 11:09 | [v11.26-CREATOR-FORGE] | `calculate_hash()`, `safe_send_telegram()`, `run_grand_synergy_relay()`, `get_synergy_relay_status()` |
| `deep_duplicate_scan.py` | 2.3KB | 2026-08-18 13:28 | - | - |
| `deep_sweep_final_purger.py` | 16.6KB | 2026-10-18 23:29 | [v11.26-CREATOR-FORGE] | `purge_second_wave_files()`, `streamline_and_purify_keys()`, `execute_deep_sweep()` |
| `delete_todo_sheet.py` | 1.5KB | 2026-08-26 15:28 | - | - |
| `dept_mission_backlog.py` | 18.4KB | 2026-10-18 21:21 | dept_mission_backlog.py [6대 부서 18대 클린룸 벤치마킹 일거리 엔진 & 실물 산출물 생성기] | `load_work_queue()`, `execute_department_task()`, `execute_all_18_tasks()`, `get_all_work_queue()`, `execute_task()`, `audit_backlog_integrity()` |
| `dept_sub_agents_corps.py` | 17.1KB | 2026-10-19 10:41 | ══════════════════════════════════════════════════════════════════════════════ | `safe_send_telegram()`, `load_sub_agents_state()`, `save_sub_agents_state()`, `map_dept_to_agent_id()`, `inspect_dept_sub_agent()`, `dispatch_sub_agent()`, `dispatch_all_sub_agents()`, `get_sub_agents_status()` |
| `diagnose_fail.py` | 945B | 2026-08-30 22:04 | - | - |
| `dump_0939.py` | 379B | 2026-09-25 10:11 | - | - |
| `dump_4193.py` | 346B | 2026-09-25 09:56 | - | - |
| `dump_account_state.py` | 193B | 2026-09-25 10:11 | - | - |
| `dump_client.py` | 270B | 2026-09-25 10:12 | - | - |
| `dump_exact.py` | 327B | 2026-09-25 10:11 | - | - |
| `dump_listener.py` | 300B | 2026-09-25 10:10 | - | - |
| `dump_p40_artifacts.py` | 1.1KB | 2026-08-31 00:38 | - | `print_file_content()` |
| `dump_p42_details.py` | 877B | 2026-08-31 02:44 | - | `cat_file()` |
| `dump_p43_details.py` | 979B | 2026-08-31 03:58 | - | `cat_file()` |
| `dump_p44_all.py` | 1.4KB | 2026-08-31 04:17 | - | `print_raw()` |
| `dump_pod.py` | 310B | 2026-09-25 09:59 | - | - |
| `dump_pod_def.py` | 307B | 2026-09-25 09:59 | - | - |
| `dump_scan_result.py` | 271B | 2026-09-25 10:15 | - | - |
| `dump_scanner_methods.py` | 277B | 2026-09-25 10:14 | - | - |
| `dump_sched_709.py` | 269B | 2026-09-25 10:14 | - | - |
| `dump_sched_run.py` | 470B | 2026-09-25 10:13 | - | - |
| `dump_sched_throttle.py` | 397B | 2026-09-25 10:16 | - | - |
| `dump_stop_loss_code.py` | 269B | 2026-09-25 10:41 | - | - |
| `dump_target_lines.py` | 707B | 2026-09-25 10:11 | - | - |
| `dump_task_logs.py` | 585B | 2026-09-25 09:56 | - | - |
| `dump_telegram.py` | 287B | 2026-09-25 10:15 | - | - |
| `dump_verify_ps1.py` | 206B | 2026-09-25 09:58 | - | - |
| `ecc_pipeline_engine.py` | 5.9KB | 2026-10-18 02:21 | 🧠 [ECC: Extreme Claude Code Pipeline Engine] | `class ECCPipelineEngine [__init__, _load_vault, log, run_pipeline]` |
| `export_secrets_helper.py` | 3.1KB | 2026-10-16 10:13 | ══════════════════════════════════════════════════════════════════ | `export_secrets()` |
| `external_kitchen_worker.py` | 25.7KB | 2026-10-20 11:40 | 외부 손질 워커. dry-run/check-brain은 표준 라이브러리만 사용합니다. | `log()`, `run()`, `write_json()`, `class BrainState`, `load_brain()`, `recall()`, `build_recipe()`, `critic()`, `reflect()`, `finish()`, `brain_loop()`, `find_font()`, `frames()`, `stats()`, `tempo_chain()`, `tts_save()`, `voice()`, `bgm()`, `render()`, `main()`, `build_recipe()` |
| `extract_and_check.py` | 571B | 2026-10-17 23:12 | - | - |
| `extract_literals_p30.py` | 2.2KB | 2026-08-30 17:56 | - | - |
| `extract_live_pod.py` | 2.3KB | 2026-08-20 19:04 | - | `run_pod()` |
| `extract_live_pod_accurate.py` | 2.5KB | 2026-08-20 19:04 | - | `run_pod()` |
| `extract_n1_bodies.py` | 558B | 2026-08-20 15:32 | - | - |
| `fast_patch_1.py` | 1.6KB | 2026-10-19 19:35 | - | - |
| `fast_patch_3.py` | 4.5KB | 2026-10-19 19:47 | - | - |
| `fast_patch_5.py` | 5.6KB | 2026-10-19 20:03 | - | - |
| `fast_patch_6.py` | 4.2KB | 2026-10-19 20:10 | - | - |
| `fast_patch_7.py` | 6.7KB | 2026-10-19 20:21 | - | - |
| `fast_patch_8.py` | 4.3KB | 2026-10-19 20:35 | - | - |
| `fetch_raw_posts.py` | 1.2KB | 2026-08-18 13:29 | - | - |
| `fetch_route_signals.py` | 1.3KB | 2026-08-22 22:06 | - | - |
| `final_round_check.py` | 1.6KB | 2026-08-18 17:36 | - | - |
| `find_broker_loop.py` | 381B | 2026-09-25 10:12 | - | - |
| `find_canvas_positions.py` | 427B | 2026-10-17 22:07 | - | - |
| `find_listener.py` | 324B | 2026-09-25 10:09 | - | - |
| `find_logs.py` | 776B | 2026-09-25 10:10 | - | - |
| `find_nvda_paths.py` | 1.3KB | 2026-08-19 11:19 | - | `find_dirs()` |
| `find_order_routes.py` | 1.1KB | 2026-08-23 23:20 | - | - |
| `find_pod_classes.py` | 343B | 2026-09-25 10:39 | - | - |
| `find_scheduler_bits.py` | 365B | 2026-09-25 10:09 | - | - |
| `find_scheduler_lines.py` | 396B | 2026-09-25 10:50 | - | - |
| `find_sl_mutations.py` | 743B | 2026-08-30 22:03 | - | - |
| `find_throttle.py` | 365B | 2026-09-25 10:15 | - | - |
| `find_trading_files.py` | 691B | 2026-08-19 11:21 | - | `find_file()` |
| `finish_boot.py` | 1.6KB | 2026-10-21 10:11 | - | - |
| `fix_17_and_locate_01_02.py` | 2.2KB | 2026-08-18 17:38 | - | - |
| `fix_accepted_live_guard.py` | 2.3KB | 2026-08-30 18:20 | - | - |
| `fix_ad_host.py` | 3.8KB | 2026-10-19 22:35 | - | - |
| `fix_ad_popup_studio.py` | 5.2KB | 2026-10-19 22:55 | - | - |
| `fix_and_generate_p44.py` | 3.5KB | 2026-08-31 04:17 | - | - |
| `fix_and_verify_d3.py` | 5.4KB | 2026-08-21 14:28 | - | `run_cmd()` |
| `fix_app_null_guards.py` | 1.8KB | 2026-08-21 22:53 | - | - |
| `fix_app_residual_fallbacks.py` | 1.9KB | 2026-08-21 14:36 | - | - |
| `fix_auto_sync_master.py` | 44.2KB | 2026-10-21 00:10 | RGON dashboard zero-click auto-sync patcher (Python standard library only) | `info()`, `kst_now_str()`, `P()`, `read_bytes()`, `read_text()`, `write_text()`, `ascii_escape()`, `node_check_text()`, `default_antibodies()`, `default_ledger()`, `plan_ledgers()`, `find_first()`, `_name_of()`, `extract_antibodies()`, `extract_offices()`, `extract_treasury()`, `extract_tunnel()`, `build_snapshot()`, `build_js()`, `find_insert_index()`, `inject_html()`, `main()` |
| `fix_backtester_weights.py` | 1.2KB | 2026-08-21 23:01 | - | - |
| `fix_bb_syntax.py` | 1.1KB | 2026-08-21 15:27 | - | - |
| `fix_boot_now.py` | 2.2KB | 2026-10-21 10:09 | - | - |
| `fix_comp_name.py` | 731B | 2026-08-22 23:05 | - | - |
| `fix_component_score_sig.py` | 2.9KB | 2026-08-21 23:58 | - | - |
| `fix_components_exact.py` | 5.2KB | 2026-08-22 23:02 | - | - |
| `fix_components_grid.py` | 7.9KB | 2026-08-22 22:58 | - | - |
| `fix_conf_65.py` | 2.7KB | 2026-08-22 00:17 | - | - |
| `fix_conf_var.py` | 1.3KB | 2026-08-22 22:48 | - | - |
| `fix_corr_and_api.py` | 2.3KB | 2026-08-22 00:12 | - | - |
| `fix_cs_ms.py` | 1.5KB | 2026-08-21 23:59 | - | - |
| `fix_datetime_patch.py` | 1001B | 2026-09-07 18:42 | - | - |
| `fix_debt.py` | 1.9KB | 2026-08-17 11:49 | - | - |
| `fix_defect48_returns.py` | 3.5KB | 2026-08-21 16:47 | - | - |
| `fix_defect59_pkg.py` | 1.6KB | 2026-08-21 21:15 | - | - |
| `fix_err_test_import.py` | 753B | 2026-09-07 19:27 | - | - |
| `fix_event_msg.py` | 2.8KB | 2026-09-25 10:20 | - | - |
| `fix_final_corr.py` | 1.1KB | 2026-08-22 00:23 | - | - |
| `fix_flush_indent.py` | 628B | 2026-09-14 08:47 | - | - |
| `fix_function_injection.py` | 3.3KB | 2026-10-17 22:48 | dashboard/index.html의 마지막 <script> 태그 내부에 | `apply_fix()` |
| `fix_grid_and_kelly.py` | 13.5KB | 2026-08-21 21:47 | - | - |
| `fix_inv_caller.py` | 1.7KB | 2026-08-21 17:17 | - | - |
| `fix_inv_def.py` | 1.4KB | 2026-08-21 17:18 | - | - |
| `fix_inv_exact.py` | 1.4KB | 2026-08-21 17:19 | - | - |
| `fix_inv_score.py` | 841B | 2026-08-22 23:08 | - | - |
| `fix_kc.py` | 429B | 2026-08-20 19:02 | - | - |
| `fix_kc_defaults.py` | 2.1KB | 2026-08-22 21:49 | - | - |
| `fix_kc_insert.py` | 1.4KB | 2026-08-22 21:50 | - | - |
| `fix_kelly_calls.py` | 2.6KB | 2026-08-20 19:01 | - | - |
| `fix_kelly_ceiling.py` | 1.6KB | 2026-08-22 00:15 | - | - |
| `fix_kelly_dataclass.py` | 1.1KB | 2026-08-23 22:35 | - | - |
| `fix_kelly_final.py` | 1.6KB | 2026-08-22 00:16 | - | - |
| `fix_kelly_identity.py` | 2.3KB | 2026-08-21 21:48 | - | - |
| `fix_kelly_sig.py` | 1.3KB | 2026-08-22 22:52 | - | - |
| `fix_leaders_clean.py` | 966B | 2026-08-22 00:23 | - | - |
| `fix_llm_conf_field.py` | 1.5KB | 2026-08-21 21:56 | - | - |
| `fix_lock.py` | 759B | 2026-09-14 08:45 | - | - |
| `fix_main_import.py` | 1.3KB | 2026-08-22 22:43 | - | - |
| `fix_mock_trader.py` | 531B | 2026-09-25 11:00 | - | - |
| `fix_mock_trader_exact.py` | 1.3KB | 2026-09-25 11:00 | - | - |
| `fix_ms_dataclass.py` | 945B | 2026-08-23 22:34 | - | - |
| `fix_ms_dc_avail.py` | 1.4KB | 2026-08-21 21:28 | - | - |
| `fix_ms_imports.py` | 891B | 2026-08-23 22:33 | - | - |
| `fix_ms_indent.py` | 1.2KB | 2026-08-23 23:22 | - | - |
| `fix_opt_unavail.py` | 1.1KB | 2026-08-22 22:09 | - | - |
| `fix_pm_5returns.py` | 993B | 2026-08-21 21:23 | - | - |
| `fix_pod_and_route.py` | 3.0KB | 2026-08-21 21:21 | - | - |
| `fix_pod_division.py` | 1.3KB | 2026-09-25 09:35 | - | - |
| `fix_pod_manager_avail.py` | 942B | 2026-08-21 21:23 | - | - |
| `fix_post_17_margin_and_verify.py` | 2.6KB | 2026-08-18 17:35 | - | - |
| `fix_rebal_clean.py` | 1.1KB | 2026-08-23 23:25 | - | - |
| `fix_rebal_perfect.py` | 1.5KB | 2026-08-23 23:25 | - | - |
| `fix_rebal_typing.py` | 657B | 2026-08-23 23:24 | - | - |
| `fix_rebal_typing_all.py` | 665B | 2026-08-23 23:25 | - | - |
| `fix_rebalance.py` | 281B | 2026-09-25 09:52 | - | - |
| `fix_route_imports.py` | 1.8KB | 2026-08-23 23:22 | - | - |
| `fix_scanner_bb.py` | 1.2KB | 2026-08-21 15:25 | - | - |
| `fix_scanner_change_pct.py` | 1.1KB | 2026-08-21 15:41 | - | - |
| `fix_sched_clean.py` | 4.2KB | 2026-08-30 18:17 | - | - |
| `fix_sched_exact.py` | 985B | 2026-08-30 18:17 | - | - |
| `fix_sched_indent.py` | 618B | 2026-08-30 18:14 | - | - |
| `fix_scheduler_import.py` | 926B | 2026-09-25 10:52 | - | - |
| `fix_scheduler_syntax.py` | 1.3KB | 2026-09-07 18:51 | - | - |
| `fix_score_to_signal.py` | 1.2KB | 2026-08-21 21:59 | - | - |
| `fix_sec9_conf.py` | 2.8KB | 2026-08-21 21:23 | - | - |
| `fix_services_init.py` | 811B | 2026-08-21 22:51 | - | - |
| `fix_sizing_clean.py` | 2.9KB | 2026-08-22 22:53 | - | - |
| `fix_sizing_safe.py` | 2.9KB | 2026-08-22 22:55 | - | - |
| `fix_stock_order.py` | 1.4KB | 2026-08-23 23:01 | - | - |
| `fix_stock_pod_block.py` | 1.8KB | 2026-08-21 21:21 | - | - |
| `fix_stock_price_param.py` | 742B | 2026-08-20 19:13 | - | - |
| `fix_stock_route_param.py` | 1.2KB | 2026-08-21 22:08 | - | - |
| `fix_stock_settings.py` | 664B | 2026-08-23 23:02 | - | - |
| `fix_strict_pod_and_conf.py` | 5.8KB | 2026-08-21 21:07 | - | - |
| `fix_tech_avail.py` | 1.2KB | 2026-08-21 16:49 | - | - |
| `fix_tech_conf.py` | 2.2KB | 2026-08-22 00:09 | - | - |
| `fix_tech_conf_clean.py` | 1.4KB | 2026-08-22 00:10 | - | - |
| `fix_test_endpoint_gate.py` | 1.4KB | 2026-08-21 22:29 | - | - |
| `fix_test_jobstore.py` | 697B | 2026-09-07 18:52 | - | - |
| `fix_trader_exact.py` | 1.2KB | 2026-08-23 23:24 | - | - |
| `fix_trader_sig.py` | 1.1KB | 2026-08-23 23:24 | - | - |
| `fix_v604_full_autowiring.py` | 16.9KB | 2026-10-20 21:42 | RGON Omni-Link Hub v6.0.4 긴급 버그 수정 & 전 구간 풀 오토와이어링 | `say()`, `patch_manifest()`, `patch_background()`, `patch_content()`, `check_js_syntax()`, `main()` |
| `fix_v607_claude_master.py` | 35.9KB | 2026-10-20 23:28 | RGON Aside Extension v6.0.6 -> v6.0.7 patcher (Python standard library only) | `info()`, `read_text()`, `write_text()`, `node_check_text()`, `node_check_file()`, `is_balanced()`, `remove_previous_v607()`, `strip_legacy_blocks()`, `insert_static_container()`, `rename_refresh_scan()`, `handle_shims()`, `build_block()`, `insert_block()`, `build_content()`, `main()` |
| `fix_voice_close_and_tabs.py` | 5.2KB | 2026-10-19 19:49 | - | - |
| `fix_weights_and_dataclasses.py` | 4.2KB | 2026-08-21 16:19 | - | - |
| `gen_apply_round3k.py` | 6.9KB | 2026-09-24 00:35 | - | - |
| `gen_apply_round3l.py` | 12.9KB | 2026-09-24 01:01 | - | - |
| `gen_audit_ledger_logs.py` | 7.0KB | 2026-09-23 23:21 | Audit all ledger rows against disk log files in antigravity-ide brain. | - |
| `gen_audit_ledger_logs_k.py` | 8.3KB | 2026-09-24 00:34 | Audit all ledger rows against disk log files in antigravity-ide brain. | - |
| `gen_audit_ledger_logs_l.py` | 8.7KB | 2026-09-24 01:00 | Audit all ledger rows against disk log files in antigravity-ide brain. | - |
| `gen_compare_ram_metrics.py` | 1.7KB | 2026-09-24 00:33 | Compare memory metrics between GlobalMemoryStatusEx and CIM FreePhysicalMemory. | `class MEMORYSTATUSEX`, `compare_ram_metrics()` |
| `gen_evaluate_filtered.py` | 2.5KB | 2026-09-24 00:33 | Evaluate moving window RAM drift on filtered samples (>= 19:37:13). | `evaluate_filtered_window()` |
| `gen_inspect_transcript_window.py` | 1.7KB | 2026-09-24 00:59 | Inspect task-744 sampling window for tool calls in transcript.jsonl. | `inspect_tool_calls_in_window()` |
| `gen_p44_git_proof.py` | 1.4KB | 2026-08-31 04:18 | - | - |
| `gen_parse_task123.py` | 3.0KB | 2026-09-24 01:00 | Calculate exact elapsed times from task-123.log for 6 alternating runs. | `parse_task123_timing()` |
| `gen_run_verify_gate.py` | 916B | 2026-09-23 23:24 | Execute verify.ps1 with external stopwatch and measure wall clock. | - |
| `gen_verify_line_history.py` | 1.0KB | 2026-09-23 23:21 | - | - |
| `gen_verify_line_history_k.py` | 1.1KB | 2026-09-24 01:00 | Verify line counts and diffs of docs/testing_runtime_protocol.md across commits. | - |
| `general_affairs_treasury.py` | 11.1KB | 2026-10-18 22:25 | general_affairs_treasury.py [제6청사: 총무·재무회계·정산청 백엔드 엔진] | `get_clean_zero_ledger_data()`, `reset_to_clean_zero_ledger()`, `load_ledger()`, `save_ledger()`, `recalculate_summary()`, `record_transaction()`, `get_disk_free_gb()`, `get_treasury_status()`, `audit_and_clean_scratch()` |
| `generate_p40_artifacts.py` | 6.6KB | 2026-08-31 00:37 | - | - |
| `generate_p41_artifacts.py` | 7.4KB | 2026-08-31 01:36 | - | - |
| `generate_p42_artifacts.py` | 7.3KB | 2026-08-31 02:42 | - | - |
| `generate_p42_part2.py` | 3.4KB | 2026-08-31 02:44 | - | - |
| `get_p41_hashes.py` | 524B | 2026-08-31 01:37 | - | - |
| `get_p42_hashes.py` | 524B | 2026-08-31 02:42 | - | - |
| `get_p43_hashes.py` | 748B | 2026-08-31 03:58 | - | - |
| `get_p43_hashes_final.py` | 751B | 2026-08-31 03:59 | - | - |
| `get_paths_from_transcript.py` | 608B | 2026-08-19 11:23 | - | - |
| `github_scout_adapter.py` | 25.0KB | 2026-10-17 06:15 | 🔭 한걸음씩 AI 제국 : 제2원(미래지향·공존개발팀) | `evaluate_license()`, `scout_github_repositories()`, `build_default_adaptation_plan()`, `generate_adaptation_plan_with_gemini()`, `get_rea_deep_dive_analysis()`, `get_super_trend_preset_analysis()`, `run_daily_cloud_scout()` |
| `google_sheets_archaeologist.py` | 16.6KB | 2026-10-18 23:30 | [v11.26-CREATOR-FORGE] | `mask_sheet_id()`, `discover_google_cloud_sheets()`, `discover_local_spreadsheets()`, `analyze_sheet_historical_context()`, `conduct_archaeology()`, `generate_markdown_report()` |
| `grep_master_calls.py` | 616B | 2026-08-20 17:07 | - | - |
| `grep_of_empty.py` | 325B | 2026-08-20 18:20 | - | - |
| `grok_viral_schedule_engine.py` | 6.4KB | 2026-10-19 17:32 | Grok 4.7 기반 골든타임 바이럴 4대 편성표 및 Suno AI 프롬프트 스케줄러 엔진 | `class GrokViralScheduleEngine [__init__, _load_plan, get_full_plan, get_active_or_next_slot, get_pinned_comment, get_suno_prompt…]` |
| `healing_music_producer.py` | 17.0KB | 2026-10-16 16:48 | ══════════════════════════════════════════════════════════════════ | `log()`, `generate_ass_subtitle()`, `render_master_block()`, `assemble_longform()`, `extract_shorts()`, `ensure_fallback_assets()`, `run_pipeline()` |
| `immortal_tunnel_daemon.py` | 13.5KB | 2026-10-19 02:29 | ══════════════════════════════════════════════════════════════════ | `log()`, `get_secrets()`, `send_telegram_direct()`, `is_local_server_alive()`, `ensure_local_server()`, `check_external_tunnel_health()`, `sync_tunnel_records()`, `spawn_new_cloudflare_tunnel()`, `get_current_tunnel_url()`, `run_daemon_loop()` |
| `inject_v39_canvas_blocks.py` | 4.4KB | 2026-10-17 22:08 | dashboard/index.html과 dashboard/dream_closet_future_master_app.html의 | `update_file()`, `main()` |
| `insert_showroom_index.py` | 793B | 2026-10-17 22:07 | - | - |
| `inspect_all_empty.py` | 806B | 2026-08-20 17:05 | - | - |
| `inspect_audit_exact.py` | 1.9KB | 2026-08-20 19:09 | - | `run_cmd()`, `safe_print()` |
| `inspect_audit_items.py` | 2.8KB | 2026-08-20 18:55 | - | `run_cmd()`, `safe_print()` |
| `inspect_avatar_code.py` | 408B | 2026-10-17 23:08 | - | - |
| `inspect_base_promises.py` | 297B | 2026-08-20 15:51 | - | - |
| `inspect_cards_l.py` | 297B | 2026-08-20 15:51 | - | - |
| `inspect_collector_hist.py` | 372B | 2026-08-20 17:05 | - | - |
| `inspect_components_list.py` | 300B | 2026-08-20 15:20 | - | - |
| `inspect_components_tail.py` | 300B | 2026-08-20 15:20 | - | - |
| `inspect_converters.py` | 300B | 2026-08-20 15:19 | - | - |
| `inspect_corrupt_test.py` | 600B | 2026-08-30 22:03 | - | - |
| `inspect_def_lines.py` | 999B | 2026-08-20 14:57 | - | - |
| `inspect_details_p30.py` | 2.2KB | 2026-08-30 17:55 | - | `read_file_lines()` |
| `inspect_effects.py` | 714B | 2026-08-20 16:10 | - | - |
| `inspect_empty_lines.py` | 738B | 2026-08-20 17:04 | - | - |
| `inspect_err_jsx.py` | 343B | 2026-08-20 16:21 | - | - |
| `inspect_kis_and_portfolio.py` | 3.3KB | 2026-08-21 08:31 | - | `test_api()` |
| `inspect_kis_broker.py` | 675B | 2026-08-30 22:04 | - | - |
| `inspect_kis_raw.py` | 2.8KB | 2026-08-21 08:54 | - | `run_cmd()`, `fetch_kis_raw()` |
| `inspect_l2.py` | 523B | 2026-08-20 16:34 | - | - |
| `inspect_l3_blocks.py` | 616B | 2026-08-20 17:21 | - | - |
| `inspect_l3_l4_safe.py` | 1.1KB | 2026-08-20 17:39 | - | `run_cmd()` |
| `inspect_l3_l4_status.py` | 974B | 2026-08-20 17:39 | - | - |
| `inspect_l3_l4_supersafe.py` | 1.2KB | 2026-08-20 17:40 | - | `run_cmd()`, `safe_print()` |
| `inspect_l3_precheck.py` | 1.5KB | 2026-08-20 17:15 | - | - |
| `inspect_l3_safe.py` | 1.3KB | 2026-08-20 17:15 | - | - |
| `inspect_l_blocks.py` | 523B | 2026-08-20 16:22 | - | - |
| `inspect_master_calc.py` | 432B | 2026-08-20 15:19 | - | - |
| `inspect_master_signal.py` | 453B | 2026-08-20 15:19 | - | - |
| `inspect_middle_area.py` | 403B | 2026-10-17 23:54 | - | - |
| `inspect_ms_calc.py` | 572B | 2026-08-23 23:27 | - | - |
| `inspect_ms_calc_lines.py` | 514B | 2026-08-20 18:43 | - | - |
| `inspect_ms_weights.py` | 570B | 2026-08-20 18:34 | - | - |
| `inspect_n1b.py` | 2.2KB | 2026-08-20 15:36 | - | - |
| `inspect_nyda_trace.py` | 397B | 2026-08-20 17:38 | - | - |
| `inspect_o1.py` | 348B | 2026-08-20 15:52 | - | - |
| `inspect_opatch1_pre.py` | 2.7KB | 2026-08-20 18:40 | - | `run_cmd()`, `safe_print()` |
| `inspect_p1.py` | 988B | 2026-08-20 15:52 | - | - |
| `inspect_p1_details.py` | 636B | 2026-08-20 17:20 | - | - |
| `inspect_p1_rem.py` | 840B | 2026-08-20 17:15 | - | - |
| `inspect_p1_scope.py` | 708B | 2026-08-20 16:38 | - | - |
| `inspect_p1_types.py` | 740B | 2026-08-20 16:26 | - | - |
| `inspect_paragraphs.py` | 1.5KB | 2026-08-18 13:29 | - | - |
| `inspect_pod_calc.py` | 895B | 2026-08-20 18:28 | - | - |
| `inspect_post_routes.py` | 997B | 2026-08-23 23:21 | - | - |
| `inspect_q2.py` | 428B | 2026-08-20 16:24 | - | - |
| `inspect_q2_details.py` | 523B | 2026-08-20 16:25 | - | - |
| `inspect_q2_patch.py` | 523B | 2026-08-20 16:32 | - | - |
| `inspect_q2_verif.py` | 1.0KB | 2026-08-20 17:12 | - | - |
| `inspect_q_n1b.py` | 2.5KB | 2026-08-20 16:10 | - | - |
| `inspect_real_5_google_sheets.py` | 12.5KB | 2026-10-18 23:50 | - | `mask_id()`, `get_hash()`, `clean_cell()`, `inspect_all()` |
| `inspect_rebalance_bytes.py` | 517B | 2026-08-30 22:03 | - | - |
| `inspect_remaining.py` | 2.4KB | 2026-08-21 06:45 | - | `run_cmd()` |
| `inspect_risk_reb.py` | 735B | 2026-08-20 16:24 | - | - |
| `inspect_risk_reb_safety.py` | 1.4KB | 2026-08-20 16:35 | - | - |
| `inspect_scanner_and_adj.py` | 1.5KB | 2026-08-21 21:29 | - | - |
| `inspect_scanner_and_stats.py` | 1.2KB | 2026-08-21 21:51 | - | - |
| `inspect_scanner_jsx.py` | 366B | 2026-08-20 16:22 | - | - |
| `inspect_sched_init.py` | 359B | 2026-08-30 18:16 | - | - |
| `inspect_sig_details.py` | 736B | 2026-08-20 17:07 | - | - |
| `inspect_signal_tail.py` | 334B | 2026-08-20 15:52 | - | - |
| `inspect_signals.py` | 1.3KB | 2026-08-20 15:18 | - | - |
| `inspect_signatures_and_hunks.py` | 2.4KB | 2026-08-21 08:30 | - | `run_cmd()` |
| `inspect_sl_tests.py` | 1.0KB | 2026-08-30 22:02 | - | - |
| `inspect_slices.py` | 327B | 2026-09-25 10:53 | - | - |
| `inspect_sources_p30.py` | 1.8KB | 2026-08-30 17:55 | - | `print_section()` |
| `inspect_step_i.py` | 746B | 2026-08-20 15:17 | - | `print_fn_body()` |
| `inspect_step_r.py` | 2.0KB | 2026-08-20 16:24 | - | - |
| `inspect_step_s.py` | 1.2KB | 2026-08-20 17:03 | - | - |
| `inspect_step_s_4items.py` | 1.3KB | 2026-08-20 17:25 | - | - |
| `inspect_step_s_details.py` | 1.9KB | 2026-08-20 17:13 | - | - |
| `inspect_step_t.py` | 1.1KB | 2026-08-20 17:23 | - | `call_and_print()` |
| `inspect_tabs.py` | 444B | 2026-10-17 22:45 | - | - |
| `inspect_tech_components.py` | 801B | 2026-08-20 15:18 | - | - |
| `inspect_turn11.py` | 2.8KB | 2026-08-21 15:51 | - | `run_cmd()` |
| `inspect_turn12.py` | 2.2KB | 2026-08-21 16:09 | - | `run_cmd()` |
| `inspect_turn13.py` | 1.7KB | 2026-08-21 16:19 | - | `run_cmd()` |
| `inspect_turn15.py` | 2.4KB | 2026-08-21 16:42 | - | `run_cmd()` |
| `inspect_turn16.py` | 2.2KB | 2026-08-21 16:58 | - | `run_cmd()` |
| `inspect_turn18.py` | 1.5KB | 2026-08-21 21:07 | - | - |
| `inspect_u_and_pod.py` | 2.7KB | 2026-08-20 17:46 | - | - |
| `inspect_verification_all.py` | 2.5KB | 2026-08-20 18:33 | - | `run_cmd()`, `safe_print()` |
| `inspect_volume_samples.py` | 1.4KB | 2026-08-20 17:25 | - | - |
| `investigate_b2_and_d3.py` | 2.1KB | 2026-08-21 14:25 | - | `run_cmd()` |
| `investigate_p0_3.py` | 2.5KB | 2026-08-30 22:02 | - | - |
| `investigate_p43_routes.py` | 2.7KB | 2026-08-31 03:56 | - | - |
| `launch_tunnel_and_send_telegram.py` | 6.4KB | 2026-10-20 23:47 | 1. cloudflared 터널 기동 및 최신 *.trycloudflare.com 확보 | `get_telegram_creds()`, `ensure_tunnel()`, `send_telegram()`, `main()` |
| `legal_compliance_engine.py` | 6.0KB | 2026-10-18 12:19 | legal_compliance_engine.py [제5청사 자율법무·컴플라이언스 5대 안전망 감사 엔진] | `audit_file_content()`, `audit_all_safe_apps()`, `run_full_legal_audit()` |
| `legal_security_guardian.py` | 7.8KB | 2026-10-16 19:37 | ══════════════════════════════════════════════════════════════════ | `class LegalSecurityGuardian [__init__, audit_text_content, audit_zero_leak_filesystem, run_full_council_audit]` |
| `list_scheduler_jobs.py` | 337B | 2026-09-25 10:42 | - | - |
| `master_clean_fix.py` | 8.2KB | 2026-10-19 20:44 | - | - |
| `measure_snapshot.py` | 576B | 2026-09-08 06:52 | - | - |
| `measure_stop_loss_performance.py` | 841B | 2026-09-25 10:57 | - | - |
| `measure_stop_loss_speed.py` | 1.0KB | 2026-09-25 10:54 | - | `measure()` |
| `measure_thread_stop_loss.py` | 662B | 2026-09-25 10:55 | - | `test_in_worker_thread()` |
| `multi_agent_orchestrator.py` | 12.1KB | 2026-10-17 17:50 | Omni-Nexus 5대 분산 멀티 에이전트 오케스트레이터 (multi_agent_orchestrator.py) | `class DOMIntegrityParser [__init__, handle_starttag, handle_endtag]`, `audit_dom_integrity()`, `class BaseSectionAgent [__init__, validate_boundary, process_task, _execute]`, `class CommandAgent [__init__, _execute]`, `class SunoAgent [__init__, _execute]`, `class ChatAgent [__init__, _execute]`, `class DaughtersAgent [__init__, _execute]`, `class MultiAgentOrchestrator [__init__, dispatch]` |
| `night_autonomous_daemon.py` | 4.4KB | 2026-10-18 16:43 | night_autonomous_daemon.py [대표님 취침 중 르곤x안총리 야간 무인 자율주행 데몬 & 모닝 브리핑 엔진] | `run_night_autonomous_shift()` |
| `night_seal_v607.py` | 9.1KB | 2026-10-20 23:37 | 사령관님 취침 전 최종 봉인 스크립트: | `update_master_schedule()`, `update_evolution_json()`, `update_evolution_md()`, `find_token()`, `get_sheets_service()`, `sync_sheets()`, `git_commit_and_push()`, `main()` |
| `nvda_trading_auditor.py` | 8.3KB | 2026-10-19 04:33 | ══════════════════════════════════════════════════════════════════ | `mask_secret()`, `audit_nvda_trading_system()` |
| `nvda_trading_manager.py` | 11.3KB | 2026-10-19 04:59 | ══════════════════════════════════════════════════════════════════ | `get_nvda_trading_status()`, `run_nvda_unblock_test()`, `run_nvda_trading_audit()` |
| `omni_claude_20261022_225837.py` | 21.1KB | 2026-10-23 07:30 | rgon_finish_step2_step3.py (Windows / Python 3 표준 라이브러리 전용) | `say()`, `section()`, `hidden_si()`, `run_hidden()`, `ps()`, `backup()`, `human()`, `guard()`, `find_chrome()`, `git_remote()`, `step_dashboard()`, `patch_no_window()`, `write_bridge()`, `running_scripts()`, `port_open()`, `start_if_absent()`, `enable_tasks()`, `step_patch_and_start()`, `step_archive()`, `step_memory()`, `step_heartbeat()`, `send_telegram()`, `main()` |
| `omni_claude_20261022_231830.py` | 17.7KB | 2026-10-23 07:30 | rgon_local_cleanup.py (Python 3 표준 라이브러리 전용 / 네트워크 전송 없음) | `say()`, `section()`, `human()`, `fmt_time()`, `backup()`, `read_text()`, `write_text()`, `walk_files()`, `rel()`, `scan_clipboard_hits()`, `disable_js_clipboard()`, `neutralize_python_clip()`, `step_clipboard()`, `step_html()`, `step_shortcuts_and_open()`, `step_log()`, `find_memory_file()`, `step_memory_status()`, `save_summary()`, `main()` |
| `one_touch_auto_executor.py` | 28.9KB | 2026-10-19 02:14 | one_touch_auto_executor.py [v11.26-CREATOR-FORGE 원터치 무인 자동 집행 엔진 — One-Touch Autonomous Pipeline] | `_safe_telegram_notify()`, `_append_comm_and_consensus()`, `_append_google_sheets_queue()`, `execute_stitch_design_pipeline()`, `execute_hook_script_pipeline()`, `execute_bm_pipeline()`, `execute_all_8_agents_pipeline()`, `handle_one_touch_execute()` |
| `patch_249.py` | 3.0KB | 2026-08-19 12:06 | - | - |
| `patch_249_analyzer.py` | 749B | 2026-08-19 12:08 | - | - |
| `patch_500.py` | 1.2KB | 2026-08-19 12:29 | - | - |
| `patch_aside_v603.py` | 10.1KB | 2026-10-20 21:17 | RGON Omni-Link Hub v6.0.3 업그레이드 패치 스크립트 | `say()`, `update_manifest()`, `update_background()`, `update_content()`, `validate_javascript()`, `verify_bridge()`, `main()` |
| `patch_d43.py` | 0B | 2026-09-23 19:00 | - | - |
| `patch_detect_all.py` | 2.8KB | 2026-08-20 18:57 | - | - |
| `patch_detect_safe.py` | 2.5KB | 2026-08-20 18:57 | - | - |
| `patch_early_ret.py` | 2.2KB | 2026-08-20 18:59 | - | - |
| `patch_full_ms.py` | 10.2KB | 2026-08-20 19:00 | - | - |
| `patch_ms_kelly_and_inv.py` | 3.5KB | 2026-08-21 21:38 | - | - |
| `patch_ms_warn.py` | 1.2KB | 2026-08-20 17:40 | - | - |
| `patch_none_check.py` | 523B | 2026-08-20 18:58 | - | - |
| `patch_nvda_analysis_return.py` | 1.8KB | 2026-08-19 12:12 | - | - |
| `patch_nvda_price_attr.py` | 550B | 2026-08-19 12:11 | - | - |
| `patch_omni_agent_bus_backend.py` | 6.3KB | 2026-10-17 21:18 | run_dashboard.py에 /api/omni-agent-bus GET/POST 엔드포인트 주입 | - |
| `patch_omni_agent_bus_frontend.py` | 21.6KB | 2026-10-17 21:21 | dashboard/index.html 및 dashboard/dream_closet_future_master_app.html에 | `patch_index_html()`, `patch_dream_closet_app()`, `main()` |
| `patch_opatch2.py` | 6.0KB | 2026-08-20 19:10 | - | - |
| `patch_reb.py` | 549B | 2026-08-20 16:36 | - | - |
| `patch_rebal.py` | 1.5KB | 2026-09-25 09:53 | - | - |
| `patch_risk.py` | 623B | 2026-08-20 16:35 | - | - |
| `patch_run_dashboard_signals.py` | 4.5KB | 2026-10-17 20:52 | - | - |
| `patch_step1.py` | 1.1KB | 2026-08-19 11:24 | - | - |
| `patch_step2.py` | 913B | 2026-08-19 11:44 | - | - |
| `patch_step3.py` | 1.2KB | 2026-08-19 11:54 | - | - |
| `patch_step_c.py` | 4.9KB | 2026-08-20 14:35 | - | - |
| `patch_step_d1.py` | 2.1KB | 2026-08-20 14:42 | - | - |
| `patch_step_d2.py` | 8.6KB | 2026-08-20 14:43 | - | - |
| `patch_step_e.py` | 2.0KB | 2026-08-20 14:59 | - | - |
| `patch_step_f1.py` | 3.7KB | 2026-08-20 14:57 | - | - |
| `patch_step_f2.py` | 891B | 2026-08-20 14:58 | - | - |
| `patch_step_h.py` | 7.6KB | 2026-08-20 15:15 | - | - |
| `patch_step_l.py` | 4.2KB | 2026-08-20 16:22 | - | - |
| `patch_step_l2.py` | 3.9KB | 2026-08-20 16:34 | - | - |
| `patch_step_l3.py` | 6.3KB | 2026-08-20 17:22 | - | - |
| `patch_step_l3_correct.py` | 6.2KB | 2026-08-20 17:22 | - | - |
| `patch_step_l4.py` | 677B | 2026-08-20 17:45 | - | - |
| `patch_step_n2.py` | 851B | 2026-08-20 15:36 | - | - |
| `patch_step_p1.py` | 2.2KB | 2026-08-20 17:21 | - | - |
| `patch_step_q2.py` | 1.9KB | 2026-08-20 16:32 | - | - |
| `patch_step_s.py` | 1.9KB | 2026-08-20 18:21 | - | - |
| `patch_step_u.py` | 1.4KB | 2026-08-20 18:23 | - | - |
| `patch_stock_841.py` | 1009B | 2026-08-20 14:23 | - | - |
| `patch_stock_coverage.py` | 617B | 2026-08-20 18:46 | - | - |
| `patch_timeout_fail_count.py` | 3.2KB | 2026-09-08 06:59 | - | - |
| `patch_v360_3d_master.py` | 32.5KB | 2026-10-17 19:55 | 1. dashboard/index.html & dashboard/dream_closet_future_master_app.html에 | `patch_index_html()`, `patch_dream_closet_app()`, `main()` |
| `patch_v360_signal_sync.py` | 14.6KB | 2026-10-17 20:56 | 1. 대시보드 상단에 『⚡ IN/OUT 시그널 오토싱크 사령탑』 미니 바 탑재 | `patch_index_html()`, `patch_dream_closet_app()`, `main()` |
| `patch_v38_master_upgrade.py` | 21.8KB | 2026-10-17 21:42 | 이상일 대표님([COMMANDER-000])의 v3.8 Pro 특명 일괄 반영 스크립트 | `patch_index_html()`, `patch_dream_closet_app()`, `main()` |
| `patch_v39_remote_autotype.py` | 5.7KB | 2026-10-17 22:45 | 1. dashboard/index.html (tab-command & tab-daughters 상단)에 | `patch_index_html()`, `patch_master_app_html()` |
| `patch_v39_wardrobe_pro.py` | 43.3KB | 2026-10-17 22:06 | 이상일 대표님([COMMANDER-000])의 v3.9 Wardrobe-Pro 4대 특명 마스터 패치: | `patch_index_html()`, `patch_dream_closet_app()`, `main()` |
| `post_pinned_comment_hunters_dawn.py` | 3.1KB | 2026-08-07 17:25 | post_pinned_comment_hunters_dawn.py — 사냥꾼의 새벽 (P90h3HLw9Qk) 고정댓글 작성 | `get_creds()`, `main()` |
| `prep_and_trim_ingredients.py` | 44.9KB | 2026-10-20 10:26 | 실행: | `say()`, `run_command()`, `ensure_package()`, `load_pillow()`, `find_ffmpeg()`, `atomic_json()`, `safe_topic_name()`, `make_recipe()`, `find_korean_font()`, `wrap_text()`, `fitted_lines()`, `draw_lines()`, `render_scenes()`, `save_tts()`, `acquire_voice()`, `wav_stats()`, `atempo_filter()`, `trim_voice()`, `midi_hz()`, `make_bgm()`, `compose_video()`, `verify_video()`, `main()` |
| `prepend_import.py` | 541B | 2026-09-25 10:53 | - | - |
| `print_send_telegram.py` | 727B | 2026-08-30 17:55 | - | - |
| `print_snapshot_keys.py` | 620B | 2026-09-08 07:05 | - | - |
| `profile_modules.py` | 6.3KB | 2026-08-21 06:47 | - | `benchmark()` |
| `publish_post_17.py` | 10.6KB | 2026-08-18 13:35 | - | - |
| `pwa_install_patch.py` | 4.5KB | 2026-10-22 15:53 | PWA 고정앱 패치: 매니페스트 상대경로 교정 + 왕관 아이콘 + head 메타 3줄. | `id_counts()`, `main()` |
| `qa_50x_stress_inspector.py` | 11.7KB | 2026-10-18 23:34 | qa_50x_stress_inspector.py [v8.5 Department Mission Backlog 500회 가혹 검수기] | `check_scenario()`, `main()` |
| `qa_button_inspector_agent.py` | 11.4KB | 2026-10-17 21:45 | qa_button_inspector_agent.py [QA-901] | `check_file_onclick_integrity()`, `check_angle_buttons_removal()`, `check_3d_and_face_synthesis()`, `check_node_syntax()`, `check_omni_agent_bus()`, `check_rgon_auto_sync_daemon()`, `check_swarm_dom_isolation()`, `main()` |
| `quant_risk_engine.py` | 12.3KB | 2026-10-19 20:10 | [v11.26-CREATOR-FORGE.1-SOL-QUANT-RISK-ENGINE] | `class RiskBudget`, `class ScoreBreakdown`, `score_entry()`, `check_16_entry_block_reasons()`, `make_entry_plan()`, `get_quant_risk_master_status()` |
| `query_enabled_test_ep.py` | 933B | 2026-08-21 22:42 | - | - |
| `query_live_endpoints.py` | 1.1KB | 2026-08-21 22:07 | - | - |
| `query_normal_live_final.py` | 354B | 2026-08-21 22:43 | - | - |
| `query_turn23_endpoints.py` | 1.1KB | 2026-08-21 22:19 | - | - |
| `query_turn30_live.py` | 1.2KB | 2026-08-22 00:08 | - | - |
| `r2.py` | 1.4KB | 2026-10-21 11:58 | - | - |
| `read_conftest.py` | 323B | 2026-08-30 22:03 | - | - |
| `read_verify_fail.py` | 217B | 2026-09-25 10:20 | - | - |
| `record_evolution_and_sync.py` | 7.5KB | 2026-10-20 21:07 | 오늘자(2026-10-20) RGON Omni-Link Hub v6.0.3 진화 기록을 | `update_evolution_json()`, `update_evolution_md()`, `find_token()`, `get_sheets_service()`, `sync_sheets()`, `git_commit_and_push()`, `main()` |
| `register_final_out.py` | 1.2KB | 2026-10-17 22:09 | - | - |
| `reissue_channel_tokens.py` | 4.9KB | 2026-07-17 07:32 | - | `class LogStream [__init__, write, flush]`, `main()` |
| `remove_obsolete_func.py` | 1.0KB | 2026-08-21 16:28 | - | - |
| `remove_second_method.py` | 1.5KB | 2026-08-22 00:20 | - | - |
| `repair_bus.py` | 1022B | 2026-10-17 22:51 | - | - |
| `reproduce_growthpod.py` | 321B | 2026-09-25 10:39 | - | - |
| `restore_secrets.py` | 2.9KB | 2026-10-16 10:14 | ══════════════════════════════════════════════════════════════════ | `log()`, `restore_secrets()` |
| `restore_slices.py` | 7.0KB | 2026-09-25 10:54 | - | - |
| `rewrite_master_signal.py` | 11.7KB | 2026-08-22 00:19 | - | - |
| `rgon_alpha_clone_engine.py` | 51.0KB | 2026-10-19 18:49 | [v11.26-CREATOR-FORGE] | `safe_send_telegram()`, `sync_rgon_memory()`, `run_alpha_full_patrol()`, `execute_alpha_command()`, `get_alpha_status()`, `get_alpha_chat_history()`, `handle_alpha_chat_message()` |
| `rgon_alpha_deep_button_auditor.py` | 11.5KB | 2026-10-19 11:11 | ══════════════════════════════════════════════════════════════════════════════ | `run_deep_button_audit()`, `get_button_audit_report()` |
| `rgon_aside_browser_agent.py` | 38.3KB | 2026-10-19 20:10 | [v11.26-CREATOR-FORGE] | `load_memory()`, `save_memory()`, `safe_send_telegram()`, `get_page_context()`, `get_aside_status()`, `execute_sub_agents_7_channels()`, `execute_aside_command()`, `execute_all_in_one_multitab_mission()` |
| `rgon_auto_evolve_brain.py` | 62.4KB | 2026-10-20 22:23 | rgon_auto_evolve_brain.py — RGON 자가 진화 두뇌 엔진 v1.0 (TOP1 TOTAL WAR) | `now()`, `rel()`, `sha1_bytes()`, `sha1_file()`, `read_text()`, `backup()`, `write_text()`, `load_json()`, `save_json()`, `class AntibodyMemory [__init__, antibodies, get, hit, add_antibody, record_skill…]`, `count_copy()`, `strip_copy()`, `count_dom()`, `protect_dom()`, `ensure_nocache()`, `count_pollinations_logo()`, `add_nologo()`, `class PromptAndRecipeEvolver [__init__, _load, _items, _match, _find, _pkey…]`, `fnd()`, `health_score()`, `class SelfAuditorAndHealer [__init__, code_targets, watermark_images, _node_check_code, syntax_failures, _probe…]`, `class NextEvolutionGenerator [__init__, _candidates, generate, _to_clipboard]`, `class SheetsLink [__init__, connect, _ensure_tab, register_top, append]`, `_top1_entry()`, `_find_old()` …(+9) |
| `rgon_auto_sync_daemon.py` | 5.4KB | 2026-10-17 20:51 | ⚡ 르곤-안실장 양방향 시그널 자동 캐치 & IN/OUT 무인 동기화 데몬 엔진 | `load_state()`, `save_state()`, `handle_in_signal()`, `handle_out_signal()`, `run_self_test()`, `main()` |
| `rgon_auto_watcher.py` | 21.8KB | 2026-10-23 07:30 | RGON 오토 기어 3단 — 24시간 무토큰 문지기 로봇 & 텔레그램 리모컨 (rgon_auto_watcher.py) | `log_msg()`, `load_telegram_creds()`, `tg_send()`, `tg_get_updates()`, `r14_clean_code()`, `execute_omni_file()`, `set_clipboard()`, `prompt_ahn_queue_box()`, `scan_and_relocate_downloads()`, `check_and_process_ahn_text_queue()`, `get_latest_omni()`, `build_briefing_text()`, `prompt_pc_box()`, `main_loop()`, `class RGONQueueHandler [log_message, _send_cors, do_OPTIONS, do_GET, do_POST]`, `_start_queue_servers()` |
| `rgon_bridge_8765.py` | 3.5KB | 2026-10-23 07:30 | - | `extract_code()`, `save_code()`, `class H [log_message, _send, _trusted, do_GET, do_OPTIONS, do_POST]` |
| `rgon_full_agency_live_audit.py` | 18.1KB | 2026-10-19 01:53 | [RGON-001 수석보좌관 주관] 전 기관(본관+1~6청사+5대 안전웹앱+18대 일거리+야간자율주행+모닝브리핑) 25개 관문 실전 종합 감사 | `detect_active_port()`, `http_get()`, `http_post()`, `run_rgon_full_agency_audit()` |
| `rgon_master_scheduler.py` | 8.9KB | 2026-10-18 21:45 | rgon_master_scheduler.py [르곤 보좌관 직할 일·주·월·연 4단계 마스터 스케줄러 & 무인 통제 엔진] | `load_roadmap()`, `execute_scheduled_cycle()` |
| `rgon_morning_routine.py` | 2.1KB | 2026-10-23 07:30 | - | `run_step()`, `main()` |
| `rgon_real_browser_inspector.py` | 74.7KB | 2026-10-19 19:05 | rgon_real_browser_inspector.py [르곤 최고난도 실제 작동 검수 엔진 — Hardcore Real-Execution Inspector] | `detect_active_port()`, `http_get()`, `http_post()`, `run_inspector()` |
| `rgon_runner.py` | 10.0KB | 2026-10-22 18:17 | - | `_r14_ok()`, `_r14_is_junk()`, `_r14_trim_edges()`, `_r14_trim_tail()`, `_r14_join()`, `_r14_variants()`, `r14_smart_purify_ex()`, `r14_smart_purify()`, `r14_atomic_write()`, `r14_guard_file()`, `r14_install_funcs()`, `_r14_collect()`, `_r14_guard_call()`, `r14_install_process_hooks()`, `_send_runner_tg_report()` |
| `rgon_youtube_skill_scout.py` | 45.0KB | 2026-10-23 18:24 | RGON YouTube Skill Scout v13 — 유튜브 트렌드 감지 & 지식·스킬 자동 흡수 (Python 3 표준 라이브러리 전용) | `log()`, `now_iso()`, `http_get()`, `safe_get()`, `parse_video_id()`, `extract_json_obj()`, `text_of()`, `parse_count()`, `clean_url()`, `host_of()`, `is_youtube()`, `classify_link()`, `extract_links()`, `parse_caption_xml()`, `parse_caption_json3()`, `fetch_transcript()`, `summarize()`, `summarize_description()`, `blank_info()`, `apply_seed_hints()`, `analyze_video()`, `fetch_channel_rss()`, `_find_key()`, `_walk_videos()`, `fetch_channel_page_videos()` …(+25) |
| `run_atomic_and_gather.py` | 5.5KB | 2026-08-21 14:03 | - | `test_kis_atomic()`, `benchmark_gather_tasks()` |
| `run_benchmark_and_fault.py` | 4.1KB | 2026-08-21 06:46 | - | `time_fn()`, `fetch_signal()` |
| `run_clean_patch.py` | 5.1KB | 2026-08-21 14:26 | - | `run_cmd()` |
| `run_comprehensive_audit.py` | 7.8KB | 2026-08-21 14:35 | - | `run_cmd()`, `_norm_sig()`, `inspect_types()` |
| `run_dashboard.py` | 217.2KB | 2026-10-19 20:10 | ══════════════════════════════════════════════════════════════════ | `load_wisdom_ledger()`, `save_wisdom_ledger()`, `get_wisdom_prompt_context()`, `add_wisdom_entry()`, `get_system_version_info()`, `get_github_token()`, `get_local_secrets()`, `scan_suno_audio_files()`, `notify_telegram()`, `run_suno_render_worker()`, `check_nvda_health()`, `get_system_metrics()`, `record_dispatch_task()`, `find_available_port()`, `call_gemini_server_side()`, `clean_general_affairs()`, `run_empire_council_briefing()`, `analyze_sensory_empathy()`, `analyze_vision_clone_team()`, `analyze_youtube_url_intel()`, `register_copyright_dossier()`, `generate_neural_tts_audio()`, `analyze_app_voc_evolution()`, `generate_key_sync_hash()`, `send_tunnel_telegram_notification()` …(+5) |
| `run_deep_inspection.py` | 4.0KB | 2026-08-21 08:32 | - | `test_kis()` |
| `run_deep_profiling.py` | 5.9KB | 2026-08-21 13:55 | - | `run_single_profile()`, `main_profile()` |
| `run_full_e_inspection.py` | 3.9KB | 2026-08-21 14:02 | - | `run_cmd()` |
| `run_full_verification.py` | 4.5KB | 2026-08-18 17:32 | - | - |
| `run_master_audit_v2.py` | 6.3KB | 2026-08-21 06:46 | - | `format_res()`, `measure()` |
| `run_p14_probe.py` | 645B | 2026-09-14 09:14 | - | - |
| `run_p30_1_checks.py` | 3.1KB | 2026-08-30 18:12 | - | - |
| `run_p30_investigation.py` | 2.5KB | 2026-08-30 17:55 | - | - |
| `run_p30_tests.py` | 5.2KB | 2026-08-30 17:56 | - | `class LoopBoundFakeNotifier [__init__, send_message]`, `test_fake_notifier_execution()` |
| `run_p31_exact_measurements.py` | 3.0KB | 2026-08-30 18:51 | - | - |
| `run_p31_investigation.py` | 3.3KB | 2026-08-30 18:51 | - | - |
| `run_p32_cleanup.py` | 2.7KB | 2026-08-30 19:29 | - | - |
| `run_p32_investigation.py` | 2.7KB | 2026-08-30 19:28 | - | - |
| `run_p33_raw_measurements.py` | 6.3KB | 2026-08-30 19:46 | - | - |
| `run_p35_part1.py` | 2.2KB | 2026-08-30 22:59 | - | - |
| `run_p35_part2.py` | 3.8KB | 2026-08-30 22:59 | - | - |
| `run_p36_part2_diff.py` | 4.6KB | 2026-08-30 23:29 | - | - |

## 🌐 HTML
| 경로 | 크기 | 수정 | title | 패치 마커 |
|---|---|---|---|---|
| `index.html` | 205.2KB | 2026-10-23 19:20 | 청와대 중앙 컨트롤 타워 v11.26-CREATOR-FORGE \| Spatial Glass OS | `RGON-YT-SCOUT-V13`, `RGYT-PLACE-ONCE-V15` |
| `offline.html` | 3.5KB | 2026-10-19 17:32 | 청와대 AI 중앙 컨트롤타워 - 터널 재개통 대기 중 | - |
| `p1.htm` | 703B | 2026-10-21 13:16 | - | - |
| `p2.htm` | 610B | 2026-10-21 13:17 | - | - |
| `rgon_alpha_audience.html` | 586.9KB | 2026-10-23 19:20 | 👑 이상일 대표님 ⇄ 🛰️ 르곤-알파 1:1 전담 독립 대화창 (독대실) | `RGON-STEP11`, `RGON-YT-SCOUT-V13`, `RGYT-PLACE-ONCE-V15` |
| `rgon_alpha_chat.html` | 592.5KB | 2026-10-23 19:20 | 👑 이상일 대표님 ⇄ 🛰️ 르곤-알파 1:1 전담 독립 대화창 (독대실) | `RGON-STEP11`, `RGON-YT-SCOUT-V13`, `RGYT-PLACE-ONCE-V15` |

## 📜 JavaScript
| 경로 | 크기 | 수정 | 구분 | 주요 함수 | 마커 |
|---|---|---|---|---|---|
| `.temp_s_0.js` | 769B | 2026-10-17 23:12 | - | - | - |
| `aside_drawer.js` | 24.3KB | 2026-10-19 19:35 | - | `detectCurrentPage()`, `injectAsideStyles()`, `injectAsideDOM()`, `toggleAsideDrawer()`, `openAsideDrawer()`, `closeAsideDrawer()`, `goToAlphaChat()`, `loadAsideStatus()`, `triggerAsideAction()`, `runAsidePromptCommand()`, `renderChannelsResults()`, `renderMultitabStatusBoard()`, `initAsideDrawer()` | - |
| `pwa_bootstrap.js` | 9.3KB | 2026-10-21 07:28 | - | `injectPwaUI()`, `updatePwaBadge()`, `monitorTunnelBridge()`, `isDokdae()`, `norm()`, `ensureStyle()`, `tag()`, `tagNode()`, `scan()`, `sched()`, `boot()` | - |

## 🗂️ JSON
| 경로 | 크기 | 수정 | 구조 |
|---|---|---|---|
| `a4_a5_snapshot_output.json` | 8.5KB | 2026-08-25 23:56 | keys: s1, s2, real_elapsed |
| `active_design_theme.json` | 412B | 2026-10-19 19:06 | keys: current_theme, theme_name, palette, applied_at, applied_by, css_path |
| `active_external_tunnel.json` | 348B | 2026-10-21 10:11 | keys: active_tunnel_url, tunnel_url, dashboard_url, port, verified_status, opened_at |
| `agency_stage_gate_master.json` | 12.4KB | 2026-10-19 18:46 | version=v11.26-CREATOR-FORGE · keys: version, updated_at, agencies |
| `anchongri_exec_queue.json` | 3B | 2026-10-20 17:31 | 배열 0개 |
| `aside_local_memory.json` | 24.9KB | 2026-10-19 20:17 | keys: engine, vault_security, recent_runs, active_sub_agents_count, last_updated, last_run, last_all_in_one |
| `auto_production_queue.json` | 4.9KB | 2026-10-19 23:52 | version=v11.26-CREATOR-FORGE · keys: version, corps_latest, tasks |
| `cheongwadae_comm_log.json` | 21.8KB | 2026-10-20 20:19 | version=v11.26-CREATOR-FORGE · keys: version, channel_status, messages, updated_at |
| `cheongwadae_golden_hashes.json` | 3.5KB | 2026-10-19 19:07 | keys: departments, safe_apps |
| `clean_isolated_metrics.json` | 8.9KB | 2026-08-26 00:11 | keys: s1, s2, mem1, mem2, mem3, real_elapsed_seconds |
| `department_work_queue.json` | 12.6KB | 2026-10-19 19:06 | version=v8.5-cleanroom-work-queue · keys: version, updated_at, compliance_policy, departments |
| `dept_sub_agents_state.json` | 7.2KB | 2026-10-21 07:48 | version=v11.26-CREATOR-FORGE · keys: system, version, updated_at, parent_commander, sub_agents |
| `ecc_skills_vault.json` | 2.2KB | 2026-10-18 02:21 | version=v6.2-direct-photo · keys: system, name, version, total_skills, total_agents, categories, last_updated |
| `evolution_memory.json` | 7.0KB | 2026-10-22 19:44 | 배열 14개 |
| `google_sheets_history_report.json` | 145.3KB | 2026-10-22 19:44 | keys: report_version, generated_at, summary, sheets, evolution_sync_history |
| `google_sheets_sync_queue.json` | 28.1KB | 2026-10-19 23:52 | 배열 33개 |
| `grok_viral_master_plan.json` | 4.4KB | 2026-10-19 17:31 | version=v11.26-CREATOR-FORGE.7-VIRAL-MASTER · keys: version, updated_at, engine, slots, profile_bio, zero_violation_guard |
| `latest_tunnel_info.json` | 328B | 2026-10-21 07:29 | keys: active_tunnel_url, tunnel_url, dashboard_url, port, verified_status, opened_at |
| `master_analyze_response.json` | 3.3KB | 2026-08-19 11:56 | keys: status, symbol, master_score, signal, signal_ko, confidence, components, pod_signals, pod_allocation, recommendation, risks, timestamp |
| `memory_vault.json` | 20.9KB | 2026-10-17 07:15 | 배열 18개 |
| `morning_briefing_report.json` | 1.4KB | 2026-10-19 19:06 | version=v9.0-cheonbu-ep1-genesis · keys: version, generated_at, duty_commanders, headline, metrics, night_achievements |
| `nvda_analysis_verification.json` | 3.3KB | 2026-08-19 12:14 | keys: timestamp, nvda_price, overall_signal, overall_confidence, consensus_score, bull_count, bear_count, neutral_count, signals, summary |
| `nvda_trading_diagnosis_report.json` | 5.6KB | 2026-10-19 04:34 | version=v11.26-CREATOR-FORGE · keys: version, audit_date, auditor, target_system, four_core_diagnoses, status |
| `omni_agent_bus.json` | 39.3KB | 2026-10-19 19:06 | version=v8.0-cheongwadae-central-command · keys: system, version, registry, messages, latest_synergy_relay |
| `omni_dispatch_queue.json` | 2.6KB | 2026-10-20 22:24 | 배열 1개 |
| `omni_shared_clipboard.json` | 52B | 2026-10-20 17:31 | keys: entries, history, updated |
| `package-lock.json` | 16.7KB | 2026-04-04 23:16 | version=1.0.0 · keys: name, version, lockfileVersion, requires, packages |
| `package.json` | 323B | 2026-04-04 22:57 | version=1.0.0 · keys: name, version, description, main, scripts, dependencies |
| `phase1625_isolated_metrics.json` | 9.7KB | 2026-08-26 08:11 | keys: s1, s2, mem_samples, s1_s2_elapsed, total_elapsed |
| `posts_raw_content.json` | 126.7KB | 2026-08-18 13:29 | 배열 16개 |
| `remaining_11_wrapped_report.json` | 2.5KB | 2026-08-18 13:47 | 배열 11개 |
| `rgon_alpha_button_audit_report.json` | 3.7KB | 2026-10-19 19:06 | keys: status, success, receipt_id, timestamp, elapsed_ms, total_screens_audited, total_buttons_audited, passed_buttons_count, dummy_buttons_count, dummy_button_rate, overall_pass_rate, approval_stamp… |
| `rgon_alpha_chat_history.json` | 107.6KB | 2026-10-19 21:24 | keys: room, title, created_at, updated_at, messages, live_sub_agents, standing_state, parent_commander |
| `rgon_alpha_patrol_log.json` | 33.6KB | 2026-10-21 00:31 | 배열 41개 |
| `rgon_alpha_persona_constitution.json` | 2.2KB | 2026-10-19 09:53 | keys: agent_id, callsign, title, rank, origin, duty, constitution_articles, speech_style, created_at |
| `rgon_brain_snapshot.json` | 39.9KB | 2026-10-23 22:29 | version=v6.2.0-step16 · keys: schema, version, generated_at_kst, synced_at_kst, sync_rate, score, max_score, self_diagnosis, antibody_range, antibodies, top_priority_id, top_priority …(+19) |
| `rgon_constitution.json` | 1.8KB | 2026-10-21 20:57 | version=1.0.0-CONSTITUTION · keys: name, version, immutable, immutable_note, kill_switch, blast_radius_levels, gates, guardrails |
| `rgon_schedule_roadmap.json` | 5.6KB | 2026-10-19 19:06 | version=v8.7-rgon-master-schedule · keys: version, commander, controller, prime_executor, updated_at, daily_schedule, weekly_schedule, monthly_schedule, yearly_schedule, last_executed_cycle |
| `rgon_skill_radar.json` | 80.5KB | 2026-10-23 18:24 | version=v11.26-CREATOR-FORGE · keys: videos, channels, github_skills, version, generated_at, seed_urls, hook_engine, stats, attribution |
| `rgon_watcher_state.json` | 108B | 2026-10-22 21:55 | keys: last_file, last_mtime, last_update_id |

## 🩺 Python 문법 검증 (ast.parse)
- ✅ 스캔한 Python 551개 모두 문법 정상

<!-- [RGON-CODEMAP-STEP17-START] -->
## Step 17 (v6.3.0-step17) — 창립자 영혼 & 동양 3대 고전

| 파일 | 역할 |
|---|---|
| `step17_founder_soul_and_eastern_wisdom.py` | Step 17 단일 설치 스크립트 (멱등, 보호 파일 해시 전후 검증, Git 동기화) |
| `RGON_PHILOSOPHY.md` | 영구 보존 마스터 철학서: 제0장 창립자 선언 · 제1장 명심보감 7강령 · 제2장 도덕경 5법칙 · 제3장 주역 64괘 엔진 |
| `rgon_iching_64_engine.py` | 주역 64괘 전체 내장 6비트 상태 판독 & AI 전략 처방 엔진 (--list / --root / --no-save) |
| `rgon_today_hexagram.json` | 오늘의 괘 · 6효 판독 결과 · 궁변통구 처방 · 다음 한걸음 |
| `restore_secrets.py` | [RGON-SELF-HEAL-V17] 궁변통구 시크릿 복원기 (환경변수 있을 때만 복원, 항상 exit 0) |
| `restore_secrets_legacy.py` | 기존 restore_secrets 로직 보존본 (존재 시 자가치유판이 먼저 실행) |
| `rgon_integrity_baseline.json` | 보호 파일(.html/.js/manifest.json) SHA-256 베이스라인 (제1효 판독용) |
| `CLAUDE.md` | V17 헌법: 제0조 창립자 선언 · 동서 통합 헌법 · 항체 R16/R17 |

- 6효 매핑: 1 기반(Git/해시) · 2 소통(독대실) · 3 자동화(스케줄러) · 4 트렌드(스킬 레이더) · 5 콘텐츠(진화 로그) · 6 시장(스냅샷)
- 실행: `python rgon_iching_64_engine.py` → `rgon_today_hexagram.json`
<!-- [RGON-CODEMAP-STEP17-END] -->

<!-- [RGON-STEP18-WBC-START] -->
## Step 18 코드 맵 (v11.25-SELF-EVOLVE)

- `rgon_white_blood_cell.py`: 백혈구 자가치유 & 면역 순찰 엔진 (patrol / run_safely / shield / adapt_dict / fingerprint / install_excepthook / link_hexagram)
- `rgon_immune_ledger.json`: 면역 원장 (antibodies R1~R27, healed_events, bypass_log, fingerprints, suppressed_count, health_score)
- `step18_white_blood_cell_immune_engine.py`: Step 18 설치 스크립트 (멱등)
- 세이프가드 장착 대상: `rgon_youtube_skill_scout.py`, `control_tower_bot.py`, `telegram_morning_report.py`, `update_3channels_analytics.py`, `github_scout_adapter.py`, `agent_swarm_cloner.py`, `channel_agent.py`, `dept_sub_agents_corps.py`, `multi_agent_orchestrator.py`, `patch_omni_agent_bus_backend.py`, `patch_omni_agent_bus_frontend.py`, `qa_button_inspector_agent.py`, `rgon_aside_browser_agent.py`, `rgon_bridge_8765.py`, `tunnel_discovery_bridge.py`
- 백업: `.rgon_backup/step18_*`, 스냅샷: `.rgon_backup/wbc_snapshots`, 격리: `.rgon_backup/wbc_quarantine`
<!-- [RGON-STEP18-WBC-END] -->

<!-- RGON:STEP19-CODEMAP:BEGIN -->
## 🗺️ rgon_nutrient_engine.py — v11.26-CREATOR-FORGE (R19)

- MarkdownPurifier: purify_html(html_text, source_url=''), fetch_and_purify(url, timeout=10), self_check()
- SkillAutoForge: forge() / forge_from_radar(root_dir) → skills/<slug>/SKILL.md, SKILL_INDEX.json, README.md
- TrinityCouncil: bull() · bear() · judge() · deliberate(topic, metrics=None) → rgon_council_decisions.json
- run_digest(root) → rgon_nutrient_report.json / show_status() / self_test()
- run_safely(fn, ...): 백혈구 세이프가드 (예외 → 기본값 폴백 + rgon_nutrient_errors.log)
- rgon_youtube_skill_scout.py: run_nutrient_digest_safely(root_dir=None) 훅 (마커 RGON:STEP19-NUTRIENT-HOOK)
- step19_absorb_top100_nutrients.py: Step 19 일괄 설치·검증·동기화·푸시 스크립트
<!-- RGON:STEP19-CODEMAP:END -->

<!-- RGON-STEP20-START -->
## [Step 20] v11.25-SELF-EVOLVE — 일일 자율 순환 루프 (R20)
- 버전: v11.26-CREATOR-FORGE / 항체 범위: R1~R27
- R20: 일일 자율 순환 루프(백혈구 순찰 → 영양분 소화·스킬 주조 → 3자 심판 → 주역 64괘 아침 브리핑) 무인 자동화
- 심장: rgon_daily_cycle.py (--run / --status / --self-test)
- 4단계: 백혈구 순찰 → 영양분 3스푼 소화·SKILL.md 주조·TrinityCouncil 심의 → 주역 64괘 → MORNING_BRIEF.md / rgon_morning_brief.json
- 클라우드: .github/workflows/rgon_daily_autonomous_cycle.yml (cron '0 22 * * *' = KST 07:00, workflow_dispatch, continue-on-error)
- 보호: .html / .js / manifest.json 304개 단 1바이트도 수정 금지
- 파일 지도: rgon_daily_cycle.py(순환 심장) · get_daily_brief_text(root_dir=None)(텔레그램 헬퍼) · step20_autonomous_daily_loop.py(설치기)
<!-- RGON-STEP20-END -->

<!-- RGON:STEP21:START -->
## Step 21 (v11.25-SELF-EVOLVE)
- `GLOSSARY.md` — 도메인 공유 언어 15선
- `rgon_spec_ticket_Shield.py` — SpecTicketDecomposer · AgentShieldScanner (--run/--self-test/--status)
- `rgon_active_tickets.json` · `TICKETS_BOARD.md` — 작업 그래프/Frontier
- `rgon_agentshield_report.json` — 보안 스캔 리포트
- `skills/` — Mindung 4종 SKILL.md 추가
<!-- RGON:STEP21:END -->

<!-- STEP24 -->
## v11.25-SELF-EVOLVE (Step 24)
- `rgon_trading_council.py`: Bull/Bear/Judge 3자 심판 + 주역 64괘 필터 → `rgon_trading_council.json`, `--merge`로 brief 병합
- `skills/trinity-trading-council/SKILL.md`: 19번째 정식 스킬
- `rgon_daily_cycle.py`: STEP24 훅(atexit)으로 순환 시 자동 실행
<!-- /STEP24 -->

## 🧬 Step 26 (v11.25-SELF-EVOLVE)
- `rgon_self_evolution_engine.py` — Skill2Gene · RatchetCurator · SelfQuestioningLoop (--run/--self-test/--json/--merge/--ensure-index)
- 산출물: rgon_genes.json · rgon_capsules.json · rgon_ratchet_audit.json · rgon_self_questions.json

<!-- STEP27:BEGIN -->
## Step 27 · v11.26-CREATOR-FORGE · 항체 R1~R27 · 정식 스킬 23개 (사람의 4대 생명 단계: 오감 100% + 창조 100%)
- R27: 오감(Live Omni-Sense & Stomper 킬리스트) + 창조 공방(SkillForge·Voyager 도구 자율 합성 & 격리 검증) 상시 가동 — 검증 통과(exit_code=0)한 도구만 정식 승격(혁고정신 革故鼎新)
- 엔진: rgon_omni_creator_forge.py (LiveOmniSense·StomperKillGate #21-噬嗑 / TieredMemoryPromoter / AutonomousCreatorForge #50-鼎)
- 창조 도구: custom_tools/stomper_signal_filter.py · kelly_hexagram_sizer.py · skill_synergy_composer.py (Surrogate Verifier 3단계 통과분만 승격)
- 스킬 22 stomper-kill-list-gate(#21-噬嗑) · 스킬 23 autonomous-creator-forge(#50-鼎) · 카파시 4원칙 × 무위자연·과유불급·삼성 3/3
<!-- STEP27:END -->

<!-- [RGON-STEP28-K-AVATAR-START] -->
## Step 28 (v11.27-K-AVATAR · 아온 A-ON)
- rgon_k_avatar_engine.py — 아온(A-ON·芽溫) 성장 상태 계산·심판 줄 병합
- rgon_k_avatar_state.json — 성장 상태
- skills/k-avatar-growth-soul/SKILL.md — 24번째 정식 스킬
- 독대실 V13 블록 — 👶 아온(A-ON) 육신 탭 (V15 placeOnce 보존)
<!-- [RGON-STEP28-K-AVATAR-END] -->

<!-- [RGON-STEP29-AON-3DDROP-START] -->
## Step 29 (v11.29-ROAMING-AON · 3D 물방울 졸라맨 아온)
- skills/character-detail-master-top1/SKILL.md — 25번째 정식 스킬 (캐릭터 디테일 TOP 1 마스터)
- 독대실 V13 블록 — 💧 8-Stop 3D 물방울 + 깜찍 5겹 보석눈 + 관절형 졸라맨 팔다리 (V15 보존)
<!-- [RGON-STEP29-AON-3DDROP-END] -->

<!-- [RGON-STEP31-EXCRETORY-START] -->
## Step 31 (v11.30-EXCRETORY-CLEAN · 배설기관 정화)
- rgon_excretory_organ.py — 신장 여과·대장 백업 슬림화·autoDream 문서 중복 정화
- rgon_excretion_report.json — 배설·정화 감사 리포트
<!-- [RGON-STEP31-EXCRETORY-END] -->

<!-- [RGON-CODEMAP-STEP32] -->
## Step 32 — 제8기관: 자율 대행·위임 집행 기관 (v11.31-MUSE-DELEGATION)
- `rgon_muse_delegator.py`: Muse Wonder 비동기 위임 큐 + 3-Tier HITL 게이트 (`--self-test`, `--list`, `--add`, `--approve`, `--hold`)
- `rgon_muse_tasks.json` / `docs/rgon_muse_tasks.json`: 대행 작업 큐 (sha256 무결성)
- `skills/muse-autonomous-delegator/SKILL.md`: 28번째 정식 스킬
- 7개 HTML V13 블록(YT-SCOUT-V13 / UX-CLEANUP-V13) 내부 `[RGON-MUSE-V1]`: 아온 다이내믹 아일랜드 + 📋대행 독 + 결재 보드
- `rgon_voice_organ.py` — 제9기관 성대·청각 음성 교감 기관 (R1~R33)
- `rgon_aon_soul_brain.py` — 제10기관 감성·인격 대화 두뇌 & 해마 기억 기관 (R1~R34)
- `rgon_laptop_hands.py` — 제11기관 노트북 만능 제어 수족 & 중요 결재 수동 스위치 (R1~R39)
- `rgon_aon_desktop_playground.py`: 제12기관 아온 창틀 탈출 노트북 놀이터 & 8대 장난꾸러기 생명체 FSM (v11.38-AON-OMNI-DIALOGUE)
- `rgon_aon_iching_dao_oracle.py`: 제13기관 아온 주역 64괘·정통 음력 매화역수·육효 시운 도술관 (v11.38-AON-OMNI-DIALOGUE)
- `rgon_aon_omni_insight_eye.py`: 제14기관 아온 만물 격물치지 전방위 통찰안 (v11.38-AON-OMNI-DIALOGUE)
- `rgon_aon_dialogue_engine.py`: 제15기관 아온 초격차 대화 이해 & 올인원 대화 허브 (R39 · v11.38-AON-OMNI-DIALOGUE)

<!-- [RGON-R40-ORGAN16-START] -->
## 제16기관 · `rgon_neural_synapse_verifier.py` (스킬 #36 `aon-neural-synapse-verifier`)
12개 기관 병렬 셀프테스트 · 10대 시냅스 E2E · V13 HTML/SSOT 검증 → `rgon_neural_synapse_map.json`
<!-- [RGON-R40-ORGAN16-END] -->
