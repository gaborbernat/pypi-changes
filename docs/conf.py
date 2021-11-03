from __future__ import annotations

from datetime import date, datetime

from pypi_changes import __version__

company = "gaborbernat"
name = "pypi-changes"
version = ".".join(__version__.split(".")[:2])
release = __version__
copyright = f"2021-{date.today().year}, {company}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_argparse_cli",
    "sphinx_autodoc_typehints",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
]

templates_path = []
unused_docs = []
source_suffix = ".rst"
exclude_patterns = ["changelog/*", "_draft.rst"]

master_doc = "index"
pygments_style = "default"

project = name
today_fmt = "%B %d, %Y"

html_theme = "furo"
html_theme_options = {
    "navigation_with_keys": True,
}
html_title = "pypi changes"
html_last_updated_fmt = datetime.now().isoformat()

autoclass_content = "class"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "none"
always_document_param_types = False
typehints_fully_qualified = True
autosectionlabel_prefix_document = True

extlinks = {
    "issue": ("https://github.com/gaborbernat/pypi_changes/issues/%s", "#"),
    "pull": ("https://github.com/gaborbernat/pypi_changes/pull/%s", "PR #"),
    "user": ("https://github.com/%s", "@"),
    "pypi": ("https://pypi.org/project/%s", ""),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "packaging": ("https://packaging.pypa.io/en/latest", None),
}
nitpicky = True
nitpick_ignore = []
