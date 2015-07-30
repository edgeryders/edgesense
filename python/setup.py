from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
long_description = """
Edgesense
=========

This is the python library and scripts for the Edgsense social network analysis tool (see: https://github.com/Wikitalia/edgesense )

The python scripts build the network from source json files and compute all the metrics.

See https://github.com/Wikitalia/edgesense/python/README.md for more informations
"""

setup(
    name='edgesense',
    version='0.22.0',
    description='Edgesense Social Network Analysis and Visualization',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/Wikitalia/edgesense/python',

    # Author details
    author='Luca Mearelli',
    author_email='l.mearelli@spazidigitali.com',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='edgesense sna network socialnetwork catalyst',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=[
        'networkx==1.8.1',
        'python-louvain==0.3'
    ],
    
    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev': [],
        'test': [],
    },

    package_data={
        'edgesense': ['utils/datapackage_template.json', 'catalyst/ontology/*.ttl']
    },
    data_files=[],

    entry_points={
        'console_scripts': [
            'edgesense_drupal=edgesense.drupal_script:main',
            'edgesense_build_network=edgesense.build_network:main',
            'edgesense_catalyst_server=edgesense.catalyst_server:main',
            'edgesense_parse_catalyst=edgesense.parse_catalyst:main',
            'edgesense_parse_tweets=edgesense.parse_tweets:main',
            'edgesense_parse_mailinglist=edgesense.parse_mailinglist:main',
        ],
    },
)