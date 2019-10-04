# File: setup.py
# Date: 6-Oct-2018
#
# Update:
#
import re
import glob

from setuptools import find_packages
from setuptools import setup

packages = []
thisPackage = 'wwpdb.apps.chem_ref_data'

with open('wwpdb/apps/chem_ref_data/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


setup(
    name=thisPackage,
    version=version,
    description='wwPDB chemical reference admin application',
    long_description="See:  README.md",
    author='Ezra Peisach',
    author_email='ezra.peisach@rcsb.org',
    url='https://github.com/rcsb/py-wwpdb_apps_chem_ref_data',
    #
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    #
    install_requires=['wwpdb.utils.config', 'wwpdb.utils.db ~= 0.10',
                      'wwpdb.utils.session ~= 0.4', 'wwpdb.io >= 0.2',
                      'mmcif.utils ~= 0.18.dev2', 'wwpdb.utils.oe_util', 'jellyfish',
                      'wwpdb.utils.cc_dict_util', 'wwpdb.utils.dp ~= 0.19.dev1',
                      'rcsb.utils.multiproc', 'wwpdb.utils.ws_utils'],
    packages=find_packages(exclude=['wwpdb.apps.tests-chem_ref_data', 'mock-data']),
    # Enables Manifest to be used
    #include_package_data = True,
    package_data={
        # If any package contains *.md or *.rst ...  files, include them:
        '': ['*.md', '*.rst', "*.txt", "*.cfg"],
    },
    #
    # These basic tests require no database services -
    test_suite="wwpdb.apps.tests-chem_ref_data",
    tests_require=['tox'],
    #
    # Not configured ...
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    # Added for
    command_options={
        'build_sphinx': {
            'project': ('setup.py', thisPackage),
            'version': ('setup.py', version),
            'release': ('setup.py', version)
        }
    },
    # This setting for namespace package support -
    zip_safe=False,
)
