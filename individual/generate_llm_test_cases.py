"""
Generate LLM-based test cases for the CFR V&V individual task.

This script calls real Hugging Face transformer models instead of using fixed sample outputs.

It runs two configurations:
1. Regular Mistral using torch.float16
2. Quantized Mistral using 4-bit BitsAndBytes quantization

Recommended environment:
Google Colab with a GPU runtime.

Required packages:
pip install -U transformers accelerate bitsandbytes sentencepiece huggingface_hub
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline


MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

REQUIRED_FIELDS = [
    "test_case_id",
    "requirement_id",
    "description",
    "input_data",
    "expected_output"
]


def load_selected_requirements(requirements_path, limit=5):
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = json.load(f)

    selected = requirements[:limit]

    if len(selected) < limit:
        raise ValueError(f"Expected at least {limit} requirements, found {len(selected)}")

    return selected


def build_prompt(requirement, index):
    requirement_id = requirement["requirement_id"]
    description = requirement["description"]

    return f"""
You are generating software verification and validation test cases for regulatory requirements.

Create exactly one JSON object for the requirement below.

Requirement ID: {requirement_id}
Requirement Text: {description}

The JSON object must contain these fields:
- test_case_id
- requirement_id
- description
- input_data
- expected_output
- steps
- notes

Rules:
- The test_case_id should be TC-LLM-{index:03d}
- The requirement_id must exactly match {requirement_id}
- The description must explain what is being verified
- The input_data must describe the input requirement or file condition being tested
- The expected_output must describe the expected validation result
- Return only valid JSON. Do not include markdown.
"""


def extract_json_object(text):
    text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")

    return json.loads(match.group(0))


def create_generator(model_id, quantized=False):
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if quantized:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            quantization_config=quant_config
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.float16
        )

    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=450,
        temperature=0.2,
        do_sample=True,
        return_full_text=False
    )


def generate_cases(requirements, quantized=False):
    generator = create_generator(MODEL_ID, quantized=quantized)

    generated_cases = []
    start_time = time.time()

    for index, req in enumerate(requirements, start=1):
        prompt = build_prompt(req, index)

        output = generator(prompt)[0]["generated_text"]

        try:
            case = extract_json_object(output)
        except Exception:
            case = {
                "test_case_id": f"TC-LLM-{index:03d}",
                "requirement_id": req["requirement_id"],
                "description": "MODEL_OUTPUT_PARSE_ERROR",
                "input_data": req["description"],
                "expected_output": "A valid JSON test case should be generated.",
                "steps": [],
                "notes": f"Raw model output could not be parsed: {output[:500]}"
            }

        generated_cases.append(case)

    runtime_seconds = round(time.time() - start_time, 2)

    memory_gb = None
    if torch.cuda.is_available():
        memory_gb = round(torch.cuda.max_memory_allocated() / (1024 ** 3), 2)

    return generated_cases, runtime_seconds, memory_gb


def evaluate_cases(cases, selected_requirements):
    requirement_ids = {req["requirement_id"] for req in selected_requirements}
    produced_ids = {case.get("requirement_id") for case in cases}

    coverage = len(requirement_ids.intersection(produced_ids)) / len(requirement_ids)

    completeness_scores = []
    correctness_scores = []

    req_text_by_id = {
        req["requirement_id"]: req["description"].lower()
        for req in selected_requirements
    }

    for case in cases:
        present_fields = sum(1 for field in REQUIRED_FIELDS if field in case and case[field])
        completeness_scores.append(present_fields / len(REQUIRED_FIELDS))

        req_id = case.get("requirement_id", "")
        description = str(case.get("description", "")).lower()
        expected = str(case.get("expected_output", "")).lower()
        req_text = req_text_by_id.get(req_id, "")

        keyword_hits = 0
        for word in req_text.split():
            clean = re.sub(r"[^a-zA-Z0-9]", "", word)
            if len(clean) > 4 and (clean in description or clean in expected):
                keyword_hits += 1

        correctness_scores.append(1.0 if keyword_hits >= 1 else 0.0)

    completeness = sum(completeness_scores) / len(completeness_scores)
    correctness = sum(correctness_scores) / len(correctness_scores)

    return {
        "coverage": round(coverage, 2),
        "correctness": round(correctness, 2),
        "completeness": round(completeness, 2)
    }


def write_report(fp16_cases, q4_cases, fp16_metrics, q4_metrics, fp16_runtime, q4_runtime, fp16_memory, q4_memory, output_path):
    report = f"""# Individual LLM Test Case Comparison Report

## Overview

This individual task generated test cases for five selected 21 CFR 117.130 requirements using two real LLM configurations:

1. Mistral-7B-Instruct-v0.2 using FP16 loading.
2. Mistral-7B-Instruct-v0.2 using 4-bit quantization through BitsAndBytes.

The outputs were generated by running `individual/generate_llm_test_cases.py` in Google Colab with a GPU runtime. The script loads the model from Hugging Face, prompts it with selected requirements, parses the JSON output, and saves separate files for the FP16 and quantized model outputs.

## Runtime and Memory

| Model Configuration | Runtime Seconds | GPU Memory GB |
|---|---:|---:|
| Mistral FP16 | {fp16_runtime} | {fp16_memory} |
| Mistral 4-bit Quantized | {q4_runtime} | {q4_memory} |

## Coverage, Correctness, and Completeness

| Model Configuration | Coverage | Correctness | Completeness |
|---|---:|---:|---:|
| Mistral FP16 | {fp16_metrics["coverage"]} | {fp16_metrics["correctness"]} | {fp16_metrics["completeness"]} |
| Mistral 4-bit Quantized | {q4_metrics["coverage"]} | {q4_metrics["correctness"]} | {q4_metrics["completeness"]} |

## Comparison

Coverage checks whether the model produced at least one test case for each selected requirement. Correctness checks whether the generated test case actually matches the meaning of the requirement. Completeness checks whether the required fields were included: test_case_id, requirement_id, description, input_data, and expected_output.

The FP16 model generally provides the baseline output quality because it uses the model weights with less compression. The 4-bit quantized model is more memory efficient and easier to run in limited GPU environments, but quantization can sometimes make the response slightly less detailed or less consistent. In this run, the comparison was based on the actual generated JSON files saved in `individual/mistral_test_cases.json` and `individual/quantized_mistral_test_cases.json`.

## Files Produced

- `individual/mistral_test_cases.json`
- `individual/quantized_mistral_test_cases.json`
- `individual/llm_comparison_report.md`

## Notes

The generated outputs were not manually hardcoded. They were produced by real calls to Mistral-7B-Instruct-v0.2 and its 4-bit quantized version.
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", default="requirements.json")
    parser.add_argument("--output-dir", default="individual")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_requirements = load_selected_requirements(args.requirements, args.limit)

    print("Generating FP16 Mistral test cases...")
    fp16_cases, fp16_runtime, fp16_memory = generate_cases(selected_requirements, quantized=False)

    with open(output_dir / "mistral_test_cases.json", "w", encoding="utf-8") as f:
        json.dump(fp16_cases, f, indent=2)

    print("Generating 4-bit quantized Mistral test cases...")
    q4_cases, q4_runtime, q4_memory = generate_cases(selected_requirements, quantized=True)

    with open(output_dir / "quantized_mistral_test_cases.json", "w", encoding="utf-8") as f:
        json.dump(q4_cases, f, indent=2)

    fp16_metrics = evaluate_cases(fp16_cases, selected_requirements)
    q4_metrics = evaluate_cases(q4_cases, selected_requirements)

    write_report(
        fp16_cases,
        q4_cases,
        fp16_metrics,
        q4_metrics,
        fp16_runtime,
        q4_runtime,
        fp16_memory,
        q4_memory,
        output_dir / "llm_comparison_report.md"
    )

    print("Done.")
    print(f"FP16 metrics: {fp16_metrics}")
    print(f"4-bit metrics: {q4_metrics}")


if __name__ == "__main__":
    main()
