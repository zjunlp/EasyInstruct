from setuptools import setup, find_packages
from setuptools.command.install import install


REQUIRES = """
torch==2.1.0
torchvision==0.16.0
transformers==4.34.1
tokenizers==0.14.1
accelerate==0.20.3
openai==1.35.7
anthropic==0.5.0
cohere==4.31.0
hanlp==2.1.0b52
zhconv==1.4.3
beautifulsoup4==4.11.2
bs4==0.0.1
lxml==4.9.2
sqlitedict==2.1.0
Pillow==10.1.0
tiktoken==0.5.1
nltk==3.8.1
rouge-score==0.1.2
matplotlib==3.8.2
scikit-learn==1.3.2
lexicalrichness==0.5.1
pandarallel==1.6.5
"""

def get_install_requires():
    reqs = [req for req in REQUIRES.split("\n") if len(req)>0]
    return reqs


with open("README.md") as f:
    readme = f.read()


def do_setup():
    setup(
        name="easyinstruct",
        version = '0.1.2',
        description = "An Easy-to-use Instruction Processing Framework for Large Language Models.",
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
                "figs*",
                "data*",
                "experiments*",
                "demo*",
                "configs*",
                "scripts*",
            ]
        ),
        keywords=["AI", "NLP", "instruction", "language model"],
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
        ]
    )


if __name__ == "__main__":
    do_setup()
