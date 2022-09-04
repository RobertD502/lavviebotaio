import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lavviebotaio",
    version="0.0.1.2",
    author="Robert Drinovac",
    author_email="unlisted@gmail.com",
    description="Asynchronous Python library for the PurrSong API utilized by LavvieBot S litter boxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertD502/lavviebotaio',
    keywords='lavviebot, lavviebot s, purrsong, litter box',
    packages=setuptools.find_packages(),
    python_requires= ">=3.9",
    install_requires=[
        "aiohttp>=3.8.1",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
    project_urls={  # Optional
    'Bug Reports': 'https://github.com/RobertD502/lavviebotaio/issues',
    'Source': 'https://github.com/RobertD502/lavviebotaio/',
    },
)
