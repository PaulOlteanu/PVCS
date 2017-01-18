import os

def expand_directory(directory_path):
    ret = []

    for file_path in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, file_path)):
            # Append instead of extend or += because those separate the string into its individual characters
            # This has to do with the way strings act like lists in python
            ret.append(os.path.join(directory_path, file_path))

    return ret

def find_file_id_in_commit(file_name, revision_number):
    with open(".pvcs/revisions/" + str(revision_number) + "/change_map") as change_map:
        for line in change_map.readlines():
            if line.find(file_name) != -1:
                return int(line.split(",")[0])
