# paperbot

[![PyPI - Version](https://img.shields.io/pypi/v/paperbot.svg)](https://pypi.org/project/paperbot)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/paperbot.svg)](https://pypi.org/project/paperbot)

-----

## Table of Contents

- [Configure](#configure)
- [Installation](#installation)
- [Running](#running)
    - [Without Hatch](#without-hatch-installed)
    - [With Hatch](#with-hatch-installed)
- [License](#license)

## Configure

> [!NOTE]
> Inside of src/paperbot/__main__.py, a few things should be adjusted.

- At the top of the file, you may want to change the news feed URLs in the variable `FEED`.
- At the bottom of the file, you must change what program you use for playing text to speech. I suggest researching edge-tts or piper-tts.

## Installation

> [!WARNING]
> Don't install it yet. Its not ready for production use.

Rather than installing it, we will prepare to run it from the source code.

Instead just go to the directory where you cloned it to and run:
```shell title:Minimal install
python -m venv .venv
``````

## Running

### Without hatch installed

In the directory where you cloned it to, run:
```shell title:Run paperbot without installation
source .venv/bin/activate && python src/paperbot/__main__.py && deactivate
```

### With hatch installed

In the directory where you cloned it to, run:
```shell title:Run paperbot via hatch
hatch run python src/paperbot/__main__.py
```

## License

`paperbot` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
