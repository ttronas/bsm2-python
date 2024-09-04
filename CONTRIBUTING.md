# Contributing

Welcome to the contributor guide of BSM2-Python.

This document focuses on getting any potential contributor familiarized with
the development processes, but [other kinds of contributions] are also appreciated.

If you are new to using [git] or have never collaborated in a project previously,
please have a look at [contribution-guide.org]. Other resources are also
listed in the excellent [guide created by FreeCodeCamp].

Please notice, all users and contributors are expected to be **open,
considerate, reasonable, and respectful**. When in doubt,
[Python Software Foundation's Code of Conduct] is a good reference in terms of
behavior guidelines.

## Issue Reports

If you experience bugs or general issues with BSM2-Python, please have a look
on the [issue tracker].
If you don't see anything useful there, please feel free to fire an issue report.

!!! tip
    Please don't forget to include the closed issues in your search.
    Sometimes a solution was already reported, and the problem is considered
    **solved**.

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.

## Documentation improvements

You can help improve the documentation of BSM2-Python by making them more readable
and coherent, or by adding missing information and correcting mistakes.

This documentation uses [mkdocs] as its main documentation compiler.
This means that the docs are kept in the same repository as the project code, and
that any documentation update is done in the same way was a code contribution.

!!! tip
      Please notice that the [GitHub web interface] provides a quick way for
      proposing changes. While this mechanism can  be tricky for normal code contributions,
      it works perfectly fine for contributing to the docs, and can be quite handy.

      If you are interested in trying this method out, please navigate to
      the `docs` folder in the source [repository], find which file you
      would like to propose changes and click in the little pencil icon at the
      top, to open [GitHub's code editor]. Once you finish editing the file,
      please write a message in the form at the bottom of the page describing
      which changes have you made and what are the motivations behind them and
      submit your proposal.

When working on documentation changes in your local machine, you can
build and serve them using [hatch] with `hatch run docs:build` and
`hatch run docs:serve`, respectively.

## Code Contributions

### Submit an issue

Before you work on any non-trivial code contribution it's best to first create
a report in the [issue tracker] to start a discussion on the subject.
This often provides additional considerations and avoids unnecessary work.

### Clone the repository

1. Create a user account on GitHub if you do not already have one.

2. Fork the project [repository]: click on the *Fork* button near the top of the
   page. This creates a copy of the code under your account on GitHub.

3. Clone this copy to your local disk:

   ```console
   git clone git@github.com:YourLogin/bsm2-python.git
   cd bsm2-python
   ```
### Install the project

You can install the project in two ways:
#### Installation via dev container
1. If you want to use a dev container (tested with [VSCode]):
   Open the project folder in [VSCode] and click on the green button in the bottom left corner.
   Choose `Remote-Containers: Reopen in Container` and wait for the container to build.
   To make it work, you need to have [Docker] installed on your machine.
   The dev container is preconfigured with all necessary tools and dependencies.

#### Installation via hatch
1. Make sure [pipx] is installed using [pip] and install [hatch]:

   ```console
   pip install pipx
   pipx install hatch
   ```

2. \[only once\] install [pre-commit] hooks in the default environment with:

   ```console
   hatch run pre-commit install
   ```

3. Set `hatch run test` as default environment:
   Find your path to the `test` environment by running `hatch env find test`.
   In VSCode, open the `Python: Select Interpreter` command and choose the python executable within the folder structure.
   Now you can run the code just as you would in a normal python environment.

### Implement your changes

1. Create a branch to hold your changes:

   ```console
   git checkout -b my-feature
   ```

   and start making changes. Never work on the main branch!

2. Start your work on this branch. Don't forget to add [docstrings] in [Google style]
   to new functions, modules and classes, especially if they are part of public APIs.

3. Add yourself to the list of contributors in `AUTHORS.md`.

4. When you’re done editing, do:

   ```console
   git add <MODIFIED FILES>
   git commit
   ```

   to record your changes in [git].

   Please make sure to see the validation messages from [pre-commit] and fix
   any eventual issues.
   This should automatically use [flake8]/[black] to check/fix the code style
   in a way that is compatible with the project.

    !!! info
        Don't forget to add unit tests and documentation in case your
        contribution adds a feature and is not just a bugfix.

        Moreover, writing an [descriptive commit message] is highly recommended.
        In case of doubt, you can check the commit history with:
        ```
        git log --graph --decorate --pretty=oneline --abbrev-commit --all
        ```
        to look for recurring communication patterns.

5. Please check that your changes don't break any unit tests with
   `hatch run test:cov` or `hatch run test:no-cov` to run the unittest with
   or without coverage reports, respectively. If you want to run only your newly
   added tests, you can use `hatch run test:cov <path-to-your-test-files>`

### Submit your contribution

1. If everything works fine, push your local branch to the remote server with:

   ```console
   git push -u origin my-feature
   ```

2. Go to the web page of your fork and click "Create pull request"
   to send your changes for review.

   Find more detailed information in [creating a PR]. You might also want to open
   the PR as a draft first and mark it as ready for review after the feedbacks
   from the continuous integration (CI) system or any required fixes.


## Bonus: A short word on [hatch]

A special feature that makes hatch very different from other familiar tools is that you almost never
activate, or enter, an environment. Instead, you use `hatch run env_name:command` and the `default` environment
is assumed for a command if there is no colon found. Thus you must always define your environment in a declarative
way and hatch makes sure that the environment reflects your declaration by updating it whenever you issue
a `hatch run ...`. This helps with reproducability and avoids forgetting to specify dependencies since the
hatch workflow is to specify everything directly in [pyproject.toml](pyproject.toml). Only in rare cases, you
will use `hatch shell` to enter the `default` environment, which is similar to what you may know from other tools.

To get you started, use `hatch run test:cov` or `hatch run test:no-cov` to run pytest with or without coverage reports,
respectively. Use `hatch run lint:all` to run all kinds of typing and linting checks. Try to automatically fix linting
problems with `hatch run lint:fix` and use `hatch run docs:serve` to build and serve your documentation.
You can also easily define your own environments and commands. Check out the environment setup of hatch
in [pyproject.toml](pyproject.toml) for more commands as well as the package, build and tool configuration.

[black]: https://pypi.org/project/black/
[contribution-guide.org]: http://www.contribution-guide.org/
[creating a PR]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
[Docker]: https://docs.docker.com/desktop/
[docstrings]: https://peps.python.org/pep-0257/
[flake8]: https://flake8.pycqa.org/en/stable/
[git]: https://git-scm.com
[github web interface]: https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository
[hatch]: https://hatch.pypa.io/latest/
[other kinds of contributions]: https://opensource.guide/how-to-contribute
[pre-commit]: https://pre-commit.com/
[pipx]: https://pypa.github.io/pipx/
[python software foundation's code of conduct]: https://www.python.org/psf/conduct/
[Google style]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[guide created by FreeCodeCamp]: https://github.com/FreeCodeCamp/how-to-contribute-to-open-source
[VSCode]: https://code.visualstudio.com/
