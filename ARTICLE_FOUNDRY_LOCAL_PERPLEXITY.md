# Build a local Perplexity-style research assistant with Azure AI Foundry Local and LangGraph

This article explains how this repository uses **Azure AI Foundry Local** and **LangGraph** to build a Perplexity-style question answering workflow that runs on your machine.

> [!NOTE]
> This project is **inspired by** Perplexity’s user experience (web search + synthesis). It is **not affiliated with Perplexity**.

## What you’ll build

You’ll run a local research assistant that:

- Turns one user question into 3–5 focused search queries.
- Searches the web (via Tavily) and extracts page content.
- Summarizes each source with a local LLM served by Foundry Local.
- Produces a final answer that includes numbered citations.

## Architecture at a glance

The solution is split into three layers:

- **UI**: Streamlit app (entry point in `perplexity.py`).
- **Orchestration**: LangGraph state machine (query planning → parallel research → final writing).
- **Models**: Local LLMs served from Azure AI Foundry Local (OpenAI-compatible `/v1/chat/completions` API).

A typical request flows like this:

1. **Build queries** (LLM)
2. **Parallel web research** (Tavily search + extract)
3. **Summarize sources** (LLM)
4. **Write final answer** (LLM) + append **References**

## Prerequisites

- Windows 10/11
- Python 3.11+
- Azure AI Foundry Local installed
- Disk space for models (several GB)
- A Tavily API key (required for web search)

## Step 1: Install Azure AI Foundry Local (Windows)

If you don’t already have it installed, you can use WinGet:

```powershell
winget install Microsoft.AzureAIFoundryLocal
```

Verify the CLI is available:

```powershell
foundry --version
```

## Step 2: Download local models

This project is configured to use two models (one for “fast” tasks and another for reasoning-style output). You can download the model IDs used by default in `config.py`.

Example:

```powershell
foundry models download Phi-4-mini-instruct-generic-gpu:5
foundry models download deepseek-r1-distill-qwen-7b-generic-gpu:3
```

> [!TIP]
> If you don’t have a GPU, you can still run locally, but it may be slow. Consider switching to CPU-friendly model variants (and then update `LLM_MODEL` / `REASONING_MODEL` in `config.py`).

## Step 3: Start the Foundry Local server

On Windows, this repo includes a helper script:

```bat
start_foundry.bat
```

That script starts:

```bat
foundry serve --port 52576
```

> [!IMPORTANT]
> The app reads the Foundry endpoint from the `FOUNDRY_ENDPOINT` environment variable (or defaults in `config.py`). Make sure the port in `FOUNDRY_ENDPOINT` matches the port you start Foundry on.
>
> - If you start Foundry on port `52576`, set `FOUNDRY_ENDPOINT=http://127.0.0.1:52576`.
> - If you use a different port, update the endpoint accordingly.

## Step 4: Configure environment variables

Create a `.env` file (or export environment variables) with at least:

```dotenv
# Foundry Local server
FOUNDRY_ENDPOINT=http://127.0.0.1:52576
FOUNDRY_API_KEY=local

# Web search
TAVILY_API_KEY=your_tavily_key_here
```

### Why these settings matter

- `FOUNDRY_ENDPOINT` is used by the LLM wrapper (`llm_client.py`) to call `POST {FOUNDRY_ENDPOINT}/v1/chat/completions`.
- `FOUNDRY_API_KEY` is sent as an `api-key` HTTP header.
- `TAVILY_API_KEY` enables web search and extraction.

## Step 5: Install Python dependencies

This repository uses Poetry. From the project folder:

```powershell
poetry install
```

If you prefer a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
poetry install
```

## Step 6: Run the app

Start the Streamlit UI:

```powershell
streamlit run perplexity.py
```

Enter a question, select **Pesquisar**, and the workflow will:

- Generate search queries.
- Fetch and summarize sources.
- Produce a final response with citations.

## How the workflow works (LangGraph)

The graph is built around a state object (see `schemas.py`) and three main nodes:

- **build_first_queries**
  - Uses a structured JSON response format (Pydantic schema) to reliably produce 3–5 queries.
  - Prompt templates live in `prompts.py`.

- **single_search**
  - Uses Tavily to search and extract content from sources.
  - Truncates raw content to `MAX_RAW_CHARS` (from `config.py`) to keep prompts bounded.
  - Summarizes each source with the LLM.

- **final_writer**
  - Formats the per-source summaries and asks the model to write a cohesive final answer.
  - Appends a reference list (e.g., `[1] - [Title](URL)`), so users can verify sources.

Concurrency is achieved by spawning one researcher task per query using `langgraph.types.Send`.

## Customization guide

### Swap models

Update the model IDs in `config.py`:

- `LLM_MODEL` for query generation + summarization
- `REASONING_MODEL` for longer-form synthesis

### Tune quality and speed

Key knobs in `config.py`:

- `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`, `LLM_TIMEOUT`
- `REASONING_MAX_TOKENS`, `REASONING_TEMPERATURE`, `REASONING_TIMEOUT`
- `MAX_RAW_CHARS` (how much page content is sent to the model)

### Change prompting

Edit prompt templates in `prompts.py`:

- `build_queries` to change how queries are generated.
- `resume_search` to change summarization format.
- `build_final_response` to change final answer structure and citation requirements.

## Troubleshooting

### “Connection refused” or timeouts

- Confirm Foundry Local is running.
- Confirm `FOUNDRY_ENDPOINT` matches the running port (default: `52576`).
- Increase `LLM_TIMEOUT` / `REASONING_TIMEOUT` in `config.py` for slower machines.

### “Model not found”

- List installed models: `foundry model ls`
- Download the configured model IDs.

### Web search returns empty results

- Verify `TAVILY_API_KEY` is set.
- Try increasing `TAVILY_MAX_RESULTS` (in `config.py`) to pull more sources per query.

## Next steps

- Add caching (per-query and per-URL) to speed up repeated questions.
- Increase parallelism and fetch more sources per query.
- Add a local document indexer (so you can search your own files offline).
- Add evaluation prompts to self-check citations and factual consistency.
