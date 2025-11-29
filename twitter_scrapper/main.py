import json
import asyncio
from twikit import Client

client = Client('en-US')

async def main():
    # Load cookies (not async)
    client.load_cookies('cookies_converted.json')

    # Now you can make requests
    query = 'AI since:2025-10-30 until:2025-11-01 lang:en'
    tweets = await client.search_tweet(query, "Latest")
    for tweet in tweets:
        print(tweet.created_at, '-', tweet.user.name, ':', tweet.text)
    


asyncio.run(main())