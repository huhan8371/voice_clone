from setuptools import setup, find_packages

setup(
    name="voice_clone",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pytest>=8.0.0",
        "pytest-asyncio>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.7",
)
