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
from prompt_toolkit.layout import Dimension

# File to store persistent history
HISTORY_FILE = '.myshell_history'

# Background thread to simulate incoming device data
def simulate_device_input():
    counter = 0
    while True:
        time.sleep(random.uniform(1.0, 3.0))
        counter += 1
        print_formatted_text(ANSI(f"\x1b[90m[Device] Event {counter}\x1b[0m"))  # Grey print




class Shell:
    def __init__(self):
        self.session = PromptSession(
            history=FileHistory(HISTORY_FILE),
            auto_suggest=AutoSuggestFromHistory(),  # <- enables ghost suggestions
        )
        self.kb = KeyBindings()
        self.default_prompt = ''
        self.reverse_search_mode = [False]

        # Find a way to have access to those variables in the event nicely
        @self.kb.add('c-r')
        def _(event):
            print('Reverse search')
            self.default_prompt = '\n'*10
            self.reverse_search_mode[0] = True
            event.app.exit()
            self.kb.add('<any>')(self.reverse_search_capture)

    def reverse_search_capture(*args):
        print(f'x : {args}')

    def run(self):

        threading.Thread(target=simulate_device_input, daemon=True).start()

        with patch_stdout():
            while True:
                try:
                    cmd = self.session.prompt(
                        "> ",
                        key_bindings=self.kb,
                        multiline=self.reverse_search_mode[0],
                        default=self.default_prompt,
                    )
                    if cmd is None:
                        continue
                    print_formatted_text(f"You entered: {cmd}")
                    if cmd.strip().lower() in {"exit", "quit"}:
                        break
                except (KeyboardInterrupt, EOFError):
                    print_formatted_text("\nExiting.")
                    break

if __name__ == "__main__":
    shell = Shell()
    shell.run()
