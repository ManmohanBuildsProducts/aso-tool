from setuptools import setup, find_packages

setup(
    name="aso-tool",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "google-play-scraper==1.2.4",
        "nltk==3.8.1",
        "python-multipart==0.0.6",
        "aiohttp==3.9.3",
        "psutil==5.9.8",
        "gunicorn==21.2.0"
    ],
    python_requires=">=3.11",
)