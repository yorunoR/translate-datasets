import json
import litellm
import os
import re

input_file = 'output/AIW-JP/prompts.json'
output_file = 'output/AIW-JP/prompts_remove_format.json'

template = """文章に「以下」という語句が有った時、語句を含むその文を削除する！
* 「以下」で指定されているものが無く、読む人が理解できません。
* 「兄」もしくは「弟」を「兄弟」に置き換えなさい。brother から翻訳したので「兄」と「弟」を判別できません。
* 「姉」もしくは「妹」を「姉妹」に置き換えなさい。sister から翻訳したので「姉」と「妹」を判別できません。
* それ以外は、そのまま使用してください。文章を変えないでください。
* 回答を続けて書く必要はありません。
* 「以下」を使うな！
* 「次のように」を使うな！
* 「次のような」を使うな！
* 「以下の形式」を使うな！

# 修正前の文章
{prompt}

# 修正後の文章
"""

def gen_expected_return_value(json, temperature=0.01):
    prompt = re.sub(r"「### (答え|Answer):.+。", "", json["prompt"])
    content = template.format(prompt=prompt)

    try:
        response = litellm.completion(
            model="gpt-4o",
            api_key=os.environ["OPENAI_API_KEY"],
            messages=[
                {"role": "system", "content": 'あなたは優れた編集者です。文章に特定の語句が含まれることを禁じます。指示に従い文章を修正してください。'},
                {"role": "user", "content": content},
            ],
            max_tokens=1000,
            temperature=temperature,
            frequency_penalty=0,
            presence_penalty=0, # vllm
            top_p=0.99,
            stop='<NL>'
        )
    except Exception as e:
        print(e)
        return None

    try:
        if response.choices[0].finish_reason != "stop":
            raise Exception(response.choices[0].finish_reason)

        result = response.choices[0].message.content.strip()
        if '以下の' in result:
            print(f"E: {result}")
            result = None
    except Exception as e:
        print(e)
        print(response)
        return None

    return result

def add_key_value_to_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    for i, line in enumerate(lines, 1):
        # if i != 31:
        #     continue
        json_obj = json.loads(line)

        expected_return_value = gen_expected_return_value(json_obj)
        if expected_return_value is None:
            expected_return_value = gen_expected_return_value(json_obj, 0.2)
            if expected_return_value is None:
                expected_return_value = "FAILED: 修正にに失敗しました！"

        json_obj["prompt"] = expected_return_value
        updated_lines.append(json.dumps(json_obj, ensure_ascii=False))
        print(i, expected_return_value)

    with open(output_file, 'w', encoding='utf-8') as file:
        for line in updated_lines:
            file.write(line + '\n')


add_key_value_to_jsonl(input_file, output_file)
