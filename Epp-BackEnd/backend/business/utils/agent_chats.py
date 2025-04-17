import os
from openai import OpenAI, AzureOpenAI
import openai
import backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

# 自定义一个名为 CustomError 的错误类型
class NoAPIKeyError(Exception):
    """自定义错误类型，用于特定业务场景"""
    def __init__(self, message="请检查系统环境变量是否有相应的API密钥"):
        self.message = message
        super().__init__(self.message)

def query_agent(syetem_prompt,llm,query):
    pass

def create_chat_func(llm):
    if llm.lower() == "deepseek-r1":
        return deepseek_R1_chat()
    elif llm.lower() == "deepseek-v3":
        return deepseek_v3_chat()
    elif llm.lower() == "chatglm3-6b":
        return chatglm3_6b_chat()
    elif llm.lower().find("infini") != -1 and llm.lower().find("gpt4") != -1:
        return infini_gpt4()
    else:
        raise NotImplementedError
    
def deepseek_R1_chat():
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY") #TODO 请确保环境变量里有deepseek api key
    if not deepseek_api_key:
        raise NoAPIKeyError
    def backoff_hdlr(details):
        print ("Backing off {wait:0.1f} seconds after {tries} tries calling function {target} \
        with args {args} and kwargs {kwargs}".format(**details))
    @backoff.on_exception(
        backoff.constant,
        (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, ValueError),
        interval=5,
        on_backoff=backoff_hdlr
    )
    def chat(messages,temperature=0.5,max_tokens=2048):
        client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # reasoning_content = response.choices[0].message.reasoning_content
        # content = response.choices[0].message.content
        # messages.append({'role': 'assistant', 'content': content}) 
        return response
    return chat

def deepseek_v3_chat():
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY") #TODO 请确保环境变量里有deepseek api key
    if not deepseek_api_key:
        raise NoAPIKeyError
    def backoff_hdlr(details):
        print ("Backing off {wait:0.1f} seconds after {tries} tries calling function {target} \
        with args {args} and kwargs {kwargs}".format(**details))
    @backoff.on_exception(
        backoff.constant,
        (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, ValueError),
        interval=5,
        on_backoff=backoff_hdlr
    )
    def chat(messages,temperature=0.5,max_tokens=2048,tools = None):
        client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
        if tools is None:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,  
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
        return response
    return chat

def infini_gpt4():
    infini_api_key = os.environ.get("INFINI_API_KEY")
    if not infini_api_key:
        raise NoAPIKeyError
    def backoff_hdlr(details):
        print ("Backing off {wait:0.1f} seconds after {tries} tries calling function {target} \
        with args {args} and kwargs {kwargs}".format(**details))
    @backoff.on_exception(
        backoff.constant,
        (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, ValueError),
        interval=5,
        on_backoff=backoff_hdlr
    )
    def chat(messages,temperature=0.5,max_tokens=2048):
        url = "https://cloud.infini-ai.com/maas/gpt-4o-20240513/azure/chat/completions"
        payload = {
            "model": "gpt-4o-20240513",
            "messages":messages,
            "temperature":temperature,
            "max_tokens":max_tokens
        }
        headers = {
            "Authorization": "Bearer "+infini_api_key, 
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise ValueError
        return response.json()["choices"][0]["message"]["content"]
    return chat

def chatglm3_6b_chat():
    def queryGLM(msg: str, history=None,temperature=0.3) -> str:
        '''
        对chatGLM3-6B发出一次单纯的询问
        '''
        print(msg)
        chat_chat_url = 'http://172.17.62.88:7861/chat/chat'
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "query": msg,
            "prompt_name": "default",
            "temperature": temperature
        })

        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        try:
            response = session.post(chat_chat_url, data=payload, headers=headers, stream=False)
            response.raise_for_status()

            # 确保正确处理分块响应
            decoded_line = next(response.iter_lines()).decode('utf-8')
            print(decoded_line)
            if decoded_line.startswith('data'):
                data = json.loads(decoded_line.replace('data: ', ''))
            else:
                data = decoded_line
            return data['text']
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"ChunkedEncodingError: {e}")
            return "错误: 响应提前结束"
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
            return f"错误: {e}"
    return queryGLM

