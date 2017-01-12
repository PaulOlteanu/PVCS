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
        with open(".pvcs/current_rev_number", "a") as f:
            f.write("0")

    # Not sure what exception will be thrown, if any
    # If one is thrown, specific handling can be added for it
    except Exception as e:
        print(repr(e))

    click.echo("Initialized repository")

# TODO: Add support for deleting files
@cli.command("stage")
@click.argument("paths", nargs=-1)
def stage_files(paths):
    files_to_stage = []
    for file_path in paths:

        # Create list of full path for each file listed
        if os.path.isdir(file_path):
            # Loop through directory
            files_to_stage.extend(file_helpers.expand_directory(file_path))
        else:
            # Append instead of extend because extend separates the string into its individual characters
            # This has to do with the way strings act like lists in python
            files_to_stage.append(file_path)

    with open(".pvcs/staged", "r+") as staged_files:
        staged_files_string = staged_files.read()

        for file_to_stage in files_to_stage:
            # If the file is not already being tracked, track it
            if staged_files_string.find(file_to_stage) == -1:
                staged_files.write(file_to_stage + "\n")

@cli.command("unstage")
@click.argument("paths", nargs=-1)
def unstage_files(paths):
    files_to_unstage = []
    for file_path in paths:

        # Create list of full path for each file listed
        if os.path.isdir(file_path):
            # Loop through directory
            files_to_unstage.extend(file_helpers.expand_directory(file_path))
        else:
            # Append instead of extend because extend separates the string into its individual characters
            # This has to do with the way strings act like lists in python
            files_to_unstage.append(file_path)

    with open(".pvcs/staged", "r+") as staged_files:
        for file_to_unstage in files_to_unstage:
            staged_files_list = staged_files.readlines()
            staged_files.seek(0)

            for staged_file in staged_files_list:
                if staged_file.split(",")[1].strip() != file_to_unstage:
                    staged_files.write(staged_file)

            staged_files.truncate()
            staged_files.seek(0)
    

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
