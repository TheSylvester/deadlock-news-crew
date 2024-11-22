import httpx
from typing import Dict, Any, Optional, List

class StrapiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def get_author_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an author by name"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/authors",
                headers=self.headers,
                params={
                    "filters[name][$eq]": name,
                    "populate": "*"
                }
            )
            response.raise_for_status()
            data = response.json()
            return {"data": data["data"][0]} if data["data"] else None

    async def get_tag_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get a tag by slug"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tags",
                headers=self.headers,
                params={
                    "filters[slug][$eq]": slug,
                    "populate": "*"
                }
            )
            response.raise_for_status()
            data = response.json()
            return {"data": data["data"][0]} if data["data"] else None

    async def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get an article by slug"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/articles",
                headers=self.headers,
                params={
                    "filters[slug][$eq]": slug,
                    "populate": "*"
                }
            )
            response.raise_for_status()
            data = response.json()
            return {"data": data["data"][0]} if data["data"] else None

    async def create_author(self, name: str, bio: str, avatar_url: str) -> Dict[str, Any]:
        """Create an author with the given details"""
        # Check if author already exists
        existing_author = await self.get_author_by_name(name)
        if existing_author:
            print(f"Author '{name}' already exists with ID: {existing_author['data']['id']}")
            return existing_author

        async with httpx.AsyncClient() as client:
            # First download the avatar image
            image_response = await client.get(avatar_url)
            image_response.raise_for_status()
            image_data = image_response.content
            
            # Prepare the file upload
            files = {
                'files': (f"{name.lower()}-avatar.jpg", image_data, 'image/jpeg')
            }
            headers = {
                "Authorization": f"Bearer {self.token}"
            }  # Don't include Content-Type here, it will be set automatically for multipart

            # Upload the avatar
            upload_response = await client.post(
                f"{self.base_url}/upload",
                headers=headers,
                files=files
            )
            upload_response.raise_for_status()
            avatar_id = upload_response.json()[0]["id"]  # Strapi returns an array of uploaded files

            # Create the author
            author_data = {
                "data": {
                    "name": name,
                    "bio": bio,
                    "avatar": avatar_id
                }
            }
            
            response = await client.post(
                f"{self.base_url}/authors",
                headers=self.headers,
                json=author_data
            )
            response.raise_for_status()
            return response.json()

    async def create_tag(self, name: str, slug: str) -> Dict[str, Any]:
        """Create a tag with the given details"""
        # Check if tag already exists
        existing_tag = await self.get_tag_by_slug(slug)
        if existing_tag:
            print(f"Tag '{name}' already exists with ID: {existing_tag['data']['id']}")
            return existing_tag

        data = {
            "data": {
                "name": name,
                "slug": slug
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tags",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def create_article(
        self,
        title: str,
        content: str,
        excerpt: str,
        slug: str,
        published: str,
        cover_url: str,
        author_id: int,
        tag_ids: List[int]
    ) -> Dict[str, Any]:
        """Create an article with the given details"""
        # Check if article already exists
        existing_article = await self.get_article_by_slug(slug)
        if existing_article:
            print(f"Article '{title}' already exists with ID: {existing_article['data']['id']}")
            return existing_article

        async with httpx.AsyncClient() as client:
            # First download the cover image
            image_response = await client.get(cover_url)
            image_response.raise_for_status()
            image_data = image_response.content
            
            # Prepare the file upload
            files = {
                'files': (f"{slug}-cover.jpg", image_data, 'image/jpeg')
            }
            headers = {
                "Authorization": f"Bearer {self.token}"
            }  # Don't include Content-Type here, it will be set automatically for multipart

            # Upload the cover image
            upload_response = await client.post(
                f"{self.base_url}/upload",
                headers=headers,
                files=files
            )
            upload_response.raise_for_status()
            cover_id = upload_response.json()[0]["id"]  # Strapi returns an array of uploaded files

            # Create the article
            article_data = {
                "data": {
                    "title": title,
                    "content": content,
                    "excerpt": excerpt,
                    "slug": slug,
                    "publishedAt": published,  # Changed from published to publishedAt
                    "cover": cover_id,
                    "author": {
                        "connect": [author_id]
                    },
                    "tags": {
                        "connect": tag_ids
                    }
                }
            }
            
            response = await client.post(
                f"{self.base_url}/articles",
                headers=self.headers,
                json=article_data
            )
            response.raise_for_status()
            return response.json()
