from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "motor",
        "python-dotenv",
        "beautifulsoup4",
        "aiohttp",
        "cryptography"
    ]
)