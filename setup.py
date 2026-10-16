from distutils.core import setup
from setuptools import find_packages

url = "https://github.com/nelsonaloysio/nlp-dashboard"

description = """
Python package for the Natural Language Processing Dashboard App.
"""

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open(f"src/nlp_dashboard/__version__.py") as f:
    version = f.read().split()[-1].strip('"')

setup(
    name="nlp-dashboard",
    version=version.strip(),
    description=description.strip(),
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    author="Nelson Aloysio Reis de Almeida Passos",
    # license="",
    # keywords=[],
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        exclude=["build.*", "test.*"]
    ),
    project_urls={
        "Source": url,
        "Tracker": f"{url}/issues",
    },
    entry_points={
        "console_scripts": [
            "nlp-dashboard = nlp_dashboard.cli.dashboard:main",
            "nlp-pipeline = nlp_dashboard.cli.pipeline:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        # "License :: OSI Approved :: {}",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
