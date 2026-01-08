# Tracing quickstart

[*Observability*](/langsmith/observability-concepts) is a critical requirement for applications built with Large Language Models (LLMs). LLMs are non-deterministic, which means that the same prompt can produce different responses. This behavior makes debugging and monitoring more challenging than with traditional software.

LangSmith addresses this by providing end-to-end visibility into how your application handles a request. Each request generates a [*trace*](/langsmith/observability-concepts#traces), which captures the full record of what happened. Within a trace are individual [*runs*](/langsmith/observability-concepts#runs), the specific operations your application performed, such as an LLM call or a retrieval step. Tracing runs allows you to inspect, debug, and validate your application’s behavior.

In this quickstart, you will set up a minimal [*Retrieval Augmented Generation (RAG)*](https://www.mckinsey.com/featured-insights/mckinsey-explainers/what-is-retrieval-augmented-generation-rag) application and add tracing with LangSmith. You will:

1. Configure your environment.
2. Create an application that retrieves context and calls an LLM.
3. Enable tracing to capture both the retrieval step and the LLM call.
4. View the resulting traces in the LangSmith UI.

<Tip>
  If you prefer to watch a video on getting started with tracing, refer to the quickstart [Video guide](#video-guide).
</Tip>

## Prerequisites

Before you begin, make sure you have:

* **A LangSmith account**: Sign up or log in at [smith.langchain.com](https://smith.langchain.com).
* **A LangSmith API key**: Follow the [Create an API key](/langsmith/create-account-api-key#create-an-api-key) guide.
* **An OpenAI API key**: Generate this from the [OpenAI dashboard](https://platform.openai.com/account/api-keys).

The example app in this quickstart will use OpenAI as the LLM provider. You can adapt the example for your app's LLM provider.

<Tip>
  If you're building an application with [LangChain](https://python.langchain.com/docs/introduction/) or [LangGraph](https://langchain-ai.github.io/langgraph/), you can enable LangSmith tracing with a single environment variable. Get started by reading the guides for tracing with [LangChain](/langsmith/trace-with-langchain) or tracing with [LangGraph](/langsmith/trace-with-langgraph).
</Tip>

## 1. Create a directory and install dependencies

In your terminal, create a directory for your project and install the dependencies in your environment:

<CodeGroup>
  ```bash Python theme={null}
  mkdir ls-observability-quickstart && cd ls-observability-quickstart
  python -m venv .venv && source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -U langsmith openai
  ```

  ```bash TypeScript theme={null}
  mkdir ls-observability-quickstart-ts && cd ls-observability-quickstart-ts
  npm init -y
  npm install langsmith openai typescript ts-node
  npx tsc --init
  ```
</CodeGroup>

## 2. Set up environment variables

Set the following environment variables:

* `LANGSMITH_TRACING`
* `LANGSMITH_API_KEY`
* `OPENAI_API_KEY` (or your LLM provider's API key)
* (optional) `LANGSMITH_WORKSPACE_ID`: If your LangSmith API key is linked to multiple workspaces, set this variable to specify which workspace to use.

```bash  theme={null}
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="<your-langsmith-api-key>"
export OPENAI_API_KEY="<your-openai-api-key>"
export LANGSMITH_WORKSPACE_ID="<your-workspace-id>"
```

If you're using Anthropic, use the [Anthropic wrapper](/langsmith/annotate-code#wrap-the-anthropic-client-python-only) to trace your calls. For other providers, use [the traceable wrapper](/langsmith/annotate-code#use-%40traceable-%2F-traceable).

## 3. Define your application

You can use the example app code outlined in this step to instrument a RAG application. Or, you can use your own application code that includes an LLM call.

This is a minimal RAG app that uses the OpenAI SDK directly without any LangSmith tracing added yet. It has three main parts:

* **Retriever function**: Simulates document retrieval that always returns the same string.
* **OpenAI client**: Instantiates a plain OpenAI client to send a chat completion request.
* **RAG function**: Combines the retrieved documents with the user’s question to form a system prompt, calls the `chat.completions.create()` endpoint with `gpt-4o-mini`, and returns the assistant’s response.

Add the following code into your app file (e.g., `app.py` or `app.ts`):

<CodeGroup>
  ```python Python theme={null}
  from openai import OpenAI

  def retriever(query: str):
      # Minimal example retriever
      return ["Harrison worked at Kensho"]

  # OpenAI client call (no wrapping yet)
  client = OpenAI()

  def rag(question: str) -> str:
      docs = retriever(question)
      system_message = (
          "Answer the user's question using only the provided information below:\n"
          + "\n".join(docs)
      )

      # This call is not traced yet
      resp = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
              {"role": "system", "content": system_message},
              {"role": "user", "content": question},
          ],
      )
      return resp.choices[0].message.content

  if __name__ == "__main__":
      print(rag("Where did Harrison work?"))
  ```

  ```typescript TypeScript theme={null}
  import "dotenv/config";
  import OpenAI from "openai";

  // Minimal example retriever
  function retriever(query: string): string[] {
      return ["Harrison worked at Kensho"];
  }

  // OpenAI client call (no wrapping yet)
  const client = new OpenAI();

  async function rag(question: string) {
      const docs = retriever(question);
      const systemMessage =
          "Answer the user's question using only the provided information below:\n" +
          docs.join("\n");

      // This call is not traced yet
      const resp = await client.chat.completions.create({
          model: "gpt-4o-mini",
          messages: [
              { role: "system", content: systemMessage },
              { role: "user", content: question },
          ],
      });

      return resp.choices[0].message?.content;
  }

  (async () => {
    console.log(await rag("Where did Harrison work?"));
  })();
  ```
</CodeGroup>

## 4. Trace LLM calls

To start, you’ll trace all your OpenAI calls. LangSmith provides wrappers:

* Python: [`wrap_openai`](https://docs.smith.langchain.com/reference/python/wrappers/langsmith.wrappers._openai.wrap_openai)
* TypeScript: [`wrapOpenAI`](https://docs.smith.langchain.com/reference/js/functions/wrappers_openai.wrapOpenAI)

This snippet wraps the OpenAI client so that every subsequent model call is logged automatically as a traced child run in LangSmith.

1. Include the highlighted lines in your app file:

   <CodeGroup>
     ```python Python highlight={2,7} theme={null}
     from openai import OpenAI
     from langsmith.wrappers import wrap_openai  # traces openai calls

     def retriever(query: str):
         return ["Harrison worked at Kensho"]

     client = wrap_openai(OpenAI())  # log traces by wrapping the model calls

     def rag(question: str) -> str:
         docs = retriever(question)
         system_message = (
             "Answer the user's question using only the provided information below:\n"
             + "\n".join(docs)
         )
         resp = client.chat.completions.create(
             model="gpt-4o-mini",
             messages=[
                 {"role": "system", "content": system_message},
                 {"role": "user", "content": question},
             ],
         )
         return resp.choices[0].message.content

     if __name__ == "__main__":
         print(rag("Where did Harrison work?"))
     ```

     ```typescript TypeScript highlight={3,9} theme={null}
     import "dotenv/config";
     import OpenAI from "openai";
     import { wrapOpenAI } from "langsmith/wrappers"; // traces openai calls

     function retriever(query: string): string[] {
         return ["Harrison worked at Kensho"];
     }

     const client = wrapOpenAI(new OpenAI()); // log traces by wrapping the model calls

     async function rag(question: string) {
         const docs = retriever(question);
         const systemMessage =
             "Answer the user's question using only the provided information below:\n" +
             docs.join("\n");

         const resp = await client.chat.completions.create({
             model: "gpt-4o-mini",
             messages: [
                 { role: "system", content: systemMessage },
                 { role: "user", content: question },
             ],
         });

         return resp.choices[0].message?.content;
     }

     (async () => {
         console.log(await rag("Where did Harrison work?"));
     })();
     ```
   </CodeGroup>

2. Call your application:

   <CodeGroup>
     ```bash Python theme={null}
     python app.py
     ```

     ```bash TypeScript theme={null}
     npx ts-node app.ts
     ```
   </CodeGroup>

   You'll receive the following output:

   ```
   Harrison worked at Kensho.
   ```

3. In the [LangSmith UI](https://smith.langchain.com), navigate to the **default** Tracing Project for your workspace (or the workspace you specified in [Step 2](#2-set-up-environment-variables)). You'll see the OpenAI call you just instrumented.

<div style={{ textAlign: 'center' }}>
  <img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=ba8074e55cc17ec7bbf0f6987ce15b8d" alt="LangSmith UI showing an LLM call trace called ChatOpenAI with a system and human input followed by an AI Output." data-og-width="750" width="750" data-og-height="573" height="573" data-path="langsmith/images/trace-quickstart-llm-call.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=280&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=b94da918edfd11078bc637fdfc7fcc44 280w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=560&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=7f5f480bee06c54f0e5ad7ce122f722c 560w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=840&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=5e4e621619664b26cbe2d54719667ded 840w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=1100&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=c63599fdd8f12bc1abc80982af376053 1100w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=1650&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=69730a230b5d2cff4d737fab7d965c9f 1650w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call.png?w=2500&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=d5e73432bdd2f3788f7600364f84c96f 2500w" />

  <img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=a00c55450b4a9937b8e557ef483a4bd6" alt="LangSmith UI showing an LLM call trace called ChatOpenAI with a system and human input followed by an AI Output." data-og-width="728" width="728" data-og-height="549" height="549" data-path="langsmith/images/trace-quickstart-llm-call-dark.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=280&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=9b67fab1c4d3d0e2e45d4a38caa1aa82 280w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=560&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=3090d984d38ebac8d83272d235a11662 560w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=840&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=e515ea96b0e90b2c8dc639bccb7d81b2 840w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=1100&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=85584b64773a98555f22cad5c85ba46e 1100w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=1650&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=bc6e44054bb139c9ed00eeb375eb0f4f 1650w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-llm-call-dark.png?w=2500&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=e2cb7aa22421bc4a7d355658a6371d14 2500w" />
</div>

## 5. Trace an entire application

You can also use the `traceable` decorator for [Python](https://docs.smith.langchain.com/reference/python/run_helpers/langsmith.run_helpers.traceable) or [TypeScript](https://langsmith-docs-bdk0fivr6-langchain.vercel.app/reference/js/functions/traceable.traceable) to trace your entire application instead of just the LLM calls.

1. Include the highlighted code in your app file:

   <CodeGroup>
     ```python Python highlight={3,10} theme={null}
     from openai import OpenAI
     from langsmith.wrappers import wrap_openai
     from langsmith import traceable

     def retriever(query: str):
         return ["Harrison worked at Kensho"]

     client = wrap_openai(OpenAI())  # keep this to capture the prompt and response from the LLM

     @traceable
     def rag(question: str) -> str:
         docs = retriever(question)
         system_message = (
             "Answer the user's question using only the provided information below:\n"
             + "\n".join(docs)
         )
         resp = client.chat.completions.create(
             model="gpt-4o-mini",
             messages=[
                 {"role": "system", "content": system_message},
                 {"role": "user", "content": question},
             ],
         )
         return resp.choices[0].message.content

     if __name__ == "__main__":
         print(rag("Where did Harrison work?"))
     ```

     ```typescript TypeScript highlight={3,11} theme={null}
     import "dotenv/config";
     import OpenAI from "openai";
     import { wrapOpenAI, traceable } from "langsmith/wrappers";

     function retriever(query: string): string[] {
         return ["Harrison worked at Kensho"];
     }

     const client = wrapOpenAI(new OpenAI()); // keep this to capture the prompt and response from the LLM

     const rag = traceable(async (question: string) => {
         const docs = retriever(question);
         const systemMessage =
             "Answer the user's question using only the provided information below:\n" +
             docs.join("\n");

         const resp = await client.chat.completions.create({
             model: "gpt-4o-mini",
             messages: [
                 { role: "system", content: systemMessage },
                 { role: "user", content: question },
             ],
         });

         return resp.choices[0].message?.content;
     });

     (async () => {
         console.log(await rag("Where did Harrison work?"));
     })();
     ```
   </CodeGroup>

2. Call the application again to create a run:

   <CodeGroup>
     ```bash Python theme={null}
     python app.py
     ```

     ```bash TypeScript theme={null}
     npx ts-node app.ts
     ```
   </CodeGroup>

3. Return to the [LangSmith UI](https://smith.langchain.com), navigate to the **default** Tracing Project for your workspace (or the workspace you specified in [Step 2](#2-set-up-environment-variables)). You'll find a trace of the entire app pipeline with the **rag** step and the **ChatOpenAI** LLM call.

<div style={{ textAlign: 'center' }}>
  <img className="block dark:hidden" src="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=204edddb78b671c11a48de751c2e8e19" alt="LangSmith UI showing a trace of the entire application called rag with an input followed by an output." data-og-width="750" width="750" data-og-height="425" height="425" data-path="langsmith/images/trace-quickstart-app.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=280&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=d5ad99d3c107fe3ccb63487f43bf912e 280w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=560&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=9f3cdb47af6471d1e508f1fa76883900 560w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=840&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=d1a496530ed1f98ccabbda138ef10b68 840w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=1100&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=d165f3f228f5ffaeb68b0bacc00a0f6e 1100w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=1650&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=ccc05e2cdbaf9bd71a6bcb8536997f2e 1650w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app.png?w=2500&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=2ebc113e6930abffa89644ccfd871404 2500w" />

  <img className="hidden dark:block" src="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=2392204346d412554fbda817e082bdcd" alt="LangSmith UI showing a trace of the entire application called rag with an input followed by an output." data-og-width="738" width="738" data-og-height="394" height="394" data-path="langsmith/images/trace-quickstart-app-dark.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=280&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=7987f9046d36d015624c91f06d38efb2 280w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=560&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=4cf9bef39d55a3aa9a31e3911fe7bdba 560w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=840&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=0f0dc65c6705b4239afc33777e214cb7 840w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=1100&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=d2ccb5a3e2e91e45757f57f43b261861 1100w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=1650&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=2aec3b239854f4fd4f38807b991e5812 1650w, https://mintcdn.com/langchain-5e9cc07a/C5sS0isXOt0-nMfw/langsmith/images/trace-quickstart-app-dark.png?w=2500&fit=max&auto=format&n=C5sS0isXOt0-nMfw&q=85&s=b6ee98094ed25e6f2d61fed7241d648e 2500w" />
</div>

## Next steps

Here are some topics you might want to explore next:

* [Tracing integrations](/langsmith/trace-with-langchain) provide support for various LLM providers and agent frameworks.
* [Filtering traces](/langsmith/filter-traces-in-application) can help you effectively navigate and analyze data in tracing projects that contain a significant amount of data.
* [Trace a RAG application](/langsmith/observability-llm-tutorial) is a full tutorial, which adds observability to an application from development through to production.
* [Sending traces to a specific project](/langsmith/log-traces-to-project) changes the destination project of your traces.

<Callout type="info" icon="bird">
  After logging traces, use **[Polly](/langsmith/polly)** to analyze them and get AI-powered insights into your application's performance.
</Callout>

## Video guide

<iframe className="w-full aspect-video rounded-xl" src="https://www.youtube.com/embed/fA9b4D8IsPQ?si=0eBb1vzw5AxUtplS" title="YouTube video player" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/langsmith/observability-quickstart.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.
</Tip>


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.langchain.com/llms.txt