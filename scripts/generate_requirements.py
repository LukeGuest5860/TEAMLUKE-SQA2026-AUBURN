import argparse
import json
import re
from pathlib import Path
from forensic_logger import get_logger

logger = get_logger('generate_requirements')

PARENT_RE = re.compile(r'^## \(([a-z])\)\s*(.*?)\s*→\s*(REQ-[\d.]+-\d+)', re.I)
MAIN_CHILD_RE = re.compile(r'^- \((\d+)\)\s*(.*?)\s*→\s*([A-Z])$')
SUB_CHILD_RE = re.compile(r'^\s*- (?:\(([ivx]+)\)\s*)?(.*?)\s*→\s*([A-Z]\d*|[A-Z])$', re.I)


def clean_text(text):
    text = re.sub(r':$', '', text.strip())
    return text


def parse_markdown(path, source):
    requirements = []
    parents = {}
    current_parent = None
    seen = set()
    skipped = 0

    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()
        parent_match = PARENT_RE.match(line)
        if parent_match:
            current_parent = parent_match.group(3)
            parents[current_parent] = []
            logger.info('parent_detected | parent=%s | title=%s', current_parent, parent_match.group(2))
            continue

        if not current_parent or not line.lstrip().startswith('-'):
            continue

        child_match = MAIN_CHILD_RE.match(line.strip()) or SUB_CHILD_RE.match(line)
        if not child_match:
            skipped += 1
            logger.info('requirement_skipped | reason=no_rule_match | line=%s', line.strip())
            continue

        description = clean_text(child_match.group(2))
        letter = child_match.group(3).upper()
        requirement_id = f'{current_parent}{letter}'

        if requirement_id in seen:
            logger.info("requirement_skipped | reason=duplicate_child_letter | requirement_id=%s | line=%s", requirement_id, line.strip())
            skipped += 1
            continue
        seen.add(requirement_id)

        if letter not in parents[current_parent]:
            parents[current_parent].append(letter)

        requirements.append({
            'requirement_id': requirement_id,
            'description': description,
            'source': source,
            'parent': current_parent
        })
        logger.info('requirement_extracted | requirement_id=%s | parent=%s', requirement_id, current_parent)

    logger.info('parse_complete | requirements=%s | parents=%s | skipped=%s', len(requirements), len(parents), skipped)
    return requirements, parents


def main():
    parser = argparse.ArgumentParser(description='Parse CFR markdown into atomic requirement JSON files.')
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-c', '--citation', default='21 CFR 117.130')
    parser.add_argument('-s', '--structure-output', default='expected_structure.json')
    parser.add_argument('-n', '--limit', type=int, default=10)
    args = parser.parse_args()

    requirements, structure = parse_markdown(args.input, args.citation)
    selected = requirements[:args.limit]
    selected_ids = {item['requirement_id'] for item in selected}
    selected_structure = {}
    for parent, letters in structure.items():
        chosen = [letter for letter in letters if f'{parent}{letter}' in selected_ids]
        if chosen:
            selected_structure[parent] = chosen

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(selected, indent=2), encoding='utf-8')
    Path(args.structure_output).write_text(json.dumps(selected_structure, indent=2), encoding='utf-8')
    logger.info('output_written | requirements_file=%s | structure_file=%s', args.output, args.structure_output)


if __name__ == '__main__':
    main()
