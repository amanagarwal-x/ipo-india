from setuptools import setup, find_packages
__version__ = '0.0.10'
setup(
    name='ipo_india',
    version=__version__,

    url='https://github.com/MichaelKim0407/tutorial-pip-package',
    author='Aman Agarwal',
    author_email='aman.agarwal150@gmail.com',

    install_requires=[
        "beautifulsoup4==4.12.2",
        "bs4==0.0.1",
        "html5lib==1.1",
        "pydantic==1.10.7",
        "pytz==2023.3",
        "requests==2.30.0",
    ],
    packages=find_packages(),
    python_requires='>=3.9',
)
