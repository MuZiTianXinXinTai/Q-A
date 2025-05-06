import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv
import os
import os.path as op
from Extractor import file_extractor
from q_a_save import save_qa_pairs_to_json
import re
from openai import OpenAI


def split_text(text: str, max_chunk_size: int = 10000) -> List[str]:
    """ 将长文本按字符数切分为小段 """
    # article = text.split('\t')  # 按自然换行先分段
    article = re.split(r'Article \d+\.', text)
    chunks = []
    current_chunk = ""

    i = 1
    for para in article:
        if len(para.strip()) == 0:
            continue  # 跳过空段
        if len(current_chunk) + len(para) <= max_chunk_size:
            current_chunk += para + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + " "
        # print(f'para_{i}:', para)
        i += 1
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def generate_qa_pair(text_chunk: str, model_client) -> Dict[str, str]:
    """ 给定一个文本块，生成一对 Q&A """
    prompt = f"""
    请根据以下内容生成一对问答：

    内容：
    {text_chunk}

    要求：
    - 问题要具体且可回答。
    - 答案要准确简洁。
    - 格式要求：
    问题：xxx
    答案：xxx
    """
    # 调用Gemini模型
    # response = model_client.generate_content(prompt)
    # content = response.text

    # 调用openai模型
    response = model_client.chat.completions.create(
        model="gpt-3.5-turbo",  # 或者你自己的模型id
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content

    # 简单解析成Q&A
    lines = content.strip().split('\n')
    question, answer = None, None
    for line in lines:
        if line.startswith('问题：'):
            question = line[3:].strip()
        if line.startswith('答案：'):
            answer = line[3:].strip()

    return {"question": question, "answer": answer}


def batch_generate_qa(text: str, model_client, n_q_a=6) -> List[Dict[str, str]]:
    """ 批量生成Q&A对 """
    chunks = split_text(text)
    qa_pairs = []
    qa_num = 0
    for i, chunk in enumerate(chunks):
        j = n_q_a
        # print(f'chunk_{i}:', chunk)
        if i >= 1:
            while j != 0:
                qa = generate_qa_pair(text_chunk=chunk, model_client=model_client)
                j -= 1
                if qa["question"] and qa["answer"]:
                    qa_pairs.append(qa)
                    # print(f'qa{i}:', qa)
                    qa_num += 1
    print(qa_num)
    return qa_pairs


if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()
    # 你的 Gemini API KEY
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # print(GOOGLE_API_KEY)
    # genai.configure(api_key=GOOGLE_API_KEY)
    genai.configure(api_key=f"{GOOGLE_API_KEY}", transport="rest")

    # 查看models_available
    # for m in genai.list_models():
    #     print(m.name)
    #     print(m.supported_generation_methods)

    # # 定义model（传入 model_client）
    # model = genai.GenerativeModel('gemini-1.5-pro-latest')
    #
    project_path = os.getcwd()
    file_path = op.join(project_path, './document')
    file_name = 'constitution_split.pdf'
    test_text = file_extractor(fp=file_path, fn=file_name)

    txt_split = split_text(text=test_text, max_chunk_size=10)
    i = 1
    for chunk in txt_split:
        print(f'chunk{i}：\n', chunk)
        i += 1
    # print(txt_split)

    # q_a_s = batch_generate_qa(text=test_text, model_client=model)
    #
    # # 存入json文件
    # save_qa_pairs_to_json(qa_pairs=q_a_s, output_path="qa_pairs.json")


