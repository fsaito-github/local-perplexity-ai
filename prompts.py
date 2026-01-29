"""Templates de prompts para os diferentes estágios do LangGraph"""

agent_prompt = """
You are a research planner.

You are working on a project that aims to answer user's questions
using sources found online. 

Your answer MUST be technical, using up to date information.
Cite facts, data and specific informations.

Here's the user input
<USER_INPUT>
{user_input}
</USER_INPUT>
"""

# Prompt para gerar queries de busca
build_queries = agent_prompt + """
Your first objective is to with build a list of queries
that will be used to find answers to the user's question.

Answer with anything between 3-5 queries.

IMPORTANT: You MUST respond with ONLY a valid JSON object in this exact format:
{{
    "queries": ["query1", "query2", "query3"]
}}

Do NOT include any other text, explanation, or formatting. Just the JSON object.
"""

# Prompt para resumir resultados de busca
resume_search = agent_prompt + """
Your objective here is to analyze the web search results and make a synthesis of it,
emphasizing only what is relevant to the user's question.

After your work, another agent will use the synthesis to build a final response to the user, so
make sure the synthesis contains only useful information.
Be concise and clear.

Here's the web search results:
<SEARCH_RESULTS>
{search_results}
</SEARCH_RESULTS>
"""

# Prompt para gerar resposta final
build_final_response = agent_prompt + """
Your objective here is develop a final response to the user using
the reports made during the web search, with their synthesis.

The response should contain something between 500 - 800 words.

Here's the web search results:
<SEARCH_RESULTS>
{search_results}
</SEARCH_RESULTS>

You must add reference citations (with the number of the citation, example: [1]) for the 
articles you used in each paragraph of your answer.
"""

__all__ = ["build_queries", "resume_search", "build_final_response"]