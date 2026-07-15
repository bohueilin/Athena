# Normalized Research Ontology

Derived from **432** tagged papers (one normalized tag record per paper in `paper-to-ontology-map.jsonl`). Machine-readable vocab + frequencies in `ontology.json`; queryable graph in `research-relationship-graph.json`.

> Frequency = how many papers touch a token. It reflects **corpus coverage, not evidence weight** — weight is judged in the syntheses by reproducibility, threat-model realism, and replication.

## Evidence strength distribution

| strength | papers |
|---|--:|
| moderate | 312 |
| insufficient | 65 |
| preliminary | 38 |
| strong | 17 |

## Top assets (of 15 distinct)

| token | papers |
|---|--:|
| `model_outputs` | 275 |
| `model_weights` | 163 |
| `training_data` | 143 |
| `user_data` | 112 |
| `safety_policies` | 90 |
| `prompts_context` | 67 |
| `ip` | 57 |
| `embeddings` | 54 |
| `identity_authz` | 49 |
| `execution_env` | 30 |
| `retrieval_corpus` | 23 |
| `eval_artifacts` | 22 |
| `audit_records` | 21 |
| `agent_memory` | 19 |
| `tool_credentials` | 7 |

## Top adversaries (of 12 distinct)

| token | papers |
|---|--:|
| `external_attacker` | 255 |
| `malicious_user` | 136 |
| `insider` | 62 |
| `supply_chain` | 43 |
| `compromised_data_source` | 42 |
| `model_extractor` | 39 |
| `malicious_model_provider` | 34 |
| `physical_world` | 32 |
| `malicious_app_dev` | 24 |
| `adaptive_evaluator_aware` | 23 |
| `coordinating_agents` | 22 |
| `compromised_tool` | 9 |

## Top surfaces (of 21 distinct)

| token | papers |
|---|--:|
| `model_serving` | 250 |
| `training_pipeline` | 125 |
| `api_boundary` | 110 |
| `prompt_context` | 88 |
| `model_distribution` | 80 |
| `fine_tuning` | 71 |
| `physical_sensors` | 48 |
| `network` | 38 |
| `post_training` | 36 |
| `data_storage` | 29 |
| `agent_to_agent` | 28 |
| `embeddings` | 24 |
| `rag_ingestion` | 22 |
| `tool_invocation` | 16 |
| `retrieval` | 15 |
| `human_approval` | 15 |
| `identity_authz` | 15 |
| `logging_telemetry` | 12 |

## Top attacks (of 33 distinct)

| token | papers |
|---|--:|
| `evasion` | 133 |
| `privacy_leakage` | 81 |
| `adversarial_example` | 76 |
| `data_poisoning` | 68 |
| `jailbreak` | 55 |
| `prompt_injection` | 49 |
| `membership_inference` | 47 |
| `backdoor` | 45 |
| `forgery` | 27 |
| `attribute_inference` | 25 |
| `model_inversion` | 23 |
| `training_data_reconstruction` | 21 |
| `watermark_removal` | 21 |
| `unauthorized_adaptation` | 19 |
| `model_extraction` | 17 |
| `deepfake` | 17 |
| `provenance_manipulation` | 15 |
| `model_theft` | 14 |

## Top defenses (of 31 distinct)

| token | papers |
|---|--:|
| `detection` | 159 |
| `robust_optimization` | 94 |
| `runtime_monitoring` | 64 |
| `input_filtering` | 54 |
| `adversarial_training` | 46 |
| `data_validation` | 33 |
| `differential_privacy` | 28 |
| `evidence_logging` | 28 |
| `watermarking` | 28 |
| `output_filtering` | 25 |
| `red_teaming` | 23 |
| `policy_gating` | 22 |
| `federated_learning` | 21 |
| `rollback` | 21 |
| `incident_containment` | 20 |
| `human_approval` | 17 |
| `authentication` | 15 |
| `rate_limiting` | 14 |

## Top evidence mechanisms (of 16 distinct)

| token | papers |
|---|--:|
| `holdout` | 296 |
| `adversarial_eval` | 270 |
| `statistical_guarantee` | 67 |
| `reproducible_traces` | 47 |
| `human_review` | 42 |
| `formal_verification` | 33 |
| `adaptive_attack_testing` | 28 |
| `continuous_monitoring` | 5 |
| `independent_audit` | 3 |
| `integration_tests` | 2 |
| `tamper_evident_logs` | 2 |
| `residual_risk_acceptance` | 2 |
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

- Tag lines parsed: **432** / 432. Malformed lines: **0** (none).
