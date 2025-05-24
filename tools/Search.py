import asyncio
import json
from typing import Optional, List, Dict
from playwright.async_api import async_playwright
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(description="搜索查询字符串")
    max_results: int = Field(default=10, description="最大搜索结果数量")


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


async def search_async(query: str, max_results: int = 10) -> List[SearchResult]:
    """
    使用 Playwright 执行搜索 (使用 DuckDuckGo)
    
    Args:
        query: 搜索查询字符串
        max_results: 最大返回结果数量
        
    Returns:
        搜索结果列表
    """
    results = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        try:
            # 使用 DuckDuckGo 搜索
            search_url = f"https://duckduckgo.com/?q={query}"
            await page.goto(search_url, timeout=15000)
            
            # 等待搜索结果加载
            await page.wait_for_selector('[data-testid="result"]', timeout=10000)
            
            # 提取搜索结果
            search_results = await page.query_selector_all('[data-testid="result"]')
            
            for i, result in enumerate(search_results[:max_results]):
                try:
                    # 提取标题
                    title_element = await result.query_selector('[data-testid="result-title-a"]')
                    title = await title_element.inner_text() if title_element else ""
                    
                    # 提取链接
                    link_element = await result.query_selector('[data-testid="result-title-a"]')
                    url = await link_element.get_attribute('href') if link_element else ""
                    
                    # 提取描述片段 - 使用多个备用选择器
                    snippet = ""
                    snippet_selectors = [
                        '[data-testid="result-snippet"]',  # 原始选择器
                        '.result__snippet',                # 备用选择器1
                        '.js-result-snippet',              # 备用选择器2  
                        '.result-snippet',                 # 备用选择器3
                        'span[data-layout="organic"]',     # 备用选择器4
                        '.snippet',                        # 备用选择器5
                        'div[data-layout] span'           # 更通用的选择器
                    ]
                    
                    for selector in snippet_selectors:
                        snippet_element = await result.query_selector(selector)
                        if snippet_element:
                            snippet = await snippet_element.inner_text()
                            if snippet.strip():  # 确保找到非空内容
                                break
                    
                    # 如果以上选择器都没找到，尝试提取所有文本内容
                    if not snippet.strip():
                        all_text = await result.inner_text()
                        # 移除标题部分，只保留描述
                        if title and title in all_text:
                            snippet = all_text.replace(title, "").strip()
                        else:
                            snippet = all_text
                    
                    # 清理snippet，移除噪声文本
                    snippet = _clean_snippet(snippet, title)
                    
                    if title and url and snippet:
                        results.append(SearchResult(
                            title=title.strip(),
                            url=url,
                            snippet=snippet.strip()
                        ))
                        
                except Exception as e:
                    print(f"解析搜索结果时出错: {e}")
                    continue
                    
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            
        finally:
            await browser.close()
    
    return results


def _clean_snippet(snippet: str, title: str = "") -> str:
    """
    清理snippet文本，移除噪声和导航文本
    
    Args:
        snippet: 原始snippet文本
        title: 页面标题，用于进一步清理
        
    Returns:
        清理后的snippet
    """
    if not snippet:
        return ""
    
    # 要移除的噪声文本模式
    noise_patterns = [
        "Only include results for this site",
        "Hide site from these results", 
        "Share feedback about this site",
        "runoob.com",
        "zhuanlan.zhihu.com",
        "blog.csdn.net",
        "scikit-learn.org",
        "c.biancheng.net",
        "w3school.com.cn",
        "菜鸟教程",
        "知乎专栏",
        "CSDN博客",
        "C语言中文网",
        "w3school",
        "scikit-learn",
        "https://",
        "http://",
        "www.",
        "›",
        "Only include results for",
        "Hide site from",
        "Share feedback",
        # 添加更多URL和技术片段
        "ml ml-python.html",
        "ml ml-python",
        "p 25761248",
        "PUSHIAI article details",
        "PUSHIAI article",
        "stable index.html",
        "stable index",
        "ml_alg",
        "article details",
        "documentation",
        "python_ml_getting_started",
        "python python_ml",
        "在线教程"
    ]
    
    # 移除噪声文本
    cleaned_snippet = snippet
    for pattern in noise_patterns:
        cleaned_snippet = cleaned_snippet.replace(pattern, "")
    
    # 移除重复的标题
    if title:
        cleaned_snippet = cleaned_snippet.replace(title, "")
    
    # 使用正则表达式移除URL路径片段和数字序列
    import re
    # 移除类似 "119448628" 这样的长数字序列
    cleaned_snippet = re.sub(r'\b\d{6,}\b', '', cleaned_snippet)
    # 移除类似 "p/" "ml/" 这样的单字母+斜杠组合
    cleaned_snippet = re.sub(r'\b[a-zA-Z]{1,3}/\b', '', cleaned_snippet)
    # 移除单独的 "p" "ml" 等短词
    cleaned_snippet = re.sub(r'\b[a-zA-Z]{1,2}\b', '', cleaned_snippet)
    # 移除文件扩展名
    cleaned_snippet = re.sub(r'\.\w{2,4}\b', '', cleaned_snippet)
    # 移除下划线连接的技术词汇
    cleaned_snippet = re.sub(r'\b\w+_\w+\b', '', cleaned_snippet)
    # 移除多余的空白字符和换行
    cleaned_snippet = re.sub(r'\s+', ' ', cleaned_snippet)
    cleaned_snippet = cleaned_snippet.strip()
    
    # 移除开头和结尾的标点符号
    cleaned_snippet = cleaned_snippet.strip('.,;:!?-\n\r\t ')
    
    # 移除开头的介词或连接词
    start_words = ['and', 'or', 'is', 'an', 'with', 'for', 'to', 'in', 'on', 'at', 'the', 'a']
    words = cleaned_snippet.split()
    if words and words[0].lower() in start_words:
        cleaned_snippet = ' '.join(words[1:])
    
    # 确保句子以合适的方式开始（首字母大写）
    if cleaned_snippet and len(cleaned_snippet) > 0:
        cleaned_snippet = cleaned_snippet[0].upper() + cleaned_snippet[1:] if len(cleaned_snippet) > 1 else cleaned_snippet.upper()
    
    # 如果清理后文本太短，返回空字符串
    if len(cleaned_snippet) < 15:
        return ""
    
    # 限制长度
    if len(cleaned_snippet) > 200:
        # 在句号处截断，如果没有句号则直接截断
        sentences = cleaned_snippet[:200].split('。')
        if len(sentences) > 1:
            cleaned_snippet = '。'.join(sentences[:-1]) + '。'
        else:
            cleaned_snippet = cleaned_snippet[:200] + "..."
    
    return cleaned_snippet


def search(query: str, max_results: int = 10) -> List[Dict]:
    """
    同步版本的搜索函数
    
    Args:
        query: 搜索查询字符串
        max_results: 最大返回结果数量
        
    Returns:
        搜索结果字典列表
    """
    try:
        results = asyncio.run(search_async(query, max_results))
        return [result.model_dump() for result in results]  # 修复：使用model_dump()替代dict()
    except Exception as e:
        print(f"搜索失败: {e}")
        return []


class SearchTool(BaseTool):
    """LangChain 工具类，用于搜索"""
    
    name: str = "web_search"
    description: str = "使用网络搜索获取最新信息。输入搜索查询，返回相关的搜索结果。"
    args_schema: type[BaseModel] = SearchInput
    
    def _run(self, query: str, max_results: int = 10) -> str:
        """执行搜索并返回格式化的结果"""
        results = search(query, max_results)
        
        if not results:
            return "未找到相关搜索结果。"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""
{i}. 标题: {result['title']}
   链接: {result['url']}
   摘要: {result['snippet']}
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)
    
    async def _arun(self, query: str, max_results: int = 10) -> str:
        """异步执行搜索"""
        results = await search_async(query, max_results)
        
        if not results:
            return "未找到相关搜索结果。"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""
{i}. 标题: {result.title}
   链接: {result.url}
   摘要: {result.snippet}
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)





if __name__ == "__main__":
    # results = search(test_query, 10)
    
    # print(f"搜索查询: {test_query}")
    # print(f"找到 {len(results)} 个结果:")
    
    # for i, result in enumerate(results, 1):
    #     print(f"\n{i}. {result['title']}")
    #     print(f"   {result['url']}")
    #     print(f"   {result['snippet']}")
    
    
    # 创建工具实例
    search_tool = SearchTool()
    test_query = "ISSN of Information System Research"
    results = search_tool.run(test_query)
    print(results)

    results = search_tool.run(test_query)
    print(results)

    results = search_tool.run(test_query)
    print(results)

    results = search_tool.run(test_query)
    print(results)
