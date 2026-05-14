"""
爬虫核心模块：负责目录解析、章节内容爬取、反爬破解
"""
from playwright.sync_api import TimeoutError
from lxml import etree
import re
from utils import clean_text, init_output_dir, write_to_file

def get_child_url(page, url):
    """
    目录页解析函数：提取所有章节链接
    :param page: Playwright页面对象
    :param url: 目录页URL
    :return: 章节链接列表
    """
    base_url = 'https://www.feelxs.com/books/93681/'
    full_url_list = []
    try:
        page.goto(url)
        page.wait_for_selector('div', timeout=10000)
        html = page.content()
        et_obj = etree.HTML(html)
        onclicks = et_obj.xpath('//div[@class="row row-section"]/div/ul/li/a/@onclick')

        if not onclicks:
            print("未提取到任何章节链接")
            return full_url_list

        # 正则匹配章节ID（破解反爬加密标识）
        pattern = re.compile(r'.*?\((?P<num>\d+)\);')
        for onclick in onclicks:
            result = pattern.search(onclick)
            if not result:
                print(f"跳过无效链接：{onclick}")
                continue
            full_url = f"{base_url}{result.group('num')}.html"
            full_url_list.append(full_url)
    except TimeoutError:
        print("目录页面加载超时")
    except Exception as e:
        print(f"目录页解析失败：{str(e)}")
    return full_url_list

def get_content(page, url, index):
    """
    章节内容爬取函数：破解JS加密、获取并清洗文本、写入文件
    :param page: Playwright页面对象
    :param url: 章节详情页URL
    :param index: 章节序号
    """
    # 初始化输出目录
    init_output_dir()
    file_path = './output/龙族.txt'

    try:
        # 注入脚本，拦截document.writeln破解反爬
        page.add_init_script("""
            // 保存浏览器原生的document.writeln写入方法，保证页面正常渲染
            window.originalWriteln = document.writeln;
            // 定义数组：存储解密后的所有正文片段
            window.textPart = [];
            // 定义集合：自动去重，记录已经保存过的内容
            window.seenContent = new Set();

            // 重写浏览器原生writeln方法，截获解密后的内容
            document.writeln = function(content) {
                // 去重逻辑：只保存从未出现过的内容
                if (!window.seenContent.has(content)) {
                    window.seenContent.add(content);
                    window.textPart.push(content);
                }
                // 执行原始方法，让网页正常显示，规避反爬弹窗
                window.originalWriteln(content);
            };
        """)

        page.goto(url, timeout=15000)
        page.wait_for_function("window.textPart.length > 0", timeout=15000)
        page.wait_for_timeout(500)

        # 获取并清洗文本
        all_content = page.evaluate("window.textPart.join('')")
        if not all_content:
            print(f"第{index}章：未获取到文本内容")
            return

        final_content = clean_text(all_content)
        # 写入文件
        if write_to_file(file_path, final_content, index):
            print(f"第{index}章爬取完成")
    except TimeoutError:
        print(f"第{index}章：页面加载超时，跳过")
    except Exception as e:
        print(f"第{index}章爬取失败：{str(e)}")