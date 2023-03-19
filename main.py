import asyncio
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import httpx
import random

BASE_URL = 'https://erowid.org/experiences/'
SEMAPHORE_LIMIT = 5
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

def fetch_experience_links():
    try:
        print("Fetching experience links...")
        response = requests.get(f'{BASE_URL}exp.cgi?ShowViews=0&Cellar=0&Start=0&Max=100000')
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching experience links: {e}")
        return []

    soupParser = BeautifulSoup(response.content, 'html.parser')
    expRows = soupParser.select('tr[class=""]')
    experience_links = [row.select('td a')[0].get('href') for row in expRows if row.select('td a')]
    print(f"Found {len(experience_links)} experience links")
    return experience_links

async def fetch_experience_page(client, link):
    async with semaphore:
        try:
            await asyncio.sleep(random.uniform(2, 5))  
            response = await client.get(f'{BASE_URL}{link}')
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Error while fetching experience page {BASE_URL}{link}  {e}. Status code: {response.status_code}")
            return (None, link)
        except httpx.RequestError as e:
            print(f"Error while sending request to experience page {BASE_URL}{link}  {e}")
            return (None, link)
        except Exception as e:
            print(f"Unexpected error while fetching experience page {BASE_URL}{link}  {e}")
            return (None, link)

        expPage = BeautifulSoup(response.content, 'html.parser')
        print(f'Fetched experience page: {BASE_URL}{link}')
        return (expPage, None)

async def fetch_experience_pages(experience_links):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_experience_page(client, link) for link in experience_links]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        expPages = [result[0] for result in results if result[0] is not None]
        failed_links = [result[1] for result in results if result[1] is not None]
    return expPages, failed_links
    
async def main():
    experience_links = fetch_experience_links()
    if experience_links:
        print("Fetching experience pages...")
        experience_pages, failed_links = await fetch_experience_pages(experience_links)
        print(f"Fetched {len(experience_pages)} experience pages")
        print(f"{len(failed_links)} links failed, retrying...")

        if failed_links:
            retried_experience_pages, _ = await fetch_experience_pages(failed_links)
            experience_pages.extend(retried_experience_pages)
            print(f"Fetched {len(retried_experience_pages)} retried experience pages")
    print("--------------------- finished requests ---------------------")
    
asyncio.run(main())
