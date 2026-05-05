"""
数据分块脚本
基于Markdown标题层级进行智能分块
"""
import re
from typing import List, Tuple
from pathlib import Path

def chunk_markdown_by_headings(text: str, max_chunk_size: int = 500, overlap_size: int = 50) -> List[Tuple[str, str]]:
    """
    基于Markdown标题层级分块
    返回: [(标题, 内容), ...]
    """
    # 匹配Markdown标题
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = text.split('\n')
    
    chunks = []
    current_heading = "概述"
    current_content = []
    
    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            # 保存之前的块
            if current_content:
                content = '\n'.join(current_content).strip()
                if content:
                    chunks.append((current_heading, content))
            
            # 更新当前标题
            current_heading = match.group(2)
            current_content = []
        else:
            current_content.append(line)
    
    # 保存最后一个块
    if current_content:
        content = '\n'.join(current_content).strip()
        if content:
            chunks.append((current_heading, content))
    
    # 如果块太大，进一步分割
    final_chunks = []
    for heading, content in chunks:
        if len(content) > max_chunk_size:
            sub_chunks = split_large_chunk(content, max_chunk_size, overlap_size)
            for i, sub_content in enumerate(sub_chunks):
                sub_heading = f"{heading} (部分{i+1})" if len(sub_chunks) > 1 else heading
                final_chunks.append((sub_heading, sub_content))
        else:
            final_chunks.append((heading, content))
    
    return final_chunks

def split_large_chunk(text: str, max_size: int, overlap: int) -> List[str]:
    """分割大块文本，按段落分割并保持重叠"""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        if current_size + para_size > max_size and current_chunk:
            # 保存当前块
            chunks.append('\n\n'.join(current_chunk))
            
            # 保留重叠部分
            overlap_text = '\n\n'.join(current_chunk[-2:]) if len(current_chunk) >= 2 else current_chunk[-1]
            current_chunk = [overlap_text, para]
            current_size = len(overlap_text) + para_size
        else:
            current_chunk.append(para)
            current_size += para_size
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def process_directory(input_dir: str, output_file: str):
    """处理整个目录的Markdown文件"""
    import json
    
    input_path = Path(input_dir)
    all_chunks = []
    
    for md_file in input_path.glob("*.md"):
        print(f"分块文件: {md_file.name}")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_markdown_by_headings(content)
        
        for i, (heading, chunk_content) in enumerate(chunks):
            all_chunks.append({
                "id": f"{md_file.stem}_{i}",
                "heading": heading,
                "content": chunk_content,
                "source": md_file.name
            })
    
    # 保存分块结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"分块完成！共生成 {len(all_chunks)} 个块，保存到 {output_file}")

if __name__ == "__main__":
    INPUT_DIR = "./cleaned_docs"
    OUTPUT_FILE = "./chunks.json"
    
    process_directory(INPUT_DIR, OUTPUT_FILE)
