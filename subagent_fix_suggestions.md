# Fix for Duplicate Output in @agent Invocations

## Problem
The subagent's response is displayed twice:
1. Once during the streaming loop (real-time text accumulation)
2. Again after the streaming loop completes (final markdown render)

## Root Cause
The `invoke_subagent()` function in `commands.py` accumulates text during streaming (lines 2075-2100) and then displays it again at the end (lines 2243-2257), but the streaming itself may already be rendering content.

## Recommended Fixes

### Option 1: Remove Final Render (Cleanest)
Don't display `pending_text` after streaming completes since it was already displayed during streaming.

**Location:** `commands.py`, lines 2242-2257

**Change:**
```python
# Stop spinner when done
if spinner_active:
    status.stop()

# NOTE: Don't render pending_text here because it was already displayed
# during the streaming loop. The text is accumulated in pending_text
# to return to the caller if needed, but we've already shown it to the user.

# Just return the text without re-displaying it
if pending_text:
    text = pending_text.strip()
    return text
```

**Issue:** This might not work if text isn't being displayed during streaming. Need to verify.

### Option 2: Prevent Duplicate Text Accumulation
Track which text has already been displayed and only display new text.

**Location:** `commands.py`, line 1964 - add tracking variable

**Change:**
```python
# Add tracking variable
displayed_text_segments: set[str] = set()  # Track what we've displayed

# In the streaming loop (around line 2076-2100), display text immediately:
if hasattr(message, "content"):
    content = message.content
    if isinstance(content, str) and content:
        if content not in displayed_text_segments:
            displayed_text_segments.add(content)
            pending_text += content
            # Display immediately
            if not has_responded:
                console.print("●", style=COLORS["agent"], markup=False, end=" ")
                has_responded = True
            console.print(content, style=COLORS["agent"])

# Then at the end (lines 2242-2257), don't re-display:
if pending_text:
    text = pending_text.strip()
    return text  # Just return, don't display
```

### Option 3: Add a Flag to Track if Text Was Displayed
Track whether any text was actually displayed during streaming, and only display at the end if nothing was shown.

**Location:** `commands.py`

**Change:**
```python
# Add tracking variable (line 1963)
text_displayed_during_stream = False  # Track if we showed text during streaming

# In streaming loop, set flag when displaying:
if hasattr(message, "content"):
    content = message.content
    if isinstance(content, str) and content:
        if content not in pending_text:
            pending_text += content
            text_displayed_during_stream = True
            # Display real-time...

# At the end (lines 2242-2257):
if pending_text:
    text = pending_text.strip()
    if text and not text_displayed_during_stream:
        # Only display if nothing was shown during streaming
        if not has_responded:
            console.print("●", style=COLORS["agent"], markup=False, end=" ")
            has_responded = True
        try:
            markdown = Markdown(text)
            console.print(markdown, style=COLORS["agent"])
        except Exception:
            console.print(text, style=COLORS["agent"])
    return text
```

### Option 4: Defer All Rendering Until End (Simplest)
Don't display anything during streaming, only at the end. This removes real-time display but fixes duplication.

**Location:** `commands.py`

**Change:**
```python
# Remove all display logic from streaming loop (lines 2075-2214)
# Just accumulate text without displaying

# Keep only tool call displays during streaming (lines 2182-2213)
# Remove any text rendering from the streaming loop

# Keep final render (lines 2243-2257) unchanged
```

## Recommendation

**Option 3** is the best balance - it keeps real-time display if it happens, but prevents duplication by checking if text was already shown.

However, you first need to **diagnose** whether text is actually being displayed during streaming. The code as written only accumulates text during streaming and displays at the end. If you're seeing duplicates, there might be:

1. Multiple AIMessages with the same content being processed
2. The subagent generating duplicate content
3. The main agent echoing the subagent's response

Add debug logging to see what's happening:

```python
# At line 2076, add:
console.print(f"[dim][DEBUG] Processing message: {msg_id}, content length: {len(content) if content else 0}[/dim]")

# At line 2243, add:
console.print(f"[dim][DEBUG] Final render, pending_text length: {len(pending_text)}[/dim]")
```

Then run the code and see what the debug output shows.