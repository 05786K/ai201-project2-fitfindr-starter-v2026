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
The search and outfit tools depend on the listing data and model responses, so occasional variation can cause a run to fail. A 4-of-5 target requires the complete happy path to work reliably without demanding perfection from model-dependent calls.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
An empty search result is deterministic: there is no listing to pass to the outfit tool. Because the loop can directly check whether the search returned any results, this branch should behave consistently every time rather than depending on model output.
---

## 3. An item is passed through session state correctly
<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

For 5 matching queries, the item passed to suggest_outfit must be the same listing selected by search_listings in all 5 runs, with the item's `name`, `price`, and `size` matching exactly between the two tool calls.

**Why this target:**
Passing the search result through session state is a required part of the agent design. Testing five runs makes it difficult for a state bug to pass by chance, while comparing identifiable fields such as the listing name, price, and size makes the state transfer directly observable.


---

## 4. The fit card reflects both the selected item and the outfit
<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->
For 5 successful runs, every fit card must include at least two of: the listing's name, price, or size, and at least one named outfit piece from suggest_outfit's result, while staying at 50 words or fewer.


**Why this target:**
A fit card should be based on the actual results of the agent rather than being a generic caption. Requiring details from both the listing and the generated outfit verifies that information is carried through the full tool chain, while the 50-word limit keeps the result short enough to be a realistic post caption.


---

## 5. Search respects the user's size and price constraints
<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->
For 5 matching queries that specify both a size and a maximum price, every listing passed to suggest_outfit must match the requested size and have a price at or below the requested maximum in all 5 runs.


**Why this target:**
Size and price are both explicit inputs to search_listings, so returning an item that violates either constraint would give the agent a result the user did not ask for. Requiring both constraints to hold across all 5 runs makes the search behavior consistently testable rather than checking only one filter at a time.


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
