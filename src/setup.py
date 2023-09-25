from setuptools import setup, find_packages

setup(
    name='stac-validator',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',  # Add any other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'stac-validate=validators.stac_validator.stac_validator:main',
        ],
    },
)