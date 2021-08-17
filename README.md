# BRITE-Decorrelation-Codes

This repo serves as a basis for this and all future BRITE decorrelation mettings. Shared codes and various jupyter notebooks, used for the upcoming catalog papers can be found here.

# Pre-requisits

This repo will be completely kept in Python code. The various settings and codes have been tested with **Python 3.8**, but all versions >= 3.7 should work.
To get Python, you have various options:

- [Using pyenv (MacOS/Linux)](https://github.com/pyenv/pyenv)
- [Directly Downloading (all OS)](https://www.python.org/)
- [Pyenv also exists for Windows](https://github.com/pyenv-win/pyenv-win)

It is assumed that you have installed a Python version that is suitable, and you can call it using python3 in your terminal of choice.

Other requirements are [pip](https://pip.pypa.io/en/stable/installation/), a packet manager for Python. It is also generally 
recommended to create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

This makes sure that we encapsulate our resources and packages. After you have created your virtual environment, you can then 
install the packages:

```bash
pip install -r requirements.txt
```

The requirements file will contain all necessary packages.