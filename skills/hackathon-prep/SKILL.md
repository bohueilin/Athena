---
name: hackathon-prep
description: >-
  Hard-won learnings and checklists for preparing a hackathon / demo-day / pitch-competition project
  that actually ADVANCES (finalist, prize, investor follow-up) — not just one that demos. Born from the
  AGI House and Y Combinator hackathons where a working, polished build did NOT make finalist. Two core
  lessons so far: (1) PRODUCT NAMING — a generic/overloaded metaphor name ("Passport") quietly caps you;
  and (2) ENGINEERING DEPTH — judges expect a real, layered architecture they can interrogate, prepared
  and saved BEFORE the event. Use this skill whenever the user is preparing for, pitching at, or doing a
  retro on a hackathon, demo day, or pitch competition (AGI House, Y Combinator, etc.); naming or
  renaming a product/project; choosing branding; or preparing an architecture diagram, technical-depth
  story, or "how it actually works" explanation for judges/investors. Trigger even if they don't say
  "hackathon" — e.g. "what should we call this", "is X a good product name", "make an architecture
  diagram for the pitch", "judges said it lacked depth", "why didn't we get picked", "prep for demo day".
---

# Hackathon / Demo-Day Prep — learnings that make you advance

This is a **living retro**, not generic advice. It exists because a *working, polished, honest* build
(real wallet, scoped credentials, phone approvals, end-to-end agent flow) did **not** make finalist at
the AGI House and Y Combinator hackathons. The bar to advance is higher than "it works." Two failures
keep recurring; both are cheap to fix if you plan for them **before** the event.

When this skill triggers, do two things: (1) apply the relevant learning below to the user's current
task, and (2) if you spot a *new* generalizable lesson during the event/retro, append it (see
**Keeping this alive**).

---

## Learning 1 — The name is a product decision, not a label

**What happened:** the product was called **"Passport."** It tested poorly: it's a crowded, generic
metaphor (passport.js, Passkeys, 1Password "passwordless", literal passports, dozens of "Passport"
SaaS), it describes a *vibe* (trust/identity) instead of the *wedge* (runtime-issued, scoped, revocable
agent authority), it isn't ownable (SEO/domain/trademark/GitHub all contested), and it doesn't sound
like serious infrastructure a technical team would bet on. A weak name doesn't sink you on its own — it
quietly taxes every impression: judges can't place the category, can't remember it, can't search it.

**The principle:** in a 60-second judging window, the name is the first compression of your idea. It
should make the category and the wedge *click* instantly, and be *ownable* so the win compounds.

**Do this:** run any candidate name through the rubric in
[references/naming.md](references/naming.md) — distinctiveness, ownability (domain/npm/GitHub/trademark
search done, not assumed), wedge-signal, memorability/say-ability, and the "serious-infra" test. Generate
20+, score the top handful, then verify availability *before* committing. The reference has the full
scorecard, the "Passport" postmortem, and naming territories for an agent-authority / credential-broker
product.

---

## Learning 2 — Bring depth: a layered architecture, saved and explainable

**What happened:** the demo was smooth, but there was **no prepared, layered architecture artifact** to
show the engineering underneath. Technical judges at AGI House / YC probe for depth — the threat model,
the trust boundaries, where secrets actually live, the request lifecycle, what's hard. A polished demo
with no visible substructure reads as shallow or vaporware, and you lose the room exactly when a
strong team would be pulling ahead.

**The principle:** the demo proves it *works*; the architecture proves it's *real and defensible*. Some
of the audience is there for the depth. If you can't draw the system and defend a boundary in 30
seconds, you've ceded the high ground.

**Do this:** before the event, commit a **layered architecture diagram** to the repo
(`docs/ARCHITECTURE.md` + a versioned diagram), and rehearse a 30-second "how it actually works" plus a
depth Q&A. Use the layered template in
[references/architecture-depth.md](references/architecture-depth.md) and the ready-to-edit Mermaid
starter in [assets/layered-architecture.mmd](assets/layered-architecture.mmd) (renders on GitHub; export
to PNG for slides). The reference covers which layers to show, how to draw trust boundaries, the
prepare-ahead checklist, and how to present depth without drowning the demo.

---

## Pre-event checklist (the 80/20)

Run this a few days out, not the night before:

- [ ] **Name** passes the rubric and is *available* (domain + GitHub org + npm/PyPI + a clean trademark search). See [references/naming.md](references/naming.md).
- [ ] **`docs/ARCHITECTURE.md`** committed, with a **layered diagram** (Mermaid in-repo → PNG for slides).
- [ ] You can **draw the architecture from memory** and **defend one trust boundary** in 30 seconds.
- [ ] **One-liner** states the category + wedge in plain words (no metaphor-only descriptions).
- [ ] The **hardest engineering decision** has a crisp "why we did it this way" answer ready.
- [ ] Demo has a **10-second "how it works"** beat that points at the architecture, so depth is *visible*, not buried.
- [ ] You know the **track/judges' bias** (security? infra? consumer?) and lead with the depth they reward.

---

## How to apply this skill in the moment

- **Naming task** → read [references/naming.md](references/naming.md), generate + score candidates against the rubric, and *insist on availability checks* before recommending one. Don't hand over a single clever name; give 3–5 vetted directions with the tradeoffs.
- **Architecture/depth task** → read [references/architecture-depth.md](references/architecture-depth.md), adapt [assets/layered-architecture.mmd](assets/layered-architecture.mmd) to their system, save it to their repo as `docs/ARCHITECTURE.md`, and draft the 30-second depth script.
- **General retro ("why didn't we get picked?")** → walk both learnings, be honest about which applied, and capture anything new.

## Keeping this alive

This is a retro that should compound. After each hackathon, append a new `## Learning N — …` section here
(or a new file under `references/`) with: *what happened → the principle → what to do next time*. Keep
each one concrete and grounded in a real event, the way the two above are. The goal is that the next
build starts from everything the last one learned the hard way.
