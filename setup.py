from pathlib import Path

from setuptools import setup

CURRENT_DIR = Path(__file__).parent


def get_long_description():
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md, encoding="utf8") as ld_file:
        return ld_file.read()


setup(
    name="karbon",
    version="0.1.0",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    description="Turn mouse events into art!",
    keywords=["mouse tracking", "karbon"],
    author="Furkan Onder",
    author_email="furkanonder@protonmail.com",
    url="https://github.com/furkanonder/karbon/",
    license="MIT",
    python_requires=">=3.6",
    py_modules=["karbon"],
    install_requires=[
        "pygame==2.1.2",
        "pygame-gui==0.6.4",
        "pynput==1.7.6",
    ],
    extras_require={},
    zip_safe=False,
    include_package_data=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Topic :: Games/Entertainment",
        "Topic :: Artistic Software",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        "console_scripts": [
            "karbon = karbon:main",
        ],
    },
)
