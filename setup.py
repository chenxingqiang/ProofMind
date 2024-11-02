# setup.py
from setuptools import setup, find_packages

setup(
    name="proofmind",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'torch',
        'scikit-learn',
        'matplotlib',
        'tqdm'
    ],
)
