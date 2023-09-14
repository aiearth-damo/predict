import re
from pathlib import Path
from setuptools import setup, find_packages, find_namespace_packages


def get_version():
    with open("./aiearth/predict/__init__.py") as f:
        return re.findall(r"__version__\s*=\s*\"([.\d]+)\"", f.read())[0]


this_directory = Path(__file__).parent
long_description = (this_directory / "long_description.md").read_text()

version = get_version()

packages = find_namespace_packages(include=["aiearth.*"], exclude=['*tests*'])
requirements = open("requirements.txt").readlines()

setup(
    name="aiearth-predict",
    version=version,
    description="AIEarth Spatio-temporal data and AI development kit",
    url="https://engine-aiearth.aliyun.com/",
    packages=packages,
    package_data={"": ['py.typed', '*.pyi']},
    python_requires=">=3.8.13",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
