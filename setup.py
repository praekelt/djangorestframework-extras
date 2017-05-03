import multiprocessing
from setuptools import setup, find_packages


setup(
    name="djangorestframework-extras",
    version="0.2.1",
    description="Autogenerate API's for models. Expose core Django functionality. Validate against existing forms.",
    long_description = open("README.rst", "r").read(),
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    url="http://github.com/praekelt/djangorestframework-extras",
    packages = find_packages(),
    install_requires = [
        "djangorestframework>=3.0",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
