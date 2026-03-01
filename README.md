# pypi-changes

[![PyPI](https://img.shields.io/pypi/v/pypi-changes?style=flat-square)](https://pypi.org/project/pypi-changes/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pypi-changes.svg)](https://pypi.org/project/pypi-changes/)
[![check](https://github.com/gaborbernat/pypi_changes/actions/workflows/check.yaml/badge.svg)](https://github.com/gaborbernat/pypi_changes/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/pypi-changes/month)](https://pepy.tech/project/pypi-changes)

A CLI tool that inspects a Python interpreter's installed packages and compares them against the latest releases on
PyPI. It shows which packages are outdated, how long ago each release was published, and highlights major version bumps
so you can make informed upgrade decisions.

[![asciicast](https://asciinema.org/a/446966.svg)](https://asciinema.org/a/446966)

## Getting started

Install from PyPI:

```bash
pip install pypi-changes
```

Run against the current Python interpreter:

```bash
pypi-changes
```

Or point it at a specific interpreter (useful for checking virtual environments):

```bash
pypi-changes /path/to/venv/bin/python
```

## How-to guides

### Check for outdated packages

Run `pypi-changes` without arguments to see a tree of all installed packages with their version status. Outdated
packages appear in red, with major version bumps in bold red:

```console
$ pypi-changes
🐍 Distributions within /usr/bin/python
├── virtualenv 20.38.0 10 days remote 21.1.0 2 days
├── certifi 2026.1.4 2 months remote 2026.2.25 4 days
├── rich 14.3.3 9 days
├── packaging 26.0 a month
├── urllib3 1.26.20 1 year, 6 months remote 2.6.3 2 months
├── requests 2.32.5 6 months
├── pluggy 1.6.0 10 months
└── covdefaults 2.3.0 2 years
```

### Generate a requirements file for upgrades

Use the `requirements` output format to produce a `requirements.txt`-compatible list of outdated packages pinned to
their latest versions:

```console
$ pypi-changes --output requirements
virtualenv==21.1.0
certifi==2026.2.25
urllib3==2.6.3
wheel-filename==2.1.0
```

Pipe directly into `pip install` to upgrade:

```bash
pypi-changes --output requirements > upgrades.txt
pip install -r upgrades.txt
```

### Get machine-readable output

Use JSON output for scripting or integration with other tools:

```console
$ pypi-changes --output json
[
  {
    "name": "virtualenv",
    "version": "20.38.0",
    "up_to_date": false,
    "current": {
      "version": "20.38.0",
      "date": "2026-02-19T07:47:59.778389+00:00",
      "since": "10 days"
    },
    "latest": {
      "version": "21.1.0",
      "date": "2026-02-27T08:49:27.516392+00:00",
      "since": "2 days"
    }
  },
  {
    "name": "rich",
    "version": "14.3.3",
    "up_to_date": true,
    "current": {
      "version": "14.3.3",
      "date": "2026-02-19T17:23:13.732467+00:00",
      "since": "9 days"
    },
    "latest": {
      "version": "14.3.3",
      "date": "2026-02-19T17:23:13.732467+00:00",
      "since": "9 days"
    }
  }
]
```

Each entry includes `name`, `version`, `up_to_date`, and detailed `current`/`latest` release information with dates and
human-readable time deltas.

### Sort packages alphabetically

By default, packages are sorted by release date (most recently updated first). To sort alphabetically:

```bash
pypi-changes --sort alphabetic
```

### Speed up repeated runs with caching

Requests to PyPI are cached in a local SQLite database for 1 hour by default. To adjust the cache duration:

```bash
pypi-changes --cache-duration 7200  # cache for 2 hours
pypi-changes --cache-duration 0     # bypass cache entirely
pypi-changes --cache-duration -1    # cache forever
```

To change the cache file location:

```bash
pypi-changes --cache-path /tmp/pypi-cache.sqlite
```

### Use with a private package index

Set the `PIP_INDEX_URL` environment variable to merge releases from a private index server (e.g. Artifactory) with PyPI
data:

```bash
PIP_INDEX_URL=https://my-artifactory.example.com/simple pypi-changes
```

### Control request parallelism

PyPI release information is fetched in parallel. Adjust the number of concurrent requests with `--jobs`:

```bash
pypi-changes --jobs 20  # increase parallelism
pypi-changes --jobs 1   # sequential requests
```

## Reference

### Usage

```
pypi-changes [-h] [--jobs COUNT] [--cache-path PATH] [--cache-duration SEC]
             [--sort [{a,alphabetic,u,updated}]] [--output {tree,json,requirements}]
             [PYTHON_EXE]
```

### Positional arguments

| Argument     | Description                                                           |
| ------------ | --------------------------------------------------------------------- |
| `PYTHON_EXE` | Python interpreter to inspect. Defaults to `python` found on `$PATH`. |

### Options

| Flag                     | Default       | Description                                                                          |
| ------------------------ | ------------- | ------------------------------------------------------------------------------------ |
| `--jobs`, `-j`           | `10`          | Maximum number of parallel requests when loading distribution information from PyPI. |
| `--cache-path`, `-c`     | platform path | Path to the SQLite file used for caching HTTP requests.                              |
| `--cache-duration`, `-d` | `3600`        | Seconds to cache requests. `0` bypasses the cache, `-1` caches forever.              |
| `--sort`, `-s`           | `updated`     | Sort order: `a`/`alphabetic` or `u`/`updated` (most recent first).                   |
| `--output`, `-o`         | `tree`        | Output format: `tree`, `json`, or `requirements`.                                    |

### Output formats

**`tree`** (default) -- a Rich-rendered tree showing each package with its installed version, time since release, and
remote version if outdated. Major version bumps appear in bold red; minor/patch bumps in red.

**`json`** -- a JSON array where each element contains:

- `name` -- package name
- `version` -- installed version
- `up_to_date` -- boolean
- `current` -- object with `version`, `date` (ISO 8601), and `since` (human-readable delta)
- `latest` -- object with the same fields for the newest stable release

**`requirements`** -- prints only outdated packages in `name==version` format, suitable for piping into
`pip install -r`.

### Environment variables

| Variable        | Description                                                                                |
| --------------- | ------------------------------------------------------------------------------------------ |
| `PIP_INDEX_URL` | When set to a non-PyPI URL, merges releases from that index server with PyPI release data. |

## How it works

`pypi-changes` inspects the target Python interpreter's `sys.path` to discover all installed distributions (packages
with `.dist-info` or `.egg-info` directories). It then fetches each package's release history from the
[PyPI JSON API](https://warehouse.pypa.io/api-reference/json/) in parallel, using a thread pool controlled by `--jobs`.

Releases are sorted by semantic version. The latest stable release (excluding dev and pre-releases) is selected for
comparison against the installed version. When a release has no uploaded artifacts (common for some yanked or
placeholder versions), a synthesized timestamp is generated internally for sorting purposes but is not displayed to the
user.

HTTP responses are cached in a local SQLite database via
[requests-cache](https://requests-cache.readthedocs.io/en/stable/) to avoid redundant network calls on repeated runs.
Expired entries are cleaned up automatically on each invocation.

When `PIP_INDEX_URL` is set to a non-PyPI URL, `pypi-changes` also queries that index via the
[Simple Repository API](https://packaging.python.org/en/latest/specifications/simple-repository-api/) and merges any
versions not found on PyPI into the release list. This is useful for organizations hosting internal packages on private
registries.
