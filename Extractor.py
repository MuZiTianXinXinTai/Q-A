import fitz
import os
import os.path as op


def file_extractor(fp, fn):
    doc = fitz.open(f'{fp}/{fn}')
    all_text = ""

    # ----------------------------------------------------每页-----------------------------------------------------------
    i = 1
    for page in doc:
        text = page.get_text()
        # print(f'page_{i}:', text)
        all_text += text + "\t"
        i += 1

    doc.close()

    # ----------------------------------------------------分块-----------------------------------------------------------
    # for page in doc:
    #     blocks = page.get_text("blocks")  # 返回一个元组列表，每个元组是一个文本块
    #     blocks = sorted(blocks, key=lambda x: (x[1], x[0]))  # 先按y坐标排，再按x坐标排
    #     for block in blocks:
    #         text = block[4]  # 第四项是文本内容
    #         all_text += text + "\n"
    #
    # doc.close()
    return all_text


if __name__ == '__main__':
    project_path = os.getcwd()
    file_path = op.join(project_path, './document')
    file_name = '巴西国际刑事司法合作：理论、制度、成效_刘天来.pdf'
    text = file_extractor(fp=file_path, fn=file_name)
    # print(text)


