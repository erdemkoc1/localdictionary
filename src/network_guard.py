"""Process-local network kill switch for the desktop application.

The release has no network feature. This guard is defense in depth against a
future transitive dependency accidentally attempting Python-level network I/O.
It does not contact or inspect the network.
"""

from __future__ import annotations

import socket


_installed = False


def enforce_no_network() -> None:
    """Block common Python socket paths for the lifetime of this process."""
    global _installed
    if _installed:
        return

    def blocked(*_args, **_kwargs):
        raise RuntimeError("LocalDictionary runtime network access is disabled")

    socket.getaddrinfo = blocked
    socket.create_connection = blocked
    socket.socket.connect = blocked
    socket.socket.connect_ex = blocked
    _installed = True
