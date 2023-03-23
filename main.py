import asyncio
from bs4 import BeautifulSoup, Comment
import requests
import httpx
import random

BASE_URL = 'https://erowid.org/experiences/'
## it will take more time, but at least I wont be doing some bodged up thing with proxies for requests
SEMAPHORE_LIMIT = 5
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

def fetch_experience_uris():
    try:
        print("Fetching experience uris...")
        response = requests.get(f'{BASE_URL}exp.cgi?ShowViews=0&Cellar=0&Start=0&Max=100000')
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching experience uris: {e}")
        return []

    soup_parser = BeautifulSoup(response.content, 'html.parser')
    exp_rows = soup_parser.select('tr[class=""]')
    experience_uris = [row.select('td a')[0].get('href') for row in exp_rows if row.select('td a')]
    print(f"Found {len(experience_uris)} experience uris")
    return experience_uris

async def fetch_experience_page(client, uri):
    async with semaphore:
        try:
            await asyncio.sleep(random.uniform(2, 5))  
            response = await client.get(f'{BASE_URL}{uri}')
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Error while fetching experience page {BASE_URL}{uri}  {e}. Status code: {response.status_code}")
            return (None, uri)
        except httpx.RequestError as e:
            print(f"Error while sending request to experience page {BASE_URL}{uri}  {e}")
            return (None, uri)
        except Exception as e:
            print(f"Unexpected error while fetching experience page {BASE_URL}{uri}  {e}")
            return (None, uri)

        exp_page = BeautifulSoup(response.content, 'html.parser')
        print('Page content has been parsed successfully')
        
        print(f'Fetched and parsed experience page: {BASE_URL}{uri}')
        return (exp_page, None)

async def fetch_experience_pages_concurrently(experience_uris):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_experience_page(client, uri) for uri in experience_uris]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # result[0]: page CONTENT or None if the search has failed.
        # result[1]: page URI which has FAILED to be fetched or None if the search has been successful.
        exp_pages_content = [result[0] for result in results if result[0] is not None]
        failed_uris = [result[1] for result in results if result[1] is not None]
    return exp_pages_content, failed_uris    

def format_experience_page_content(exp_pages_content):
    formatted_data = []   
    for exp_page in exp_pages_content:
        exp_content = exp_page.select_one('div[class"report-text-surround"]')
        if exp_content:
            start_comment = exp_content.find(string=lambda string: isinstance(string, Comment) and 'Start Body' in string)
            end_comment = exp_content.find(string=lambda string: isinstance(string, Comment) and 'End Body' in string)
            
            content = start_comment.find_all_next(string=True)
            page_report = content[:content.index(end_comment)]
            body_text = ''.join(page_report)

            formatted_info = {
                'body_text': body_text,
                'dose_chart': exp_content.select_one('table=[class="dosechart"]'),
                'body_weight': exp_content.select_one('table=[class="bodyweight"]'),
                'exp_footer_data': exp_content.select_one('table=[class="footdata"]'),
            }

        formatted_data.append(formatted_info)
    print('Data has been formatted and saved dict')
    return formatted_data

async def main():
    experience_uris = fetch_experience_uris()
    if experience_uris:
        print("Fetching experience pages...")
        experience_pages, failed_uris = await fetch_experience_pages_concurrently(experience_uris)
        print(f"Fetched {len(experience_pages)} experience pages")
        print(f"{len(failed_uris)} uris failed, retrying...")

        if failed_uris:
            retried_experience_pages, _ = await fetch_experience_pages_concurrently(failed_uris)
            experience_pages.extend(retried_experience_pages)
            print(f"Fetched {len(retried_experience_pages)} retried experience pages")
    print("--------------------- finished requests ---------------------")
    
asyncio.run(main())
