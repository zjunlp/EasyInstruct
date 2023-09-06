import os

API_NAME_DICT = {
    "openai": {
        "gpt3": ["text-davinci-003", "text-davinci-002"],
        "chatgpt": ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"],
        "gpt4": ["gpt-4", "gpt-4-0613", "gpt-4-0314"]
    },
    "anthropic": {
        "claude": ["claude-2", "claude-2.0"],
        "claude-instant": ["claude-instant-1", "claude-instant-1.2"]
    },
    "cohere": ["command", "command-nightly", "command-light", "command-light-nightly"]
}

def set_proxy(proxy):
    os.environ["https_proxy"] = proxy

def set_openai_key(key):
    os.environ["OPENAI_API_KEY"] = key

def get_openai_key():
    return os.getenv("OPENAI_API_KEY")

def set_anthropic_key(key):
    os.environ["ANTHROPIC_API_KEY"] = key

def get_anthropic_key():
    return os.getenv("ANTHROPIC_API_KEY")

def set_cohere_key(key):
    os.environ["COHERE_API_KEY"] = key

def get_cohere_key():
    return os.getenv("COHERE_API_KEY")