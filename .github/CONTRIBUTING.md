# Contributing to `pypi_changes`

Thank you for your interest in contributing to `pypi_changes`! There are many ways to contribute, and we appreciate all
of them. As a reminder, all contributors are expected to follow our [Code of Conduct][coc].

## Development Documentation

Our [development documentation](http://tox.readthedocs.org/en/latest/development.html#development) contains details on
how to get started with contributing to `tox`, and details of our development processes.

## Release notes

Add a `changelog.d/+short-name.<type>.md` fragment for each user-facing change. The name must be unique in the pull
request. During release preparation, `release-creator fragments --git` links each fragment to its merged squash pull
request and credits the pull request author. It reads the number from the squash commit subject, so you can name
fragments before a pull request exists.

Use these fragment types:

- `feature` for additions and Python support additions or removals, rendered under **Added**.
- `change` for other user-visible changes, rendered under **Changes**.
- `bugfix` for fixes, rendered under **Fixed**.
- `doc` for user-facing documentation changes.
- `breaking` for changes that require users to update their code or configuration. Python support removals are features.
- `security`, `performance`, `deprecation`, `removal`, and `packaging` for changes in those areas.

Write each fragment for package users. Omit internal maintenance with the `skip news` label; the label can be added
after the pull request opens. Add a `by` credit only when multiple people wrote the change. List each human author in
the same `by` phrase, such as `by [@alice](https://github.com/alice) and [@bob](https://github.com/bob)`. Do not credit
bots or reviewers. A bot-authored pull request needs no fragment unless it contains a user-facing change and provides
one.

[coc]: https://www.pypa.io/en/latest/code-of-conduct/
