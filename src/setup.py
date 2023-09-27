from setuptools import setup, find_packages

setup(
    name='source-stac-validator',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'stac-validate=validators.stac_validator.stac_validator:main',
        ],
    },
)
