from setuptools import setup

requirements = [
    'click',
]

test_requirements = [
    'pytest',
    'pytest-pudb',
    'pytest-sugar',
    'pytest-tldr',
    'tox',
    'mock',  # py2 only
]

dev_requirements = [
    'flake8',
    'bump2version',
]

setup_requirements = [
    'pytest-runner',
]

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
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require={
        'dev': dev_requirements,
    },
    entry_points={
        'console_scripts': ['whats-next=composer.whatsnext:main',
                            'collect-logs=composer.collectlogs:main',
                            'update-index=composer.updateindex:main',
                            'show-advice=composer.advice:main'],
    },
)
