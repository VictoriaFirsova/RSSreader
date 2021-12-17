from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='rss_reader',
    version='4.0.0',
    description='Pure Python command-line RSS reader.',
    long_description=long_description,
    long_description_content_type='markdown',
    author='Victoria Firsova',
    author_email='firsovavictoria@mail.ru',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9 :: Only',
        ],

    keywords='rss_reader, development',
    include_package_data=True,
    py_modules=["rss_reader"],

    python_requires='>=3.9, <3.10',

    install_requires=[

        'requests==2.26.0',
        'pandas==1.3.3',
        'argparse',
        'bs4==0.0.1',
        'lxml==4.6.3',
        'beautifulsoup4==4.10.0',
        'yattag==1.14.0',
        'fpdf==1.7.2'
        ],
    package_data={
        '': ['DejaVuSansCondensed.ttf']
    },

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'rss_reader=rss_reader.rss_reader:entry',
        ],
    },

)



