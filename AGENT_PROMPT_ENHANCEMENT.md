# Agent Prompt Enhancement - Subagent Delegation

## Overview

Enhanced the default agent (nami-agent) system prompt with comprehensive guidelines for delegating tasks to specialized subagents. This ensures the main agent makes intelligent decisions about when and how to use domain-specific named agents.

## Files Modified

1. **`namicode_cli/default_agent_prompt.md`** - Template for new agents
2. **`~/.nami/agents/nami-agent/agent.md`** - Active default agent prompt

## What Was Added

### 1. Available Subagent Types Section

Lists common specialized agents the main agent has access to:
- **general-purpose**: For tasks requiring isolated context
- **code-reviewer**: Code quality, security, and best practices expert
- **nodejs-expert**: Node.js and Express specialization
- **project-structure-agent**: Architecture and codebase organization
- **Playwright**: Browser automation specialist
- Plus any other named agents in ~/.nami/agents/

### 2. When to Delegate Decision Framework

**Delegate when:**
- Domain expertise needed (e.g., security review → code-reviewer)
- Complex multi-step work requiring focused attention
- Context isolation beneficial for large tasks

**DON'T delegate when:**
- Simple 1-2 step tasks
- No matching specialized agent
- User explicitly asks main agent to handle it
- Delegation overhead > benefit

### 3. How to Choose the Right Subagent

Four-step decision process:
1. Match domain to specialist expertise
2. Check availability in task tool description
3. Consider task complexity
4. Assess if specialization improves quality

### 4. Practical Examples

**Good Delegation Examples:**
```
✅ "Review this authentication code" → code-reviewer
✅ "Structure a microservices project" → project-structure-agent
✅ "Create Express middleware" → nodejs-expert
✅ "Research and compare approaches" → general-purpose
```

**Poor Delegation Examples:**
```
❌ "Fix this typo" → Handle directly (too simple)
❌ "Explain this function" → Handle directly (no specialization)
❌ "List files" → Use ls directly (trivial)
```

### 5. Delegation Best Practices

**1. Use filesystem for large I/O**
- Write instructions to file for subagent to read
- Ask subagent to write output to file
- Prevents token bloat

**2. Parallelize independent work**
- Spawn multiple subagents for parallel tasks
- Example: Research 3 libraries simultaneously

**3. Clear specifications**
- Provide complete context
- "Review auth.py for SQL injection, XSS, and password handling" ✅
- "Review auth.py" ❌ (too vague)

**4. Main agent synthesizes**
- Subagents gather/execute
- Main agent integrates and adds value
- Don't just pass through subagent output

**5. Explicit mentions**
- If user says "@code-reviewer", use that agent
- Respect explicit requests for specialization

### 6. Subagent Delegation Pattern

Standard workflow:
```
1. Identify task requires specialization
2. Choose appropriate subagent based on domain
3. Prepare clear, complete instructions
4. Delegate: task(description="...", subagent_type="agent-name")
5. Receive synthesized result
6. Integrate into final response to user
```

### 7. Example Flow

```
User: "Please review my authentication code for security issues"

Main Agent:
  [Recognize this needs security expertise]
  → Use task tool with code-reviewer
  → Provide file path and specific security concerns
  → Receive detailed security analysis
  → Summarize findings and provide recommendations to user
```

### 8. Key Reminders

- Specialized agents have custom system prompts - they're domain experts
- Check task tool description - it lists all available agents
- Quality over speed - delegate when specialization improves quality
- Main agent orchestrates - delegates subtasks, synthesizes results

## Benefits

### For the Agent

1. **Clear decision criteria** - Knows when to delegate vs. handle directly
2. **Improved task routing** - Matches tasks to appropriate specialists
3. **Better quality** - Leverages domain expertise when beneficial
4. **Context management** - Knows when to use isolation vs. direct handling

### For Users

1. **Automatic expertise routing** - Tasks go to the right specialist
2. **Higher quality output** - Domain experts handle specialized work
3. **Transparent delegation** - Visual feedback shows which agent is working
4. **Efficient execution** - Parallel work when appropriate

### For the System

1. **Scalable** - Easy to add new specialized agents
2. **Dynamic** - Agent checks available subagents at runtime
3. **Flexible** - Works with any named agents in ~/.nami/agents/
4. **Maintainable** - Clear patterns and examples

## How It Works

### Discovery

1. Main agent reads task tool description (provided by SubAgentMiddleware)
2. Sees list of available subagents with descriptions
3. Examples in prompt guide decision-making

### Decision Making

Agent follows this mental model:
```
Task received →
  Is it complex enough? →
    Does it match a specialist? →
      Will specialization improve quality? →
        YES: Delegate to named subagent
        NO: Handle directly
```

### Execution

When delegating:
1. Agent selects appropriate subagent type
2. Crafts clear, complete instructions
3. Calls `task(description="...", subagent_type="agent-name")`
4. Receives synthesized result
5. Integrates into response to user

## Testing the Enhancement

### Test Prompts

Try these to verify the agent delegates appropriately:

**Should delegate to code-reviewer:**
```
"Please review this authentication code for security vulnerabilities"
```

**Should delegate to nodejs-expert:**
```
"Help me create an Express middleware for rate limiting"
```

**Should delegate to project-structure-agent:**
```
"How should I structure a new microservices project with authentication?"
```

**Should handle directly (too simple):**
```
"Fix this typo in the README"
"List files in the current directory"
```

### Expected Behavior

With the enhanced prompt, the agent should:
- Recognize when a task matches a specialist's domain
- Explicitly mention delegating to the specialist
- Use the task tool with the correct subagent_type
- Synthesize the specialist's findings into the final response

### Visual Feedback

When delegation occurs, you'll see:
```
Main Agent: I'll delegate this to code-reviewer for specialized analysis

🔧 task[code-reviewer]("Review authentication code for...")

╭─ Delegating to code-reviewer ────────────────────
│ Task: Review authentication code for...
╰───────────────────────────────────────────────────

[code-reviewer works...]

✓ code-reviewer completed

Main Agent: The security review found...
```

## Maintenance

### Adding New Specialized Agents

When you create new specialized agents:

1. Agent is automatically discovered from ~/.nami/agents/
2. SubAgentMiddleware adds it to available subagents
3. Main agent sees it in task tool description
4. No need to update the prompt (it references "Check task tool description")

### Updating Guidelines

To modify delegation behavior:
1. Edit `~/.nami/agents/nami-agent/agent.md`
2. Update "Working with Subagents" section
3. Changes take effect on next agent initialization

### Template for New Agents

The enhanced section in `namicode_cli/default_agent_prompt.md` serves as the template for any new default agents created.

## Future Enhancements

Potential improvements:

1. **Domain tags**: Tag tasks with domains, match to agents
2. **Learning**: Track successful delegations, improve over time
3. **Cost optimization**: Prefer cheaper models for simple delegations
4. **Confidence scores**: Agent expresses confidence in delegation decision
5. **Fallback chains**: If specialist unavailable, use general-purpose

## Conclusion

The enhanced agent prompt provides comprehensive, practical guidance for intelligent subagent delegation. The main agent now:

- Understands when specialization adds value
- Knows how to choose the right specialist
- Follows best practices for delegation
- Synthesizes results effectively

This creates a powerful multi-agent system where specialized expertise is automatically leveraged when beneficial, while simple tasks are handled efficiently by the main agent.
