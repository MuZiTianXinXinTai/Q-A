import time
import os
import os.path as op
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv
from Extractor import file_extractor
from q_a_save import save_qa_pairs_to_json
import Generator
from Generator import split_text, generate_qa_pair
from Evaluator import judge_qa_from_text
from openai import OpenAI

# -----------------------------------------------GEMINI配置-------------------------------------------------------------
load_dotenv()
# 你的 Gemini API KEY
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=f"{GOOGLE_API_KEY}", transport="rest")
model = genai.GenerativeModel('gemini-2.0-flash-001')

# --------------------------------------------------OpenAI配置-------------------------------------------------------
evaluate_client = OpenAI(api_key="key_1", base_url="https://openkey.cloud/v1")
generate_client = OpenAI(api_key="key_2", base_url="https://openkey.cloud/v1")

# -------------------------------------------------文档路径--------------------------------------------------------------
root_path = os.getcwd()
file_path = op.join(root_path, './document')
file_name = 'constitution_split.pdf'


def main():
    constitution = file_extractor(fp=file_path, fn=file_name)

    articles = split_text(text=constitution, max_chunk_size=100)

    qa_results = []

    for idx, chunk in enumerate(articles):
        if idx >= 1:
            try:
                # 生成qa对
                qa_pair = generate_qa_pair(text_chunk=chunk, model_client=generate_client)
                if qa_pair is None or qa_pair.get('question') is None or qa_pair.get('answer') is None:
                    print(f'pair_{idx}生成失败，跳过。')
                    continue
                else:
                    print(f'pair_{idx} generated')

                # 判别
                evaluation = judge_qa_from_text(chunk, qa_pair, client=evaluate_client)
                print(f'pair_{idx} evaluated')

                result = {
                    # "id": idx + 1,
                    "id": idx,  # 不加一了哈，idx=0的分块没有内容，直接跳过。
                    "question": qa_pair['question'],
                    "answer": qa_pair['answer'],
                    "relevance_score": evaluation['relevance_score'],
                    "gpt_confidence_score": evaluation['gpt_confidence_score'],
                    "calculate_method": evaluation['calculate_method']
                }
                qa_results.append(result)

                # time.sleep(5)

            except Exception as e:
                print(f"第{idx}个块处理失败，错误：{e}")
                continue

    save_qa_pairs_to_json(qa_pairs=qa_results, output_path="qa_results.json")


if __name__ == "__main__":
    main()
