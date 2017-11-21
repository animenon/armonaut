from setuptools import setup, find_packages
setup(name='armonaut',
      packages=find_packages('.', exclude=['tests', '.tox']))
