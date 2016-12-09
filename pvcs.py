import os
import sys
import click

@click.group()
def cli(args=sys.argv):
    """A simple, easy-to-use version control system
    """
    pass

@cli.command("init")
def initialize():
    pass

@cli.command("track")
@click.argument("paths", nargs=-1)
def track_file(paths):
    pass

@cli.command("stage")
@click.argument("paths", nargs=-1)
def stage_file(paths):
    pass

@cli.command("unstage")
@click.argument("paths", nargs=-1)
def unstage_file(paths):
    pass

@cli.command("commit")
@click.option("--message", "-m")
def commit_file(message):
    pass

@cli.command("log")
def show_log():
    pass

@cli.command("revert")
@click.option("--back", "-b", is_flag=True)
@click.option("number")
def switch_to_commit(back, number):
    pass

@cli.command("status")
def show_status():
    pass

if __name__ == "__main__":
    cli()
