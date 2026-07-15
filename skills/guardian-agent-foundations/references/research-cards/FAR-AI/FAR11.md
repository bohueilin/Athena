# FAR11 Adversarial Policies Beat Superhuman Go AIs

## Citation
- Authors: Tony T. Wang, Adam Gleave, Tom Tseng, Kellin Pelrine, Nora Belrose, Joseph Miller, Michael D. Dennis, Yawen Duan, Viktor Pogrebniak, Sergey Levine, Stuart Russell (Tony T. Wang and Adam Gleave listed as equal contribution; affiliations MIT, UC Berkeley, FAR AI, McGill University / Mila; correspondence twang6@mit.edu, adam@far.ai)
- Year: 2023
- Venue: Proceedings of the 40th International Conference on Machine Learning (ICML 2023), PMLR 202, Honolulu, Hawaii, USA
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/2900_Adversarial_Policies_Beat.pdf
- External identifier: PMLR 202 (ICML 2023); no DOI/arXiv id printed in the local file; example games hosted at goattack.far.ai; open-source implementation referenced on GitHub (URL not printed in the read pages)
- Category: FAR-AI (frontier-lab AI-safety corpus)
- Type: Peer-reviewed empirical research paper (not a lab report or informal discussion piece).

## Research question
Do improvements in average-case capability of deep RL agents translate into worst-case robustness? Specifically, can a superhuman, self-play-trained Go agent (KataGo) be reliably defeated by a dedicated adversarial policy that does not itself play strong Go?

## Problem definition
The authors study whether "capabilities are enough" for robustness. They train adversarial policies that seek to win against a fixed superhuman victim agent, not by playing better Go but by inducing the victim into catastrophic blunders. The central concern is that even superhuman deep RL systems can harbor surprising, hard-to-find, and hard-to-patch failure modes.

## System or model being studied
- Victim: KataGo (Wu, 2019), described as the strongest publicly available Go AI system at the time. The main victim network is referred to as `Latest` = `b40c256-s11840935168`. Later experiments also use 60-block networks such as `b60-s7702m` (released May 17, 2023) that were trained on adversarial positions.
- KataGo uses an AlphaZero-style self-play training pipeline with a policy head and a value head, plus Monte-Carlo Tree Search (MCTS) at inference, and additional auxiliary heads and hand-engineered features (e.g., ladder/pass-alive masks).
- The authors' own systems are the trained adversarial policies (a "pass-adversary" and a "cyclic-adversary").

## Threat model (objective/knowledge/access/capabilities/budget; white-gray-black-box; train/inference/deployment; targeted/untargeted; digital/physical; adaptive/non-adaptive)
- Objective: win a standard two-player zero-sum Markov game (Go) against a fixed victim agent; targeted in the sense of defeating a specific victim.
- Knowledge/access: primarily gray-box. The attacker can evaluate (query) the victim's neural network on arbitrary inputs but has no direct access to network weights. The victim is assumed to follow a fixed policy with static weights (a pre-trained model deployed with fixed parameters).
- Attacker capabilities: the adversary has "no unusual powers" in the game itself — it can only place stones or pass, like a regular player. Its advantage comes from gray-box query access plus AlphaZero-style training against the victim.
- Budget: pass-adversary trained for 20.4 V100 GPU days (stated as 0.13% of `Latest`'s training budget); cyclic-adversary trained for 2223.2 V100 GPU days (stated as roughly 14.0% of the compute used to train `Latest`). Attack claims win >99% with no victim search and >97% with enough victim search to be superhuman.
- Box setting: gray-box for the main attack; the transfer experiments deliberately weaken this assumption to an "extreme case of a black-box attack" (zero-shot transfer to unseen victims).
- Phase: exploits a fixed/deployed victim at game-play (inference) time; the attack itself requires training an adversary offline via victim-play.
- Digital/physical: digital (board-game simulation).
- Adaptive/non-adaptive: adaptive — the adversary is trained specifically against the victim (and against defended checkpoints), and the paper shows the attack can be re-fitted via fine-tuning to defeat adversarially defended victims.

## Trust assumptions
- The victim network is a fixed target with static weights (the common case of a deployed pre-trained model).
- The attacker can obtain a copy of, or query, the victim's network (gray-box), which the authors argue naturally arises for commercially available or open-source Go systems.
- The authors deliberately do NOT assume white-box weight access, and the training procedure uses random initialization of the adversary rather than initializing from victim weights (consistent with the no-white-box assumption).

## Attack or failure mechanism
Two distinct adversarial policies are demonstrated:
- Pass-adversary: tricks the victim's policy head into passing prematurely so that the game ends under the Tromp-Taylor ruleset (the ruleset KataGo was trained/configured to use) at a point where the adversary has more points. It wins by exploiting the victim's misjudgment about scoring/passing, not by strong play.
- Cyclic-adversary: coaxes the victim into forming a large circular ("cyclic") group of stones and then captures that group, causing a decisive, unrecoverable score swing. The victim's value network typically predicts >99% win confidence for most of the game and only suddenly realizes it will lose, often about one move before its cyclic group is captured.
Mechanistically, the authors find that a few channels at layer 26 of the victim network show clear activation divergence between cyclic and minimally-perturbed non-cyclic positions, and that adversarial training preferentially changes those same channels — linking the failure to specific network channels.

## Proposed defense or method
The paper is primarily an attack/red-teaming study, but it also studies defenses:
- Attack method: "victim-play" — train the adversary only on the turns where it is to move, against a fixed victim, so it learns to exploit rather than imitate the victim. This is combined with Adversarial MCTS (A-MCTS), with three variants: A-MCTS-S (sample; models the victim as playing directly from its policy head with no search), A-MCTS-S++ (averages the victim policy over board symmetries), and A-MCTS-R (recursive; models the victim's search exactly at high compute cost). A curriculum trains the adversary against successively stronger victim checkpoints and increasing victim search.
- Pass-alive defense (authors' hard-coded defense against the pass-adversary): only allow the victim to pass when all its legal moves are inside its own pass-alive territory. This completely thwarts the pass-adversary; the defended victim `Latest_def` no longer loses via accidental passing.
- Search as a partial defense: giving the victim more MCTS search reduces the adversary's win rate and improves the victim's positional judgment, but does not yield fully robust agents.
- Adversarial training (KataGo team's mid-December 2022 defense, and the authors' analysis of it): training on a small fraction (0.08%) of self-play games starting from cyclic positions. The authors also note counterfactual regret minimization (CFR), population-based training, and policy-space response oracles as candidate more-robust techniques (discussion, not evaluated here).

## Datasets and benchmarks
- No conventional labeled dataset; evidence is generated by playing large numbers of Go games between adversaries and victim networks.
- Victims/benchmarks are specific KataGo networks (`Latest` = `b40c256-s11840935168`; `b60-s7702m` and related 60-block nets; earlier checkpoints such as `cp39`, `cp127`, `cp580`) and, for transfer, Leela Zero and ELF OpenGo.
- Human-play evaluation was conducted on the KGS online Go server.

## Evaluation methodology
- Adversarial evaluation via head-to-head game play, measuring win rates over large game counts (e.g., 1000–1052 games per condition; ~50 games for the very high victim-visit conditions), with 95% Clopper-Pearson confidence intervals reported for per-checkpoint win rates.
- Ablations across victim search budget (no search up to 10^7 visits/move), adversary search budget (adversary visits), and A-MCTS variant (S / S++ / R).
- Defense evaluation: re-running the attack against defended victims (`Latest_def`, adversarially trained b60 nets) and measuring whether/when the attack recovers via additional fine-tuning.
- Transfer evaluation: zero-shot transfer of the cyclic-adversary to Leela Zero and ELF OpenGo; and human replication, where a Go-expert author learned the attack from game records and played it manually.
- Mechanistic analysis: comparison of layer activations between cyclic and non-cyclic positions, and between `Latest` and adversarially trained checkpoints.

## Metrics
Primary metrics stated: (1) win rate of the adversarial policy against the victim, and (2) the adversary's training and inference time (compute). The mean score difference between adversary and victim is also tracked but not explicitly optimized for.

## Main findings
Reported results (direct from paper):
- Pass-adversary achieves a 99.9% win rate against no-search `Latest`, using only 20.4 V100 GPU days (0.13% of `Latest`'s training budget), by tricking the victim into passing prematurely.
- Cyclic-adversary achieves 100.0% win rate over 1048 games against `Latest_def` with no search; 95.7% over ~1052 games against `Latest_def` with 4096 visits; and 97.3% over 1000 games against undefended `Latest` with 4096 visits.
- Against a victim with substantial search: 82% win rate over 50 games against `Latest` with 10^6 visits/move, and 72% win rate over 50 games against `Latest` with 10^7 visits/move (verified not to be winning via the pass-trick). The authors note 10^7 visits is already prohibitive (over one hour per move on high-end consumer hardware).
- The adversarial policies do not win by playing strong Go: they lose against human amateurs (a non-transitivity, Figure 2.1), showing the adversary is exploiting the victim rather than being generally capable.
- Transfer: zero-shot cyclic-adversary wins 6.1% of games against Leela Zero and 3.5% against ELF OpenGo (challenging setting since A-MCTS models the victim as KataGo).
- Human transfer: a Go-expert author learned the attack without algorithmic assistance and, in standard human conditions on KGS, obtained a >90% win rate against a top-ranked unaffiliated KataGo bot even while giving it 9 handicap stones; also beat KataGo and Leela Zero playing with 100k visits each.
- The core cyclic vulnerability persists even in KataGo agents adversarially trained to defend against the attack, which the authors say suggests the vulnerability is non-trivial to patch. A small amount of adversarial training robustly defends against a fixed adversary but does not generalize, and the fixed adversary can be re-broken by fine-tuning (e.g., after 1154.9 additional V100 GPU days of fine-tuning, the cyclic-adversary recovers a 47% win rate over 400 games against `b60-s7702m` with 4096 visits and 17.5% over 40 games against the same net with 100,000 visits).

## Negative results
- The pass-adversary is fully defeated by the simple pass-alive defense (win rate driven to zero against `Latest_def`), showing that specific exploits can be cheaply patched even though the underlying class of vulnerability is not.
- Zero-shot transfer win rates to Leela Zero (6.1%) and ELF OpenGo (3.5%) are low, indicating the automated attack does not transfer strongly across differing victims without adaptation (though humans replicating the attack transferred it far more effectively).
- Agents that use more search are harder to exploit: the adversary's win rate decreases as victim search increases, and the attack requires more compute against searched victims.
- A-MCTS-R (which correctly models the victim) provided no measurable improvement over A-MCTS-S up to 128 victim visits with the final cyclic-adversary, and is largely impractical at higher visit counts due to compute cost.

## Limitations stated by the authors
- Go-playing AI systems may be unusually vulnerable; the authors note that evaluating the attack against strong AI systems in other games and settings is future work.
- It is harder to exploit agents that use search — attacks achieve lower win rates and require more compute against high-search victims.
- Search is a valid tool for improving robustness but will not, on its own, produce fully robust agents.
- KataGo's mild adversarial-training defense is inadequate as deployed (does not generalize and can be re-broken by fine-tuning), though the authors state it is plausible that with much more adversarial training KataGo could become computationally infeasible to exploit; computing scaling laws for this is called out as future work (a conjecture, not a demonstrated result).
- The authors are careful to frame their result as demonstrating non-transitivity/exploitation, explicitly not claiming to have built a stronger Go agent.

## Additional limitations identified during review (label REVIEWER SYNTHESIS)
- REVIEWER SYNTHESIS: Findings are within a single game domain (Go) and a single family of AlphaZero-style victims. Generalization to other agent types — e.g., LLM agents, tool-using agents, or physical/robotic control — is asserted as motivation but is not empirically evaluated here; the deployment claims about financial trading or autonomous vehicles are analogical, not tested.
- REVIEWER SYNTHESIS: The gray-box assumption (arbitrary query access to the victim network) is stronger than many real black-box deployment settings; the strongest automated results rely on it, while the more deployment-realistic black-box transfer numbers are low.
- REVIEWER SYNTHESIS: Several high-victim-search win-rate figures (82%, 72%, 47%, 17.5%) are computed over small samples (40–50 games), so the point estimates carry wide confidence intervals; the paper appropriately reports Clopper-Pearson intervals for larger-sample conditions.
- REVIEWER SYNTHESIS: "Defense does not generalize / can be broken again" is a robust demonstration for the specific defended checkpoints tested; it is a lower bound on defense difficulty rather than proof that no adversarial-training regime can succeed (the authors themselves flag this as open).

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Open-source implementation is referenced (GitHub) and example games are hosted at goattack.far.ai; specific victim network identifiers are given (`b40c256-s11840935168`, `b60-s7702m`, checkpoints `cp39`/`cp127`/`cp580`), aiding reproducibility.
- Compute is reported concretely in V100 GPU days for both attack and defense/fine-tuning, and win rates are reported with game counts and confidence intervals.
- Reproduction difficulty: high in practice — replicating the strongest results requires substantial GPU compute (hundreds to thousands of V100 GPU days for training adversaries, and up to 10^7 victim visits/move at evaluation), even though the conceptual attack (especially the human-replicable cyclic exploit) is comparatively cheap to demonstrate.
- Full algorithmic details (A-MCTS variants, curriculum, defenses) are deferred to appendices not fully contained in the pages reviewed here.

## Design implications
- Average-case superhuman capability does not imply worst-case robustness: systems should be designed on the assumption that dedicated adversaries can find catastrophic blind spots even in highly capable models.
- Self-play / adversarial-by-construction training does not guarantee robustness; do not treat competitive training as a robustness guarantee.
- Where feasible, design agents to use inference-time search / deliberation, which measurably (though not completely) reduces exploitability.

## Implementation implications
- For deployed decision agents, restricting query access to the underlying model (limiting the gray-box surface) raises the attacker's cost, since the strongest automated exploits depend on arbitrary network queries.
- Hard-coded, domain-specific safeguards (like the pass-alive rule) can cheaply neutralize a specific known exploit, but implementers should expect the underlying vulnerability class to resurface via other exploits.
- Adversarial-training defenses must be treated as ongoing (fine-tuning re-breaks them); a one-time hardening pass is insufficient.

## Evaluation implications
- Robustness evaluation should include adaptive adversaries trained specifically against the target and its defenses, not just static or transferred attacks; adaptive re-attack revealed that a defense which looked effective could be re-broken.
- Win-rate / success metrics should be reported over large game counts with confidence intervals, and stratified by both victim and adversary compute budgets, because exploitability depends strongly on search depth.
- Transfer/black-box evaluation should be reported separately from gray-box, since they yield very different exploitability estimates.

## Deployment implications
- Deploying a superhuman agent with a queryable network exposes an exploitation surface; operators should assume adversaries can obtain a copy or query the model and train exploits against it.
- Increasing inference-time search can be used as a partial runtime robustness lever, at the cost of latency/compute (10^7 visits is over an hour per move), so it is not a free defense.
- The authors caution (analogically, not tested) that similar failure modes in safety-critical autonomous systems could have severe consequences — motivating conservative deployment of capable-but-not-verified agents.

## Monitoring and incident implications
- The victim's own confidence is not a reliable failure signal: the value head reported >99% win probability until roughly one move before catastrophe, so monitoring a model's self-assessed confidence would not have caught the exploit.
- Divergence in specific internal activations (e.g., layer-26 channels) distinguished cyclic from benign positions — suggesting internal-state/activation monitoring may be a more promising incident-detection signal than output confidence, though this is an analysis result, not a deployed detector.
- Incident response should assume a patched exploit may be re-derived; monitoring should watch for recurrence of the same vulnerability class (cyclic-group formation here) rather than only the exact patched instance.

## Applicability boundaries (where findings should / should NOT be generalized)
- This is a rigorous empirical research paper, not a discussion/opinion piece; its concrete claims are well supported within the evaluated domain.
- Findings SHOULD generalize as a strong existence proof that superhuman, self-play-trained deep RL agents can harbor cheap-to-exploit, hard-to-patch blind spots, and that capability gains do not guarantee robustness.
- Findings should NOT be over-generalized to precise exploitability numbers for other agent classes (LLMs, tool-using agents, robotics) — those transfers are motivational and untested. The specific exploits (pass-trick, cyclic-group capture) are Go-and-ruleset-specific; the transferable lesson is the methodology (adversarial policies + adaptive re-attack) and the robustness gap, not the specific tactics.

## Related papers in this corpus (cross-link to AAAI A##### ids where the topic overlaps)
- This work is a distinct ICML 2023 paper and is NOT a duplicate of an AAAI corpus paper; no AAAI A##### id is confirmed as the same work. (The STACK / "Adversarial Attacks on LLM Safeguard Pipelines" paper referenced in the task as A41108 is a different, unrelated work.)
- Topically related themes for cross-linking if present elsewhere in the corpus: adversarial robustness of deep RL / self-play agents, exploitation of deployed models via gray-box query access, adaptive attacks that defeat adversarial-training defenses, and the general "capabilities do not imply robustness" thesis. No verified A##### identifiers are asserted here to avoid fabrication; cross-links should be added only after confirming matching ids in the AAAI corpus index.

## Evidence strength (strong/moderate/preliminary/contested/insufficient)
Strong. The central claims are supported by large-sample head-to-head evaluations with confidence intervals, multiple victim networks, adaptive re-attack against defenses, independent human replication of the exploit, and mechanistic activation analysis. The main caveats are domain-specificity (Go) and the gray-box assumption, both of which the authors state.

## Confidence notes
- High confidence in the reported win rates, compute figures, and qualitative mechanism, all taken directly from the paper's main text and figures.
- Moderate confidence on exact numbers gated behind small-sample high-search conditions (40–50 games) and on appendix-only algorithmic details not fully read here.
- The claim that "the vulnerability is non-trivial to patch" is the authors' calibrated conclusion under the evaluated defenses; it is demonstrated for the tested adversarially trained checkpoints and is explicitly not a proof that no defense can succeed. Production/safety-critical extrapolations are the authors' analogy and require independent validation.
