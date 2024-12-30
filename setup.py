from setuptools import setup, find_packages

setup(
    name="polar-h10-monitor",
    version="0.1.0",
    description="A Python package for monitoring Polar H10 heart rate sensors via Bluetooth LE",
    author="andrewlee377",
    author_email="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "bleak>=0.20.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

