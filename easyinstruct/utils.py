import os

API_NAME_DICT = {
    "openai": {
        "gpt3": ["text-davinci-003", "text-davinci-002", "code-davinci-002"],
        "chatgpt": ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
    },
    "google": {},
    "baidu": {},
    "anthropic": {}
}

def set_openai_key(key):
    os.environ["OPENAI_API_KEY"] = key

def get_openai_key():
    return os.getenv("OPENAI_API_KEY")

def set_proxy(proxy):
    os.environ["https_proxy"] = proxy