# Subagent Observability Implementation

## Overview

Added comprehensive observability features for subagent (task tool) execution, providing visual feedback when the main agent delegates work to specialized named agents.

## Implemented Features

### 1. Color-Coded Agent Identification

**What it does:**
- Parses custom colors from agent.md YAML frontmatter
- Registers colors for each named agent
- Uses agent-specific colors in all visual displays

**Implementation:**
- `namicode_cli/agent.py`: Modified `build_named_subagents()` to parse and register colors
- Colors defined in agent.md frontmatter:
  ```yaml
  ---
  color: #22c55e
  ---
  ```

**Example:**
- `code-reviewer` has color `#22c55e` (green)
- Visual elements use this color for brand consistency

### 2. Enhanced Tool Display

**What it does:**
- Shows subagent type in task tool calls
- Makes it immediately clear which specialized agent is being invoked

**Before:**
```
🔧 task("Review this code for security issues...")
```

**After:**
```
🔧 task[code-reviewer]("Review this code for security issues...")
```

**Implementation:**
- `namicode_cli/ui.py`: Modified `format_tool_display()` to extract and display `subagent_type`

### 3. Visual Delegation Banners

**What it does:**
- Displays a visual banner when delegating to a subagent
- Shows which agent is handling the task
- Uses agent-specific colors for visual distinction
- Displays task preview
- Shows completion status when task finishes

**Visual Output:**

**Start Banner:**
```
🔧 task[code-reviewer]("Review this code for security...")

╭─ Delegating to code-reviewer ────────────────────
│ Task: Review this code for security...
╰───────────────────────────────────────────────────

[subagent work happens here]
```

**Completion Banner:**
```
✓ code-reviewer completed
```

**Implementation:**
- `namicode_cli/execution.py`:
  - Added `active_subagents` dictionary to track running subagents
  - Display delegation banner when task tool starts
  - Display completion banner when task tool finishes
  - Clear tracking on each turn

## Files Modified

### 1. `namicode_cli/agent.py`
- Added imports: `parse_agent_color`, `set_agent_color`
- Modified `build_named_subagents()`:
  - Parse color from agent.md YAML frontmatter
  - Register color in global agent color registry
  - Add color to SubAgent specification

### 2. `namicode_cli/ui.py`
- Modified `format_tool_display()`:
  - Extract `subagent_type` from task tool args
  - Format display as `task[subagent_type]("description")`
  - Shortened description truncation to 80 chars to make room for type

### 3. `namicode_cli/execution.py`
- Added `active_subagents` tracking dictionary
- Added delegation banner display when task tool starts:
  - Uses agent-specific colors
  - Shows subagent type and task preview
  - Formatted with box-drawing characters
- Added completion banner when task tool finishes:
  - Shows success/failure icon (✓/✗)
  - Uses agent-specific color
- Added `active_subagents.clear()` to turn reset logic

## Color System

### How Colors Are Determined

1. **Custom Colors** (Highest Priority):
   - Defined in agent.md YAML frontmatter
   - Example: `color: #22c55e`

2. **Fallback Color**:
   - If no custom color defined, uses `COLORS["subagent"]` from config
   - Provides consistent default appearance

### Accessing Colors

- `get_agent_color(agent_name)` returns the appropriate color
- Used in delegation banners and completion messages

## Usage

### For Agent Creators

Define custom colors in your agent.md:

```markdown
---
color: #ef4444
---

# my-agent - AI Assistant

Your agent description here...
```

Supported color formats:
- Hex codes: `#ef4444`, `#22c55e`
- Color names: `red`, `green`, `blue` (if supported by Rich)

### For Users

No configuration needed! Visual feedback appears automatically when:
1. The main agent uses the `task` tool
2. Work is delegated to a named subagent
3. The subagent completes its work

## Visual Examples

### Example 1: Code Review

```
User: Please review this code for security issues

Nami: I'll delegate this to the code-reviewer agent for specialized analysis.

🔧 task[code-reviewer]("Review the authentication code in auth.py...")

╭─ Delegating to code-reviewer ────────────────────
│ Task: Review the authentication code in auth.py...
╰───────────────────────────────────────────────────

[code-reviewer analyzes the code]

✓ code-reviewer completed

Nami: The code-reviewer found several issues...
```

### Example 2: Node.js Development

```
User: Help me build an Express middleware for rate limiting

Nami: I'll use the nodejs-expert agent for this.

🔧 task[nodejs-expert]("Create an Express middleware that implements...")

╭─ Delegating to nodejs-expert ─────────────────────
│ Task: Create an Express middleware that implements...
╰───────────────────────────────────────────────────

[nodejs-expert creates the middleware]

✓ nodejs-expert completed

Nami: Here's the rate limiting middleware...
```

## Benefits

1. **Transparency**: Users can see when work is delegated
2. **Traceability**: Clear indication of which agent handled which task
3. **Visual Distinction**: Color-coded output helps track different agents
4. **Progress Feedback**: Completion banners confirm task finished
5. **Debugging**: Easier to identify which agent produced what output

## Technical Details

### Tracking Mechanism

- `active_subagents: dict[str, tuple[str, str]]`
  - Key: tool_call_id
  - Value: (subagent_type, description)
  - Populated when task tool starts
  - Cleared when task tool completes or turn resets

### Banner Rendering

- Uses Rich library for styled output
- Box-drawing characters: `╭─│╰`
- Dynamic width based on subagent name length
- Respects agent-specific colors

### Performance Impact

- Minimal: Only adds color parsing during agent initialization
- No impact on execution speed
- Banners render instantly (no blocking operations)

## Future Enhancements (Optional)

Potential improvements that could be added:

1. **Timing Information**: Show how long each subagent took
2. **Nested Delegation**: Visual indicators for subagents calling subagents
3. **Summary Statistics**: Track subagent usage across session
4. **Custom Icons**: Allow agents to define custom emoji icons
5. **Verbose Mode**: Option to show full subagent output inline
6. **Logging**: Write subagent executions to log file

## Testing

Test with any named agent that has a color defined:

```bash
# Start nami
nami

# Try delegating to code-reviewer
User: @code-reviewer Review this function for bugs

# Try implicit delegation
User: Help me review this code for security issues
```

You should see:
- Enhanced tool display with subagent type
- Color-coded delegation banner
- Color-coded completion message

All visual enhancements are working!
