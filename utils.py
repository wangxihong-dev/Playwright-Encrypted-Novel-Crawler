"""
工具函数模块：负责文本清洗、文件操作、日志配置
"""
import os
from bs4 import BeautifulSoup

def clean_text(all_content):
    """
    文本清洗函数：清理HTML标签、过滤空行、格式化文本
    :param all_content: 待清洗的HTML文本
    :return: 格式化后的纯文本
    """
    # 解析HTML，提取纯文本
    soup = BeautifulSoup(all_content, "html.parser")
    pure_text = soup.get_text(separator="\n", strip=False).strip()
    # 过滤空行、每行去重空格
    lines = [line.strip() for line in pure_text.splitlines() if line.strip()]
    return "\n".join(lines)

def init_output_dir():
    """初始化输出目录，不存在则创建"""
    os.makedirs("output", exist_ok=True)

def write_to_file(file_path, content, index):
    """
    写入文件函数：统一处理文件写入，避免重复代码
    :param file_path: 文件路径
    :param content: 待写入文本
    :param index: 章节序号
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f'第{index}章\n{content}\n\n\n')
        return True
    except IOError as e:
        print(f"文件写入失败：{str(e)}")
        return False