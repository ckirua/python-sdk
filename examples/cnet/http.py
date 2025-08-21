from sdk.cnet import HTTPClient, HTTPRequest

async def main():
    async with HTTPClient() as client:
        response = await client.request(HTTPRequest("https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD", "GET"))
        print(response.content)
        print(response.status_code)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())