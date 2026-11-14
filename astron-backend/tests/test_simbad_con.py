import asyncio

from app.providers.simbad import search_objects

async def main():
    try:
        result = await search_objects(
            ra=83.6331,
            dec=22.0145,
            radius=0.5,
            limit=100,
        )

        print("SIMBAD connection: SUCCESS")
        print("Response keys:", result.keys())
        print("Metadata:", result.get("metadata"))
        print("Data:", result.get("data"))


    except Exception as error:
        print("SIMBAD connection: FAILED")
        print(type(error).__name__, error)

    if __name__ == "__main__":
        asyncio.run(main())