# Platform

UI and control application for the RamBOT.

## Prerequisites

pipenv: https://pipenv.pypa.io

pyenv: https://github.com/pyenv/pyenv

## Installation

This project uses pyenv and pipenv to manage the python environment, instead of using system packages which has an easily broken dependency tree.

tldr:

```bash
# Install pyenv
curl -fsSL https://pyenv.run | bash

# Install pipenv
pip install pipenv

# Install this repo
# Typically I will put it in /opt
cd /opt/RamBOTs
git clone https://github.com/RAMBotsCSU/platform.git
cd platform
# this should ask you to install python with pyenv, select yes
pipenv install
```

You may need to add pyenv and pipenv to PATH, see their respective documentation for more information.

In order for the PS4 LED control to work:

```bash
cp 99-ds-controller.rules /etc/udev/rules.d/
```

and reboot.

## Running

After install,

```bash
cd /opt/RamBOTs/platform
pipenv run launch
```
