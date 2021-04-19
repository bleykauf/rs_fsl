from ._version import get_versions  # noqa

__version__ = get_versions()["version"]
del get_versions

from .rs_fsl import FSL, read_csv
