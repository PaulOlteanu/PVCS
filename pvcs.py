import os
import sys
import click
import shutil
import difflib
from helpers import file_helpers
from helpers import patch_applier

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
        with open(".pvcs/newest_commit_version", "a") as f:
            # The first commit id will be 1
            f.write("1")

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
@click.argument("commit_message")
def commit_files(commit_message):
    current_revision_number = None

    with open(".pvcs/newest_commit_version", "r+") as newest_version_file,\
         open(".pvcs/current_commit_version", "r+") as current_version_file:
        current_revision_number = int(newest_version_file.read())
        

        # Increment current version
        newest_version_file.seek(0)
        current_version_file.write(str(current_revision_number))
        newest_version_file.write(str(current_revision_number + 1))
        newest_version_file.truncate()

    os.mkdir(".pvcs/revisions/" + str(current_revision_number))
    os.mkdir(".pvcs/revisions/" + str(current_revision_number) + "/diffs")
    os.mkdir(".pvcs/revisions/" + str(current_revision_number) + "/copies")

    open(".pvcs/revisions/" + str(current_revision_number) + "/change_map", "a").close()
    open(".pvcs/revisions/" + str(current_revision_number) + "/commit_message", "a").close()

    with open(".pvcs/revisions/" + str(current_revision_number) + "/commit_message", "r+") as commit_file:
        commit_file.write(commit_message)

    with open(".pvcs/tracked", "r+") as tracked_files,\
         open(".pvcs/staged", "r+") as staged_files,\
         open(".pvcs/revisions/" + str(current_revision_number) + "/change_map", "r+") as change_map:

        staged_files_list = staged_files.readlines()
        tracked_files_string = tracked_files.read()
        staged_files.seek(0)
        tracked_files.seek(0)

        file_id = 1
        for staged_file in staged_files_list:
            staged_file = staged_file.strip()

            if tracked_files_string.find(staged_file) == -1:
                change_map.write(str(file_id) + ",CREATE," + staged_file + "\n")
                tracked_files.write(staged_file + "\n")
                shutil.copyfile(staged_file, ".pvcs/revisions/" + str(current_revision_number) + "/copies/" + str(file_id))
            
            else:
                change_map.write(str(file_id) + ",CHANGE," + staged_file + "\n")
                file_creation_revision_version = None
                previous_file_version_string = ""

                found = False
                for i in range(1, current_revision_number):
                    with open(".pvcs/revisions/" + str(i) + "/change_map") as old_change_map:
                        for line in old_change_map.readlines():
                            if line.find(staged_file) != -1:
                                file_creation_revision_version = i

                                old_file_id = int(line.split(",")[0])
                                with open(".pvcs/revisions/" + str(i) + "/copies/" + str(old_file_id)) as previous_file:
                                    previous_file_version_string = previous_file.read()
                                    found = True
                    if found:
                        break

                for i in range(file_creation_revision_version + 1, current_revision_number):
                    old_file_id = file_helpers.find_file_id_in_commit(staged_file, i)

                    try:
                        with open(".pvcs/revisions/" + str(i) + "/diffs/" + str(old_file_id) + "_diff") as diff_file:
                            diff_to_apply = diff_file.read()
                            previous_file_version_string = patch_applier.apply_patch(previous_file_version_string, diff_to_apply)

                    except FileNotFoundError as e:
                        pass

                with open(".pvcs/revisions/" + str(current_revision_number) + "/diffs/" + str(file_id) + "_diff", "w") as diff_file,\
                     open(staged_file) as staged:
                    
                    diff_file.writelines(difflib.unified_diff(
                        [x + "\n" for x in previous_file_version_string.split("\n")[0:-1]],
                        [x + "\n" for x in staged.readlines()]))

            file_id += 1

    # Clear stage
    open(".pvcs/staged", "w").close()

@cli.command("revert")
@click.option("--back", "-b", is_flag=True)
@click.argument("number")
def switch_to_commit(back, number):
    start_commit = None
    end_commit = None

    if back:
        pass

    else:
        pass

@cli.command("log")
def show_log():
    pass

@cli.command("status")
def show_status():
    pass

if __name__ == "__main__":
    cli()
