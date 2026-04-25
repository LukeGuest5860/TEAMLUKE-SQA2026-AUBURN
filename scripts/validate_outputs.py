import argparse
import json
import sys
from pathlib import Path
from forensic_logger import get_logger

logger = get_logger('validate_outputs')
REQUIRED_CASE_FIELDS = {'test_case_id', 'requirement_id', 'description', 'input_data', 'expected_output'}
REQUIRED_REQ_FIELDS = {'requirement_id', 'description', 'source', 'parent'}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def fail(message):
    logger.error('validation_failed | %s', message)
    print(f'FAIL: {message}')
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Validate CFR V&V generated JSON files.')
    parser.add_argument('--requirements', required=True)
    parser.add_argument('--structure', required=True)
    parser.add_argument('--test-cases', required=True)
    args = parser.parse_args()

    requirements = load_json(args.requirements)
    structure = load_json(args.structure)
    test_cases = load_json(args.test_cases)

    if not requirements:
        fail('requirements.json is empty')
    if not structure:
        fail('expected_structure.json is empty')
    if not test_cases:
        fail('test_cases.json is empty')

    req_ids = set()
    for req in requirements:
        missing = REQUIRED_REQ_FIELDS - set(req.keys())
        if missing:
            fail(f'requirement {req} missing fields {sorted(missing)}')
        req_ids.add(req['requirement_id'])

    expected_ids = {f'{parent}{letter}' for parent, letters in structure.items() for letter in letters}
    missing_expected = expected_ids - req_ids
    if missing_expected:
        fail(f'expected structure references missing requirements {sorted(missing_expected)}')

    case_ids = set()
    for case in test_cases:
        missing = REQUIRED_CASE_FIELDS - set(case.keys())
        if missing:
            fail(f'test case {case.get("test_case_id", "UNKNOWN")} missing fields {sorted(missing)}')
        if case['test_case_id'] in case_ids:
            fail(f'duplicate test case id {case["test_case_id"]}')
        case_ids.add(case['test_case_id'])
        if case['requirement_id'] not in req_ids:
            fail(f'test case references missing requirement {case["requirement_id"]}')

    missing_case_requirements = expected_ids - {case['requirement_id'] for case in test_cases}
    if missing_case_requirements:
        fail(f'expected requirements without test cases {sorted(missing_case_requirements)}')

    logger.info('validation_passed | requirements=%s | expected=%s | test_cases=%s', len(requirements), len(expected_ids), len(test_cases))
    print('PASS: requirements, expected structure, and test cases are valid.')


if __name__ == '__main__':
    main()
