from setuptools import setup, find_packages

setup(
    name="trading_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "vnstock",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'trading-bot=src.cli:main',
        ],
    },
) 