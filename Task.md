
# Tasks: 

## Context

- This code below is the handing off tasks to subagents isolates context, keeping the main (supervisor) agent’s context window clean while still going deep on a task.
The subagents middleware allows you to supply subagents through a task tool.

```agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-5-20250929",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": "Use the get_weather tool to get the weather in a city.",
                    "tools": [get_weather],
                    "model": "gpt-4o",
                    "middleware": [],
                }
            ],
        )
    ],
)
```


- A subagent is defined with a name, description, system prompt, and tools. You can also provide a subagent with a custom model, or with additional middleware. This can be particularly useful when you want to give the subagent an additional state key to share with the main agent.


## Task: 

- I want to pass the named specified agents, i have in my codebase, the ones where i use @<--agentname--> <--query--> to be passed also as subagents to the core agent (NAMI) at the agent.py file in 'namicode_cli/agent.py'