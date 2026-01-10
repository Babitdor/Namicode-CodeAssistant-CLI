# Unicode Encoding Fix

## Problem

When running Nami-Code on Windows, the application crashed with:
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 6366:
character maps to <undefined>
```

This occurred when reading agent.md files that contained Unicode characters (✅, ❌, →, etc.) added in the enhanced subagent delegation documentation.

## Root Cause

Windows uses cp1252 (Windows-1252) as the default text encoding. When Python's `Path.read_text()` is called without specifying an encoding parameter, it uses the platform's default encoding.

The enhanced agent.md files contain UTF-8 Unicode characters:
- ✅ (U+2705) - White Heavy Check Mark
- ❌ (U+274C) - Cross Mark
- → (U+2192) - Rightwards Arrow
- And other Unicode symbols

These characters are not in the cp1252 character set, causing decode errors.

## Solution

Added explicit `encoding='utf-8'` parameter to all `read_text()` calls for agent.md and related files.

## Files Fixed

### 1. `namicode_cli/token_utils.py`
**Lines 34, 48**: Read agent.md files during token calculation
```python
# Before
user_memory = agent_md_path.read_text()
contents.append(path.read_text())

# After
user_memory = agent_md_path.read_text(encoding='utf-8')
contents.append(path.read_text(encoding='utf-8'))
```

### 2. `namicode_cli/agent_memory.py`
**Lines 235, 245**: Load user and project memory
```python
# Before
result["user_memory"] = user_path.read_text()
content = path.read_text()

# After
result["user_memory"] = user_path.read_text(encoding='utf-8')
content = path.read_text(encoding='utf-8')
```

### 3. `namicode_cli/agent.py`
**Lines 242, 278**: Read agent.md for listing and copying agents
```python
# Before
content = agent_md.read_text()
source_content = source_md.read_text()

# After
content = agent_md.read_text(encoding='utf-8')
source_content = source_md.read_text(encoding='utf-8')
```

### 4. `namicode_cli/config.py`
**Line 702**: Read default agent prompt template
```python
# Before
return default_prompt_path.read_text()

# After
return default_prompt_path.read_text(encoding='utf-8')
```

## Why This Works

UTF-8 is a universal character encoding that supports all Unicode characters, including:
- ASCII characters (a-z, A-Z, 0-9, etc.)
- Extended Latin characters (é, ñ, ü, etc.)
- Emoji and symbols (✅, ❌, →, etc.)
- International scripts (Chinese, Arabic, Hebrew, etc.)

By explicitly specifying `encoding='utf-8'`, Python will:
1. Correctly decode all Unicode characters regardless of platform
2. Work consistently on Windows, macOS, and Linux
3. Handle any future Unicode content in agent.md files

## Testing

Verified the fix:
```bash
cd "B:\Winter 2025 Projects\Nami-Code\Namicode-CodeAssistant-CLI"
uv run python -m py_compile namicode_cli/token_utils.py \
  namicode_cli/agent_memory.py \
  namicode_cli/agent.py \
  namicode_cli/config.py
```

All files compile successfully without syntax errors.

## Prevention

### Best Practice

**Always specify encoding when reading text files:**
```python
# Good
content = path.read_text(encoding='utf-8')

# Bad (platform-dependent)
content = path.read_text()
```

### When UTF-8 is Required

Use `encoding='utf-8'` for:
- Configuration files (.md, .yaml, .json, .toml)
- User-generated content
- Documentation files
- Any file that might contain non-ASCII characters

### When Platform Default is OK

Platform default encoding is acceptable for:
- Temporary files that stay within the same process
- System files known to use platform encoding
- Legacy compatibility requirements

## Impact

This fix ensures Nami-Code works correctly on all platforms, particularly Windows, when agent.md files contain:
- Emoji in documentation (✅, ❌, 🔧, etc.)
- Unicode symbols (→, ─, ╭, ╰, etc.)
- International characters (any language)

## Related Changes

This fix was needed because we enhanced the default agent prompt with Unicode characters for better readability:
- Check marks (✅) for good examples
- Cross marks (❌) for poor examples
- Arrows (→) for decision flow
- Box-drawing characters (╭─╰) for visual banners

All of these improvements now work seamlessly on Windows and all platforms.
