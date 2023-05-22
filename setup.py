from setuptools import setup, find_packages
from setuptools.command.install import install


REQUIRES = """
torch>=1.13.0
transformers>=4.28.0
peft==0.2.0
accelerate==0.17.1
openai==0.27.0
anthropic==0.2.7
llama-index==0.4.29
langchain==0.0.116
tiktoken
nltk
"""

def get_install_requires():
    reqs = [req for req in REQUIRES.split("\n") if len(req)>0]
    return reqs


with open("README.md") as f:
    readme = f.read()


def do_setup():
    setup(
        name="easyinstruct",
        version = '0.0.5',
        description = "A easy-to-use framework to instruct large language models.",
        url="https://github.com/zjunlp/EasyInstruct",
        author = 'Yixin Ou',
        long_description=readme,
        long_description_content_type="text/markdown",
        install_requires=get_install_requires(),
        python_requires=">=3.7.0",
        packages=find_packages(
            exclude=[
                "test*",
                "examples*",
                "gitbook*",
                "figs*"
            ]
        ),
        keywords=["AI", "NLP", "instruction", "language model"],
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
        ]
    )


if __name__ == "__main__":
    do_setup()
