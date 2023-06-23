"""This module contains the logic to handle the homepage."""
from __future__ import annotations

import asyncio

from modules.rpiserver import RPiServer


async def main():
    """Program entry point, starting the server."""
    r = RPiServer()
    await r.startAsync()


if __name__ == "__main__":
    asyncio.run(main())
