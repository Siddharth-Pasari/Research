from setuptools import setup, find_packages

setup(
    name='braunschweig_lab_research',
    version='1.0.0',
    description='A package for fluorescence and profilometry data analysis developed by high school students at the Braunschweig Group Laboratory at the CUNY ASRC',
    author='Anthony Russo, Siddharth Pasari',
    author_email='anthonyrusso@hunterschools.org, siddharthpasari@hunterschools.org',
    packages=find_packages(),
    install_requires=[
        'matplotlib>=3.10.0',
        'numpy>=2.0,<3.0',
        'pandas>=2.2.3',
        'pillow>=11.1.0',
        'openpyxl>=3.1.5',
        'scipy>=1.15.2',
        'opencv-python>=4.11.0.86',
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'mypy',
            'flake8',
        ]
    },
    entry_points={
        'console_scripts': [
            'fluorescence-cli = fluorescence.fluorescence:main',
            'profilometry-cli = profilometry.opdx_plotter:main',
        ],
    },
)
