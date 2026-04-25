import argparse
import json
from pathlib import Path
from forensic_logger import get_logger

logger = get_logger('generate_test_cases')
REQUIRED_FIELDS = ['test_case_id', 'requirement_id', 'description', 'input_data', 'expected_output']


def load_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def build_test_case(index, req):
    rid = req['requirement_id']
    desc = req['description']
    return {
        'test_case_id': f'TC-{index:03d}',
        'requirement_id': rid,
        'description': f'Verify that the CFR analysis includes: {desc}.',
        'input_data': {
            'requirement_id': rid,
            'requirement_text': desc,
            'source': req.get('source', '21 CFR 117.130')
        },
        'expected_output': {
            'present': True,
            'parent': req.get('parent'),
            'atomic': True,
            'matches_requirement': desc
        },
        'steps': [
            'Load requirements.json.',
            f'Find requirement_id {rid}.',
            'Check that the description and parent mapping match the CFR rule.',
            'Confirm that the rule can be validated as one atomic requirement.'
        ],
        'notes': 'Generated minimal V&V test case for selected CFR atomic rule.'
    }


def main():
    parser = argparse.ArgumentParser(description='Generate minimal test cases from requirements and expected structure.')
    parser.add_argument('-r', '--requirements', required=True)
    parser.add_argument('-s', '--structure', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()

    requirements = load_json(args.requirements)
    structure = load_json(args.structure)
    allowed = {f'{parent}{letter}' for parent, letters in structure.items() for letter in letters}

    cases = []
    for req in requirements:
        if req['requirement_id'] in allowed:
            cases.append(build_test_case(len(cases) + 1, req))
            logger.info('test_case_created | test_case_id=%s | requirement_id=%s', cases[-1]['test_case_id'], req['requirement_id'])
        else:
            logger.info('requirement_skipped | requirement_id=%s | reason=not_in_expected_structure', req['requirement_id'])

    Path(args.output).write_text(json.dumps(cases, indent=2), encoding='utf-8')
    logger.info('test_generation_complete | count=%s | output=%s', len(cases), args.output)


if __name__ == '__main__':
    main()
