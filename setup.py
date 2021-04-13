
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-lavviebot",
    version="0.0.5",
    author="Robert Drinovac",
    author_email="unlisted@gmail.com",
    description="A Python library for the Purrsong API utilized by LavvieBot S litterboxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertD502/python-lavviebot',
    keywords='lavviebot, lavviebot s, purrsong',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
    project_urls={  # Optional
    'Bug Reports': 'https://github.com/RobertD502/python-lavviebot/issues',
    'Source': 'https://github.com/RobertD502/python-lavviebot/',
    },
)
