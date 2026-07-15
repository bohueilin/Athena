# Naming a product so it helps you win

The name is the first (and often only) compression of your idea that a judge or investor retains. In a
short window it has to make the **category** and the **wedge** click, and it has to be **ownable** so
every mention compounds instead of leaking value to someone else's brand.

## The "Passport" postmortem (why it underperformed)

Concrete so the lesson sticks. "Passport" failed on most axes at once:

- **Overloaded / not distinctive.** `passport.js` (the dominant Node auth library), Passkeys, 1Password's
  "passwordless", literal travel passports, and a long tail of "Passport" SaaS/insurance/banking brands.
  The name lands in a crowded room and borrows none of it.
- **Describes a vibe, not the wedge.** It gestures at "trust / identity / credentials" but says nothing
  about the actual differentiator: **runtime-issued, scoped, ephemeral, revocable authority for agents,
  where the secret never enters the model.** The judge has to do the work to find the point.
- **Not ownable.** Domain, GitHub org, npm/PyPI, and trademark are all contested. SEO is hopeless — you'll
  never rank for your own name. Every win you generate partly markets someone else.
- **Doesn't sound like serious infra.** Control-plane / security infrastructure names tend to feel
  engineered or coined; a generic English metaphor reads as a hackathon skin, not a company.

None of these is fatal alone. Together they tax every impression and cap how far a 60-second pitch can
carry you.

## The naming rubric (score each candidate 0–2)

| Axis | 0 | 1 | 2 |
|---|---|---|---|
| **Distinctive** | common word / crowded metaphor | somewhat used | rare or coined; stands alone |
| **Ownable** | domain + GitHub + npm + TM all taken | some taken | `.com`/`.ai` gettable, GitHub org free, package name free, no obvious TM conflict |
| **Signals the wedge** | pure vibe | hints at category | category + differentiator click instantly |
| **Memorable / sayable** | forgettable or hard to spell/say | ok | sticky; spell-on-first-hear; no "how do you spell that?" |
| **Serious-infra feel** | toy/skin | neutral | sounds like a company a team would bet on |

Ship a name only if it scores **8+/10** *and* clears the availability check below. Anything under ~7 is a
liability you'll feel in every demo.

## Availability check (do it for real, before committing)

Assumed-available is how teams ship a name they have to abandon later. Actually check:

- **Domain**: `.com` and/or `.ai` reachable (a registrar search, not a guess).
- **GitHub org / handle** free.
- **Package name** free on npm and/or PyPI (matters for dev-infra credibility).
- **Trademark**: a quick USPTO TESS / Google search for the exact term in your class — no obvious collision.
- **SEO sanity**: search the bare name; if page one is unrelated giants, you'll never own it.

## Process

1. **Name the wedge in one literal sentence first** (no metaphor). For the agent-authority product:
   *"Runtime-issued, task-scoped, revocable access for AI agents — the secret never enters the model."*
   Good names compress *that*, not "trust."
2. **Generate 20+** across distinct territories (below). Quantity first; judge later.
3. **Score the top ~8** on the rubric.
4. **Availability-check the top 3–5.** Most "great" names die here — expected.
5. **Say them out loud** in a sentence: "We built ___, the control plane for agent authority." The right
   one sounds inevitable.
6. Present **3–5 vetted finalists with tradeoffs**, not one clever pick. Let the human choose.

## Naming territories for an agent-authority / credential-broker product

Directions to brainstorm within (these are *prompts*, not vetted names — run every candidate through the
rubric + availability check):

- **Brokerage / issuance** — the thing mints scoped, short-lived authority on demand (evokes a broker,
  an issuer, a mint, a grant).
- **Attenuation / scope** — power that narrows as it's delegated (evokes a valve, an aperture, a lease, a
  scoped key).
- **Boundary / gate** — the trust boundary where capability ≠ permission is enforced (evokes a gate, a
  threshold, a checkpoint — but avoid the literal "passport/customs" cliché that just bit you).
- **Coined / abstract** — an invented, ownable word (often the winner for infra: clean SEO, free domain,
  trademarkable, sounds engineered). Worth over-indexing on given the ownability problem above.

Avoid: another generic trust/identity metaphor ("Passport", "Trust", "Aegis", "Sentinel", "Guardian",
"Vault" — all heavily used in security). If the word already prints on a competitor's homepage, skip it.

## Tie-break heuristics

- Prefer the name you can **own** over the name that's **cleverest**. Ownability compounds; cleverness doesn't.
- Prefer **say-able on first hear**. If people need it spelled, you lose word-of-mouth.
- Prefer a name that lets you **state the category next to it** ("___, the control plane for agent
  authority") without sounding redundant or strained.
