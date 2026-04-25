# Group Report - CFR V&V Project

## Activities Performed

For this project, our group created a GitHub repository for the 21 CFR 117.130 Verification and Validation assignment. We added the CFR markdown input file, Python scripts, generated JSON files, a GitHub Actions workflow, forensic logging, and project reports. The goal was to turn a CFR section into atomic requirements and then verify that the generated outputs were structured correctly.

## Task 0: Project Repo and CI

We created a repo named `TEAMNAME-SQA2026-AUBURN`. The repo includes all input files, scripts, outputs, reports, and a GitHub Actions workflow. The workflow is similar to Assignment 6 because it automatically runs the scripts on push and pull request, then prints and uploads the evidence files.

## Task 1: Extract and Structure Requirements

We used `scripts/generate_requirements.py` to parse `Input CFR File/CFR-117.130.md`. The script detects parent requirements, extracts atomic child rules, ignores repeated parent numbering, and writes the selected 10 rules to `requirements.json`. It also creates `expected_structure.json`, which maps each parent requirement ID to its selected child letters.

The selected requirements are focused on hazard analysis, hazard documentation, identifying known and foreseeable hazards, evaluating hazards, and considering biological, chemical, and physical hazards.

## Task 2: Generate Minimal Test Cases

We wrote `scripts/generate_test_cases.py` to read `requirements.json` and `expected_structure.json`. It creates one test case per selected atomic requirement. Each test case includes a unique ID, requirement ID, description, input data, expected output, steps, and notes.

## Task 3: Verification and Validation

We used `scripts/validate_outputs.py` to check that the generated files are valid. The validator confirms that requirements have the required fields, expected structure references real requirements, test cases have required fields, test case IDs are unique, and every selected expected requirement has a matching test case.

## Task 4: Forensic Integration

We integrated forensic logging through `scripts/forensic_logger.py`. The log records parent detection, extracted requirements, skipped requirements, duplicate child letters, test case creation, validation failures, and validation success. This gives traceable evidence of what happened during script execution and CI.

## What We Learned

This project showed how regulatory text can be broken into smaller atomic rules that are easier to verify. We also learned that the structure of a CFR section matters because parent and child numbering can create repeated labels. The validation script helped catch missing fields and broken mappings before submission. The forensic log was useful because it created evidence showing how each output file was produced and checked.

## Evidence to Screenshot

Screenshots should show:

1. The repo file structure.
2. A successful local run of `python3 scripts/run_all.py`.
3. The generated `logs/forensic.log` file.
4. A successful GitHub Actions build.
5. The uploaded GitHub Actions artifact named `cfr-vv-evidence`.
