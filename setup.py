import setuptools

with open("README.md", "r") as desc:
    long_description = desc.read()

with open("requirements.txt", 'r') as require:
    packages = require.readlines()
    packages = [p.strip('\n') for p in packages]

setuptools.setup(
    name="bulma-load",
    version="0.0.3",
    author="Kiran Patel",
    author_email="na@gmail.com",
    description="Wrapper for Vegeta Load Testing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiran94/bulma",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=packages,
    python_requires='>=3.6',
)
