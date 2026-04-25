# CFR_TEST
# Verification & Validation Project - 21 CFR Atomic Rules

Team name: TEAMNAME  
Team members: Luke Guest

This repository completes the CFR V&V project for 21 CFR 117.130. It parses a CFR markdown file into atomic requirements, selects 10 atomic rules, builds the expected parent-to-child structure, generates minimal test cases, validates the outputs, and records forensic logs.

## Repo Structure

```text
Input CFR File/
  CFR-117.130.md
  InputVisualization.md
scripts/
  forensic_logger.py
  generate_requirements.py
  generate_test_cases.py
  validate_outputs.py
  run_all.py
requirements.json
expected_structure.json
test_cases.json
logs/
  forensic.log
reports/
  group_report.md
individual/
  generate_llm_test_cases.py
  mistral_test_cases.json
  quantized_mistral_test_cases.json
  llm_comparison_report.md
.github/workflows/
  vv-ci.yml
```

## How to Run Locally

From the repo root:

```bash
python3 scripts/run_all.py
```

Or run each part separately:

```bash
python3 scripts/generate_requirements.py -i "Input CFR File/CFR-117.130.md" -o requirements.json -c "21 CFR 117.130" -s expected_structure.json -n 10
python3 scripts/generate_test_cases.py -r requirements.json -s expected_structure.json -o test_cases.json
python3 scripts/validate_outputs.py --requirements requirements.json --structure expected_structure.json --test-cases test_cases.json
```

## Forensic Integration

The forensic logger records these events:

1. Parent requirement detected.
2. Atomic requirement extracted.
3. Requirement skipped or duplicate child letter found.
4. Test case created.
5. Validation pass or validation failure.

The log is written to `logs/forensic.log`. GitHub Actions also uploads the JSON files and forensic log as CI artifacts.

## GitHub Actions

The workflow `.github/workflows/vv-ci.yml` runs on every push and pull request. It executes the full pipeline and validates that the generated files are consistent.

## Individual Task

The `individual` folder contains LLM-based test case outputs for 5 selected rules using:

1. Mistral
2. Quantized Mistral

It also includes `llm_comparison_report.md`, which compares coverage, correctness, and completeness.


## Evidence Screenshots

Execution screenshots are included in the `screenshots/` folder. These screenshots show local validation output, forensic logging evidence, and the passing GitHub Actions workflow run.
