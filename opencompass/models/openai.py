import os
from contextlib import contextmanager

@contextmanager
def temp_proxy():
    """临时设置代理的上下文管理器"""
    original_http_proxy = os.environ.get('http_proxy')
    original_https_proxy = os.environ.get('https_proxy')
    
    try:
        os.environ['http_proxy'] = 'socks5://127.0.0.1:7890'
        os.environ['https_proxy'] = 'socks5://127.0.0.1:7890'
        yield
    finally:
        if original_http_proxy:
            os.environ['http_proxy'] = original_http_proxy
        else:
            os.environ.pop('http_proxy', None)
        if original_https_proxy:
            os.environ['https_proxy'] = original_https_proxy
        else:
            os.environ.pop('https_proxy', None)

class OpenAI:
    def generate(self, inputs, **kwargs):
        with temp_proxy():
            # 实际的API调用代码
            response = self.client.chat.completions.create(...)
            return response 