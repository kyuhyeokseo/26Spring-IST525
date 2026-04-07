# AI References in GitHub PR Discussions

This repository contains a research pipeline for collecting and analyzing AI-related references in GitHub Pull Request discussions. It focuses on how tools such as `ChatGPT`, `Copilot`, `Claude`, and other `LLM` systems are mentioned, debated, adopted, or criticized during collaborative software development.

The project follows four main stages:

1. Collect candidate PR discussions with explicit AI references from GH Archive through BigQuery.
2. Enrich the sampled PRs with metadata from the GitHub REST API.
3. Compare AI-reference PRs with a non-AI control group.
4. Analyze the social function, timing, uptake, and refinement of AI-related discussion using rule-based and LLM-assisted labeling.

## Overview

- `collect_ai_reference_github.py`: Collects PR discussions containing AI-related keywords.
- `collect_control_github.py`: Builds a control group of PRs without explicit AI references.
- `compare_ai_vs_control.py`: Compares summary metrics across the AI-reference and control datasets.
- `analyze_ai_reference_patterns.py`: Analyzes who mentions AI, when it is mentioned, where it appears, and how mention intensity relates to PR outcomes.
- `build_llm_labeling_inputs.py`: Prepares structured CSV inputs for LLM-based mention labeling.
- `run_openai_function_labeling.py`: Labels the social function of AI mentions with the OpenAI API.
- `run_ollama_function_labeling.py`: Labels mentions with a local Ollama model.
- `analyze_llm_labeled_functions.py`: Aggregates and summarizes LLM labeling outputs.
- `build_invocation_*`, `analyze_invocation_uptake.py`: Examines whether AI suggestions are accepted, challenged, or ignored.
- `build_suggestion_refinement_inputs.py`, `analyze_suggestion_refinement.py`: Studies how AI suggestions are refined during discussion.

## Repository Structure

```text
.
├── data_ai_refs/          # Collected AI-reference PR data
├── data_control_refs/     # Collected control-group PR data
├── analysis_ai_refs/      # Derived analyses, coding samples, and labeling outputs
├── papers/                # Background literature and reference papers
├── requirements.txt
└── *.py                   # Collection, analysis, and labeling scripts
```

## Requirements

- Python 3.10+
- Access to Google BigQuery
- GitHub personal access token
- OpenAI API key or a local Ollama setup for labeling workflows

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Environment Variables

The following environment variables are required for the full pipeline:

```bash
export GITHUB_TOKEN=your_github_token
export GOOGLE_CLOUD_PROJECT=your_gcp_project_id
export OPENAI_API_KEY=your_openai_api_key
```

- `GITHUB_TOKEN`: Used to enrich PRs, comments, and reviews through the GitHub REST API.
- `GOOGLE_CLOUD_PROJECT`: Used to query GH Archive in BigQuery.
- `OPENAI_API_KEY`: Required only when running the OpenAI-based labeling scripts.

## Typical Workflow

### 1. Collect AI-reference PRs

```bash
python collect_ai_reference_github.py \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --limit-comments 2000 \
  --output-dir data_ai_refs
```

### 2. Collect the control group

```bash
python collect_control_github.py \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --limit-prs 500 \
  --output-dir data_control_refs
```

### 3. Compare AI-reference and control datasets

```bash
python compare_ai_vs_control.py \
  --ai-dir data_ai_refs \
  --control-dir data_control_refs \
  --output comparison_ai_vs_control.json
```

### 4. Analyze AI-reference patterns

```bash
python analyze_ai_reference_patterns.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
```

### 5. Build LLM labeling inputs

```bash
python build_llm_labeling_inputs.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
```

### 6. Label mention functions with OpenAI

```bash
python run_openai_function_labeling.py \
  --input-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --model gpt-5-mini
```

### 7. Summarize labeling results

```bash
python analyze_llm_labeled_functions.py \
  --labels-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --base-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-dir analysis_ai_refs
```

## Included Outputs

The repository already includes collected datasets and analysis outputs.

- AI-reference dataset: 418 PRs, 292 repositories, 7,265 comments, and 966 reviews
- Control dataset: 376 PRs, 292 repositories, 5,032 comments, and 516 reviews
- AI-reference PR merged rate: 77.51%
- Control PR merged rate: 50.27%
- AI mentions identified in the detailed pattern analysis: 4,034
- Human-authored mention labeling sample: 925 rows

## Example Findings

Based on the outputs currently included in this repository:

- Most AI mentions appear in `issue_comment` threads (86.59%).
- More than half of all AI mentions appear early in the PR lifecycle (51.96%).
- In the LLM-labeled function analysis, `Suggestion` is the dominant category (79.89%).
- AI mention count is strongly correlated with total comment count (`r = 0.857`).
- In a 100-row uptake coding sample, `positive_uptake` accounts for 62% and `corrective_critique` for 33%.

These results should be interpreted as exploratory descriptive findings rather than causal claims.

## Notes

- The `papers/` directory contains background literature used for framing the project.
- Some analysis files include pilot annotations, manually coded samples, and intermediate outputs.
- The repository includes generated CSV and JSON artifacts so the analysis can be inspected without rerunning the full pipeline.

## Suggested GitHub Description

Research pipeline for collecting AI references in GitHub PR discussions and analyzing collaboration patterns, functions, and uptake against a control group.
