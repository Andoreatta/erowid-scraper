import asyncio
from bs4 import BeautifulSoup, Comment
import requests
import httpx
import random

#Semaphore initiated outside of asyncio.run() grabs the asyncio 
# "default" loop and so cannot be used with the event loop created with asyncio.run().
#so i initiated semaphore from main

BASE_URL = 'https://erowid.org/experiences/'
## it will take more time, but at least I wont be doing some bodged up thing with proxies for requests
contents = set()


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

async def fetch_experience_page(client, uri, semaphore):

    async with semaphore:
        try:
            await asyncio.sleep(random.uniform(2, 5))  
            response = await client.get(f'{BASE_URL}{uri}')
            response.raise_for_status()
        except asyncio.SendfileNotAvailableError as e:
            print(f"Unexpected error while fetching experience page {BASE_URL}{uri}  {e}")
            return (None, uri)
        except httpx.HTTPStatusError as e:
            print(f"Error while fetching experience page {BASE_URL}{uri}  {e}. Status code: {response.status_code}")
            return (None, uri)
        except httpx.RequestError as e:
            print(f"Error while sending request to experience page {BASE_URL}{uri}  {e.with_traceback}")
            return (None, uri)
        except Exception as e:
            print(f"Unexpected error while fetching experience page {BASE_URL}{uri}  {e}")
            return (None, uri)

        exp_page = BeautifulSoup(response.content, 'html.parser')
        print('Page content has been parsed successfully')
        
        print(f'Fetched and parsed experience page: {BASE_URL}{uri}')
        return (exp_page, None)

async def fetch_experience_pages_concurrently(experience_uris, sem):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_experience_page(client, uri,sem) for uri in experience_uris]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # result[0]: page CONTENT or None if the search has failed.
        # result[1]: page URI which has FAILED to be fetched or None if the search has been successful.
        ##[result[0] for result in results if result[0] is not None] TypeError: 'RuntimeError' object is not subscriptable--semaphore problem--
        exp_pages_content = [result[0] for result in results if result[0] is not None]
        failed_uris = [result[1] for result in results if result[1] is not None]
    return exp_pages_content, failed_uris    

def format_experience_page_content(exp_pages_content):
    formatted_data = []   
    for exp_page in exp_pages_content:
        exp_content = exp_page.select_one('div[class"report-text-surround"]')
        if exp_content:
            # the anonymous function is executed for each string iterated to check if it contains 'Start Body', might be slow, will test in the future.
            start_comment = exp_content.find(string=lambda string: isinstance(string, Comment) and 'Start Body' in string)
            end_comment = exp_content.find(string=lambda string: isinstance(string, Comment) and 'End Body' in string)
            # string=True is only to return text and nothing else
            author = exp_page.select('div.author>a')
            content = start_comment.find_all_next(string=True)
            page_report = content[:content.index(end_comment)]
            body_text = ''.join(page_report)
            trs = exp_content.select('table[class="footdata"] > tr ')


            author_dict={
                'username':author[0].text,
                'gender':trs[1].text[trs[1].index(":")+1:].strip(),
                
            }

            exp_dict={
                'title':exp_page.select_one('.title').text,
                'body_text': body_text.text,
                'body_weight': int(exp_content.select_one('table=[class="bodyweight"]').text),
                'age':int(trs[2].text[trs[2].index(":")+1:].strip()),
                'exp_year':int(trs[0].text[trs[0].index(":")+1:trs[0].index("ExpID")]),
                'pub_date':trs[3].text[trs[3].index(":")+1:trs[3].index("Views")]
            }


            formatted_info = {
                'author':author_dict,
                'exp':exp_dict
            }

        formatted_data.append(formatted_info)
    print('Data has been formatted and saved to dict')
    return formatted_data

async def main():
    experience_uris = fetch_experience_uris()

    contents = set()
    SEMAPHORE_LIMIT = 5
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    if experience_uris:
        print("Fetching experience pages...")
        experience_pages, failed_uris = await fetch_experience_pages_concurrently(experience_uris, semaphore)
        print(f"Fetched {len(experience_pages)} experience pages")
        print(f"{len(failed_uris)} uris failed, retrying...")

        {contents.add(page) for page in experience_pages }



        if failed_uris:
            retried_experience_pages, _ = await fetch_experience_pages_concurrently(failed_uris)
            experience_pages.extend(retried_experience_pages)
            print(f"Fetched {len(retried_experience_pages)} retried experience pages")
    

    print("--------------------- finished requests ---------------------")

asyncio.run(main())
form = format_experience_page_content(contents)
print(form)