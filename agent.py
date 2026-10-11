"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
import json
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable, generate
# from trace import step, start_trace, get_trace, check_iterations


PARSE_SYSTEM_PROMPT = (
    "Extract the item description, size, and maximum price from the user's query. "
    "Respond with ONLY a JSON object with these keys: "
    '"description" (string), "size" (string or null), "max_price" (integer in dollars, '
    "no symbols, or null). Use null for any value that is not present. "
    "Do not include markdown or any other text."
)


def parse_query(query: str) -> dict | None:
    """
    Ask the model to pull description / size / max_price out of the query.

    Returns a dict with those three keys, or None if the response
    couldn't be parsed or no item description was found.
    """
    response = generate(query, PARSE_SYSTEM_PROMPT)

    # Strip code fences in case the model adds them anyway
    text = (
        response.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    description = data.get("description")
    if isinstance(description, str):
        description = description.strip() or None
    if description is None:
        return None

    # Models occasionally return the string "None" or "null" instead of null
    size = data.get("size")
    if isinstance(size, str) and size.strip().lower() in ("none", "null", ""):
        size = None

    try:
        max_price = int(data["max_price"]) if data.get("max_price") is not None else None
    except (TypeError, ValueError):
        max_price = None

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """

    session = new_session(query, wardrobe)

    # TODO: delete these two lines and build the loop.
    # session["error"] = "The planning loop isn't built yet — see the TODO in agent.py."

    loop_count = 0
    while True:
        loop_count += 1
        trace.check_iterations(loop_count)

        # 1. Parse the query
        parsed = parse_query(query)
        if parsed is None:
            session["error"] = (
                "I couldn't tell what item you're after. "
                "Try something like 'vintage graphic tee under $30, size M'."
            )
            return session
        session["parsed"] = parsed

        # 2. Search. This is the branch: stop here if nothing came back.
        session["search_results"] = search_listings(
            parsed["description"], parsed["size"], parsed["max_price"]
        )
        if not session["search_results"]:
            session["error"] = (
                f"Nothing matched '{parsed['description']}'. Try a broader "
                "description, a different size, or a higher max price."
            )
            return session

        # 3. Choose an item (first result is fine)
        session["selected_item"] = session["search_results"][0]

        # 4. Outfit suggestion
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"], session["wardrobe"]
        )

        # 5. Fit card
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"], session["selected_item"]
        )

        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
