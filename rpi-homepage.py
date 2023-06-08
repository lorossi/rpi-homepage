"""This module contains the logic to handle the homepage."""
from __future__ import annotations

import logging

from modules.rpiserver import RPiServer


def main():
    """Program entry point, starting the server."""
    logging.basicConfig(
        filename=__file__.replace(".py", ".log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )

    r = RPiServer()
    r.start()


if __name__ == "__main__":
    main()
