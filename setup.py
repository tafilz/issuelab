import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="issuelab",
    version="0.0.2",
    author="Tafil Avdyli",
    author_email="tafil@tafhub.de",
    description="Migrate issue boards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tafilz/issuelab",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "python-gitlab", "youtrack"]
)
