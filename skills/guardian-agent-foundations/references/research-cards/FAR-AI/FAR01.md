# FAR01 Can Go AIs Be Adversarially Robust?

## Citation
- Authors: Tom Tseng, Euan McLean, Kellin Pelrine, Tony T. Wang, Adam Gleave
- Year: 2025 (this v3 dated 14 Jan 2025; original v1 June 2024)
- Venue: Not stated in the paper. The document is an arXiv preprint (arXiv:2406.12843v3 [cs.LG]); affiliations are FAR.AI, Mila, and MIT. No conference/journal venue is printed on the PDF. (REVIEWER SYNTHESIS: this is a full empirical research paper, not a blog post or informal lab report; treat "venue = not stated" as literal, do not assume peer-review status from this card.)
- Local source: /Users/bohueilin/hackathons/Athena/corpus/far-ai/2406.12843v3.pdf
- External identifier: arXiv:2406.12843v3; project/code site https://goattack.far.ai (as printed in the paper)
- Category: FAR-AI (frontier-lab AI-safety corpus)

## Research question
Can superhuman Go AIs be made adversarially robust by adding "natural" countermeasures? Concretely: given that superhuman Go AIs are defeated by simple "cyclic" adversarial attacks, can defenses make such agents (a) "human robust" — not commit game-losing blunders that a human would not — and (b) not cheaply exploitable by an adversary trained with a small amount of compute? Go is chosen as a favorable, tractable testbed because average-case play is massively superhuman, the attack surface (legal moves) is narrow, and the domain is inherently adversarial.

## Problem definition
Prior work (Wang et al. 2023a) showed that superhuman Go AIs such as KataGo can be reliably defeated by adversarial "cyclic" attacks despite superhuman average-case play. This paper studies whether three natural defenses can convert strong average-case performance into robust worst-case performance (minimal exploitability by adversaries). The paper frames robustness via three complementary notions: human robustness (no game-losing blunders a human would avoid), training-compute robustness (an adversary that beats the victim should require large training compute), and inference-compute robustness (the victim should be able to overcome vulnerabilities by spending additional inference-time search).

## System or model being studied
- KataGo (Wu 2020b), the strongest open-source Go AI: self-play-trained neural network combined with Monte Carlo tree search (MCTS); search budget quantified as "victim visits."
- Multiple KataGo victim checkpoints: base-victim (Wang et al.'s "Latest"), dec23-victim, may24-victim (from KataGo's own adversarially-trained main run), and v9 (final victim of the authors' iterated adversarial training).
- A Vision Transformer (ViT) backbone variant, ViT-victim — described in the paper as the first professional-level ViT-based Go AI (trained ~563 V100 GPU-days; won 2 of 3 games vs Go professionals; superhuman when playing at 32,768 visits).
- Adversary agents trained to exploit victims: base-adversary (Wang et al.'s original cyclic adversary), gift-adversary, continuous-adversary, big-adversary, may23-adversary, atari-adversary, stall-adversary, ViT-adversary.

## Threat model (objective/knowledge/access/capabilities/budget; white-gray-black-box; train/inference/deployment; targeted/untargeted; digital/physical; adaptive/non-adaptive)
- Setting: two-player zero-sum Markov game (following Wang et al. 2023a). A threat actor trains an adversary agent to defeat a victim agent.
- Knowledge/access: gray-box. The adversary can run inference on the victim's policy network on arbitrary inputs, but does NOT have direct access to the victim's weights and cannot take gradients through the victim.
- Capability/budget: the adversary trains via victim-play using Adversarial MCTS (A-MCTS, a modified MCTS that queries the victim's network at opponent nodes; typically 600 A-MCTS visits/move). Adversaries are trained with only a small fraction of the victim's compute (paper reports figures such as 6%, 8%, and <5% in specific cases). Compute measured in V100 GPU-days.
- Box type: gray-box.
- Phase: defenses operate at training time; the exploit is applied at inference/deployment time (a trained adversary plays and beats the victim during games across a range of victim search visits, 1 up to ~10^5).
- Targeted/untargeted: targeted in the sense of training a specialized adversary to exploit a specific victim and induce a game loss.
- Digital vs physical: digital (board game Go).
- Adaptive vs non-adaptive: adaptive — adversaries are adaptively fine-tuned against each defended victim (adaptive attack against each defense).

## Trust assumptions
- Adversary is limited to gray-box query access to the victim's policy network; no weight access, no gradient access.
- Victim defends via MCTS search with a variable visit budget; higher visits are assumed to (partially) improve robustness (inference-compute robustness hypothesis).
- To count as a meaningful ("human-relevant") vulnerability, attacks must be replicable by a human expert (the paper reports human experts replicating the attacks by hand; Appendix J), and victims are evaluated against human professionals on the KGS server.

## Attack or failure mechanism
- Primary: cyclic attacks — the adversary builds large cyclic groups of stones that the victim's network misjudges (fails to recognize as vulnerable/capturable), leading to catastrophic misevaluation and loss. The specific cyclic shapes are described as qualitatively distinct across adversaries (varying size/location of the cyclic group) yet easy for a human to navigate correctly.
- New non-cyclic "gift attack": a "sending-two-returning-one" situation in which the victim needlessly gifts the adversary two stones and then fails to recapture because positional superko rules block the recapture, resurrecting one of the victim's dead groups into a disaster. Described as strange because the victim was trained with superko rules and has a neural-net input feature marking superko-illegal moves.
- Failure root cause is attributed to the self-play training process failing to represent a feature (cyclic shapes / group liveness) that amateur humans learn easily; the paper argues CNN inductive biases are NOT the cause (ViT is also vulnerable).

## Proposed defense or method
Three natural defenses are tested (the paper's contribution is evaluating whether they work, and they do not):
1. Positional adversarial training — augment KataGo's training data with hand-constructed board positions exhibiting the cyclic attack (as KataGo's official run did).
2. Iterated adversarial training — an "arms race": alternately train an adversary to find new attacks and train the victim to defend against the latest adversary, repeated for 9 iterations (v0 = base-victim, a0 = base-adversary; each victim v_n fine-tuned from v_{n-1} with ~18% of games vs a frozen a_{n-1} and the rest self-play).
3. Vision Transformer backbone — replace KataGo's CNN backbone with a ViT to test whether the cyclic vulnerability stems from CNN inductive biases.

## Datasets and benchmarks
- No standard external benchmark dataset. The paper uses KataGo self-play training data (augmented with adversarial/cyclic positions for positional adversarial training) and evaluates via head-to-head game win rates between adversaries and victims across many victim search-visit budgets.
- Uses publicly available KataGo networks/checkpoints (open-source). Human evaluation via games on the KGS Go Server against professional players. Interactive game histories and code are published at https://goattack.far.ai.

## Evaluation methodology
- Train adversaries by victim-play with A-MCTS (typically 600 A-MCTS visits/move), initializing from cyclic adversary checkpoints or from base-adv-early (to find diverse, non-cyclic attacks).
- Measure adversary win rate versus each victim as a function of victim search visits (1 up to ~10^5) and as a function of training compute (V100 GPU-days).
- Report 95% Clopper-Pearson confidence intervals on win rates.
- Verify human relevance by having a human expert replicate the attacks by hand (Appendix J) and by playing ViT-victim against Go professionals.

## Metrics
- Adversary win rate (%) against a victim, reported vs. victim search visits and vs. training compute (GPU-days).
- Training/defense compute in V100 GPU-days (with the ratio of attack vs. defense compute used as a robustness measure).

## Main findings
- All three defenses are found ineffective under the evaluated gray-box threat model: given query access, it is relatively cheap to train new adversaries that reliably defeat the defended systems. No defended system was robust to freshly trained adaptive adversaries.
- Positional adversarial training: dec23-victim never loses to Wang et al.'s original fixed cyclic attack (0%), but adaptively fine-tuning that adversary brings its win rate from 0% back up to 92%, using just 8% of the compute used for the defense, via only a slight variant of the original strategy. Separately, gift-adversary defeats dec23-victim in 91% of games at 512 victim visits using the new non-cyclic gift exploit, after training with just ~6% as much compute as the victim (this gift attack does not scale to high victim visits).
- Against KataGo's own later checkpoints: may23-adversary achieves a 47% win rate vs may23-victim at 4096 visits; continuous-adversary wins 65% vs dec23-victim at 4096 visits; big-adversary wins 56% vs may24-victim even at 65,536 victim visits (cyclic attacks still work at high visits, though with a narrower range than against non-adversarially-trained victims).
- Iterated adversarial training: the final victim v9 is still vulnerable. A newly trained atari-adversary wins 81% vs v9 at 512 visits despite <5% of v9's compute, and wins 13% even without any A-MCTS search; it wins >60% vs v9 at 256 visits after ~500 V100 GPU-days. a9 wins 42% vs v9 even at 65,536 visits. Iterated training offers partial protection (harder to attack at high visits): atari-adversary plateaus after 1401 GPU-days with only a 4% win rate at 4096 visits.
- ViT defense: cyclic vulnerability is not caused by the CNN backbone. ViT-victim at 65,536 visits still loses 78% of games to a fine-tuned base-adversary variant (ViT-adversary), and ViT-victim at 512 visits even loses 2.5% of games to the original (unmodified) base-adversary via zero-shot transfer.
- Cross-cutting: the reliably effective attacks are different realizations of the same broad class of cyclic attacks; the paper reports an offense-defense balance favoring attackers, and that the underlying attack algorithm is always able to find a successful attack, often with a small fraction of the victim's training compute.

## Negative results
The paper is fundamentally a negative-result study within its threat model. None of the three defenses achieve human-level robustness; the attack algorithm always finds a successful attack. Specific negative outcomes: positional adversarial training reverts to 92% adversary win under adaptive fine-tuning; iterated adversarial training's victim v9 remains exploitable (81% at 512 visits); ViT-victim remains vulnerable (78% at high visits) and even loses to zero-shot transfer of the original attack. Some individual attacks fail at high victim visits (e.g., the gift attack does not scale; atari-adversary plateaus at 4% at 4096 visits; stall-adversary's attack fails at high victim visits), but these limits are on specific attacks, not evidence of victim robustness.

## Limitations stated by the authors
- Defenses make attacks harder (increase attacker compute) but none make attacks impossible; the attack algorithm from Wang et al. is always able to find a successful attack, often with a small fraction of the victims' training compute.
- None of the defenses reach human-level robustness, and humans can even execute the successful attacks against the defended systems.
- Results indicate an offense-defense balance favoring attackers.
- Iterated adversarial training was bottlenecked by the attack (search) component, which took 18x more compute than the defense component (Table 5), limiting how many attacks the victim could be trained against.
- may24-victim and v9 remain vulnerable to cyclic attacks even after training against many variants of cyclic attacks.
- The authors do not rule out that a much deeper ViT or some other architecture could solve the cyclic vulnerability.
- Defending against fixed (non-adaptive) attacks may be feasible; the strong negative result is specifically about adaptive attackers.
- Authors caution that even in this favorable, well-defined, self-contained domain robustness is hard, and expect open-ended real-world domains to be even harder — implying results should be read as a lower bound on difficulty rather than as measurements transferable to other domains.

## Additional limitations identified during review (label REVIEWER SYNTHESIS)
- REVIEWER SYNTHESIS: The threat model assumes gray-box query access to the victim's policy network. The findings do not establish what happens under strictly black-box (no policy-network inference) or fully white-box (weight/gradient) access; robustness claims should not be generalized beyond gray-box query access.
- REVIEWER SYNTHESIS: All numbers are single-domain (Go) and specific to KataGo-style AlphaZero training. Extrapolation to LLM/agent safeguards, RL agents in other games, or physical-world control is argued qualitatively by the authors but is not empirically demonstrated here.
- REVIEWER SYNTHESIS: "Ineffective defense" is a property of these three specific defenses at the compute scales tested; it is not a proof that no training-time defense can work. The authors themselves suggest scaling the attack corpus or sample-efficiency of adversarial training as untested routes.
- REVIEWER SYNTHESIS: Win-rate metrics depend heavily on the victim's search-visit budget; comparisons across adversaries/victims are only meaningful at matched visit counts, and some headline numbers hold only at specific (often low) visit budgets.

## Reproducibility (code/data/model; config completeness; reproduction difficulty)
- Code and interactive attack examples published at https://goattack.far.ai; built on open-source KataGo. Attacks are reported as replicable by a human expert (Appendix J), which lowers the barrier to qualitative verification.
- Compute is documented in V100 GPU-days (per-attack/defense figures in Appendix A; iterated-training compute in Table 5). Training configs and checkpoints described across appendices.
- Reproduction difficulty: HIGH. Full reproduction requires very large compute (e.g., ViT-victim ~563 V100 GPU-days; atari-adversary training into the low thousands of GPU-days; iterated training over 9 rounds). Qualitative reproduction of the attacks by a human is feasible; quantitative re-training is expensive.

## Design implications
- For the Origin/Guardian safety stack: strong average-case (even superhuman) capability does not imply worst-case robustness. Do not equate "the model almost never errs on typical inputs" with "the model is safe against an adversary who can query it." Design assuming an adaptive attacker with query access can find catastrophic-blunder inputs.
- Architecture changes alone (here, CNN -> ViT) do not remove a capability-level blind spot; the failure lived in the learned representation / self-play training process, not the backbone. Guardrail design should not rely on model-architecture swaps as a robustness fix.
- Inference-time search/deliberation only partially mitigates: more victim search raised the attacker's cost but never closed the gap. Treat "spend more compute at inference" as risk reduction, not elimination.

## Implementation implications
- Assume adaptive adversaries with gray-box query access. Any defense validated only against a fixed/known attack (like the original cyclic attack, which dec23-victim beat 100%) can revert to near-total failure (92%) once the attacker is allowed to adapt, at a small fraction of the defense's compute.
- Budget for an offense-defense imbalance: in this study attackers succeeded with 5-8% of the victim's compute, and iterated defense cost 18x the attack. Defenses that must out-spend attackers by large multiples are operationally fragile.

## Evaluation implications
- Robustness evaluation must include re-training an adaptive attacker against the defended system, not merely re-running prior fixed attacks. Reporting "0% against the known attack" is misleading without an adaptive re-attack.
- Report results across the defender's full deliberation/compute budget (here, victim visits from 1 to ~10^5); a defense that holds at high search may collapse at low search and vice versa.
- Use human-replicability and human/expert baselines as a sanity check on whether a vulnerability is "real" (a blunder a human would not make) versus an artifact.

## Deployment implications
- Deploying a system with superhuman average-case performance into an adversarial, safety-relevant setting is not justified by average-case metrics alone; a motivated adversary with query access may reliably trigger catastrophic failures.
- Where full robustness is unattainable, prefer restricting attacker access (reduce/monitor query access to the policy) and layering defenses, rather than relying on a single trained-in defense.

## Monitoring and incident implications
- Because adaptive adversaries reuse a broad attack class (cyclic shapes) with variations, monitoring should target the attack class/pattern rather than a specific instance, and should assume new realizations will appear after each patch.
- Maintain reproducible attack traces (as the paper does via published game histories) to support incident triage and regression testing after each defense update.

## Applicability boundaries (where findings should / should NOT be generalized)
- This is a full empirical research paper (not a discussion post or informal report), but it is single-domain (Go / KataGo) and single-threat-model (gray-box, adaptive, inference-time exploitation of a self-play-trained agent).
- Findings SHOULD generalize as a cautionary prior: superhuman average-case capability + simple natural defenses did not yield robustness even in a favorable, narrow, well-defined domain, so expect at least as much difficulty in open-ended domains (LLM agents, robotics, safeguards).
- Findings should NOT be read as quantitative predictions for other systems, nor as a claim that robustness is impossible — the authors explicitly leave open larger attack corpora, more sample-efficient adversarial training, latent/relaxed adversarial training, population-based methods (PSRO/DeepNash), and stateful/online defenses as untested routes. Do not port specific win-rate numbers to non-Go systems.

## Related papers in this corpus (cross-link to AAAI A##### ids where the topic overlaps)
- Directly builds on Wang et al. 2023a, "Adversarial Policies Beat Superhuman Go AIs" (the origin of the cyclic attack and the two-player gray-box threat model), and Gleave et al. 2020, "Adversarial Policies: Attacking Deep Reinforcement Learning." If either is present in the AAAI corpus, cross-link its A##### id here (no matching id was available at card-writing time; leave for later reconciliation).
- Topically adjacent to adversarial-robustness / adversarial-training and adaptive-attack-evaluation work in the broader corpus. NOTE: this paper is NOT the same work as "STACK: Adversarial Attacks on LLM Safeguard Pipelines" (A41108) — that is a distinct LLM-safeguard paper; no same-work AAAI duplicate was identified for FAR01.

## Evidence strength (strong/moderate/preliminary/contested/insufficient)
Strong (for its scoped claim). The central claim — that three natural defenses fail to make superhuman Go AIs robust against adaptively trained gray-box adversaries — is supported by multiple independent defenses, multiple victim checkpoints, a wide range of search budgets, confidence intervals, human replication, and released code/traces. Evidence strength is strong within the evaluated Go / gray-box / adaptive threat model; it is not a general impossibility result and does not transfer quantitatively to other domains.

## Confidence notes
- High confidence in all reported numbers, checkpoint names, and the three-defense structure (read directly from the paper body and figures).
- Venue is genuinely not printed on the PDF; recorded as "not stated." Do not infer peer-review status from this card.
- Cross-references to AAAI A##### ids are left unresolved because the AAAI corpus index was not available to this review; the STACK/A41108 non-match is asserted on topic grounds (distinct subject matter), and the Wang et al. 2023a / Gleave et al. 2020 links are prior-work relations, not same-work duplicates.
