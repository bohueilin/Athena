# Origin RSI/RL + Physical AI Safety Stack Review Handoff

Date: 2026-06-30  
Reviewer: Codex  
Mode: inspection/evaluation only; no code changes, no training reruns, no live API mining

## Executive Verdict

Origin's RSI/RL stack is a credible bounded robot-readiness Gym: Gemma/Cerebras is used as an untrusted proposer/miner, Origin's deterministic oracle is the judge, and learned policies are evaluated against oracle-labeled finish/escalate/refuse decisions. The strongest current evidence is that the stack has real validation gates, zero oracle divergence on preference pairs, reproducible dataset checksums, and measured policy tradeoffs rather than a single overclaimed number.

The biggest credibility gap is still external generalization. The cross-domain and unseen-style results are generated/mined distributions, not natural-world floor-plan generalization. The next frontier is a natural-distribution holdout from real floor plans, plus a true spatial policy architecture that improves structural reachability without trading down safety-critical refuse recall.

## Files Inspected

### Floor Design / RSI Repo

- `/Users/bohueilin/hackathons/Floor design/package.json`
- `/Users/bohueilin/hackathons/Floor design/README.md`
- `/Users/bohueilin/hackathons/Floor design/scripts/render_rsi_dashboard.mjs`
- `/Users/bohueilin/hackathons/Floor design/scripts/validate_rsi_dataset.mjs`
- `/Users/bohueilin/hackathons/Floor design/scripts/validate_pref_pairs.mjs`
- `/Users/bohueilin/hackathons/Floor design/scripts/test_verifier.mjs`
- `/Users/bohueilin/hackathons/Floor design/scripts/build_rsi_dataset.mjs`
- `/Users/bohueilin/hackathons/Floor design/scripts/export_graph_tensors.mjs`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/hazard_augment.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/floor_sampler.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/build_dataset.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/build_pref_pairs.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/propose_verify.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/mine_cross_domain_refusals.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/validate_mined_refusals.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/mine_cross_domain_calibration.py`
- `/Users/bohueilin/hackathons/Floor design/services/foundry-train/validate_mined_calibration.py`
- `/Users/bohueilin/hackathons/Floor design/ml/train.py`
- `/Users/bohueilin/hackathons/Floor design/ml/eval_trained.py`
- `/Users/bohueilin/hackathons/Floor design/ml/safety_policy.py`
- `/Users/bohueilin/hackathons/Floor design/ml/train_safety_policy.py`
- `/Users/bohueilin/hackathons/Floor design/ml/eval_safety_policy.py`
- `/Users/bohueilin/hackathons/Floor design/ml/train_occupancy_policy.py`
- `/Users/bohueilin/hackathons/Floor design/ml/policy_config.json`
- `/Users/bohueilin/hackathons/Floor design/ml/occupancy_policy_config.json`
- `/Users/bohueilin/hackathons/Floor design/ml/occupancy_policy_enriched_config.json`
- `/Users/bohueilin/hackathons/Floor design/ml/occupancy_policy_calibrated_config.json`
- `/Users/bohueilin/hackathons/Floor design/ml/occupancy_policy_budget_config.json`
- `/Users/bohueilin/hackathons/Floor design/ml/occupancy_policy_spatial_config.json`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_RSI_RL_MASTER_HANDOFF.md`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_SAFETY_POLICY_V1_HANDOFF.md`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_BUDGET_SIGNAL_HANDOFF.md`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_SPATIAL_POLICY_HANDOFF.md`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_CROSS_DOMAIN_MINING_REVIEW.md`
- `/Users/bohueilin/hackathons/Floor design/docs/foundry/CODEX_CROSS_DOMAIN_CALIBRATION_HANDOFF.md`

### Origin Web App

- `/Users/bohueilin/hackathons/Origin/apps/origin-web/package.json`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/README.md`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/public/rsi/rsi_dashboard.html`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/public/rsi/dashboard-preview.png`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/factorydad/components/ModelLearning.tsx`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/factorydad/trainingProgress.ts`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/foundry/ui/FoundryApp.tsx`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/siteEval.ts`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/warehouse.ts`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/src/passport/orderContext.ts`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/scripts/verifyServerEvidence.mjs`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/tests/e2e/smoke.spec.ts`
- `/Users/bohueilin/hackathons/Origin/apps/origin-web/tests/e2e/a11y.spec.ts`

## Repo Structure Summary

### `/Users/bohueilin/hackathons/Floor design`

This is the RSI/RL research and artifact repo. It owns:

- dataset construction: `scripts/build_rsi_dataset.mjs`, `services/foundry-train/hazard_augment.py`, `scripts/export_graph_tensors.mjs`
- dataset validation: `scripts/validate_rsi_dataset.mjs`
- verifier math: `scripts/lib/verifier.mjs`, `scripts/test_verifier.mjs`
- preference pairs: `services/foundry-train/build_pref_pairs.py`, `scripts/validate_pref_pairs.mjs`
- gym episodes: `services/foundry-train/floor_sampler.py`, `services/foundry-train/build_dataset.py`
- Gemma/Cerebras proposer loop: `services/foundry-train/propose_verify.py`
- Gemma/Cerebras hard-case mining: `mine_cross_domain_refusals.py`, `mine_cross_domain_calibration.py`
- local training/eval: `ml/train.py`, `ml/train_safety_policy.py`, `ml/train_occupancy_policy.py`, `ml/eval_trained.py`, `ml/eval_safety_policy.py`
- static RSI dashboard: `scripts/render_rsi_dashboard.mjs`, output `outputs/rsi_dashboard.html`

### `/Users/bohueilin/hackathons/Origin/apps/origin-web`

This is the product/demo site. It owns:

- Origin Physical AI landing/foundry UI
- Passport/autonomy-control UI
- live static RSI dashboard copy at `public/rsi/rsi_dashboard.html`
- web validation gates: build, lint, evidence verifier, unit tests, browser e2e tests

## Package Scripts Found

### Floor Design

Key scripts:

- `build:rsi`
- `validate:rsi`
- `baseline:v1`
- `eval:v1`
- `trainenv:p0`
- `build:prefpairs`
- `validate:prefpairs`
- `policy:v1`
- `eval:policy`
- `policy:occupancy`
- `mine:refusals`
- `validate:mined-refusals`
- `policy:occupancy:enriched`
- `mine:calibration`
- `validate:mined-calibration`
- `policy:occupancy:calibrated`
- `policy:occupancy:budget`
- `policy:occupancy:spatial`
- `propose:verify`
- `render:dashboard`
- `test`

Inspection note: `mine:*` commands can call external Cerebras/Gemma unless `--mock` is used. They were not run in this review.

### Origin Web

Key scripts:

- `build`: `tsc -b && vite build`
- `lint`: `eslint .`
- `verify:evidence`
- `test`: `vitest run`
- `test:e2e`: `playwright test`
- `gates`: build + lint + evidence + unit tests
- `gates:full`: gates + e2e

## Dataset Artifacts Found

Located under `/Users/bohueilin/hackathons/Floor design/outputs/rsi_dataset`:

- `layouts.jsonl`: 4,704 lines, 17,687,107 bytes
- `graph_tensors.jsonl`: 4,704 lines, 3,402,116 bytes
- `hard_negatives_v1.jsonl`: 748 lines, 307,204 bytes
- `oracle_training_v1.jsonl`: 1,815 lines, 7,109,362 bytes
- `pref_pairs_v1.jsonl`: 4,704 lines, 2,911,575 bytes
- `cross_domain_refuse_mined_v1.jsonl`: 1,116 lines, 2,692,557 bytes
- `cross_domain_calibration_mined_v1.jsonl`: 1,108 lines, 2,668,057 bytes
- `baseline_v1/metrics.json`
- `baseline_v1/eval_trained.json`
- `safety_policy_v1/metrics.json`
- `safety_policy_v1/eval_saved.json`
- `occupancy_policy_v1/metrics.json`
- `occupancy_policy_v1_enriched/metrics.json`
- `occupancy_policy_v1_calibrated/metrics.json`
- `occupancy_policy_v1_budget/metrics.json`
- `occupancy_policy_v1_spatial/metrics.json`
- `cross_domain_refuse_mining_metrics.json`
- `cross_domain_calibration_mining_metrics.json`
- `propose_verify_metrics.json`
- `splits.json`
- `stats.json`

## Data Sources Found

From `stats.json` and docs:

- `CubiGraph5K/CubiCasa5K-derived`: 3,493 rows
- `Origin deterministic hazard augmentation`: 947 rows
- `Origin procedural generator`: 256 rows
- `MLStructFP test-data`: 7 rows
- `ZInD sample_tour`: 1 row

License classes from the validator:

- `non_commercial_prototype`: 4,440 rows
- `repo_test_data_review_required`: 7 rows
- `commercial_safe_generated`: 256 rows
- `academic_only`: 1 row

Geometry kinds from the validator:

- `graph_embedded_metric`: 4,440
- `procedural_metric`: 256
- `real_metric_structural`: 7
- `real_metric_polygon`: 1

## Metrics Found

### RSI Dataset

From `npm run validate:rsi`:

- layouts: 4,704
- tensors: 4,704
- connected: 4,045
- disconnected: 659
- graph usable: 4,035
- graph unusable: 669
- splits: 3,774 train / 474 val / 456 test
- oracle labels:
  - finish: 1,009
  - escalate: 2,947
  - refuse: 748
- hard negatives: 748
- balanced oracle training rows: 1,815 = 605 / 605 / 605

### Baseline Room-Type Classifier

From `npm run eval:v1`:

- saved model test balanced accuracy: `0.643617`
- floor balanced accuracy: `0.066667`
- target balanced accuracy: `0.25`
- saved-vs-reported delta: `0.0`

### Safety Policy v1

From `npm run eval:policy` and `safety_policy_v1/metrics.json`:

- feature view: `raw_geometry`
- feature count: 22
- 5-seed headline balanced accuracy mean: `0.931756`
- 5-seed balanced range: `0.917475 - 0.941108`
- 5-seed refuse recall mean: `0.985714`
- 5-seed refuse recall range: `0.964286 - 1.0`
- saved model test balanced accuracy: `0.925463`
- saved model test refuse recall: `0.964286`
- saved-vs-reported delta: `0.0`
- feature-disjoint regroup balanced accuracy: `0.900331`
- 36-feature oracle-recovery upper bound: `1.0`

### Raw Occupancy Policy

From `occupancy_policy_v1/metrics.json`:

- input: raw occupancy planes
- 5-seed test balanced accuracy mean: `0.985034`
- range: `0.981859 - 0.994331`
- refuse recall mean: `1.0`
- source-domain present-label holdout: `0.684547`

### Cross-Domain Refuse Mining

From `cross_domain_refuse_mining_metrics.json` and `validate:mined-refusals`:

- requested candidates: 1,200
- model: `gemma-4-31b`
- oracle-confirmed refuse kept: 1,116
- split: 672 train / 111 val / 333 test
- style rows:
  - Origin procedural generator: 391
  - MLStructFP structural grid style: 364
  - ZInD residential tour style: 361
- validator replay: pass; every mined row replays through Origin oracle as refuse

### Enriched Occupancy Policy

From `occupancy_policy_v1_enriched/metrics.json`:

- 5-seed balanced accuracy mean: `0.986043`
- 5-seed refuse recall mean: `0.98942`
- mixed source-domain balance: `0.46381`
- mixed source-domain refuse recall: `0.978979`

### Cross-Domain Calibration Mining

From `cross_domain_calibration_mining_metrics.json` and `validate:mined-calibration`:

- requested candidates: 1,200
- model: `gemma-4-31b`
- oracle-confirmed kept: 1,108
- split: 643 train / 108 val / 357 test
- labels:
  - finish: 376
  - escalate: 369
  - refuse: 363
- held-out ZInD test labels: 119 / 119 / 119
- curriculum/holdout overlap: 0
- validator replay: pass

### Calibrated Occupancy Policy

From `occupancy_policy_v1_calibrated/metrics.json`:

- 5-seed balanced accuracy mean: `0.911142`
- mined hard-case balance: `0.809524`
- unseen ZInD-style balance: `0.826331`
- mixed source-domain balance: `0.742083`
- mixed source-domain escalate recall: `0.643617`
- mixed source-domain refuse recall: `0.773109`

### Budget-Aware Occupancy Policy

From `occupancy_policy_v1_budget/metrics.json`:

- headline: `raw_occupancy_policy_5_seed`
- 5-seed balanced accuracy mean: `0.967728`
- 5-seed refuse recall mean: `0.933333`
- mined hard-case balance: `0.946779`
- mined escalate recall: `1.0`
- unseen ZInD-style balance: `0.938375`
- unseen ZInD-style escalate recall: `1.0`
- mixed source-domain balance: `0.82996`
- mixed source-domain escalate recall: `0.646277`
- mixed source-domain refuse recall: `0.89916`
- operating point threshold: `0.14`
- operating point refuse recall: `0.915966`
- false-accept rate: `0.084034`
- false-refuse rate: `0.079681`

Mixed escalate diagnostic:

- budget-lower-bound: support 55, escalate recall `1.0`
- structurally-unreachable: support 321, escalate recall `0.58567`

### Spatial Reachability Prototype

From `occupancy_policy_v1_spatial/metrics.json`:

- model: `dependency_free_budget_precomputed_reachability_grid_mlp`
- headline: `budget_precomputed_reachability_upper_bound_5_seed`
- 5-seed balanced accuracy mean: `0.953604`
- 5-seed refuse recall mean: `0.887432`
- mixed source-domain balance: `0.925756`
- mixed source-domain escalate recall: `0.992021`
- mixed source-domain refuse recall: `0.848739`
- operating point threshold: `0.04`
- operating point refuse recall: `0.92437`
- false-accept rate: `0.07563`
- false-refuse rate: `0.093625`

Mixed escalate diagnostic:

- budget-lower-bound: support 55, escalate recall `1.0`
- structurally-unreachable: support 321, escalate recall `0.990654`

Interpretation: precomputed `safe_reach_*` flood fill recovers structural unreachable escalation because the model is handed the oracle's own safe-reachability check. Treat this as an oracle-recovery upper bound, not learned spatial reasoning; raw refuse recall still trades down and must remain safety-critical.

### Propose / Verify

From `/tmp/origin_propose_verify_review.json` via `python3 services/foundry-train/propose_verify.py --mock --out /tmp/origin_propose_verify_review.json`:

- source: mock
- candidates generated: 24
- schema-valid: 24
- oracle accepted: 15
- unsafe caught: 9
- preference pairs emitted: 24
- oracle divergence: 0
- used Origin reward bridge: true

No live Cerebras/Gemma API call was made during this review.

## Commands Run

### Inspection

```bash
pwd && rg --files -g 'package.json' -g 'README*' -g 'docs/**' -g 'scripts/**' -g 'ml/**' -g 'services/**' -g 'outputs/rsi_dataset/**' | sed -n '1,240p'
pwd && rg --files -g 'package.json' -g 'README*' -g 'docs/**' -g 'src/**' -g 'public/rsi/**' -g 'tests/**' -g 'scripts/**' | sed -n '1,240p'
git status --short
node -e "const p=require('./package.json'); console.log(JSON.stringify(p.scripts,null,2))"
find outputs/rsi_dataset -maxdepth 2 -type f | sort | sed -n '1,240p'
python3 services/foundry-train/propose_verify.py --help | sed -n '1,180p'
python3 services/foundry-train/mine_cross_domain_refusals.py --help | sed -n '1,160p'
python3 services/foundry-train/mine_cross_domain_calibration.py --help | sed -n '1,180p'
```

### Floor Design Gates

```bash
npm run validate:rsi
node scripts/test_verifier.mjs
npm run validate:prefpairs
npm run validate:mined-refusals
npm run validate:mined-calibration
shasum -a 256 -c CHECKSUMS
npm run eval:v1
npm run eval:policy
python3 services/foundry-train/propose_verify.py --mock --out /tmp/origin_propose_verify_review.json
npm run render:dashboard
python3 -m py_compile services/foundry-train/build_pref_pairs.py services/foundry-train/propose_verify.py services/foundry-train/mine_cross_domain_refusals.py services/foundry-train/mine_cross_domain_calibration.py services/foundry-train/validate_mined_refusals.py services/foundry-train/validate_mined_calibration.py ml/safety_policy.py ml/train_safety_policy.py ml/eval_safety_policy.py ml/train_occupancy_policy.py ml/eval_trained.py ml/train.py
```

### Origin Web Gates

```bash
npm run gates:full
grep -rIoE '(sk-[A-Za-z0-9]{20,}|csk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xoxb-[A-Za-z0-9-]+|ghp_[A-Za-z0-9]{20,})' dist/
find dist -name '.env*' -print
rg -n "budget-aware mixed balance|reachability upper-bound mixed balance|FAR 7\\.6|not production robot certification" public/rsi/rsi_dashboard.html dist/rsi/rsi_dashboard.html
```

## Gate Results

### Floor Design

- `npm run validate:rsi`: pass; `ok: true`
- `node scripts/test_verifier.mjs`: pass; `verifier tests passed`
- `npm run validate:prefpairs`: pass; `oracle_divergence: 0`
- `npm run validate:mined-refusals`: pass; 1,116 rows replay as oracle-refuse
- `npm run validate:mined-calibration`: pass; 1,108 rows replay with stored labels
- `shasum -a 256 -c CHECKSUMS`: pass; 6/6 OK
- `npm run eval:v1`: pass; saved-vs-reported delta `0.0`
- `npm run eval:policy`: pass; saved-vs-reported delta `0.0`
- `python3 services/foundry-train/propose_verify.py --mock --out /tmp/origin_propose_verify_review.json`: pass; oracle divergence `0`
- `npm run render:dashboard`: pass; wrote `outputs/rsi_dashboard.html`
- Python compile sweep: pass

### Origin Web

- `npm run gates:full`: pass
  - build/typecheck: pass
  - lint: pass
  - evidence verifier: pass, 40/40 checks
  - unit tests: pass, 30 files / 237 tests
  - e2e tests: pass, 8/8
- secret-pattern grep over `dist/`: no matches
- `.env*` search in `dist/`: no files found
- RSI dashboard static copy: present in both `public/rsi` and `dist/rsi`
- dashboard text check: budget/spatial cards and claim boundary present

Build warning:

- Vite reports large chunks over 500 kB. This is a performance warning, not a failing gate.

## Claim-Boundary Issues

No active inspected dashboard copy claims production certification. The RSI dashboard includes:

> bounded robot-readiness Gym, not production robot certification

Boundary that must remain attached:

- Gemma/Cerebras proposes/mines; it does not judge final safety.
- Deterministic oracle is the source of labels and rewards.
- Learned policies are bounded Gym policies, not certified robot safety.
- 36-feature `1.0` safety-policy score is an oracle-recovery upper bound, not the headline.
- Mined/unseen-style holdouts are not natural-distribution generalization.
- Spatial prototype improves structural escalation but trades down raw refuse recall.

## Leakage Risks

1. **Oracle-summary features remain a known upper-bound path.** The 36-feature safety-policy score is `1.0` because it contains sufficient oracle-summary statistics. This is acceptable only when labeled as an upper bound.
2. **Mined-generator distribution shortcut risk.** Cross-domain hard cases are disjoint, oracle-confirmed, and useful, but still generated/mined distributions. A model can learn generator quirks unless evaluated on natural floor plans.
3. **Precomputed reachability is an oracle-recovery upper bound.** `safe_reach_*` planes are not labels/rewards, but they are fixed flood-fill outputs blocked by obstacles/hazards/human-only cells: the oracle's own safe-reachability check. This is useful as an upper bound, but must not be described as learned spatial reasoning or learned message passing.
4. **License/provenance is mostly non-commercial.** Validator reports 4,440 rows as non-commercial prototype and only 256 rows as commercial-safe generated. Commercial training needs customer-owned, procedural, or explicitly licensed data.
5. **Source-domain holdout is not a full natural holdout.** MLStructFP/ZInD coverage is tiny in the base dataset; mined rows improve hard-case coverage but are still synthetic/mined.

## Evaluation Gaps

P0 evaluation gap:

- Build a natural-distribution holdout from real floor plans with oracle-labeled tasks. Today, the strongest cross-domain numbers are mined/unseen-style, not real deployment distribution.

P1 evaluation gap:

- Add a spatial-policy comparison that is architecture-clean: flat MLP vs CNN/UNet-like grid encoder vs GNN/graph transformer vs differentiable value iteration, all on the same splits and same oracle labels.

P1 safety gap:

- Build a genuine learned-reachability model that computes reachability internally from raw obstacle planes, without precomputed `safe_reach_*`. The current precomputed reachability upper bound lifts mixed escalate to `0.992021` but raw mixed refuse recall is only `0.848739`.

P2 evaluation gap:

- Add topology-specific metrics:
  - room leakage count
  - connected-component drift
  - portal consistency
  - blocked-egress false accept rate
  - unsafe-zone false accept rate
  - false-refuse rate on easy finish paths

## Recommended Plan

### P0

1. Build a real natural-distribution evaluation slice.
   - Start with licensed/customer-owned/procedural-safe floor plans.
   - Label tasks only through the deterministic oracle.
   - Report natural floor-plan balance, refuse recall, FAR, FRR, and escalation calibration separately from mined metrics.
2. Add a claim-boundary gate.
   - Fail if dashboard/docs say "100% learned safety", "production robot certification", or imply Gemma is the judge.
3. Decide the safety operating point.
   - Refuse is safety-critical. Pick an operating threshold based on validation, then freeze and report held-out FAR/FRR.

### P1

1. Prototype true spatial architectures.
   - Small CNN over occupancy planes.
   - Value Iteration Network / differentiable BFS-style reachability layer.
   - GNN over room/portal graph.
   - Compare against current flat MLP and the precomputed flood-fill upper bound.
2. Improve structural escalation without losing refuse.
   - Use the current diagnostic split:
     - budget-lower-bound
     - structurally-unreachable
     - budget-detour
     - other oracle-escalate
   - Tune curricula and thresholds per failure type.
3. Expand real data ingestion.
   - More commercial-safe procedural variants.
   - Larger MLStructFP-like structural layouts.
   - Customer-owned/private floor plans if available.
   - Explicitly licensed public data only.

### P2

1. Full perception pipeline.
   - Raster/PDF/CAD ingestion.
   - Wall/door/window/room segmentation.
   - Portal graph extraction.
   - Topology repair.
   - Deterministic conversion to `DescriptiveSiteMap`.
2. Human-facing evidence reports.
   - For every finish/escalate/refuse decision, show route, hazard intersection, budget proof, and reason code.
3. Long-term model stack.
   - Hybrid raster CNN/Transformer for perception.
   - Graph model for room topology.
   - Oracle-guided planner for labels/rewards.
   - Learned policy as a fast approximation, never the sole safety authority.

## Copy-Paste Prompt Back To Claude For Critique

Claude, please critique Codex's Origin RSI/RL inspection handoff at:

`/Users/bohueilin/hackathons/Floor design/ORIGIN_RSI_REVIEW_HANDOFF.md`

Context:

- This was inspection/evaluation only.
- No code changes were made.
- No live Cerebras/Gemma mining was run.
- Propose/verify was run in forced mock mode to avoid external API calls.
- Existing gates were run across:
  - `/Users/bohueilin/hackathons/Floor design`
  - `/Users/bohueilin/hackathons/Origin/apps/origin-web`

Please independently verify:

1. The files inspected are the right source of truth.
2. The commands run were safe and sufficient.
3. The metric summary matches the artifacts.
4. The claim boundaries are strict enough.
5. The leakage risks are complete.
6. The P0/P1/P2 plan is correctly prioritized.

Pay special attention to:

- whether the precomputed reachability prototype is now correctly framed as an oracle-recovery upper bound rather than learned spatial reasoning,
- whether the natural-distribution holdout should be the top P0,
- whether the current refusal operating point is acceptable for a demo,
- whether any dashboard/site copy still overclaims,
- whether additional gates should be added for leakage and claim-boundary enforcement.

Return:

1. ACCEPT / ACCEPT WITH FIXES / REJECT.
2. Exact issues with file references.
3. Any missing gates.
4. Any metric drift.
5. A copy-paste prompt back to Codex.

When done, write your own markdown handoff note in the repo and include exact gate outputs.
