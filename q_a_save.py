import json


def save_qa_pairs_to_json(qa_pairs, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    qas = [
        {"question": "什么是机器学习？", "answer": "机器学习是一种使计算机能从数据中学习的技术。"},
        {"question": "什么是深度学习？", "answer": "深度学习是机器学习的一个子领域，主要使用神经网络。"}
    ]

    save_qa_pairs_to_json(qa_pairs=qas, output_path="qa_pairs_test.json")

