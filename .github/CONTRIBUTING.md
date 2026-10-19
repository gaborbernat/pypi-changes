# Contributing to `pypi_changes`

Thank you for your interest in contributing to `pypi_changes`! There are many ways to contribute, and we appreciate all
of them. As a reminder, all contributors are expected to follow our [Code of Conduct][coc].

## Development Documentation

Our [development documentation](http://tox.readthedocs.org/en/latest/development.html#development) contains details on
how to get started with contributing to `tox`, and details of our development processes.

## Release notes

Add a `changelog.d/+short-name.<type>.md` fragment for each user-facing change. The name must be unique in the pull
request. Towncrier links the fragment to its merged squash pull request, so the filename does not need an issue or pull
request number.

Use these fragment types:

- `feature` for additions, rendered under **Added**.
- `change` for other user-visible changes, rendered under **Changes**.
- `bugfix` for fixes, rendered under **Fixed**.
- `doc` for user-facing documentation changes.
- `breaking` for changes that require users to update their code or configuration.
- `security`, `performance`, `deprecation`, `removal`, and `packaging` for changes in those areas.

Write each fragment for package users. Omit internal maintenance with the `skip news` label; the label can be added
after the pull request opens. For human authors, add a credit such as `by [@alice](https://github.com/alice)` at the end
of the fragment. List multiple authors in the same `by` phrase. Do not credit bots or reviewers. A bot-authored pull
request needs no fragment unless it contains a user-facing change and provides one.

[coc]: https://www.pypa.io/en/latest/code-of-conduct/
