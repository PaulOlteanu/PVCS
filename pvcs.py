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

    For more detailed help, use pvcs COMMAND --help
    """
    pass

@cli.command("init")
def initialize():
    """Set up internal files and folders in preparation for tracking changes
    """
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
        with open(".pvcs/newest_commit_version", "a") as f, open(".pvcs/current_commit_version", "a") as f2:
            # The first commit id will be 1
            f.write("1")
            f2.write("1")

    # Not sure what exception will be thrown, if any
    # If one is thrown, specific handling can be added for it
    except Exception as e:
        print(repr(e))

    click.echo("Initialized repository")

@cli.command("stage")
@click.argument("paths", nargs=-1)
def stage_files(paths):
    """Add files to the stage to be included in the next commit
    """
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
            if staged_files_string.find(file_to_stage) == -1:
                staged_files.write(file_to_stage + "\n")

@cli.command("unstage")
@click.argument("paths", nargs=-1)
def unstage_files(paths):
    """Remove files from the stage. They will not be included in the next commit
    """
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
        staged_files_list = staged_files.readlines()
        staged_files.seek(0)

        # Rewrite every line in the staged files list if it isn't one that needs to be unstaged
        for staged_file in staged_files_list:
            if staged_file.strip() not in files_to_unstage:
                staged_files.write(staged_file)

        staged_files.truncate()

@cli.command("commit")
@click.argument("commit_message")
def commit_files(commit_message):
    """Create a commit of the current state of the repository
    """
    current_revision_number = None

    with open(".pvcs/newest_commit_version", "r+") as newest_version_file, open(".pvcs/current_commit_version", "r+") as current_version_file:
        current_revision_number = int(newest_version_file.read())
        current_version_file.write(str(current_revision_number))
        
        # Increment current version
        newest_version_file.seek(0)
        newest_version_file.write(str(current_revision_number + 1))
        newest_version_file.truncate()

    # Create required folders and files
    os.mkdir(".pvcs/revisions/" + str(current_revision_number))
    os.mkdir(".pvcs/revisions/" + str(current_revision_number) + "/diffs")
    os.mkdir(".pvcs/revisions/" + str(current_revision_number) + "/copies")

    open(".pvcs/revisions/" + str(current_revision_number) + "/change_map", "a").close()
    open(".pvcs/revisions/" + str(current_revision_number) + "/commit_message", "a").close()

    # Write commit message to file
    with open(".pvcs/revisions/" + str(current_revision_number) + "/commit_message", "r+") as commit_file:
        commit_file.write(commit_message)

    with open(".pvcs/tracked", "r+") as tracked_files, open(".pvcs/staged", "r+") as staged_files, open(".pvcs/revisions/" + str(current_revision_number) + "/change_map", "r+") as change_map:

        staged_files_list = staged_files.readlines()
        tracked_files_string = tracked_files.read()
        staged_files.seek(0)
        tracked_files.seek(0)

        # To be used to assign a file id to every file in the commit
        file_id = 1
        for staged_file in staged_files_list:
            staged_file = staged_file.strip()

            # If the file isn't being tracked already, consider it "created" this commit, and add it to the tracked files list
            if tracked_files_string.find(staged_file) == -1:
                change_map.write(str(file_id) + ",CREATE," + staged_file + "\n")
                tracked_files.write(staged_file + "\n")
                shutil.copyfile(staged_file, ".pvcs/revisions/" + str(current_revision_number) + "/copies/" + str(file_id))
            
            # If it is being tracked, generate a diff for it
            else:
                change_map.write(str(file_id) + ",CHANGE," + staged_file + "\n")
                file_creation_revision_version = None
                previous_file_version_string = ""

                # Find the first occurence of it in a change map. This will be where it was "created"
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

                # Apply the diffs untill it reaches the most recently commited version
                for i in range(file_creation_revision_version + 1, current_revision_number):
                    old_file_id = file_helpers.find_file_id_in_commit(staged_file, i)

                    try:
                        with open(".pvcs/revisions/" + str(i) + "/diffs/" + str(old_file_id) + "_diff") as diff_file:
                            diff_to_apply = diff_file.read()
                            previous_file_version_string = patch_applier.apply_patch(previous_file_version_string, diff_to_apply)

                    except FileNotFoundError as e:
                        pass

                # Create a diff between the current version of the file and it's most recently commited version
                with open(".pvcs/revisions/" + str(current_revision_number) + "/diffs/" + str(file_id) + "_diff", "w") as diff_file,\
                     open(staged_file) as staged:
                    
                    # Difflib needs the file as a list of every line instead of one string
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
    """Switch to a specified commit number, or back n versions
    """

    start_commit = None
    end_commit = None

    with open(".pvcs/current_commit_version") as current_commit_version:
        start_commit = int(current_commit_version.read())

    if back:
        end_commit = start_commit - int(number)
    else:
        end_commit = int(number)

    start = None
    end = None
    step = None

    # If going backwards
    if start_commit > end_commit:
        start = start_commit
        end = end_commit
        step = -1
    else:
        start = start_commit + 1
        end = end_commit + 1
        step = 1

    for i in range(start, end, step):
        with open(".pvcs/revisions/" + str(i) + "/change_map") as change_map:
            # Change every file in the commit
            for line in change_map.readlines():
                file_id, action, file_path = line.strip().split(",")
                try:
                    with open(file_path, "r+") as file_to_change, open(".pvcs/revisions/" + str(i) + "/diffs/" + str(file_id) + "_diff") as diff:
                        current = file_to_change.read()
                        file_to_change.seek(0)
                        # Change the file and write it back
                        file_to_change.write(patch_applier.apply_patch(current, diff.read(), step == -1))
                        file_to_change.truncate()
                except Exception as e:
                    pass

    with open(".pvcs/current_commit_version", "w") as current_commit_version:
        current_commit_version.write(str(end_commit))

@cli.command("log")
def show_log():
    """Display information about past commits
    """

    # Get the latest commit number
    newest_commit = None
    with open(".pvcs/newest_commit_version") as newest_version_file:
        newest_commit = int(newest_version_file.read())

    # Loop to that commit and print the message for all commits
    for i in range(1, newest_commit):
        with open(".pvcs/revisions/" + str(i) + "/commit_message") as message:
            print("Version: " + str(i) + "\tMessage: " + message.read())

@cli.command("status")
def show_status():
    """Display information about the current stage, and state of the repository
    """
    print("Currently staged:")
    with open(".pvcs/staged") as stage:
        print(stage.read().strip())

if __name__ == "__main__":
    cli()
