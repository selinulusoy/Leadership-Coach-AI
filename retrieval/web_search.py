import re
import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup


def search_web(query: str, max_results: int = 3) -> list:
    """
    Retrieve cotent by web search
    """
    results = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=max_results):
            try:
                # get page content
                response = requests.get(result['href'], timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # get main content
                text = ' '.join(p.get_text() for p in soup.find_all('p'))
                text = re.sub(r'\s+', ' ', text)[:2000]  
                
                results.append({
                    "title": result['title'],
                    "url": result['href'],
                    "content": text
                })
            except:
                continue
    
    return results