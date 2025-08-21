from typing import Tuple

from .__about__ import __package_name__, __version__

class _Metadata:
    __package_name__ = __package_name__
    __version__ = __version__


__all__: Tuple[str, ...] = ("_Metadata",)
