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
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition

# File to store persistent history
HISTORY_FILE = '.myshell_history'

# Background thread to simulate incoming device data
def simulate_device_input():
    counter = 0
    while True:
        time.sleep(random.uniform(1.0, 3.0))
        counter += 1
        print_formatted_text(ANSI(f"\x1b[90m[Device] Event {counter}\x1b[0m"))  # Grey print

class ReverseSearchState:
    def __init__(self):
        self.active = False
        self.search_term = ""
        self.matches = []
        self.current_index = 0
        self.original_text = ""
        self.original_cursor_position = 0

def get_history_matches(history, search_term):
    """Get matching commands from history"""
    if not search_term:
        return []
    
    matches = []
    seen = set()  # To avoid duplicates
    
    # Search through history in reverse order (most recent first)
    for entry in reversed(list(history.get_strings())):
        if search_term.lower() in entry.lower() and entry not in seen:
            matches.append(entry)
            seen.add(entry)
    
    return matches

def update_search_display(buffer, search_state, history):
    """Update the buffer with search results"""
    if not search_state.active:
        return
    
    # Get matches
    search_state.matches = get_history_matches(history, search_state.search_term)
    
    if search_state.matches:
        # Show current match
        current_match = search_state.matches[search_state.current_index]
        buffer.text = current_match
        buffer.cursor_position = len(current_match)
        
        # Update the bottom toolbar with search info
        match_info = f"(reverse-i-search)`{search_state.search_term}': {current_match} [{search_state.current_index + 1}/{len(search_state.matches)}]"
        buffer.search_state = match_info
    else:
        # No matches found
        buffer.text = ""
        buffer.cursor_position = 0
        buffer.search_state = f"(reverse-i-search)`{search_state.search_term}': [no matches]"

def main():
    # Create search state
    search_state = ReverseSearchState()
    
    # Create key bindings for the main shell
    bindings = KeyBindings()
    
    # Create the session with history
    history = FileHistory(HISTORY_FILE)
    
    @bindings.add(Keys.ControlR)
    def start_reverse_search(event):
        """Start or continue reverse search"""
        buffer = event.app.current_buffer
        
        if not search_state.active:
            # Start reverse search
            search_state.active = True
            search_state.search_term = ""
            search_state.current_index = 0
            search_state.original_text = buffer.text
            search_state.original_cursor_position = buffer.cursor_position
            
            # Clear buffer and show initial prompt
            buffer.text = ""
            buffer.cursor_position = 0
            buffer.search_state = "(reverse-i-search)`': "
        else:
            # Continue to next match
            if search_state.matches and len(search_state.matches) > 1:
                search_state.current_index = (search_state.current_index + 1) % len(search_state.matches)
                update_search_display(buffer, search_state, history)
    
    @bindings.add(Keys.ControlS)
    def previous_search_match(event):
        """Go to previous search match"""
        if search_state.active and search_state.matches and len(search_state.matches) > 1:
            buffer = event.app.current_buffer
            search_state.current_index = (search_state.current_index - 1) % len(search_state.matches)
            update_search_display(buffer, search_state, history)
    
    @bindings.add(Keys.ControlC)
    def cancel_search(event):
        """Cancel reverse search"""
        if search_state.active:
            buffer = event.app.current_buffer
            search_state.active = False
            
            # Restore original text
            buffer.text = search_state.original_text
            buffer.cursor_position = search_state.original_cursor_position
            
            # Clear search state display
            if hasattr(buffer, 'search_state'):
                delattr(buffer, 'search_state')
    
    @bindings.add(Keys.Escape)
    def escape_search(event):
        """Escape from reverse search"""
        cancel_search(event)
    
    @bindings.add(Keys.Enter, filter=Condition(lambda: search_state.active))
    def accept_search(event):
        """Accept the current search result"""
        if search_state.active:
            buffer = event.app.current_buffer
            search_state.active = False
            
            # Keep the current text (which is the selected command)
            # Clear search state display
            if hasattr(buffer, 'search_state'):
                delattr(buffer, 'search_state')
            
            # Don't process the Enter normally, let it continue to execute the command
            return
    
    @bindings.add(Keys.Backspace, filter=Condition(lambda: search_state.active))
    def backspace_in_search(event):
        """Handle backspace in search mode"""
        if search_state.search_term:
            search_state.search_term = search_state.search_term[:-1]
            search_state.current_index = 0
            buffer = event.app.current_buffer
            update_search_display(buffer, search_state, history)
    
    @bindings.add(Keys.Any, filter=Condition(lambda: search_state.active))
    def add_to_search(event):
        """Add character to search term"""
        if event.data and event.data.isprintable():
            search_state.search_term += event.data
            search_state.current_index = 0
            buffer = event.app.current_buffer
            update_search_display(buffer, search_state, history)
    
    # Custom bottom toolbar to show search state
    def get_bottom_toolbar():
        if search_state.active:
            return getattr(event.app.current_buffer if 'event' in globals() else None, 'search_state', 
                         f"(reverse-i-search)`{search_state.search_term}': ")
        return None
    
    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=bindings,
        bottom_toolbar=get_bottom_toolbar,
    )
    
    # Start the background listener
    threading.Thread(target=simulate_device_input, daemon=True).start()
    
    print_formatted_text("Shell with CTRL+R history search.")
    print_formatted_text("CTRL+R: reverse search, CTRL+S: previous match, CTRL+C/ESC: cancel")
    print_formatted_text("Commands: exit, quit to exit")
    print_formatted_text()
    
    with patch_stdout():
        while True:
            try:
                # Store event globally for toolbar access
                globals()['event'] = None
                
                cmd = session.prompt("> ")
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