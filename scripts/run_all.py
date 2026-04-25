import subprocess
import sys

commands = [
    [sys.executable, 'scripts/generate_requirements.py', '-i', 'Input CFR File/CFR-117.130.md', '-o', 'requirements.json', '-c', '21 CFR 117.130', '-s', 'expected_structure.json', '-n', '10'],
    [sys.executable, 'scripts/generate_test_cases.py', '-r', 'requirements.json', '-s', 'expected_structure.json', '-o', 'test_cases.json'],
    [sys.executable, 'scripts/validate_outputs.py', '--requirements', 'requirements.json', '--structure', 'expected_structure.json', '--test-cases', 'test_cases.json']
]

for command in commands:
    print('Running:', ' '.join(command))
    subprocess.run(command, check=True)
