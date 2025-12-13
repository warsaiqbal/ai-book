from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vla-robotics",
    version="0.1.0",
    author="VLA Robotics Team",
    author_email="vla-robotics@example.com",
    description="Vision-Language-Action system for robotics applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/vla-robotics",
    packages=find_packages(where="src", include=["vla", "vla.*", "shared", "shared.*"]),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vla-system=src.vla.run_vla_system:main",
        ],
    },
)