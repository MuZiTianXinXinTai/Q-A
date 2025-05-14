from openai import OpenAI


def judge_qa_from_text(text_block, qa_pair, model="gpt-3.5-turbo", client=None):
    """
    输入文本块+生成的QA，请GPT判别该回答是否准确且来源于文本。

    Args:
        text_block (str): 原始文本。
        qa_pair (dict): {"question":xxx, "answer":xxx}
        model (str): 使用的大模型名字。
        api_key (str): OpenAI API key。

    Returns:
        dict: {"relevance_score": float (0~1), "gpt_confidence_score": float (0~1)}
    """

    prompt = f"""
    请判定以下问题与答案是否可以在给定的文本中找到对应内容。
    文本：
    {text_block}

    问题：
    {qa_pair['question']}

    答案：
    {qa_pair['answer']}

    请返回两个分数（0到1之间的小数）：
    1. 相关性分数（relevance_score）：答案与文本内容的相关程度。
    2. 准确性分数（gpt_confidence_score）：答案是否忠实于文本内容。
    
    并详细解释一下这两个分数的计算方式（calculate_method）

    格式：
    relevance_score: 数值
    gpt_confidence_score: 数值
    calculate_method: 文本
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    content = response.choices[0].message.content
    try:
        relevance_score = float(content.split('relevance_score:')[1].split('\n')[0].strip())
        gpt_confidence_score = float(content.split('gpt_confidence_score:')[1].split('\n')[0].strip())
        calculate_method = str(content.split('calculate_method:')[1].strip())
    except:
        relevance_score, gpt_confidence_score = 0.0, 0.0
        calculate_method = "解析失败"

    return {"relevance_score": relevance_score,
            "gpt_confidence_score": gpt_confidence_score,
            'calculate_method': calculate_method}


if __name__ == '__main__':
    i_client = OpenAI(api_key="key", base_url="https://openkey.cloud/v1")
    # completion = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     stream=False,
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": "Hello!"}
    #     ]
    # )
    # print(completion.choices[0].message)

    text_1 = "机器学习是什么呢？欸机器学习呀咱们就是说是什么呀，欸就是一种呀，欸使计算机能从数据中呀，进行这么一个学习的呀，啊，技术。"
    text_2 = '两只老虎，两只老虎，跑得快，跑得快。一只没有眼睛，一只没有尾巴，真奇怪，真奇怪。'
    text_chunks = [text_1, text_2]
    qas = [
        {"question": "什么是机器学习？", "answer": "机器学习是一种使计算机能从数据中学习的技术。"},
        {"question": "什么是深度学习？", "answer": "深度学习是机器学习的一个子领域，主要使用神经网络。"}
    ]
    qa_score = []
    for i, chunk in enumerate(text_chunks):
        score = judge_qa_from_text(text_block=chunk, qa_pair=qas[i], client=i_client)
        qa_score.append(score)

    print(qa_score)

