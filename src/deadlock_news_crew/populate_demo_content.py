import asyncio
import os
from strapi_client import StrapiClient
from demo_data import DEMO_AUTHOR, DEMO_TAG, DEMO_ARTICLES

async def populate_demo_content():
    # Initialize the Strapi client
    base_url = "http://localhost:3001/api"
    token = os.getenv("STRAPI_TOKEN", "95f938fcdd601facdc9f8b142bf9089cff0572030b6483c79b8500f713e349993b5212e83e8ea6089038ab7355ce835fc03650b77f07e40f9472c7b2119d84ea9a3ea166370371d7c1f415b4ed54c0e15c3f337397300e5e14282c73d35d89916f13445acb3d546c8846e14ca8275c961c6924b48cd11e83e5512fa3901182df")
    client = StrapiClient(base_url, token)

    try:
        # Create author
        print("Creating author...")
        author_response = await client.create_author(
            name=DEMO_AUTHOR["name"],
            bio=DEMO_AUTHOR["bio"],
            avatar_url=DEMO_AUTHOR["avatar_url"]
        )
        author_id = author_response["data"]["id"]
        print(f"Created author with ID: {author_id}")

        # Create tag
        print("Creating tag...")
        tag_response = await client.create_tag(
            name=DEMO_TAG["name"],
            slug=DEMO_TAG["slug"]
        )
        tag_id = tag_response["data"]["id"]
        print(f"Created tag with ID: {tag_id}")

        # Create articles
        print("Creating articles...")
        for article in DEMO_ARTICLES:
            article_response = await client.create_article(
                title=article["title"],
                content=article["content"],
                excerpt=article["excerpt"],
                slug=article["slug"],
                published=article["published"],
                cover_url=article["cover_url"],
                author_id=author_id,
                tag_ids=[tag_id]
            )
            print(f"Created article: {article['title']}")

        print("Demo content population completed successfully!")

    except Exception as e:
        print(f"Error populating demo content: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_demo_content())
