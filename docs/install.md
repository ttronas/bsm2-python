---
hide:
  - navigation
---

# Installation of the project on your device

<h2> Set up your Integrated Development Environment (IDE) </h2>

Before you can get started you have to install an IDE such as [VSCode](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/de-de/pycharm/) on your device. Since most of the setup instructions are for VSCode, this IDE is recommended if you are new to programming.

<h2> Install Python </h2>

Install a Python Version (3.10 - 3. 12) that works with the dependencies of the project. To install Python 3.12 download and run the installer from [this](https://www.python.org/downloads/release/python-3120/) website.

## Installation

### Easy way

To install the latest release of the project via [PyPI](https://pypi.org/), open a command prompt and type 
`install pip install bsm2-python`

### Build from source

If you want the bleeding edge version from the repo, build it yourself via the prompt `hatch build`. See the [Contribution Guide](https://bsm2-python.readthedocs.io/en/latest/contributing/) for more details on how to install hatch (or simply use the Docker image). Then you can install it to arbitrary environments via <br> `pip install dist/bsm2_python<version-hash>.whl`.
