#!/usr/bin/env python3
"""
Setup script for PC Agent with Claude
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pc-agent-claude",
    version="1.0.0",
    author="PC Agent Developer", 
    author_email="developer@example.com",
    description="A computer-using agent powered by Claude Sonnet 3.5 with advanced computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pc-agent-claude",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Automation",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.34.0",
        "opencv-python>=4.9.0",
        "opencv-contrib-python>=4.9.0", 
        "pillow>=10.4.0",
        "numpy>=1.26.0",
        "requests>=2.32.0",
        "selenium>=4.15.0",
        "pyautogui>=0.9.54",
        "pynput>=1.7.6",
        "screeninfo>=0.8.1",
        "pytesseract>=0.3.10",
        "beautifulsoup4>=4.12.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "scikit-image>=0.22.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "advanced": [
            "torch>=2.1.0",
            "torchvision>=0.16.0",
            "transformers>=4.35.0",
            "ultralytics>=8.0.0",
            "mediapipe>=0.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pc-agent=pc_agent.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)