# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

My search is, more or less, a plain keyword match, and some phrasings will miss.  My keyword scoring matches whole words only, so ‘jeans’ won’t match ‘denim’, and ‘tee’ won’t match ‘T-shirt


## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
     

---
There’s no model or ranking judgment on this path. Search is plain Python: filters plus a keyword score, and I drop listings with score > 0. If nothing survives, the list is empty, and checking for an empty list is a deterministic if not results:. Criterion 1 can miss because phrasing varies, but here the outcome doesn’t depend on phrasing. So 5 of 5 is fair, and anything less would mean a bug in my code, not variance in the tool.
     

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

In 5 of 5 tries with a matching query, the id of the listing stored as the selected item (e.g. lst_004) equals the id of the item passed into suggest_outfit, and the item text sent in the prompt contains that listing’s title.

**Why this target:**

State failures look like tool problems. If the wrong item reaches suggest_outfit, the advice is still fluent, just about the wrong jeans. Comparing ids is countable and doesn’t depend on the model’s wording. I picked 5 of 5 because this is plain data passing in my own code, with no model randomness. A single mismatch means my loop is dropping or overwriting the item, not that the tool had a bad day.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

In 5 of 5 tries, the fit card (a) mentions the item’s price or title, (b) is no longer than 100 words, and (c) for two different items, doesn’t share the same first sentence.

**Why this target:**

The card calls a model, so exact wording will vary and I can’t test for specific text. What I can test is things a person would be unhappy to see: a caption that ignores the price, one too long to post, or the same generic opening for different items. These checks are countable without judging style. I chose 5 of 5 because each check is loose enough that a working prompt should pass every time. If it fails, the prompt is probably underspecified (for example, it doesn’t tell the model to include the price or a length limit).

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

In 5 of 5 searches with a max_price set, every returned listing has price <= max_price, including the edge case where a listing’s price equals max_price exactly. Also, max_price=0 is treated as a real filter, not as “no filter.”

**Why this target:**

My first version of the price filter had two bugs: it removed items while looping (which skips elements), and if max_price: treats 0 as no filter. Either could return over-budget items without raising an error, so nothing would warn me. This is a hard rule for a shopping tool, because showing someone a $55 item after they said $30 is a visible failure. It’s also deterministic, so a miss means a bug, not variance.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
