import setuptools

with open("README.md", "r") as desc:
    long_description = desc.read()

with open("requirements.txt", 'r') as require:
    packages = require.readlines()
    packages = [p.strip('\n') for p in packages]

setuptools.setup(
    name="bulma-load",
    version="0.0.8",
    author="Kiran Patel",
    author_email="na@gmail.com",
    license='MIT',
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
    keywords='vegeta load testing stress',
    install_requires=packages,
    python_requires='>=3.6',
)
