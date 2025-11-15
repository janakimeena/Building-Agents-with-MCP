import os
import sys
#import signal
from mcp.server.fastmcp import FastMCP

# Handle SIGPIPE gracefully
#signal.signal(signal.SIGPIPE, signal.SIG_DFL)

mcp = FastMCP("AI Sticky Notes")

# Ensure we save in the current directory
notes_file = os.path.join(os.path.dirname(__file__), "notes.txt")

def ensure_file():
    """Make sure the notes file exists"""
    if not os.path.exists(notes_file):
        with open(notes_file, "w") as f:
            f.write("")

@mcp.tool()
def add_note(message: str) -> str:
    """
    Append a new note to the sticky notes file
    
    Args:
        message: The note content to be added
    
    Returns:
        Confirmation message indicating the note was saved
    """
    ensure_file()
    with open(notes_file, "a") as f:
        f.write(message + "\n")
    return "Note saved"

@mcp.tool()
def read_notes() -> str:
    """
    Read all notes from the sticky notes file
    
    Returns:
        All notes or 'No notes yet' if empty
    """
    ensure_file()
    with open(notes_file, "r") as f:
        content = f.read().strip()
    return content or "No notes yet"

@mcp.resource("notes:/latest")
def get_latest_note() -> str:
    """
    Get the most recent note as a resource
    
    Returns:
        The last note or 'No notes yet' if empty
    """
    ensure_file()
    with open(notes_file, "r") as f:
        lines = f.readlines()
    return lines[-1].strip() if lines else "No notes yet"

@mcp.prompt()
def note_summary_prompt() -> str:
    """
    Generate a prompt asking the AI to summarize all current notes
    
    Returns:
        A prompt with all notes or a message if no notes exist
    """
    ensure_file()
    with open(notes_file, "r") as f:
        content = f.read().strip()
    
    if not content:
        return "There are no notes yet."
    return f"Summarize the current notes:\n{content}"

def handle_shutdown(signum, frame):
    """Gracefully handle shutdown signals"""
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    #signal.signal(signal.SIGTERM, handle_shutdown)
    #signal.signal(signal.SIGINT, handle_shutdown)
    
    try:
        mcp.run()
    except (BrokenPipeError, IOError):
        # Handle broken pipe errors gracefully
        sys.exit(0)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        sys.exit(0)
