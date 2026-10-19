"""This module contains the logic to handle the homepage."""

import asyncio

from modules.logs import setup_logging
from modules.rpiserver import serve


async def main() -> None:
    """Program entry point, starting the server."""
    setup_logging()
    await serve()


if __name__ == "__main__":
    asyncio.run(main())
