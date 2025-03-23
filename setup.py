from setuptools import setup, find_packages

setup(
    name="chatwithdb",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        'numpy',
        'scikit-learn',
        'google-cloud-bigquery',
        'langchain-google-vertexai',
    ],
)