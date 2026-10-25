# Contributing to pypi-changes

Read the [Code of Conduct][coc] before contributing.

## Development

Create an editable environment with `tox -e dev`. Before opening a pull request, run the project checks and formatter:

```bash
tox -e 3.15,type,pkg_meta
prek run --all-files
```

## Release notes

Add a `changelog.d/+short-name.<type>.md` fragment for each user-facing change. The name must be unique in the pull
request. During release preparation, `release-creator fragments` links each fragment to its merged squash pull request
and credits the authors of that commit: the pull request author plus every `Co-authored-by` co-author. It reads the
number from the squash commit subject, so you can name fragments before a pull request exists. Preparation then runs
`release-creator contributors` to list first-time contributors at the end of the version's changelog section.

Use these fragment types:

- `feature` for additions and Python support additions or removals, rendered under **Added**.
- `change` for other user-visible changes, rendered under **Changes**.
- `bugfix` for fixes, rendered under **Fixed**.
- `doc` for user-facing documentation changes.
- `breaking` for changes that require users to update their code or configuration. Python support removals are features.
- `security`, `performance`, `deprecation`, `removal`, and `packaging` for changes in those areas.

Write each fragment for package users. Omit internal maintenance with the `skip news` label; the label can be added
after the pull request opens. Do not write credits or pull request links in fragments; to credit someone else who wrote
the change, add them as a `Co-authored-by` trailer on the commit. A bot-authored pull request needs no fragment unless
it contains a user-facing change and provides one.

[coc]: https://github.com/gaborbernat/pypi-changes/blob/main/CODE_OF_CONDUCT.md
