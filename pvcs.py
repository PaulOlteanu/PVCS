import os
import sys
import click
from lib import file_helpers

@click.group()
def cli(args=sys.argv):
    """A simple, easy-to-use version control system
    """
    pass

@cli.command("init")
def initialize():
    try:
        os.mkdir(".pvcs")
        os.mkdir(".pvcs/revisions")
    except FileExistsError:
        print("Directory has already been initialized")
        return

    try:
        # Create files for internal use
        open(".pvcs/tracked", "a").close()
        open(".pvcs/staged", "a").close()
        open(".pvcs/structure_changes", "a").close()
        with open(".pvcs/current_rev_number", "a") as f:
            f.write("1")

    # Not sure what exception will be thrown, if any
    # If one is thrown, specific handling can be added for it
    except Exception as e:
        print(repr(e))

    click.echo("Initialized repository")

@cli.command("stage")
@click.argument("paths", nargs=-1)
def stage_files(paths):
    pass

@cli.command("unstage")
@click.argument("paths", nargs=-1)
def unstage_files(paths):
    pass

@cli.command("commit")
@click.option("--message", "-m")
def commit_files(message):
    pass

@cli.command("log")
def show_log():
    pass

@cli.command("revert")
@click.option("--back", "-b", is_flag=True)
@click.argument("number")
def switch_to_commit(back, number):
    pass

@cli.command("status")
def show_status():
    pass

if __name__ == "__main__":
    cli()
