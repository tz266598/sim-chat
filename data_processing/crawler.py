"""
网站爬虫脚本
爬取武汉大学信息管理学院网站内容并生成Markdown文档
"""
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import re

BASE_URL = "https://sim.whu.edu.cn/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": "JSESSIONID=078B0201703D76F9E5A74F9D294D358B",
    "Host": "sim.whu.edu.cn"
}

# 定义要爬取的页面路径
PAGES_TO_CRAWL = [
    {"url": "https://sim.whu.edu.cn/", "filename": "首页"},
    {"url": "https://sim.whu.edu.cn/xygk/xyjs.htm", "filename": "学院简介"},
    {"url": "https://sim.whu.edu.cn/xygk/xndl.htm", "filename": "学科百年"},
    {"url": "https://sim.whu.edu.cn/xygk/xrld.htm", "filename": "现任领导"},
    {"url": "https://sim.whu.edu.cn/szdw/zzjs.htm", "filename": "专职教师"},
    {"url": "https://sim.whu.edu.cn/rcpy/bkjx.htm", "filename": "本科生教学"},
    {"url": "https://sim.whu.edu.cn/rcpy/yjsjx.htm", "filename": "研究生教学"},
    {"url": "https://sim.whu.edu.cn/rcpy/xsgz.htm", "filename": "学生工作"},
    {"url": "https://sim.whu.edu.cn/kxyj/kypt.htm", "filename": "科研平台"},
    {"url": "https://sim.whu.edu.cn/kxyj/yjcg.htm", "filename": "研究成果"},
    {"url": "https://sim.whu.edu.cn/gjhz/hzxm.htm", "filename": "国际合作项目"},
    {"url": "https://sim.whu.edu.cn/shfw/cgzh.htm", "filename": "成果转化"},
    {"url": "https://sim.whu.edu.cn/xxgk/gzzd.htm", "filename": "规章制度"},
]

# 新闻和公告列表页（需要分页）
NEWS_PAGES = [
    {"url": "https://sim.whu.edu.cn/xyxw.htm", "filename": "学院新闻", "category": "新闻"},
    {"url": "https://sim.whu.edu.cn/tzgg.htm", "filename": "通知公告", "category": "公告"},
    {"url": "https://sim.whu.edu.cn/xsxx.htm", "filename": "学术信息", "category": "学术"},
]

def clean_html(html_content):
    """清理HTML内容"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除脚本和样式标签
    for script in soup(["script", "style"]):
        script.decompose()
    
    return soup

def extract_content(soup):
    """提取页面主要内容"""
    content_parts = []
    
    # 尝试提取标题
    title = soup.find('title')
    if title:
        content_parts.append(f"# {title.get_text().strip()}\n")
    
    # 提取主要内容区域
    main_content = soup.find('div', class_='main-content') or \
                   soup.find('div', class_='content') or \
                   soup.find('div', id='content') or \
                   soup.find('article')
    
    if main_content:
        # 提取文本内容
        for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'table']):
            if element.name.startswith('h'):
                level = int(element.name[1])
                content_parts.append(f"{'#' * level} {element.get_text().strip()}\n")
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    content_parts.append(f"{text}\n")
            elif element.name in ['ul', 'ol']:
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    content_parts.append(f"- {li.get_text().strip()}\n")
            elif element.name == 'table':
                content_parts.append("\n| 列1 | 列2 | 列3 |\n|-----|-----|------|\n")
                for row in element.find_all('tr')[:10]:  # 限制表格行数
                    cells = [cell.get_text().strip() for cell in row.find_all(['td', 'th'])]
                    if cells:
                        content_parts.append(f"| {' | '.join(cells[:3])} |\n")
                content_parts.append("\n")
    else:
        # 如果没有找到主要内容区域，提取整个body的文本
        body = soup.find('body')
        if body:
            for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                text = element.get_text().strip()
                if text and len(text) > 10:  # 过滤太短的文本
                    if element.name.startswith('h'):
                        level = int(element.name[1])
                        content_parts.append(f"{'#' * min(level, 4)} {text}\n")
                    else:
                        content_parts.append(f"{text}\n")
    
    return '\n'.join(content_parts)

def extract_news_list(soup, category):
    """提取新闻/公告列表"""
    news_items = []
    
    # 查找新闻列表项
    news_list = soup.find_all('li', class_=re.compile(r'news|list|item')) or \
                soup.find_all('div', class_=re.compile(r'news|list|item'))
    
    if not news_list:
        news_list = soup.find_all('a', href=re.compile(r'info|content|news'))
    
    for item in news_list[:20]:  # 限制数量
        link = item.find('a') or item
        title = link.get_text().strip()
        href = link.get('href', '')
        
        if title and len(title) > 5:
            date = ""
            date_elem = item.find('span', class_=re.compile(r'date|time'))
            if date_elem:
                date = date_elem.get_text().strip()
            
            news_items.append({
                "title": title,
                "url": urljoin(BASE_URL, href) if href else "",
                "date": date
            })
    
    return news_items

def fetch_page(url, filename):
    """获取单个页面内容"""
    print(f"正在爬取: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = clean_html(response.text)
            content = extract_content(soup)
            
            # 添加元数据
            markdown_content = f"""# {filename}

**来源**: {url}
**爬取时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

{content}
"""
            return markdown_content
        else:
            print(f"  ❌ 失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return None

def fetch_news_detail(news_items, category):
    """抓取新闻详情"""
    results = []
    
    for i, item in enumerate(news_items[:5]):  # 只抓取前5条详情
        if item['url']:
            print(f"  正在抓取新闻详情 {i+1}/{min(5, len(news_items))}: {item['title']}")
            
            try:
                response = requests.get(item['url'], headers=HEADERS, timeout=10)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    soup = clean_html(response.text)
                    content = extract_content(soup)
                    
                    markdown_content = f"""# {item['title']}

**日期**: {item['date']}
**分类**: {category}
**来源**: {item['url']}

---

{content}
"""
                    results.append({
                        "filename": f"{category}_{item['title'][:20]}",
                        "content": markdown_content
                    })
                    time.sleep(1)  # 礼貌延迟
                    
            except Exception as e:
                print(f"  ❌ 抓取失败: {str(e)}")
    
    return results

def save_markdown(filename, content, output_dir):
    """保存Markdown文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 清理文件名
    safe_filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filepath = os.path.join(output_dir, f"{safe_filename}.md")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ 已保存: {filepath}")

def main():
    output_dir = os.path.join(os.path.dirname(__file__), "raw_docs")
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("开始爬取武汉大学信息管理学院网站")
    print("=" * 60)
    
    # 1. 爬取主要页面
    print("\n【第一步】爬取主要页面内容...")
    for page in PAGES_TO_CRAWL:
        content = fetch_page(page['url'], page['filename'])
        if content:
            save_markdown(page['filename'], content, output_dir)
        time.sleep(0.5)  # 礼貌延迟
    
    # 2. 爬取新闻和公告列表
    print("\n【第二步】爬取新闻和公告列表...")
    for news_page in NEWS_PAGES:
        print(f"\n爬取{news_page['category']}列表: {news_page['url']}")
        
        try:
            response = requests.get(news_page['url'], headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = clean_html(response.text)
                
                # 保存列表页
                content = extract_content(soup)
                list_content = f"""# {news_page['filename']}

**来源**: {news_page['url']}
**爬取时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**类型**: {news_page['category']}

---

{content}
"""
                save_markdown(news_page['filename'], list_content, output_dir)
                
                # 抓取新闻详情
                news_items = extract_news_list(soup, news_page['category'])
                if news_items:
                    print(f"  找到 {len(news_items)} 条{news_page['category']}")
                    details = fetch_news_detail(news_items, news_page['category'])
                    
                    for detail in details:
                        save_markdown(detail['filename'], detail['content'], output_dir)
                
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ 爬取失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("爬取完成！")
    print(f"文档已保存到: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
