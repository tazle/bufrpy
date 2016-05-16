from setuptools import setup
import ast

path = 'bufrpy/__init__.py'
with open(path, 'rU') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in t.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0]
            if isinstance(name, ast.Name) and name.id == '__version__':
                version = node.value.s
                break
    else:
        raise ValueError("Could not determine software version")


setup(name="bufrpy",
      packages=["bufrpy", "bufrpy.template", "bufrpy.table", "bufrpy.tool"],
      version=version,
      description="Pyre-Python BUFR decoder",
      url="https://github.com/tazle/bufrpy",
      author="Tuure Laurinolli",
      author_email="tuure@laurinolli.net",
      zip_safe=False,
      keywords=["bufr"],
      install_requires=["bitstring>=3.1.2"],
      test_suite="tests",
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
          "Topic :: Scientific/Engineering"
      ])

