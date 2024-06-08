import json
import litellm
import re

input_file = 'output/Berkeley-Function-Calling-Leaderboard-JP/gorilla_openfunctions_v1_test_simple.json'
output_file = 'output/Berkeley-Function-Calling-Leaderboard-JP/gorilla_openfunctions_v1_test_simple_with_return.json'

template = """「{question}」という指示に対して、{name}という関数を使います。
{name}の返り値を予測しなさい。

* {name}は、{description}
* 正確な情報がない場合でも、もっともらしい形式で、架空の値を出力しなさい。
* 返り値は[[と]]で囲ってください。

回答は、以下の形式でしてください。
説明:（説明）
返り値: [[返り値]]"""

def extract_bracketed_values(text):
    pattern = r'\[\[(.*?)\]\]'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0]

def gen_expected_return_value(json):
    question = json["question"]
    name = json["function"]["name"]
    description = json["function"]["description"]
    content = template.format(question=question, name=name, description=description)

    response = litellm.completion(
        model="openai/microsoft/Phi-3-medium-4k-instruct",
        api_key="EMPTY",
        api_base="http://localhost:4000/v1",
        messages=[
            {"role": "user", "content": content},
        ],
        max_tokens=1800,
        temperature=0.01,
        frequency_penalty=0,
        presence_penalty=0, # vllm
        top_p=0.99,
        stop='<NL>'
    )

    try:
        if response.choices[0].finish_reason != "stop":
            raise Exception(response.choices[0].finish_reason)

        result = extract_bracketed_values(response.choices[0].message.content.strip())
    except Exception as e:
        print(e)
        print(response)
        result = "FAILED: 期待値作成に失敗しました！"

    return result

def add_key_value_to_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    for i, line in enumerate(lines, 1):
        json_obj = json.loads(line)
        expected_return_value = gen_expected_return_value(json_obj)
        json_obj["expected_return_value"] = expected_return_value
        updated_lines.append(json.dumps(json_obj, ensure_ascii=False))
        print(i)

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in updated_lines:
            file.write(line + '\n')


add_key_value_to_jsonl(input_file, output_file)
