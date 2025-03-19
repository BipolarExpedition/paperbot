# SPDX-FileCopyrightText: 2025-present BipolarExpedition <lastdoc39@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from paperbot.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="paperbot")
def paperbot():
    click.echo("Hello world!")
