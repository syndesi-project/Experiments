import threading
import time
import random
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.filters import Condition
import re

# File to store persistent history
HISTORY_FILE = '.myshell_history'

# Fuzzy search helper
def fuzzy_search(query, items):
    pattern = '.*?'.join(map(re.escape, query))
    regex = re.compile(pattern, re.IGNORECASE)
    return [item for item in items if regex.search(item)]

# Custom reverse search state
class ReverseSearchState:
    def __init__(self, session):
        self.session = session
        self.active = False
        self.query = ''
        self.matches = []
        self.idx = 0
        self.orig_text = ''

    def start(self, event: KeyPressEvent):
        self.active = True
        self.query = ''
        self.idx = 0
        self.orig_text = event.current_buffer.text
        self.update_matches()
        self.render()

    def update_matches(self):
        history_strings = list(reversed([h for h in self.session.history.get_strings()]))
        self.matches = fuzzy_search(self.query, history_strings) if self.query else history_strings
        if self.idx >= len(self.matches):
            self.idx = max(0, len(self.matches) - 1)

    def render(self):
        print('\n' * 10, end='')
        print(f"(reverse-i-search)`{self.query}':")
        for i, cmd in enumerate(self.matches[:5]):
            prefix = '>' if i == self.idx else ' '
            print(f"{prefix} {cmd}")
        print('\033[J', end='')

    def handle_key(self, event: KeyPressEvent):
        key = event.key_sequence[0].key
        data = event.data
        if key == 'c-m':  # Enter
            if self.matches:
                event.current_buffer.document = Document(self.matches[self.idx], cursor_position=len(self.matches[self.idx]))
            self.active = False
            print('\n' * 12, end='')  # Clear overlay
        elif key == 'c-g':  # Cancel
            event.current_buffer.document = Document(self.orig_text, cursor_position=len(self.orig_text))
            self.active = False
            print('\n' * 12, end='')
        elif key == 'up':
            self.idx = max(0, self.idx - 1)
            self.render()
        elif key == 'down':
            self.idx = min(len(self.matches) - 1, self.idx + 1)
            self.render()
        elif key == 'backspace':
            self.query = self.query[:-1]
            self.idx = 0
            self.update_matches()
            self.render()
        elif data and len(data) == 1 and data.isprintable():
            self.query += data
            self.idx = 0
            self.update_matches()
            self.render()
        else:
            pass  # Ignore other keys

# Background thread to simulate incoming device data
def simulate_device_input():
    counter = 0
    while True:
        time.sleep(random.uniform(1.0, 3.0))
        counter += 1
        print_formatted_text(ANSI(f"\x1b[90m[Device] Event {counter}\x1b[0m"))  # Grey print

def main():
    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        auto_suggest=AutoSuggestFromHistory(),
    )
    kb = KeyBindings()
    reverse_state = ReverseSearchState(session)

    @kb.add('c-r')
    def _(event):
        if not reverse_state.active:
            reverse_state.start(event)
            event.app.invalidate()

    # Only handle keys if reverse search is active
    def reverse_active():
        return reverse_state.active

    @kb.add('up', filter=Condition(reverse_active))
    @kb.add('down', filter=Condition(reverse_active))
    @kb.add('backspace', filter=Condition(reverse_active))
    @kb.add('c-m', filter=Condition(reverse_active))  # Enter
    @kb.add('c-g', filter=Condition(reverse_active))  # Cancel
    def _(event):
        reverse_state.handle_key(event)
        event.app.invalidate()
        if not reverse_state.active:
            reverse_state.query = ''
            reverse_state.idx = 0
            reverse_state.matches = []
            reverse_state.orig_text = ''

    # Bind all printable characters
    for c in (chr(i) for i in range(32, 127)):
        @kb.add(c, filter=Condition(reverse_active))
        def _(event, c=c):
            reverse_state.handle_key(event)
            event.app.invalidate()
            if not reverse_state.active:
                reverse_state.query = ''
                reverse_state.idx = 0
                reverse_state.matches = []
                reverse_state.orig_text = ''

    # Start the background listener
    threading.Thread(target=simulate_device_input, daemon=True).start()
    with patch_stdout():
        while True:
            try:
                cmd = session.prompt(
                    "> ",
                    key_bindings=kb
                )
                if not cmd.strip():
                    continue
                print_formatted_text(f"You entered: {cmd}")
                if cmd.strip().lower() in {"exit", "quit"}:
                    break
            except (KeyboardInterrupt, EOFError):
                print_formatted_text("\nExiting.")
                break

if __name__ == "__main__":
    main()
