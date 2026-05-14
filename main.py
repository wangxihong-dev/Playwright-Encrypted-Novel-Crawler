"""
程序入口：整合所有模块，启动爬虫
"""
from playwright.sync_api import sync_playwright
from spider import get_child_url, get_content
def main():
    """
    【主函数】程序入口
    1. 初始化浏览器
    2. 获取所有章节链接
    3. 循环爬取所有章节内容
    """
    try:
        # 启动Playwright
        with sync_playwright() as p:
            # 启动无头浏览器，效率比有头快
            browser = p.chromium.launch(headless=True)
            # 创建浏览器上下文，模拟真实用户
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 SLBrowser/9.0.8.3131 SLBChan/112 SLBVPV/64-bit'
            )
            page = context.new_page()
            print("浏览器初始化成功")

            # 小说目录页URL
            url = 'https://www.feelxs.com/books/93681/ml1.html'
            # 获取所有单独章节的链接，得到的是一个列表
            child_url_list = get_child_url(page, url)

            # 异常处理：无有效章节
            if not child_url_list:
                print("无有效章节链接，程序退出")
                return

            print(f" 共获取到 {len(child_url_list)} 个章节，开始爬取...")

            # 遍历爬取（单章失败不中断程序），index从1开始
            for index, url in enumerate(child_url_list, start=1):
                get_content(page, url, index)

            print("\n所有章节爬取任务执行完毕")

    # 浏览器启动失败
    except Exception as e:
        print(f"程序启动失败：{str(e)}")

# 程序入口
if __name__ == '__main__':
    main()