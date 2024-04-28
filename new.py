from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urljoin
import time
import logging
from selenium.common.exceptions import TimeoutException
import os

# 设置Chrome Driver路径
chrome_driver_path = "D:\\Chrome\\chromedriver-win64\\chromedriver.exe"  # 更改为你的ChromeDriver路径
service = Service(chrome_driver_path)

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无界面模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 创建WebDriver对象
driver = webdriver.Chrome(service=service, options=chrome_options)

def is_internal_url(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc

def safe_get(url, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            driver.get(url)
            return True
        except TimeoutException:
            logging.warning(f"Timeout when accessing {url}. Retrying ({attempt+1}/{retries})...")
            time.sleep(10)
            attempt += 1
    logging.error(f"Failed to access {url} after {retries} attempts.")
    return False

def setup_logging(base_url):
    """Setup logging to file for each URL."""
    base_url_hostname = urlparse(base_url).hostname or "general"
    log_filename = f'logs/{base_url_hostname}.log'
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def crawl(base_url, limit=1000):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("stats"):
        os.makedirs("stats")

    setup_logging(base_url)

    visited = set()
    queue = [base_url]
    visited.add(base_url)
    pages_visited = 0

    while queue and pages_visited < limit:
        current_url = queue.pop(0)
        if safe_get(current_url):
            time.sleep(1)
            pages_visited += 1
            logging.info(f"Visiting: {current_url}")

            links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a')]
            process_links(links, current_url, base_url, visited, queue, pages_visited)  # 添加 pages_visited 为参数

    driver.quit()

def process_links(links, current_url, base_url, visited, queue, pages_visited):  # 添加 pages_visited 为参数
    internal_pages = 0
    external_links_total = 0
    document_links = 0
    total_links = 0
    subdomains = set()

    for link in links:
        if link and is_internal_url(link, base_url) and link not in visited:
            visited.add(link)
            queue.append(link)
            internal_pages += 1
            if link.lower().endswith(('.doc', '.docx', '.pdf')):
                document_links += 1
        elif link:
            external_links_total += 1
        total_links += 1

    save_stats(current_url, pages_visited, total_links, len(subdomains), document_links, internal_pages, external_links_total)


def save_stats(current_url, pages_visited, total_links, unique_subdomains, document_links, internal_pages, external_links_total):
    """Save statistics to a separate file for each URL."""
    filename = f"stats/{urlparse(current_url).netloc}.txt"
    with open(filename, 'w') as file:
        file.write(f"Pages visited: {pages_visited}\n")
        file.write(f"Total links found: {total_links}\n")
        file.write(f"Unique subdomains found: {unique_subdomains}\n")
        file.write(f"Document links (doc/docx/pdf): {document_links}\n")
        file.write(f"Internal pages visited: {internal_pages}\n")
        file.write(f"Total external links: {external_links_total}\n")

def main():
    base_url = "https://spbu.ru/"
    crawl(base_url)

if __name__ == "__main__":
    main()
