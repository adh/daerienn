from setuptools import setup, find_packages, Extension
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Daerienn",
    version="0.1",
    author = "Ales Hakl",
    author_email = "ales@hakl.net",
    description = ("Forms with server retained state and SPA-like experience"),
    long_description=read('README.rst'),
    url="https://github.com/adh/daerienn",
    
    license="MIT",
    keywords="flask forms ajax spa",
    install_requires=[
        'Flask>=1.0',
    ],
    extras_require = {
        "example": [
            "Flask-redis"
        ]
    },
    
    packages=[
        "daerienn",
    ],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',

        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],    
)
