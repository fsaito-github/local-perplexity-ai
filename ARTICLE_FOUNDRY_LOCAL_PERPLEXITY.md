# Build a Local Research Assistant with Azure AI Foundry Local and LangGraph

In this tutorial, you build a local research assistant that answers questions by searching the web and synthesizing results using Azure AI Foundry Local.

The solution runs large language models (LLMs) entirely on your local machine while using an external web search API for retrieval.

The application demonstrates a Perplexity-style question-answering workflow (query planning, parallel research, and synthesis). It is not affiliated with Perplexity.

## What You'll Learn

By completing this tutorial, you will learn how to:

- Run LLMs locally by using Azure AI Foundry Local
- Expose local models through an OpenAI-compatible API
- Orchestrate multi-step AI workflows with LangGraph
- Combine local inference with external web search
- Build a simple research assistant user interface with Streamlit

## Architecture Overview

The solution is organized into three logical layers:

### 1. Application Layer (UI)

- Streamlit web app
- Accepts a user question
- Displays the synthesized answer with numbered citations

### 2. Orchestration Layer

- LangGraph state machine
- Controls the research workflow:
  - Query planning
  - Parallel web research
  - Summarization
  - Final response writing

### 3. Model Layer

- Local LLMs served by Azure AI Foundry Local
- Accessed through an OpenAI-compatible REST API
- No model inference is executed in the cloud

## How the Research Workflow Works

1. The user enters a research question.
2. A local LLM generates 3–5 search queries.
3. Each query is executed in parallel using the Tavily Search API.
4. Raw web content is extracted and truncated to stay within prompt limits.
5. Each source is summarized locally using Foundry Local.
6. A final local LLM synthesizes the summaries into a single answer.
7. The response includes numbered citations linked to the original sources.

## Prerequisites

Before you begin, make sure you have:

- A Windows 10 or Windows 11 device
- Python 3.10 or later
- Azure AI Foundry Local installed
- Sufficient disk space for local models (several GB)
- A Tavily API key for web search

> **Note:** After models are downloaded, inference runs locally and does not require an internet connection.

## Step 1: Install Azure AI Foundry Local

Install Foundry Local by using winget:

```powershell
winget install Microsoft.FoundryLocal
```

Verify the installation:

```powershell
foundry --version
```

If the installation succeeded, the command returns the Foundry Local version number.

## Step 2: Download Local Models

This project uses two different models:

- A fast, lightweight model for query generation and summarization
- A reasoning-focused model for final answer synthesis

Download the models configured in the project:

```powershell
foundry model download <model-id-1>
foundry model download <model-id-2>
```

> **Tip:** Model availability and performance depend on your hardware (CPU, GPU, or NPU). Use `foundry model list` to view supported models on your system.

## Step 3: Start the Foundry Local Service

Start the local model service on a specific port:

```powershell
foundry service start --port 52576
```

By default, the service listens on `http://127.0.0.1:52576`.

Foundry Local exposes an OpenAI-compatible API surface that the application uses for chat completions.

## Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
FOUNDRY_ENDPOINT=http://127.0.0.1:52576
FOUNDRY_API_KEY=local
TAVILY_API_KEY=<your-tavily-api-key>
```

- `FOUNDRY_ENDPOINT` points to the local Foundry Local service
- `FOUNDRY_API_KEY` is required by the API client, even for local calls
- `TAVILY_API_KEY` enables web search and content extraction

## Step 5: Install Python Dependencies

The project uses Poetry for dependency management.

```powershell
poetry install
poetry shell
```

This installs LangGraph, Streamlit, and supporting libraries.

## Step 6: Run the Application

Start the Streamlit app:

```powershell
streamlit run app.py
```

In the browser interface:

1. Enter a research question.
2. The app generates search queries.
3. Sources are retrieved and summarized.
4. A synthesized answer with citations is displayed.

## Customization Options
You can customize the solution in several ways:

Swap models by updating model IDs in config.py
Adjust generation behavior:

MAX_TOKENS
TEMPERATURE
TIMEOUT


Change prompt templates:

Query planning
Source summarization
Final synthesis


Tune web search:

Number of results per query
Maximum extracted content length




Troubleshooting

### The app cannot connect to Foundry Local

- Verify that Foundry Local is running.
- Confirm that `FOUNDRY_ENDPOINT` matches the service port.
- Increase request timeouts for slower machines.

### A model is not found

- Run `foundry model list`.
- Download the model ID specified in the configuration file.

### Web search returns no results

- Verify that `TAVILY_API_KEY` is set.
- Increase the maximum number of search results per query.

