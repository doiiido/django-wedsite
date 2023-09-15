import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-wedsite',
    version='0.0.11',
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3",
    description='A simple open-source django wedding website',
    long_description=README,
    url='https://www.wedsite.io/',
    author='Dan Pipe-Mazo',
    author_email='dpipemazo@gmail.com',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only ',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],


    # Installation Requirements
    install_requires = [
        "dj-database-url",
        "Django",
        "gunicorn",
        "psycopg2",
        "whitenoise",
        "requests",
        "django-easy-maps",
        "raven",
        "django-tz-detect",
        "django-inlinecss",
        "lorem",
        "django-appconf",
    ],
)
