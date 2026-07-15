# Engineering depth: a layered architecture, prepared and explainable

The demo proves it *works*. The architecture proves it's *real, hard, and defensible*. Technical judges
at AGI House / YC are partly there for the depth — and a smooth demo with nothing underneath reads as a
skin, not a system. This is where a strong team pulls ahead, and where "Passport" left points on the
table: there was no prepared, layered architecture artifact to interrogate.

## Why this wins (and its absence loses)

- Judges have a "is this real?" check running. A diagram + a confident boundary defense flips that to yes.
- It signals you've thought about the **hard parts** (failure modes, trust boundaries, where secrets
  live), which is the difference between a hack and a company.
- It gives the room a place to ask deep questions — and depth Q&A is where you separate from the pack.
- It compresses a complex system into something a judge can *re-explain to the panel later*. That's how
  you get advocated for when you're not in the room.

## The layered diagram — what to show

Draw the system as **horizontal layers with explicit trust boundaries**, top (user) to bottom (the
secret/the world). For an agent control-plane product the layers are roughly:

1. **User / intent** — the human and what they asked for (voice/text). Where approval happens.
2. **Client / surface** — the app; holds *no* secrets; talks only to your control plane.
3. **Control plane** — the brain: intent → plan → **policy/capability engine** (capability ≠ permission),
   grant issuance, approval gating, audit. This is your moat — make it the visual center.
4. **Broker / authority layer** — mints *scoped, ephemeral, revocable* access; resolves secrets
   **server-side at the tool boundary**; the model/agent only ever holds an opaque handle.
5. **External world** — the tools/APIs/payments the agent acts on, only through brokered, gated calls.

Then overlay the two things judges actually probe:

- **Trust boundaries** — draw the lines secrets/authority must never cross (e.g., "secret never enters
  the model context", "client never sees the key", "capability can't escalate to a side-effect without a
  one-shot human approval"). The boundary lines are the most important marks on the diagram.
- **The request lifecycle** — number the steps of one real action end-to-end (intent → plan → grant →
  approval → brokered call → redacted result → audit). Be ready to trace it with your finger.

## Prepare-ahead checklist

- [ ] **Commit `docs/ARCHITECTURE.md`** to the repo with the diagram inline (Mermaid renders on GitHub).
- [ ] Start from [assets/layered-architecture.mmd](../assets/layered-architecture.mmd); adapt the layers
      and labels to your system. Keep it to ~5 layers — legible beats exhaustive.
- [ ] **Export a PNG/SVG** for slides (`mmdc -i layered-architecture.mmd -o architecture.png`, or
      paste into mermaid.live and export). A diagram only in the repo won't be on screen during the pitch.
- [ ] Write the **30-second "how it works"** script (below) and rehearse it cold.
- [ ] List your **3 hardest engineering decisions** with a one-line "why this way" each (fail-closed,
      one-shot tokens, scoped/ephemeral leases, server-side resolution, durable replay protection…).
- [ ] Pre-empt the **likely depth questions** for your track and have crisp answers.

## How to present depth without drowning the demo

- **Put a 10-second pointer in the demo itself**: at the key moment, say "and here's what's happening
  underneath" and flash the diagram. Depth must be *visible*, not only available on request.
- **Have the 30-second version memorized** — one breath per layer, ending on the trust boundary that's
  your moat. Example shape: *"The agent never holds a credential. It speaks intent to our control plane,
  which issues a scoped, revocable grant; side-effecting actions are gated on a one-shot human approval;
  and the secret is resolved server-side at the call boundary and gone — so even a prompt-injected agent
  can read but never act."*
- **Keep the full diagram for Q&A**, not the main slide. Lead with the one boundary that's hardest and
  most differentiating; let them pull the rest.
- **Tailor to the track's bias**: security/infra judges → lead with trust boundaries and failure modes;
  consumer judges → lead with the lifecycle and the "it just asks before it acts" moment.

## The depth Q&A drill (rehearse these)

- "Where does the secret actually live, and when is it in memory?"
- "What stops a compromised/injected agent from doing the dangerous thing?"
- "What's the blast radius if your server is breached / the token leaks?"
- "What's the hardest part you built, and what did you cut?"
- "How does this fail? What happens on timeout / partial failure / replay?"

If you can answer these while pointing at the diagram, you're in the top tier of the room.
