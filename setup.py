from setuptools import setup, find_packages

from t4c_utils.version import __version__

setup(
    name='t4c_utils',
    version=__version__,
    description='T4C utils',
    long_description='The 4th Coming helper tools',
    url='https://github.com/NewbiZ/t4c_utils',
    author='Aurelien Vallee',
    author_email='aurelien.vallee@protonmail.com',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'pillow == 8.3.2',
        'click >= 7.1.2',
    ],
    entry_points={
        'console_scripts': [
            't4c=t4c_utils.cli:main',
        ],
    },
)

