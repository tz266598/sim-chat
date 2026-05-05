"""
数据清洗脚本
去除网页残留、规范化Markdown格式
"""
import os
import re
from pathlib import Path

def clean_markdown(text: str) -> str:
    """清洗Markdown文本"""
    # 去除URL链接
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 去除发布时间标签
    text = re.sub(r'发布时间[：:]\s*\d{4}[年-]\d{1,2}[月-]\d{1,2}[日]?', '', text)
    text = re.sub(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', '', text)
    
    # 去除多余空白字符
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行变成两个
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格变成一个
    
    # 去除行首行尾空白
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    return text.strip()

def clean_directory(input_dir: str, output_dir: str):
    """清洗整个目录的Markdown文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for md_file in input_path.glob("*.md"):
        print(f"清洗文件: {md_file.name}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content = clean_markdown(content)
        
        output_file = output_path / md_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
    
    print(f"清洗完成！共处理 {len(list(input_path.glob('*.md')))} 个文件")

if __name__ == "__main__":
    # 使用示例
    INPUT_DIR = "./raw_docs"
    OUTPUT_DIR = "./cleaned_docs"
    
    if not os.path.exists(INPUT_DIR):
        print(f"请将原始Markdown文件放在 {INPUT_DIR} 目录中")
    else:
        clean_directory(INPUT_DIR, OUTPUT_DIR)
