#!/usr/bin/env python

import argparse
import os
import uuid
import re
import asyncio
import http
from typing import Optional

import aiohttp
import aiofiles
from playwright.async_api import Page, async_playwright


def _correct_image_url(url: str) -> str:
    """Preprocesses the image URL to remove extra slashes."""
    corrected_url = re.sub(r"^//", r"https://", url)
    return corrected_url


async def collect_image_urls(
    page: Page,
    query: str,
    max_images: int,
) -> list[str]:
    """Collects image URLs from DuckDuckGo."""
    await page.goto(
        f"https://duckduckgo.com/?t=h_&q={query}&iax=images&ia=images"
    )
    await asyncio.sleep(7)  # Wait for the page to load

    image_elements = await page.query_selector_all(
        "xpath=//img[contains(@class, 'tile--img__img')]"
    )
    image_urls = [
        _correct_image_url(await img.get_attribute("src"))
        for img in image_elements[:max_images]
    ]
    return image_urls


def _get_file_extension_from_mime(mime: str) -> Optional[str]:
    """Converts a MIME to a file extension."""
    mime_to_extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
    }
    return mime_to_extension.get(mime)


async def _save_image(
    response: aiohttp.ClientResponse,
    output_dir: str,
) -> None:
    """Saves the image to the specified directory."""
    content_type = response.headers.get("content-type")
    file_extension = _get_file_extension_from_mime(content_type)
    if file_extension is None:
        print(f"Skipping `{response.url}` due to unsupported MIME type...")
        return None

    unique_id = uuid.uuid4().hex[:15]
    file_path = os.path.join(output_dir, f"{unique_id}{file_extension}")

    async with aiofiles.open(file_path, mode="wb") as f:
        async for chunk in response.content:
            await f.write(chunk)

    print(f"Downloaded `{response.url}` to `{file_path}`.")


async def download_images(image_urls: list[str], output_dir: str) -> None:
    """Downloads images from the given URLs and saves them to the specified directory."""
    os.makedirs(output_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for image_url in image_urls:
            try:
                async with session.get(image_url) as response:
                    if response.status != http.HTTPStatus.OK:
                        print(f"Failed to download `{image_url}`...")
                        continue

                    await _save_image(response, output_dir)
            except Exception as e:
                print(f"Error downloading `{image_url}`: {e}")


async def main(args: argparse.Namespace) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        image_urls = await collect_image_urls(page, args.query, args.max_images)
        await download_images(image_urls, args.output_dir)

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download images from DuckDuckGo."
    )
    parser.add_argument(
        "query", type=str, help="write what you are looking for"
    )
    parser.add_argument(
        "-m",
        "--max-images",
        type=int,
        default=5,
        help="maximum images to download",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="collected-images",
        help="a folder to store images",
    )
    args = parser.parse_args()

    asyncio.run(main(args))
