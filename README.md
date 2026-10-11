# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

A user describes a secondhand clothing item in plain language, for example, "vintage graphic tee under $30, size M", and the agent finds a matching listing from the resale listings data. It then suggests several outfits that combine the found item with pieces from the user's own wardrobe, and writes a short, shareable fit card caption about the find. If nothing matches, or the request can't be understood, the agent stops early and tells the user what to change instead of producing an outfit.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the resale listings by max price and size, then ranks the remaining listings by how many words from the item description appear in each listing's text (title matches count more than description, brand, category, or style-tag matches).
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of listing dicts, best match first. Each dict has the keys `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. Only listings with at least one matching word are included.
- **When it has nothing:** Returns an empty list `[]` (never `None`).

### `suggest_outfit`

- **What it does:** Uses the model to build several outfit ideas that pair the selected listing with items from the user's wardrobe.
- **Inputs:** `item` (dict, one listing from `search_listings`), `wardrobe` (dict, from `get_example_wardrobe()` or `get_empty_wardrobe()`)
- **Returns:** A string of formatted text containing 5 outfit ideas. Each has a title, a one-line style note, and a list of pieces, marking which are the new items and which are already in the wardrobe. `[CHECK: confirm the return type and count]`
- **When it has nothing:** returns outfit ideas that suggest generic pieces and styling advice using that item

### `create_fit_card`

- **What it does:** Uses the model to write a short, first-person social-media-style caption about the thrifted find and how it will be styled.
- **Inputs:** `outfit` (str, the output of `suggest_outfit`), `item` (dict, the selected listing) `[CHECK: argument order and types]`
- **Returns:** A short caption string that mentions the item, its price, and the platform it was found on, with an emoji.
- **When it has nothing:**  A fallback message if the outfit or item is missing

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that tells the user what to change (broaden the description, try a different size, or raise the max price) and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise, take the first result as `selected_item` and continue to `suggest_outfit`, then `create_fit_card`. A second, earlier branch applies if the query can't be parsed or has no item description: set `session["error"]` and return before searching.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Asking the model. `agent.py::parse_query` sends the query to the model with a system prompt that requires a JSON object with `description`, `size`, and `max_price`. It strips any markdown code fences, parses the JSON, converts `"None"`/`"null"` strings back to a real `None`, and returns `None` if the response is invalid or has no description. I chose JSON over a comma-separated format because commas in a description would break splitting.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (first result) → `outfit_suggestion` (from `selected_item` and `wardrobe`) → `fit_card` (from `outfit_suggestion` and `selected_item`). `error` stays `None` on success and is set whenever the run ends early. The loop also calls `trace.check_iterations` each pass, so a runaway loop raises instead of running forever.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python -c "from agent import run_agent; from utils.data_loader import get_example_wardrobe; s = run_agent('vintage graphic tee under 30 dollars, size M', get_example_wardrobe()); print(s['error']); print(s['selected_item']); print(s['outfit_suggestion']); print(s['fit_card'])"


None
{'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'],'brand': None, 'platform': 'depop'}
Here are 5 specific, great-looking outfits you can make using your new **Mesh Long-Sleeve Top — Black** paired with items already in your wardrobe:

### 1. The 90s Grunge Streetwear Look
*Emphasize the edgy, textured look of the sheer mesh with classic denim and boots.*
* **Mesh Long-Sleeve Top — Black** (Your new item!)
* **Baggy straight-leg jeans, dark wash** — already in your wardrobe!
* **Black combat boots** — already in your wardrobe!
* **Black crossbody bag** — already in your wardrobe!

### 2. The Textured Contrast Layer
*Play with dimension by wearing the tight, sheer black mesh underneath a bright white basic.*
* **Mesh Long-Sleeve Top — Black** (Your new item!)
* **White ribbed tank top** (wear *over* the mesh for a cool contrast effect) — already in your wardrobe!
* **Wide-leg khaki trousers** — already in your wardrobe!
* **Chunky white sneakers** — already in your wardrobe!

### 3. The Cozy-Edgy Mix
*Layer the sheer, fitted mesh under a massive, cozy crewneck for a balanced high-low silhouette.*
* **Mesh Long-Sleeve Top — Black** (Your new item!)
* **Oversized grey crewneck sweatshirt** — already in your wardrobe!
* **Baggy straight-leg jeans, dark wash** — already in your wardrobe!
* **Chunky white sneakers** — already in your wardrobe!
* **Black crossbody bag** — already in your wardrobe!

### 4. All-Black Y2K Double Denim & Mesh
*Lean heavily into the Y2K and grunge aesthetic with an all-black palette and mixed textures.*
* **Mesh Long-Sleeve Top — Black** (Your new item!)
* **Vintage black denim jacket** — already in your wardrobe!
* **Baggy straight-leg jeans, dark wash** — already in your wardrobe!
* **Black combat boots** — already in your wardrobe!
* **Black crossbody bag** — already in your wardrobe!

### 5. Sporty Casual Layer
*Pair the sleek, sheer top with a cropped zip hoodie for an effortless streetwear-inspired outfit.*
* **Mesh Long-Sleeve Top — Black** (Your new item!)
* **Black cropped zip hoodie** — already in your wardrobe!
* **Wide-leg khaki trousers** — already in your wardrobe!
* **Brown leather belt** — already in your wardrobe!
* **Chunky white sneakers** — already in your wardrobe!
Picked up this sheer mesh long-sleeve on Depop for just $15 and it’s about to be my ultimate layering piece for every90s grunge and Y2K fit 🖤
```


**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[PASTE OUTPUT]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
[PASTE OUTPUT]
```

```
$ python -c "from tools import create_fit_card; ..."
[PASTE COMMAND AND OUTPUT]
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* How to get the item description, size, and max price out of the user's query using the model. My first prompt asked for comma-separated output, with the string `None` for missing values.
- *What came back:* Claude pointed out two problems: commas in a description would break `split(",")`, and the model would return the string `"None"`, which passes an `is not None` check. It suggested JSON output so missing values come back as `null`, plus a `parse_query` helper that also converts `"None"`/`"null"` strings to a real `None`.
- *What I changed:* I switched the prompt to JSON, added `parse_query` to `agent.py`, and made it return `None` on any failure so `run_agent` has a single check. I also fixed my first loop draft, which never incremented its counter and returned `{}` on a parse failure instead of the session.

**Moment 2**

- *What I asked for:* A review of my test run for "vintage graphic tee under 30 dollars, size M".
- *What came back:* The pipeline ran end to end, but the selected item was a black mesh top, not a graphic tee. Claude traced it to my scoring in `search_listings`, which only matched words in the description and brand (so "layering under a graphic tee" counted) and ignored the title. Punctuation like `tee.` also failed to match.
- *What I changed:* `[CHECK: edit to match what you actually did]` I rewrote the scoring to tokenize with a regex, search title, category, and style tags as well, and weight title matches higher than other matches. Then I reran the query to check the ranking.


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
