def apply_patch(string_to_patch, patch, reverse=False):
    """Apply a diff file to a specified string
    """

    # The strings are now represented as arrays with every element being one line
    patch_lines = patch.split("\n")
    final_text = string_to_patch.split("\n")

    current_line_number = 0
    for line in patch_lines:

        current_line_number += 1

        # Header for the patch file
        if line.startswith("---") or line.startswith("+++"):
            pass

        # Start of new diff "hunk"
        # Get info about the line numbers the new hunk takes place over
        elif line.startswith("@"):

            # TODO: A lot of this is probably unneeded
            old_lines, new_lines = line.replace("-", "").replace("+", "").strip("@").strip().split(" ")
            old_lines = old_lines.split(",")
            new_lines = new_lines.split(",")

            # Change the current line number to skip over ones that didn't change
            current_line_number = int(old_lines[0]) - 1

        # If a line was removed
        elif line.startswith("-"):

            if not reverse:
                # If applying patch to original string, remove the line
                del final_text[current_line_number - 1]
                current_line_number -= 1

            else:
                # If in reverse, add the line
                # This will change the line from "-*rest of the line*" to "*rest of the line*"
                line = line[1:]
                final_text.insert(current_line_number - 1, line)

        # If a line was added
        elif line.startswith("+"):
            if not reverse:
                # If applying patch to the original string, add the line
                # This will change the line from "+*rest of the line*" to "*rest of the line*"
                line = line[1:]
                final_text.insert(current_line_number - 1, line)

            else:
                # If in reverse, remove the line
                del final_text[current_line_number - 1]
                current_line_number -= 1

    # This will return it as one string with newlines between every line
    return "\n".join(final_text).rstrip()
