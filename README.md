# PVCS

A toy vcs. There isn't really any reason to not use `git` instead

<sup>Please don't blame me if you lose all your work</sup>

A quick demo can be seen [here](https://asciinema.org/a/52rh6e8ywncow1tc6hh51z4xc)

# Usage

| Command | Function |
|:-------:|:--------:|
| `pvcs init` | Initialize folder for tracking |
| `pvcs stage` | Add a file to the "stage". It will be included in the next commit |
| `pvcs unstage` | Remove a file from the "stage" |
| `pvcs commit` | Create a commit (a snapshot of the current state of everything) |
| `pvcs log` | Display commit history |
| `pvcs revert` | Revert to a specified commit, or back `n` versions |
| `pvcs status` | Display relevant information e.g. files that are staged |
