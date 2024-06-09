import random
import json

input_file = 'output/Berkeley-Function-Calling-Leaderboard-JP/gorilla_openfunctions_v1_test_simple_with_return.json'
output_file = 'output/Berkeley-Function-Calling-Leaderboard-JP/gorilla_openfunctions_v1_test_simple_with_return_200.json'

def extract_random_lines_from_jsonl(file_path, num_lines):
    with open(file_path, 'r', encoding='utf-8') as file:
        all_lines = file.readlines()

    lines = []
    for line in all_lines:
        json_obj = json.loads(line)
        if not json_obj["expected_return_value"].startswith("FAILED: "):
            lines.append(json.dumps(json_obj, ensure_ascii=False))

    if num_lines > len(lines):
        raise ValueError("num_lines is greater than the total number of lines in the file.")

    random_lines = random.sample(lines, num_lines)
    return [line.strip() for line in random_lines]

num_lines = 200
extracted_lines = extract_random_lines_from_jsonl(input_file, num_lines)

with open(output_file, 'w', encoding='utf-8') as file:
    for line in extracted_lines:
        file.write(line + '\n')
