## Welcome to Prism
Prism is an open source software project that automatically routes user queries to the optimal LLM. It is currently under development as an independent project at Rice University. It may take a few months for Prism to take shape and be up to production standards. Prism is an intelligent AI router that selects the best LLM for each user query based on **output quality, latency, and cost**.

Instead of routing all user queries to one designated LLM, Prism evaluates each LLM, predicts which model is best suited for the current request, and routes the query to the model. The goal is simple: deliver the **cheapest output** wihtout sacrificing reliability.

## Why Prism?
Different LLMs excel at different tasks.

- Some are faster.
- Some are cheaper, while others waste tokens.
- Some are better at logical reasoning.
- Some are better at structured output or code.


Prism treats model choice as a system problem. It benchmarks models based on a standard dataset, logs performances, scores outputs, and learns routing policies over time.

## Features

- Task aware prompt routing.
- Multi-model support.
- Cost, latency, and quality tracking.
- Benchmarking and evaluation pipeline.
- Extensible routing policies.
- Secure API-based backend.
- Transparent routing decisions.

## How It Works
 
1. A user submits a query to Prism.
2. Prism extracts task features such as:
    - Prompt length.
    - Task type.
    - Output constraints.
    - Reasoning complexity.
3. Prism selects the best LLM for the given query.
4. The selected model generates a response.
5. Prism logs:
    - Latency.
    - Token usage.
    - Estimated cost.
    - Evaluation score.
6. These metrics improve future routing decision.

## Architecture
Prism is built as a backend-first system with five main components. 
1. API Layer: recieves user requests and returns model outputs.
2. Router: chooses the best model using routing policies.
3. Model Adapters: unified wrappers for different LLM providers.
4. Evaluation Engine: measures output quality using automated judges and task-specific checks.
5. Metric Storage: stores logs for latency, quality, and cost analysis.

## Query Routing
Prism optimizes for a utility function such as: ```utility = quality - α(cost) - β(latency)```.