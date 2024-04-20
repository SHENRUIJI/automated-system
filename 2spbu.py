import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urljoin

site = 'https://spbu.ru/'  # 要查询的主域名
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    "Connection": "close"
}

# 读取successful_urls.csv文件以获取URLs
successful_urls = []
with open('successful_urls.csv', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过头部
    for row in reader:
        if row:  # 确保行不为空
            successful_urls.append(row[0])

# 首先添加主域名到列表
main_site = [site]
domains_to_check = main_site.copy()  # 先复制一份，避免影响d1
domains_to_check.extend(successful_urls)

link_count = {}  # 用于存储每个URL的链接数
actual_links_set = set()  # 用于存储所有不重复的链接
document_links_set = set()  # 用于存储所有doc, docx, pdf文件的不重复链接
external_links_set = set()  # 用于存储所有不重复的外部链接
total_external_links = 0  # 初始化外部链接总数
internal_pages_set = set()  # 存储内部页面链接
dead_links = 0  # 记录空闲页面数

# 获取主域名的netloc部分
main_netloc = urlparse(site).netloc

# 遍历所有域名，访问并计算链接数量
total_links = 0  # 初始化链接总数为零
for url in domains_to_check:
    try:
        response = requests.get(url, headers=headers, timeout=5)  # 尝试连接，设置超时时间
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            num_links = len(links)
            link_count[url] = num_links  # 计数页面中的链接并存储
            total_links += num_links  # 累加到总链接数
            # 将所有链接添加到集合中以自动去重
            for link in links:
                href = link.get('href')
                if href:
                    parsed_href = urlparse(href)
                    href_netloc = parsed_href.netloc
                    actual_links_set.add(href)
                    if href.endswith('.doc') or href.endswith('.docx') or href.endswith('.pdf'):
                        document_links_set.add(href)
                    if href_netloc and href_netloc != main_netloc:
                        external_links_set.add(href)
                        total_external_links += 1
                    if href_netloc == main_netloc or not href_netloc:
                        internal_pages_set.add(urljoin(url, href))
            print(f"已成功收集 {url} 的链接数: {num_links}")
    except Exception as e:
        print(f"连接 {url} 失败: {e}")

# 检查内部页面链接的有效性
for url in internal_pages_set:
    try:
        response = requests.head(url, headers=headers, timeout=5)
        if response.status_code != 200:
            dead_links += 1
    except requests.RequestException:
        dead_links += 1

# 打印所有域名的链接数及总链接数
print("每个URL的链接数:")
for url, count in link_count.items():
    print(f"{url}: {count}")

with open('successful_urls.csv', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过头部
    data=list(reader)

print(f"查询的主域名 Основное доменное имя: {site}")
print(f"所有域名的链接总数 всех ссылок: {total_links}")
print(f"内部子域数 количество внутренних поддоменов ':{len(data)}")
print(f"内部页面总数 количество внутренних страниц: {len(internal_pages_set)}")
print(f"空闲页面数 количество неработающих страниц: {dead_links}")
print(f"所有.doc, .docx, 和 .pdf 文件的唯一链接数量 количество уникальных ссылок на файлы doc/docx/pdf: {len(document_links_set)}")
print(f"外部资源链接总数 общее количество ссылок на внешние ресурсы: {total_external_links}")
print(f"唯一外部资源数 количество уникальных внешних ресурсов: {len(external_links_set)}")