import json
import litellm

input_file = 'input/Berkeley-Function-Calling-Leaderboard/gorilla_openfunctions_v1_test_simple.json'
output_file = 'output/Berkeley-Function-Calling-Leaderboard-JP/gorilla_openfunctions_v1_test_simple.json'
key_to_modify = ['question', 'description']


def translate(old_value):
    response = litellm.completion(
        model="openai/aixsatoshi/Honyaku-13b",
        api_key="EMPTY",
        api_base="http://localhost:4000/v1",
        messages=[
            {"role": "user", "content": old_value},
        ],
        max_tokens=1800,
        temperature=0.01,
        frequency_penalty=0,
        presence_penalty=0, # vllm
        top_p=0.99,
        stop='<NL>'
    )
    if response.choices[0].finish_reason != "stop":
        raise Exception(response.choices[0].finish_reason)

    return response.choices[0].message.content.strip()

def modify_nested_key(data, key_to_modify):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in key_to_modify:
                try:
                  data[key] = translate(data[key])
                except Exception as e:
                  print(e)
                  data[key] = "FAILED: 翻訳に失敗しました！"
            else:
                modify_nested_key(value, key_to_modify)
    elif isinstance(data, list):
        for item in data:
            modify_nested_key(item, key_to_modify)

def modify_jsonl(input_file, output_file, key_to_modify):
    modified_lines = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line.strip())
            modify_nested_key(data, key_to_modify)
            modified_lines.append(json.dumps(data, ensure_ascii=False))
            print(i)

    with open(output_file, 'w', encoding='utf-8') as f:
        for line in modified_lines:
            f.write(line + '\n')


modify_jsonl(input_file, output_file, key_to_modify)
