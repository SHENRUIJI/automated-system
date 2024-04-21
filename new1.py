import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def get_subdomain(url):
    """提取URL的子域名部分"""
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    if len(domain_parts) > 2:
        return '.'.join(domain_parts[:-2])  # 获取子域名部分，忽略顶级域名和二级域名
    return ''
#判断给定的URL是否是内部链接
def is_internal_url(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc
#doc, docx, pdf
def check_document_link(url):
    if url.lower().endswith(('.doc', '.docx', '.pdf')):
        return True
    return False
#爬虫函数，根据深度爬取网站
def crawl(url, base_url, depth, max_depth, stats):
    if depth > max_depth:
        return

    print(f"{' ' * depth * 2}Crawling: {url}")
    
    if is_internal_url(url, base_url):
        stats['internal_pages'] += 1  # 增加内部页面计数
    
    stats['pages_visited'] += 1
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            stats['unreachable_links'] += 1
            raise Exception(f"Non-success status code {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            link_url = urljoin(url, link['href'])
            stats['total_links'] += 1

            # 检查并计数特定类型的文档链接
            if check_document_link(link_url):
                stats['document_links'] += 1

            if is_internal_url(link_url, base_url):
                subdomain = get_subdomain(link_url)
                if subdomain:
                    stats['subdomains'].add(subdomain)
                
                if link_url not in stats['visited_urls']:
                    stats['visited_urls'].add(link_url)
                    time.sleep(random.uniform(1, 3))
                    crawl(link_url, base_url, depth + 1, max_depth, stats)
            else:
                stats['external_links_total'] += 1  # 累计外部链接总数
                stats['unique_external_links'].add(link_url)  # 记录唯一外部链接
                print(f"{' ' * (depth + 1) * 2}External link: {link_url}")
    except requests.RequestException as e:
        stats['unreachable_links'] += 1
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        stats['unreachable_links'] += 1
        print(f"Error: {e}")

def main():
    start_url = 'https://spbu.ru/'
    max_depth = 30
    stats = {
        'pages_visited': 0,
        'total_links': 0,
        'visited_urls': set(),
        'subdomains': set(),
        'document_links': 0,  # 初始化文档链接计数器
        'unreachable_links': 0,  # 初始化无法访问链接计数器
        'internal_pages': 0,  # 初始化内部页面计数器
        'external_links_total': 0,  # 初始化外部链接总数
        'unique_external_links': set()  # 初始化唯一外部链接集合
    }
    crawl(start_url, start_url, 0, max_depth, stats)
    print(f"Pages visited: {stats['pages_visited']}")
    print(f"Total links found: {stats['total_links']}")
    print(f"Unique subdomains found: {len(stats['subdomains'])}")
    print(f"Document links (doc/docx/pdf): {stats['document_links']}")
    print(f"Unreachable links: {stats['unreachable_links']}")
    print(f"Internal pages visited: {stats['internal_pages']}")
    print(f"Total external links: {stats['external_links_total']}")
    print(f"Unique external links: {len(stats['unique_external_links'])}")

if __name__ == "__main__":
    main()

