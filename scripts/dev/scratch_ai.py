import asyncio
from freeGPT import Client

async def main():
    try:
        resp = Client.create_completion("gpt3", "Ce este polimorfismul?")
        print("SUCCESS:", resp)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(main())
