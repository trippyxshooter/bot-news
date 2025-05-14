import asyncio
from app.fetchers.github import GitHubTrendingFetcher
from app.models import Source
from app.db import db

async def main():
    source = Source(
        id='github_trend',
        name='GitHub Trending AI',
        type='scrap',
        url='https://github.com/trending?since=daily&topic=ai',
        interval=60,
        lang='en',
        weight=1,
        active=True
    )
    fetcher = GitHubTrendingFetcher(source)
    items = await fetcher.fetch()
    print(f'Fetched: {len(items)}')
    added = 0
    for item in items:
        if db.add_news_item(item):
            print(f'Added: {item.title} | {item.url}')
            added += 1
        else:
            print(f'Skipped (duplicate?): {item.title}')
    await fetcher.close()
    print(f'Added to DB: {added}')

if __name__ == "__main__":
    asyncio.run(main()) 