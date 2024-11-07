# Installation of the project on your device

<h2> Set up your Integrated Development Environment (IDE) </h2>

Before you can get started you have to install an IDE such as [VSCode](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/de-de/pycharm/) on your device. Since most of the setup instructions are for VSCode, this IDE is recommended if you are new to programming.

<h2> Install Python </h2>

Install the correct Python Version (3.10 - 3. 12) that works with the dependencies of the project.

 - To install Python 3.12 download and run the windows installer on [this](https://www.python.org/downloads/release/python-3120/) website.

<h2> Installation of BSM2-Python </h2>

You can install the project in two ways:

<h3> Installation via dev container (remote) </h3>

A development container is a docker container configured to be used as a fully functional development environment, 
which is preconfigured with all necessary tools and dependencies.
If you want to use a dev container (tested with [VSCode]):

- Open the project folder in [VSCode] and select on the green button in the bottom left corner.

- Choose `Remote-Containers: Reopen in Container` and wait for the container to build.

- To make it work, you need to have [Docker] installed on your machine.

- The dev container is preconfigured with all necessary tools and dependencies.

<h3> Installation via hatch (local) </h3>

Make sure [pipx] is installed using [pip] and install [hatch]:

```console
pip install pipx
pipx install hatch
```

\[only once\] install [pre-commit] hooks in the default environment with:

```console
hatch run pre-commit install
```

Set `hatch run test` as default environment:

- Find your path to the `test` environment by running `hatch env find test`.

- In VSCode, open the `Python: Select Interpreter` command and choose the python executable within the folder structure.

- Now you can run the code just as you would in a normal python environment.