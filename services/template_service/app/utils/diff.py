import difflib

def generate_diff(old_text: str, new_text: str) -> str:
    """Generate a unified diff between two texts"""
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile='old',
        tofile='new'
    )
    return ''.join(diff)

def get_changes_summary(old_text: str, new_text: str) -> str:
    """Get a summary of changes"""
    if old_text == new_text:
        return "No changes"
    
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    added = len(new_lines) - len(old_lines)
    if added > 0:
        return f"Added {added} lines"
    elif added < 0:
        return f"Removed {abs(added)} lines"
    else:
        return "Content modified"
