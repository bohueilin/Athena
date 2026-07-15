# Normalized Research Ontology

Derived from **447** tagged papers (one normalized tag record per paper in `paper-to-ontology-map.jsonl`). Machine-readable vocab + frequencies in `ontology.json`; queryable graph in `research-relationship-graph.json`.

> Frequency = how many papers touch a token. It reflects **corpus coverage, not evidence weight** — weight is judged in the syntheses by reproducibility, threat-model realism, and replication.

## Evidence strength distribution

| strength | papers |
|---|--:|
| moderate | 318 |
| insufficient | 66 |
| preliminary | 39 |
| strong | 24 |

## Top assets (of 15 distinct)

| token | papers |
|---|--:|
| `model_outputs` | 290 |
| `model_weights` | 170 |
| `training_data` | 148 |
| `user_data` | 114 |
| `safety_policies` | 104 |
| `prompts_context` | 72 |
| `embeddings` | 57 |
| `ip` | 57 |
| `identity_authz` | 50 |
| `execution_env` | 31 |
| `eval_artifacts` | 28 |
| `retrieval_corpus` | 24 |
| `audit_records` | 22 |
| `agent_memory` | 20 |
| `tool_credentials` | 8 |

## Top adversaries (of 12 distinct)

| token | papers |
|---|--:|
| `external_attacker` | 265 |
| `malicious_user` | 143 |
| `insider` | 65 |
| `supply_chain` | 45 |
| `compromised_data_source` | 44 |
| `model_extractor` | 39 |
| `malicious_model_provider` | 36 |
| `physical_world` | 32 |
| `adaptive_evaluator_aware` | 30 |
| `malicious_app_dev` | 27 |
| `coordinating_agents` | 23 |
| `compromised_tool` | 10 |

## Top surfaces (of 21 distinct)

| token | papers |
|---|--:|
| `model_serving` | 262 |
| `training_pipeline` | 130 |
| `api_boundary` | 116 |
| `prompt_context` | 97 |
| `model_distribution` | 81 |
| `fine_tuning` | 80 |
| `physical_sensors` | 48 |
| `post_training` | 44 |
| `network` | 38 |
| `agent_to_agent` | 31 |
| `data_storage` | 29 |
| `embeddings` | 25 |
| `rag_ingestion` | 23 |
| `human_approval` | 18 |
| `tool_invocation` | 17 |
| `retrieval` | 16 |
| `identity_authz` | 16 |
| `logging_telemetry` | 13 |

## Top attacks (of 33 distinct)

| token | papers |
|---|--:|
| `evasion` | 141 |
| `privacy_leakage` | 82 |
| `adversarial_example` | 80 |
| `data_poisoning` | 72 |
| `jailbreak` | 63 |
| `prompt_injection` | 51 |
| `backdoor` | 48 |
| `membership_inference` | 47 |
| `forgery` | 27 |
| `attribute_inference` | 25 |
| `model_inversion` | 23 |
| `training_data_reconstruction` | 21 |
| `watermark_removal` | 21 |
| `unauthorized_adaptation` | 21 |
| `model_extraction` | 17 |
| `deepfake` | 17 |
| `provenance_manipulation` | 15 |
| `model_theft` | 14 |

## Top defenses (of 31 distinct)

| token | papers |
|---|--:|
| `detection` | 167 |
| `robust_optimization` | 100 |
| `runtime_monitoring` | 70 |
| `input_filtering` | 56 |
| `adversarial_training` | 51 |
| `red_teaming` | 36 |
| `data_validation` | 35 |
| `evidence_logging` | 29 |
| `output_filtering` | 28 |
| `differential_privacy` | 28 |
| `watermarking` | 28 |
| `policy_gating` | 26 |
| `rollback` | 22 |
| `incident_containment` | 22 |
| `federated_learning` | 21 |
| `human_approval` | 20 |
| `authentication` | 16 |
| `rate_limiting` | 14 |

## Top evidence mechanisms (of 16 distinct)

| token | papers |
|---|--:|
| `holdout` | 300 |
| `adversarial_eval` | 284 |
| `statistical_guarantee` | 67 |
| `reproducible_traces` | 56 |
| `human_review` | 48 |
| `adaptive_attack_testing` | 37 |
| `formal_verification` | 33 |
| `continuous_monitoring` | 5 |
| `residual_risk_acceptance` | 4 |
| `independent_audit` | 3 |
| `integration_tests` | 2 |
| `tamper_evident_logs` | 2 |
| `red_teaming` | 1 |
| `evidence_logging` | 1 |
| `canary` | 1 |
| `signed_evidence` | 1 |

## Relationship-graph queries

- **Which attacks target an asset?** edges `p=targets_asset, o=<asset>` → papers → their `studies_attack`.
- **Which defenses mitigate an attack?** `attack_defense_cooccurrence[attack=<x>]` ranked by `co_paper_count`.
- **Under which threat models was a defense tested?** map records with that defense → `threat_model`.
- **What evidence supports a defense?** those papers' `verified_by` + `evidence_strength`.
- **Which papers relate?** `related_to` edges.

## Provenance & integrity

- Tag lines parsed: **447** / 432. Malformed lines: **0** (none).
