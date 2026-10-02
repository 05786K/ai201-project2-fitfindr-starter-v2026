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
FitFindr lets a user ask for a secondhand clothing item using a description, size, and maximum price. The agent searches the listings data for matching items and uses the selected listing as the input for the next step. It then generates outfit ideas using the user's wardrobe and creates a short fit-card caption. If no listings are found, the agent stops and tells the user what they can change.
---

## Tool Inventory

### `search_listings`

- **What it does:** Filters the listings data by size and max price, scores what's left by keyword overlap with the description, and returns the best match first.
- **Inputs:** 
     `description` (str) — keywords describing what the user wants; 
     `size` (str | None, default None) — size to filter by, skipped when None. Size matching is case-insensitive and uses exact token matching after splitting listing sizes on spaces, slashes, and parentheses. 
     `max_price` (float | None, default None) — inclusive price ceiling, skipped when None.
- **Returns:** A list of listing dicts, each with `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform` (str) — sorted by keyword-overlap score, highest first, capped at `config.SEARCH_RESULT_LIMIT` (10) items.
- **When it has nothing:** Returns an empty list — not `None`, not an exception — when no listing scores above zero after filtering.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits pairing a selected listing with pieces from the user's wardrobe.
- **Inputs:** 
     `new_item` (dict) — the listing dict chosen from `search_listings`'s results. 
     `wardrobe` (dict) — a dict with an `items` key holding a list of wardrobe item dicts, which may be empty.
- **Returns:** A non-empty string describing the suggested outfit(s), naming at least one wardrobe item by its exact `name` string.
- **When it has nothing:** When `wardrobe['items']` is empty, returns general styling advice for the item (still a non-empty string) instead of raising or returning `""`.

### `create_fit_card`

- **What it does:** Writes a short, social-media-style caption (2-4 sentences) about the find, naming the item, its price, and its platform once each, and referencing the suggested outfit.
- **Inputs:** 
     `outfit` (str) — the outfit suggestion string returned by `suggest_outfit`
     `new_item` (dict) — the listing dict for the item
- **Returns:** A 2-4 sentence caption string.
- **When it has nothing:** When `outfit` is empty or whitespace-only, returns a fixed descriptive string (e.g. `"No fit card available — no outfit suggestion was generated for this item."`) instead of raising.

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

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (size, price, or description) and return the session without calling `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and continue on to `suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex — patterns pull out a size (e.g. "size M") and a max price (e.g. "under $30"), whatever's left of the query becomes the description passed to `search_listings`.

**What moves through the session:** `query` (the raw input) → `parsed` (description/size/max_price pulled from it) → `search_results` (everything `search_listings` returned) → `selected_item` (the first result, passed to `suggest_outfit` and `create_fit_card`) → `outfit_suggestion` → `fit_card`. `wardrobe` is carried unchanged from the start, and `error` is set only when the loop stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'silk slip dress in midi length under $40'

  Found:    90s Silk Slip Dress — Floral, Midi Length — $30.0 on depop

  Outfit:   Here are two ways to style your 90s silk slip dress using your existing wardrobe:

**Outfit 1: Casual Grunge (Daytime)**
Layer the slip dress over the "White ribbed tank top" to lean into that authentic 90s layering trend. Slip on the "Black combat boots" to give the floral print some edge, and throw the "Oversized grey crewneck sweatshirt" right over the dress for a relaxed, slouchy texture contrast. Finish with the "Black crossbody bag". 

**Outfit 2: Streetwear Contrast (Transition Weather)**
Wear the slip dress on its own and tougunt it up by layering the "Black cropped zip hoodie" over top, letting the midi hem peek out the bottom. Ground the delicate silk with the "Chunky white sneakers" for an effortless high-low mix, and top it all off with the "Vintage black denim jacket".

  Fit card: Channel ultimate 90s grunge in this ivory floral midi. Layer it with "Black combat boots" and a "White ribbed tank top" for effortless daytime cool. Grab it on depop for just $30.00 before someone else does!

2 model calls this session, 587 prompt + 238 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"


[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category':'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two quick ways to style your new Vintage Levi's 501 Jeans:

**Outfit 1: Casual & Sporty**
Pair the jeans with the "White ribbed tank top" tucked in, layered under the "Black cropped zip hoodie". Finish the look with the "Chunky white sneakers" and the "Blackcrossbody bag" for an easy, everyday street-style fit.

**Outfit 2: Edgy & Layered**
Tuck the jeans in at the waist using the "Brown leather belt" and pair them with the "Oversized grey crewneck sweatshirt". Throw the "Vintage black denim jacket" over top and anchor the outfit with the "Black combat boots" for a cool, textural vintage vibe.
```

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

```
Scored these vintage Levi's 501 jeans for casual coffee runs. They have the absolute best lived-in indigo fade. Grab them for $38.00 on depop before I change my mind. Pair with "white sneakers" for that effortless 90s off-duty look.


---

## How I Used AI

**Moment 1**
- *What I asked for:* 
     Implement `create_fit_card` according to the README and docstring requirements.
- *What came back:* 
     The first version worked, but one sample caption was 52 words, exceeding criterion 4's 50-word limit.
- *What I changed:* 
      Added an explicit 50-word limit to the model's system prompt and instructed it to check the word count before responding. Subsequent runs produced captions between 26 and 35 words.

**Moment 2**
- *What I asked for:* 
     Why `python app.py ask 's'` returned a listing instead of no results.
- *What came back:* 
     Claude found that `_tokenize()` split `"Levi's"` into `"levi"` and `"s"`, causing the one-letter query to match the stray `"s"` token.
- *What I changed:* 
     Updated tokenization to remove apostrophes before splitting, so `"Levi's"` becomes `"levis"` instead of two separate tokens.

---

## Stretch Features

### A fourth tool: `compare_price`

- **What it does:** Compares the selected listing's price against the average price of other listings in the same `category`, to flag whether it's priced above or below similar items.
- **Inputs:** `item` (dict) — the selected listing dict, as returned by `search_listings`.
- **Returns:** A string naming the item's price, the category average, the dollar difference, and the number of comparable listings it was computed from (e.g. `"At $38.00, this is $5.20 below the average price for bottoms ($43.20, based on 6 other listings)."`).
- **When it has nothing:** When no other listing shares the item's `category`, returns a fixed message instead of raising or dividing by zero (e.g. `"Not enough comparable 'bottoms' listings to compare price against."`).
- **Where it's called:** `agent.py::run_agent`, right after `session["selected_item"]` is set. Result is stored in `session["price_comparison"]`.

**Sample run:**

```
$ python -c "from tools import compare_price; from utils.data_loader import load_listings; print(compare_price(load_listings()[0]))"

At $38.00, this is $9.56 above the average price for bottoms ($28.44, based on 9 other listings).
```

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Price:    At $18.00, this is $4.00 below the average price for tops ($22.00, based on 14 other listings).

  Outfit:   **Outfit 1: Casual Y2K Streetwear**
...

  Fit card: Channeling total 2000s mall vibes with this butterfly Y2K Baby Tee. Grab it on depop for $18.00 before I change my mind. Throw it on with your favorite "Baggy straight-leg jeans, dark wash" and "Chunky white sneakers" for the ultimate off-duty look.
```

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
