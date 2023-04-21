import os

API_NAME_DICT = {
    "openai": {
        "gpt3": ["text-davinci-003", "text-davinci-002", "code-davinci-002"],
        "chatgpt": ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
    },
    "google": {},
    "baidu": {},
    "anthropic": {
        "claude": ["claude-v1", "claude-v1.0", "claude-v1.2", "claude-v1.3"],
        "claude-instant": ["claude-instant-v1", "claude-instant-v1.0"]
    }
}

def set_openai_key(key):
    os.environ["OPENAI_API_KEY"] = key

def get_openai_key():
    return os.getenv("OPENAI_API_KEY")

def set_anthropic_key(key):
    os.environ["ANTHROPIC_API_KEY"] = key

def get_anthropic_key():
    return os.getenv("ANTHROPIC_API_KEY")

def set_proxy(proxy):
    os.environ["https_proxy"] = proxy