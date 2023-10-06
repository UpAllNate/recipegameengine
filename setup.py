from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="recipegameengine",
    version="1.0.0",
    description="Parses, analyzes, and plans ratios and quantities for recipe games",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="google.com",
    author="nate",
    author_email="upallnate@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords = ["class", "features"]
)