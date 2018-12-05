import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="sctcamsoft",
        version="0.0.1",
        author="Ari Brill, Weidong Jin, Jake Powell, Marcos Santander",
        author_email="aryeh.brill@columbia.edu",
        description="Slow control software for the CTA SCT camera",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/aribrill/sct-slow-control",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3"
            ],
        )
