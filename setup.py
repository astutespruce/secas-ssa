import os
from setuptools import setup

description = "SECAS Southeast Species Status Landscape Assessment Tool"

if os.path.exists("README.md"):
    long_description = open("README.md").read()
else:
    long_description = description

setup(
    name="SECAS Southeast Species Status Landscape Assessment Tool",
    version="0.1.0",
    url="https://github.com/astutespruce/secas-ssa",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description=description,
    long_description_content_type="text/markdown",
    long_description=long_description,
    setup_requires=["numpy"],
    install_requires=["numpy>=1.23"],
    python_requires=">=3.9",
)
