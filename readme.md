# CMS From Python Proof of Concept with [Python.NET](https://pythonnet.github.io/)

## Quick Start

```bash
# You should only have to do this once on your system. Use your user@idmod.org login.
#
$ docker login idm-docker-staging.packages.idmod.org

$ docker pull idm-docker-staging.packages.idmod.org/pycms:9778b45_1597692284

# Run this from the directory where your python scripts live. The container will see them under '/host/'.
#
$ docker run --rm -it -v $(pwd):/host idm-docker-staging.packages.idmod.org/pycms:9778b45_1597692284 python3 /host/seir.py

# Or, if you are in windows command prompt:
c:\pycms> docker run --rm -it -v %cd%:/host idm-docker-staging.packages.idmod.org/pycms:9778b45_1597692284 python3 /host/seir.py

# The docker tag above includes a specific revision after the ":". IDM Artifactory is not yet set up for ":latest", see this ticket: https://helpdesk.idmod.org/browse/REQUEST-12766
# After we fix that ticket, you'll usually just use ":latest".
```

## Documentation

* [1-pager overview](https://github.com/InstituteforDiseaseModeling/pycms/blob/master/specs/one-pager.md)
* [Specification](https://github.com/InstituteforDiseaseModeling/pycms/blob/master/specs/specification.md)

## Setup

- consider creating a virtual environment with `python -m virtualenv venv`
- activate your virtual environment with `venv\scripts\activate.bat`
- install requirements (Python.NET and Matplotlib) with `pip install -r requirements.txt`

## Execution

- run the simple SEIR model with `python seir.py`

## Ideas for Extension

- Convert trajectory data from the solver to a pandas dataframe.
- `ISolver.Solve()` repeatedly calls `StartRealization()` followed by `SolveOnce()` - expose these calls in `ISolver`.
- `SolveOnce()` calls `StepOnce()` while `CurrentTime < duration` followed by `trajectories.RecordObservables()` - expose `StepOnce()` in `ISolver` and `RecordObservables()` (TBD)
- Expose `SolverBase.model` to Python code to inspect state.

### Additional Extensions

- Creating the textual representation of the model and loading it with the EMODL parser is a little clunky. Consider wrapping a Python class around the `ModelBuilder` and its various parts, e.g. `SpeciesDescription`, in order to build the model directly.

### [Mono](https://www.mono-project.com/)

- Investigate building `compartments` with Mono on macOS &| Linux.
- Verify that Python.NET on macOS &| Linux works with Mono version of `compartments`
- Might need [IronScheme](https://github.com/IronScheme/IronScheme) to compile against Mono if we don't have "Additional Extensions" above.

### [.NET Core](https://docs.microsoft.com/en-us/dotnet/core/)

- Investigate building `compartments` with .NET Core on macOS &| Linux.
- Look for Python.NET to [support .NET Core](https://github.com/pythonnet/pythonnet/issues/984)
- Might need [IronScheme](https://github.com/IronScheme/IronScheme) to compile against .NET Core if we don't have "Additional Extensions" above.

### Python.Net [Troubleshooting Installation on Linux](https://github.com/pythonnet/pythonnet/wiki/Troubleshooting-on-Windows,-Linux,-and-OSX#2-build-and-install-from-command-line)

- requires mono-complete or mono-devel
- requires clang (`sudo apt-get install clang`)
- requires glib (`sudo apt-get install libglib2.0-dev`)
- requires python-dev

- `sudo pip3 install pythonnet` fails with `error: option --single-version-externally-managed not recognized`
- try `sudo pip3 install --egg git+https://github.com/pythonnet/pythonnet`

### Python.Net Installation on macOS

- These instructions assume Python 3 on the machine [(download here)](https://www.python.org/downloads/).
- [install homebrew](https://brew.sh/)
- install pkg-config with `brew install pkg-config`
- [install mono for macOS](https://www.mono-project.com/download/stable/)
- **Note: mono includes a `mono-2.pc` file compatible with pkg-config, but does not put it where pkg-config can find it.**
  - verify that the `mono-2.pc` file is in the following location: `/Library/Frameworks/Mono.framework/Versions/6.10.0/lib/pkgconfig/`
  - run the following command to help `pkg-config` find `mono-2.pc`:  
    `export PKG_CONFIG_PATH=/Library/Frameworks/Mono.framework/Versions/6.10.0/lib/pkgconfig/`
  - verify that `pkg-config` sees the `mono-2.pc` file by running `pkg-config --libs mono-2`
- install Python.Net with `pip3 install pythonnet` (_alternatively_ install the latest Python.Net with `pip3 install git+https://github.com/pythonnet/pythonnet`)
- **Note: If using a virtual environment, activate the virtual environment before running the `export` command for `PKG_CONFIG_PATH`.**
- **Note: Python 3 might be the default Python on your system. If so, use `pip install pythonnet` rather than `pip3 install pythonnet`.**

