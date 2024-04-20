import requests
import threading
import mmap
import os
import csv

site = 'https://msu.ru'  # 要查询的主域名
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    "Connection": "close"
}

successful_urls_msu = []  # 用于存储成功连接的URL
lock = threading.Lock()  # 创建锁，用于线程安全的更新successful_urls列表

def process_url(line):
    subdomain = 'http://' + line + '.'
    url = subdomain + site.replace('https://', '').strip('/')  # 正确处理site
    try:
        response = requests.get(url, headers=headers, timeout=2)  # 尝试连接，设置超时时间
        if response.status_code == 200:
            with lock:
                successful_urls_msu.append(url)  # 将成功的URL添加到列表中
                print(url)
    except Exception as e:  # 打印具体的异常信息
        print(f"连接 {url} 失败: {e}")

def save_to_csv(urls):
    with open('successful_urls_msu.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL'])  # 写入头部
        for url in urls:
            writer.writerow([url])  # 写入每个成功的URL

def main():
    with open(r'D:\vscode\2024\automated system\Subdomain.txt', 'r+') as f:
        # 创建内存映射文件
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            lines = mm.read().decode().splitlines()
    
    threads = []
    for line in lines:
        thread = threading.Thread(target=process_url, args=(line,))
        thread.start()
        threads.append(thread)
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 打印所有成功的连接
    print("成功连接的URLs:")
    for url in successful_urls_msu:
        print(url)

    # 保存到CSV文件
    save_to_csv(successful_urls_msu)

if __name__ == "__main__":
    main()
