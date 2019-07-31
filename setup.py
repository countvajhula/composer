from setuptools import setup

requirements = []

test_requirements = []

dev_requirements = []

setup(
    name='composer',
    version='1.0.0',
    description='A life tracking, organizing, and planning framework.',
    author='Siddhartha Kasivajhula',
    author_email='sid@countvajhula.com',
    url='https://github.com/countvajhula/composer',
    include_package_data=True,
    packages=['composer'],
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={
        'dev': dev_requirements,
    }
)
