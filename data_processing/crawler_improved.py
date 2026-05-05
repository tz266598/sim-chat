"""
改进版网站爬虫 - 自动发现并爬取所有页面
"""
import requests
from bs4 import BeautifulSoup
import time
import os
import re
from urllib.parse import urljoin, urlparse

BASE_URL = "https://sim.whu.edu.cn/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Cookie": "JSESSIONID=078B0201703D76F9E5A74F9D294D358B",
    "Host": "sim.whu.edu.cn"
}

def clean_html(html_content):
    """清理HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    return soup

def extract_text_content(soup):
    """提取有意义的文本内容"""
    text_parts = []
    
    # 提取标题
    title = soup.find('title')
    if title:
        text_parts.append(f"# {title.get_text().strip()}\n")
    
    # 提取主要内容
    for tag in ['h1', 'h2', 'h3', 'h4', 'p', 'li']:
        for element in soup.find_all(tag):
            text = element.get_text().strip()
            if text and len(text) > 5:
                if tag.startswith('h'):
                    level = int(tag[1])
                    text_parts.append(f"\n{'#' * level} {text}\n")
                elif tag == 'p':
                    text_parts.append(f"\n{text}\n")
                elif tag == 'li':
                    text_parts.append(f"- {text}")
    
    return '\n'.join(text_parts)

def get_all_links_from_home():
    """从首页获取所有链接"""
    print("正在获取首页所有链接...")
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()
            
            # 提取所有链接
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(BASE_URL, href)
                
                # 只保留同域名的链接
                if urlparse(full_url).netloc == urlparse(BASE_URL).netloc:
                    # 过滤掉一些无用的链接
                    if not any(ext in href for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip']):
                        if 'javascript' not in href and href != '#':
                            links.add(full_url)
            
            print(f"找到 {len(links)} 个有效链接")
            return list(links)
        else:
            print(f"首页访问失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"获取链接失败: {e}")
        return []

def crawl_page(url, index):
    """爬取单个页面"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = clean_html(response.text)
            content = extract_text_content(soup)
            
            if len(content) > 100:  # 只保存内容有意义的页面
                return {
                    'url': url,
                    'content': content,
                    'title': soup.find('title').get_text().strip() if soup.find('title') else f'page_{index}'
                }
        return None
        
    except Exception as e:
        print(f"  爬取失败 {url}: {e}")
        return None

def save_markdown(filename, content, output_dir):
    """保存Markdown文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 清理文件名
    safe_filename = re.sub(r'[^\w\s-]', '', filename).strip()[:50]
    filepath = os.path.join(output_dir, f"{safe_filename}.md")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "raw_docs")
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("开始爬取武汉大学信息管理学院网站 - 自动发现模式")
    print("=" * 70)
    
    # 获取所有链接
    links = get_all_links_from_home()
    
    if not links:
        print("未找到任何链接，程序退出")
        return
    
    # 爬取每个链接
    print(f"\n开始爬取 {len(links)} 个页面...\n")
    success_count = 0
    
    for i, url in enumerate(links[:30]):  # 限制最多爬取30个页面
        print(f"[{i+1}/{min(30, len(links))}] 正在爬取: {url}")
        
        result = crawl_page(url, i)
        
        if result:
            filepath = save_markdown(result['title'], result['content'], output_dir)
            print(f"  ✅ 已保存: {os.path.basename(filepath)}")
            success_count += 1
        else:
            print(f"  ❌ 跳过（内容不足或爬取失败）")
        
        time.sleep(0.5)  # 礼貌延迟
    
    print("\n" + "=" * 70)
    print(f"爬取完成！成功保存 {success_count} 个文档")
    print(f"文档位置: {output_dir}")
    print("=" * 70)

if __name__ == "__main__":
    main()
