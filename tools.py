"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings

_WORD_RE = re.compile(r"[a-z0-9]+")
_APOSTROPHE_RE = re.compile(r"['’]")
_SIZE_SPLIT_RE = re.compile(r"[\s/()]+")


def _tokenize(text: str) -> set[str]:
    # Strip apostrophes before splitting so "Levi's" tokenizes to "levis",
    # not "levi" + a stray "s" that would match any one-letter query.
    return set(_WORD_RE.findall(_APOSTROPHE_RE.sub("", text.lower())))


def _size_tokens(size: str) -> set[str]:
    return {token for token in _SIZE_SPLIT_RE.split(size.upper()) if token}


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()

    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.upper() not in _size_tokens(listing["size"]):
            continue
        filtered.append(listing)

    query_tokens = _tokenize(description)
    scored = []
    for listing in filtered:
        searchable = " ".join([
            listing["title"],
            listing["description"],
            " ".join(listing["style_tags"]),
        ])
        score = len(query_tokens & _tokenize(searchable))
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item_desc = f"{new_item['title']} ({new_item['category']}, {', '.join(new_item['colors'])})"
    items = wardrobe["items"]

    if not items:
        system = (
            "You are a stylist giving quick, specific outfit advice for a "
            "secondhand clothing find. The user has no wardrobe on file, so "
            "give general styling advice — colors, silhouettes, and types of "
            "pieces that would pair well — in two or three sentences."
        )
        prompt = f"Suggest how to style this item: {item_desc}."
    else:
        wardrobe_lines = "\n".join(
            f'- "{item["name"]}" ({item["category"]}, {", ".join(item["colors"])})'
            for item in items
        )
        system = (
            "You are a stylist giving quick, specific outfit advice for a "
            "secondhand clothing find. Build one or two outfits that pair the "
            "new item with pieces the user already owns. When you reference a "
            "wardrobe item, use its exact name in quotes, exactly as listed "
            "below — don't paraphrase it."
        )
        prompt = (
            f"New item: {item_desc}.\n\n"
            f"Wardrobe:\n{wardrobe_lines}\n\n"
            "Suggest one or two complete outfits using the new item and "
            "specific pieces from the wardrobe above."
        )

    response = generate(prompt, system=system)
    if not response.strip():
        return f"This piece would work well on its own — {item_desc} is versatile enough to build an outfit around."
    return response


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit.strip():
        return "No fit card available — no outfit suggestion was generated for this item."

    item_desc = (
        f"{new_item['title']}, ${new_item['price']:.2f} on {new_item['platform']} "
        f"({new_item['condition']} condition, {', '.join(new_item['colors'])})"
    )

    system = (
        "You write short, punchy captions for a secondhand-fashion app — the "
        "kind someone would actually post, not a product listing. Write 2 to "
        "4 short sentences, 50 words total or fewer — count your words before "
        "answering and cut one if you're over. Mention the item, its price, "
        "and its platform exactly once each. Be specific about the vibe. Keep "
        "any wardrobe item names from the outfit suggestion exactly as "
        "written, in quotes — don't paraphrase them."
    )
    prompt = (
        f"Item: {item_desc}.\n\n"
        f"Outfit suggestion: {outfit}\n\n"
        "Write the caption now."
    )

    response = generate(prompt, system=system)
    if not response.strip():
        return (
            f"Found this {new_item['title']} for ${new_item['price']:.2f} on "
            f"{new_item['platform']} — too good to pass up."
        )
    return response


# ── Tool 4: compare_price ─────────────────────────────────────────────────────

def compare_price(item: dict) -> str:
    """
    Compare a listing's price against the average price of other listings in
    the same category.

    Like search_listings, this doesn't call the model — it's pure arithmetic
    over the listings data.

    Args:
        item: a listing dict — the selected item, as returned by
              search_listings().

    Returns:
        A string naming the item's price, the category average, the dollar
        difference, and how many comparable listings it was computed from.
        **Returns a fixed message — not an exception, not a divide-by-zero —
        when no other listing shares this item's category.**
    """
    others = [
        listing
        for listing in load_listings()
        if listing["category"] == item["category"] and listing["id"] != item["id"]
    ]

    if not others:
        return (
            f"Not enough comparable '{item['category']}' listings to compare "
            f"price against."
        )

    average = sum(listing["price"] for listing in others) / len(others)
    diff = item["price"] - average
    direction = "above" if diff >= 0 else "below"

    return (
        f"At ${item['price']:.2f}, this is ${abs(diff):.2f} {direction} the "
        f"average price for {item['category']} (${average:.2f}, based on "
        f"{len(others)} other listings)."
    )
