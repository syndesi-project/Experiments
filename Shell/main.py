import threading
import time
import random
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import ANSI, FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyPressEvent, KeyPress
from prompt_toolkit.keys import Keys
from prompt_toolkit.application import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import clear
import sys
import os

# File to store persistent history
HISTORY_FILE = '.myshell_history'

# Background thread to simulate incoming device data
def simulate_device_input():
    counter = 0
    while True:
        time.sleep(random.uniform(1.0, 3.0))
        counter += 1
        print_formatted_text(ANSI(f"\x1b[90m[Device] Event {counter}\x1b[0m"))  # Grey print


class TestCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        return [Completion('test'), Completion('test2')]
class Shell:
    N_COMMANDS = 10

    STYLE = Style.from_dict({
        'highlight' : 'bg:#444444 #ffffff',   # background gray, foreground white
        'prompt-marker' : 'bold #00ff00',            # bright green marker
        'rss' : 'bold bg:#505050',
        'rs' : '',
        'rs_left_line' : 'bold bg:#505050 #ff5010'
    })

    RS_CAPTURE_KEY = ['<any>', 'up', 'down', 'enter']

    PROMPT = FormattedText([('class:prompt-marker','❯ ')])

    def __init__(self):
        self._history = FileHistory(HISTORY_FILE)
        self.update_reverse_search_entries()
        self.session = PromptSession(
            history=self._history,
            auto_suggest=AutoSuggestFromHistory(),  # <- enables ghost suggestions
        )
        self.kb = KeyBindings()
        self.default_prompt = self.PROMPT
        self.reverse_search_mode = [False]
        self.reverse_search_selection = 0

        # Find a way to have access to those variables in the event nicely

        @self.kb.add('c-r')
        def _(event):
            self.update_reverse_search_entries()
            self.update_reverse_search()
            self.reverse_search_mode[0] = True
            for c in self.RS_CAPTURE_KEY:
                self.kb.add(c)(self.reverse_search_capture)

        self.update_reverse_search_entries()

    def update_reverse_search_entries(self):
        self._reverse_search_entries = []
        for _, x in zip(range(self.N_COMMANDS), self._history.load_history_strings()):
            self._reverse_search_entries.append(x)
        # Invert because the order is newest at the bottom
        self._reverse_search_entries = self._reverse_search_entries[::-1]
        self.reverse_search_selection = len(self._reverse_search_entries)-1


    def update_reverse_search(self):
        entries = []
        for i, command in enumerate(self._reverse_search_entries):
            selected = i == self.reverse_search_selection
            # Add the left margin
            entries.append(
                ('class:rs_left_line', '>' if selected else ' ')
            )
            # Space
            entries.append(
                ('class:rss' if selected else '', ' ')
            )
            # Add the command
            entries.append(
                ('class:rss' if selected else '', f' {command}\n')# Style
            )

        self.default_prompt = FormattedText(entries)

    def exit_reverse_search(self):
        for c in self.RS_CAPTURE_KEY:
            self.kb.remove(c)
        get_app().current_buffer.document = Document(self._reverse_search_entries[self.reverse_search_selection])
        self.default_prompt = self.PROMPT
        self.reverse_search_mode[0] = False

    def reverse_search_capture(self, event : KeyPressEvent):
        key = event.key_sequence[0].key
        exit = False
        if key == Keys.Up and self.reverse_search_selection > 0:
            self.reverse_search_selection -= 1
        elif key == Keys.Down and self.reverse_search_selection < len(self._reverse_search_entries) - 1:
            self.reverse_search_selection += 1
        elif key == Keys.Enter:
            exit = True
        
        
        if exit:
            self.exit_reverse_search()  
        else:
            self.update_reverse_search()
            event.app.invalidate()

    def run(self):

        threading.Thread(target=simulate_device_input, daemon=True).start()

        with patch_stdout():
            while True:
                try:
                    cmd = self.session.prompt(
                        lambda: self.default_prompt, # Allows for update of the prompt
                        key_bindings=self.kb,
                        multiline=self.reverse_search_mode[0],
                        style=self.STYLE                        
                    )
                    if cmd is None:
                        continue

                    command = cmd.strip()

                    if command in ['clear', 'cls']:
                        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
                            # linux
                            os.system('clear')
                        elif sys.platform == "win32":
                            # Windows
                            os.system('cls')
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
