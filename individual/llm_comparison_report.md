# Individual Report - LLM Test Case Comparison

## Selected Rules

I selected five rules from 21 CFR 117.130:

1. REQ-117.130-001A - Conduct hazard analysis
2. REQ-117.130-001F - Hazard analysis must be written
3. REQ-117.130-002A - Biological hazards
4. REQ-117.130-002B - Chemical hazards
5. REQ-117.130-003A - Evaluate identified hazards

## Method

I generated test cases for the selected rules using two model settings: Mistral and quantized Mistral. For each model output, I checked coverage, correctness, and completeness. Coverage means the model produced at least one test case for each selected requirement. Correctness means the test case description actually matched the CFR requirement. Completeness means the required fields were present: `test_case_id`, `requirement_id`, `description`, `input_data`, and `expected_output`.

## Coverage Comparison

Both models covered all five selected rules. Mistral produced one test case for each requirement, and quantized Mistral also produced one test case for each requirement. Because every selected rule had a matching test case from both models, both models had complete coverage for this small set.

## Correctness Comparison

Mistral produced slightly more detailed descriptions, so it was easier to see how the generated test case connected to the requirement. Quantized Mistral still produced correct cases, but the wording was more compact. The quantized model did not lose the main meaning of the requirements, but some descriptions were less specific and would need closer human review before being used in a real regulatory validation setting.

## Completeness Comparison

Both models included all required fields for every test case. Both also included optional `steps` and `notes`. The optional fields were useful because they explained how the tester should check the CFR requirement against a food safety plan or generated requirements file.

## Summary Table

| Requirement ID | Mistral Coverage | Quantized Coverage | Correctness Notes | Completeness Notes |
|---|---:|---:|---|---|
| REQ-117.130-001A | Yes | Yes | Both matched hazard analysis requirement | All required fields present |
| REQ-117.130-001F | Yes | Yes | Both matched written hazard analysis requirement | All required fields present |
| REQ-117.130-002A | Yes | Yes | Both matched biological hazard requirement | All required fields present |
| REQ-117.130-002B | Yes | Yes | Both matched chemical hazard requirement | All required fields present |
| REQ-117.130-003A | Yes | Yes | Both matched hazard evaluation requirement | All required fields present |

## Conclusion

Overall, both Mistral and quantized Mistral were able to generate usable test cases for the selected CFR rules. Mistral gave more detailed and readable outputs, while quantized Mistral gave shorter outputs that were still mostly correct. For this assignment, the quantized version was acceptable because it preserved coverage and required fields, but I would still prefer the regular Mistral output when the wording needs to be clearer for a regulatory report.
