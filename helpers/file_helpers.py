import os

def expand_directory(directory_path):
    """Recursively create a list of all the files in a directory and its subdirectories
    """
    ret = []

    for file_path in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, file_path)):
            # Append instead of extend or += because those separate the string into its individual characters
            # This has to do with the way strings act like lists in python
            ret.append(os.path.join(directory_path, file_path))
        else:
            ret.extend(expand_directory(os.path.join(directory_path, file_path)))

    return ret

def find_file_id_in_commit(file_name, revision_number):
    """Find the file id of a specified file in the change map of a specified commit
    """


    with open(".pvcs/revisions/" + str(revision_number) + "/change_map") as change_map:
        # Loop through every line, find the one containing the file, return the id
        for line in change_map.readlines():
            if line.find(file_name) != -1:
                return int(line.split(",")[0])
