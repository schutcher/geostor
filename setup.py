from setuptools import setup, find_packages

setup(
    name="geostor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.0.0",
        "SQLAlchemy>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'geostor=src.main:main',
        ],
    },
)
