from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="turboyaml",
    version="0.0.3",
    author="Fred Setra",
    author_email="fred.setra@gmail.com",
    description="An AI-powered CLI tool for converting DBT SQL files to YAML using OpenAI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fredbrowne/turboyaml",
    packages=find_packages(),
    install_requires=[
        "openai==0.27.8",
        "pyyaml==6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "turboyaml=turboyaml.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
