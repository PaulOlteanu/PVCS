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
        open(".pvcs/current_rev_number", "a").close()

    # Not sure what exception will be thrown, if any
    # If one is thrown, specific handling can be added for it
    except Exception as e:
        print(repr(e))

    click.echo("Initialized repository")

@cli.command("track")
@click.argument("paths", type=click.Path(exists=True), nargs=-1)
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
@click.argument("number")
def switch_to_commit(back, number):
    pass

@cli.command("status")
def show_status():
    pass

if __name__ == "__main__":
    cli()
