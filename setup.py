import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyegctl",
    version="1.0.1",
    author="Michal Drzymala",
    author_email="pzbbole@gmail.com",
    description="Energenie control utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pzbbole/pyenergenie",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)