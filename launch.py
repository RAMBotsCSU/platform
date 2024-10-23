import asyncio

from robot import Sparky

async def main():
    async with Sparky() as sparky:
        await sparky.run()


if __name__ == "__main__":
    asyncio.run(main())
