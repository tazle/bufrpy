from setuptools import setup

setup(name="bufrpy",
      packages=["bufrpy"],
      version="0.1",
      description="Pyre-Python BUFR decoder",
      url="https://github.com/tazle/bufrpy",
      author="Tuure Laurinolli / FMI",
      author_email="tuure.laurinolli@fmi.fi",
      license="MIT",
      zip_safe=False,
      keywords=["bufr"],
      install_requires=["bitstring>=3.1.2"],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Topic :: Scientific/Engineering"
      ])

