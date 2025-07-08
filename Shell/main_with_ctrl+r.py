import asyncio
import random
import threading
import time
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app

HISTORY_FILE = ".myshell_history"

def simulate_device_input():
    counter = 0
    while True:
        time.sleep(random.uniform(1, 3))
        counter += 1
        print_formatted_text(ANSI(f"\x1b[90m[Device] Event {counter}\x1b[0m"))

def load_history_lines():
    try:
        with open(HISTORY_FILE, "r") as f:
            seen = set()
            result = []
            for line in reversed(list(f)):
                line = line.strip()
                # Skip timestamps and empty lines
                if not line or line.startswith("#") or line.startswith("+"):
                    continue
                if line not in seen:
                    seen.add(line)
                    result.append(line)
            return list(reversed(result))
    except FileNotFoundError:
        return []

def fuzzy_filter(query, items):
    if not query:
        return items
    query = query.lower()
    return [item for item in items if all(c in item.lower() for c in query)]

async def zsh_style_fuzzy_search(session):
    history = load_history_lines()
    if not history:
        return None

    term_height = os.get_terminal_size().lines
    max_items = min(10, term_height - 4)
    selected_index = 0
    input_query = ""
    inp = get_app().input

    def render(filtered):
        print("\n" * (max_items + 3), end="")
        print(f"\x1b[{max_items + 3}A", end="")  # move up
        print("🔍 Reverse search: " + input_query)
        for i in range(max_items):
            if i < len(filtered):
                prefix = "👉" if i == selected_index else "  "
                print(f"{prefix} {filtered[i]}")
            else:
                print("")

    def clear_lines():
        print(f"\x1b[{max_items + 4}A", end="")  # move up
        print("\x1b[J", end="")                 # clear down

    filtered = fuzzy_filter(input_query, history)
    render(filtered)

    try:
        while True:
            keys = inp.read_keys()
            if not keys:
                continue
            key = keys[0].key

            if key == "c-m":  # Enter
                clear_lines()
                if filtered:
                    return filtered[selected_index]
                return None
            elif key == "c-h":  # Backspace
                input_query = input_query[:-1]
            elif key == "c-c":  # Ctrl+C
                clear_lines()
                return None
            elif key == "down":
                selected_index = (selected_index + 1) % len(filtered) if filtered else 0
            elif key == "up":
                selected_index = (selected_index - 1) % len(filtered) if filtered else 0
            elif len(key) == 1:
                input_query += key

            filtered = fuzzy_filter(input_query, history)
            selected_index = min(selected_index, len(filtered) - 1) if filtered else 0
            clear_lines()
            render(filtered)
    finally:
        inp.close()

async def main():
    threading.Thread(target=simulate_device_input, daemon=True).start()

    kb = KeyBindings()
    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        key_bindings=kb,
    )

    @kb.add("c-r")
    def _(event):
        async def reverse_search():
            result = await zsh_style_fuzzy_search(session)
            if result:
                event.app.current_buffer.insert_text(result)
        event.app.create_background_task(reverse_search())

    with patch_stdout():
        while True:
            try:
                cmd = await session.prompt_async("> ")
                if not cmd.strip():
                    continue
                print_formatted_text(f"You entered: {cmd}")
                if cmd.strip().lower() in {"exit", "quit"}:
                    break
            except (KeyboardInterrupt, EOFError):
                print_formatted_text("Exiting.")
                break

if __name__ == "__main__":
    asyncio.run(main())
