# AI References in GitHub PR Discussions

GitHub Pull Request 대화에서 `ChatGPT`, `Copilot`, `Claude`, `LLM` 같은 AI 도구 언급이 어떻게 등장하고, 협업 과정에서 어떻게 수용되거나 비판되는지 분석하는 연구용 저장소입니다.

이 프로젝트는 크게 네 가지 흐름으로 구성됩니다.

1. GH Archive(BigQuery)에서 AI 언급이 포함된 PR 후보를 수집합니다.
2. GitHub REST API로 PR, 댓글, 리뷰 메타데이터를 보강합니다.
3. AI 언급 PR과 non-AI control PR을 비교합니다.
4. AI 언급의 사회적 기능과 수용 양상을 추가 분석하거나 LLM으로 라벨링합니다.

## Overview

- `collect_ai_reference_github.py`: AI 키워드가 포함된 PR 대화 수집
- `collect_control_github.py`: AI 언급이 없는 control PR 수집
- `compare_ai_vs_control.py`: 두 데이터셋의 요약 지표 비교
- `analyze_ai_reference_patterns.py`: 역할, 시점, 위치, 강도, 복잡도 분석
- `build_llm_labeling_inputs.py`: LLM 라벨링용 입력 CSV 생성
- `run_openai_function_labeling.py`: OpenAI API로 AI 언급 기능 라벨링
- `run_ollama_function_labeling.py`: Ollama 기반 라벨링
- `analyze_llm_labeled_functions.py`: 라벨링 결과 집계
- `build_invocation_*`, `analyze_invocation_uptake.py`: AI 제안이 실제로 수용되는지 후속 분석
- `build_suggestion_refinement_inputs.py`, `analyze_suggestion_refinement.py`: AI 제안 정교화 관련 분석

## Repository Structure

```text
.
├── data_ai_refs/          # AI-reference PR 수집 결과
├── data_control_refs/     # Control group 수집 결과
├── analysis_ai_refs/      # 추가 분석 및 라벨링 결과
├── papers/                # 관련 참고 문헌 PDF
├── requirements.txt
└── *.py                   # 수집, 분석, 라벨링 스크립트
```

## Requirements

- Python 3.10+
- BigQuery access
- GitHub personal access token
- OpenAI API key 또는 로컬 Ollama 환경(선택)

패키지 설치:

```bash
pip install -r requirements.txt
```

## Environment Variables

다음 환경 변수가 필요합니다.

```bash
export GITHUB_TOKEN=your_github_token
export GOOGLE_CLOUD_PROJECT=your_gcp_project_id
export OPENAI_API_KEY=your_openai_api_key
```

- `GITHUB_TOKEN`: GitHub REST API 메타데이터 수집용
- `GOOGLE_CLOUD_PROJECT`: GH Archive BigQuery 조회용
- `OPENAI_API_KEY`: OpenAI 기반 라벨링 실행 시 필요

## Typical Workflow

### 1. AI-reference PR 수집

```bash
python collect_ai_reference_github.py \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --limit-comments 2000 \
  --output-dir data_ai_refs
```

### 2. Control group 수집

```bash
python collect_control_github.py \
  --start 2025-01-01 \
  --end 2025-12-31 \
  --limit-prs 500 \
  --output-dir data_control_refs
```

### 3. AI vs Control 비교

```bash
python compare_ai_vs_control.py \
  --ai-dir data_ai_refs \
  --control-dir data_control_refs \
  --output comparison_ai_vs_control.json
```

### 4. AI-reference 패턴 분석

```bash
python analyze_ai_reference_patterns.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
```

### 5. LLM 라벨링 입력 생성

```bash
python build_llm_labeling_inputs.py \
  --input-dir data_ai_refs \
  --output-dir analysis_ai_refs
```

### 6. OpenAI로 기능 라벨링

```bash
python run_openai_function_labeling.py \
  --input-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --model gpt-5-mini
```

### 7. 라벨링 결과 집계

```bash
python analyze_llm_labeled_functions.py \
  --labels-csv analysis_ai_refs/llm_labeling_human_mentions_labeled.csv \
  --base-csv analysis_ai_refs/llm_labeling_human_mentions.csv \
  --output-dir analysis_ai_refs
```

## Included Outputs

현재 저장소에는 이미 일부 수집 및 분석 결과가 포함되어 있습니다.

- AI-reference dataset: 418 PRs, 292 repos, 7,265 comments, 966 reviews
- Control dataset: 376 PRs, 292 repos, 5,032 comments, 516 reviews
- AI-reference PR merged rate: 77.51%
- Control PR merged rate: 50.27%
- AI mentions identified in detailed pattern analysis: 4,034
- Human-authored mention labeling sample: 925 rows

## Example Findings

현재 포함된 결과 기준으로 보면:

- AI 언급은 `issue_comment`에서 가장 많이 나타났습니다(86.59%).
- AI 언급의 절반 이상이 PR lifecycle의 초기 단계에서 등장했습니다(51.96%).
- LLM 기반 기능 라벨링에서는 `Suggestion`이 가장 큰 비중을 차지했습니다(79.89%).
- AI mention count와 total comment count 사이에는 높은 상관이 관찰되었습니다(`r = 0.857`).
- 수용 분석 샘플 100건에서는 `positive_uptake`가 62%, `corrective_critique`가 33%였습니다.

이 수치는 탐색적 분석 결과이며, 인과관계로 해석하기보다 PR 대화 내 AI 언급의 패턴을 보여주는 기술 통계로 보는 것이 적절합니다.

## Notes

- `__pycache__/`와 중간 산출물 CSV/JSON은 필요 시 `.gitignore`로 정리하는 것을 권장합니다.
- `papers/` 폴더에는 연구 배경 정리에 활용한 참고 문헌 PDF가 들어 있습니다.
- 일부 분석 파일에는 수동 코딩 샘플이나 파일럿 결과가 함께 포함되어 있습니다.

## Suggested GitHub Description

GitHub PR discussions에서 AI tool references를 수집하고, control group과 비교해 협업 패턴·기능·수용 양상을 분석하는 research pipeline.
