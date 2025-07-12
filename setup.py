from setuptools import find_packages, setup

setup(
    name="divine_arsenal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=0.900",
        "pre-commit>=2.17.0",
        "psutil>=5.9.0",
    ],
    python_requires=">=3.8",
)
