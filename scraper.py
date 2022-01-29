from bs4 import BeautifulSoup
import csv
from time import sleep
import requests
from requests_html import AsyncHTMLSession


class Scraper:
    def __init__(self, cache_file, cache_key, fieldnames):
        self.cache_file = cache_file
        self.cache_key = cache_key
        self.cached_items = {}
        self.fieldnames = fieldnames

        if cache_file:
            try:
                with open(cache_file, 'r') as cachefile:
                    cacheReader = csv.DictReader(
                        cachefile, delimiter=str('\t'), fieldnames=self.fieldnames)
                    self.cached_items = {
                        item[self.cache_key]: item for item in cacheReader}
                    self.new_cache = False
            except FileNotFoundError:
                print("Creating new cache file")
                self.new_cache = True

    async def get_data(self, title, author):
        raise NotImplementedError()

    def append_additional_records(self, book):
        if not self.cache_file:
            return

        with open(self.cache_file, 'a') as cache_file_handle:
            writer = csv.DictWriter(
                cache_file_handle, delimiter=str('\t'), fieldnames=self.fieldnames)
            writer.writerow(book)

    async def scrape_books(self, books):
        """
        books: Expecting a list of books in the form: {index: {'title': title, 'authors': ['list','of', 'authors]}}
        """
        scraped_books = []

        queue = set(books.keys())
        for retries in range(20):
            fail_queue = set()
            if len(queue) == 0:
                break

            print(f"=== queue length {len(queue)} ===")

            for idx in queue:
                book = books[idx]
                if book['title'] in self.cached_items:
                    cached_book = self.cached_items[book['title']]
                    cached_book['index'] = idx
                    scraped_books.append(cached_book)
                    continue

                try:
                    author = book['authors'][0] if book['authors'] else ''
                    scraped_data = await self.get_data(book['title'], author)
                    scraped_data['index'] = idx
                    scraped_data['title_from_src'] = book['title']
                    scraped_books.append(scraped_data)
                    self.append_additional_records(scraped_data)

                    print(scraped_data)
                    sleep(5)

                except LookupError as e:
                    print("book not found:", book['title'])
                    continue
                except RuntimeError as e:
                    print(type(e), e)
                    exit()
                except Exception as e:
                    print(type(e), e)
                    print(f'failed to fetch {idx} {book}, retrying')
                    fail_queue.add(idx)
                    continue

            queue = fail_queue

            if queue:
                print("sleeping for 15 minutes")
                for i in range(60*15):
                    try:
                        sleep(1)
                    except KeyboardInterrupt:
                        exit(0)
        return scraped_books


class OverdriveScraper(Scraper):
    def __init__(self, url, cache_file):
        self.url = url
        self.fieldnames = ['index', 'title_from_src',
                           'title', 'audiobook', 'ebook', 'available', 'link']
        super().__init__(cache_file, 'title', self.fieldnames)

    async def _get_base_div(self, title, author):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                   "Accept": "*/*"}

        params = {'query': title + " " + author}

        try:
            session = AsyncHTMLSession()
            r = await session.get(self.url, headers=headers, params=params)
            await r.html.arender()
            await session.close()

        except Exception as e:
            print(type(e), e)
            if session:
                await session.close()
            raise Exception(f"{type(e)}: {e}")

        content = r.html.html
        url = r.html.url
        soup = BeautifulSoup(content, features="html.parser")

        d = soup.find('section', attrs={'id': 'search'})
        d = d.find('div', attrs={'id': 'main'})
        return d, content, url

    async def get_data(self, title, author):
        d = None
        count = 0
        while d is None and count < 2:
            sleep(15)
            d, content, link = await self._get_base_div(title, author)
            count += 1
            if "We couldn't find any matches for" in str(content):
                raise LookupError("No matches")

        if d is None:
            if "Your session has expired" in str(content):
                raise Exception("It knows I'm a robot")
            else:
                filename = f"overdrive_errors/output_{title}.html"
                with open(filename, 'w') as file:
                    file.write(content)
                print(f"Div not found, output saved to {filename}")
                print("Div not found")
                raise LookupError("Div not found")

        name = 'unknown'
        audiobook = False
        ebook = False
        available = False

        for li in d.find_all('li', attrs={'class': 'js-titleCard Item'}):
            title_from_page = li.find(
                'h3', attrs={'class': 'title-name'})['title']

            if title not in title_from_page:
                continue

            name = title
            if li.find('i', attrs={'class': 'icon-ebook'}):
                ebook = True
            if li.find('i', attrs={'class': 'icon-audiobook'}):
                audiobook = True

            if li.find('button', attrs={'class': 'TitleActionButton u-allCaps secondary-color is-borrow js-borrow secondary'}):
                available = True

        if name == 'unknown':
            raise LookupError("Name not found")

        return {
            "title": name,
            "audiobook": audiobook,
            "ebook": ebook,
            "available": available,
            "link": link
        }


# Inspired by https://www.datacamp.com/community/tutorials/amazon-web-scraping-using-beautifulsoup
class AmazonScraper(Scraper):
    def __init__(self, cache_file):
        fieldnames = ['index', 'title_from_src', 'name', 'rating', 'users_rated',
                      'kindle_price', 'audible_price', 'paperback_price', 'link']
        super().__init__(cache_file, 'title_from_src', fieldnames)

    def get_base_div(self, title, author):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding": "gzip, deflate",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

        params = {'k': title + " " + author,  'i': 'stripbooks'}
        r = requests.get('https://www.amazon.com/s',
                         headers=headers, params=params)
        content = r.content

        soup = BeautifulSoup(content, features="html.parser")

        d = soup.find(
            'div', attrs={'class': 'sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20 s-list-col-right'})
        return d, content

    async def get_data(self, title, author):
        d = None
        count = 0
        while d is None and count < 10:
            d, content = self.get_base_div(title, author)
            count += 1
            sleep(5)

        if d is None:
            if "Sorry, we just need to make sure you\\'re not a robot." in str(content) or \
                "To discuss automated access to Amazon data please contact api-services-support@amazon.com" in str(content):
                print("It knows I'm a robot")
                raise Exception("It knows I'm a robot")
            else:
                filename = f"amazon_errors/output_{title}.html"
                with open(filename, 'w') as file:
                    file.write(content)
                print(f"Div not found, output saved to {filename}")
                raise LookupError("Expected div not found")

        name = d.find(
            'span', attrs={'class': 'a-size-medium a-color-base a-text-normal'})
        if name is not None:
            name = name.text
            if title not in name:
                raise LookupError("Name does not match")
        else:
            raise LookupError("Name not found")

        link = d.find(
            'a', attrs={'class': 'a-link-normal s-link-style a-text-normal'})
        if link is not None:
            link = link['href']
        else:
            link = ''

        rating = d.find('span', attrs={'class': 'a-icon-alt'})
        if rating is not None:
            rating = rating.text
        else:
            rating = ''

        users_rated = '0'
        try:
            users_rated = d.find('a', attrs={'class': 'a-link-normal s-link-style'}) \
                .find('span', attrs={'class': 'a-size-base'})
            if users_rated is not None:
                users_rated = users_rated.text.replace(",", "")
        except AttributeError:
            pass

        prices = {}
        for price in d.findAll('div', attrs={'class': 'a-row a-spacing-mini'}):
            try:
                price_type = price.find(
                    'a', attrs={'class': 'a-size-base a-link-normal s-link-style a-text-bold'}).text
                price_value = price.find('span', attrs={
                    'class': 'a-price'}).find('span', attrs={'class': 'a-offscreen'}).text.replace("$", "")
                prices[price_type] = price_value
            except:
                pass

        return {
            "name": name,
            "rating": rating,
            "link": link,
            "users_rated": users_rated,
            "kindle_price": prices.get('Kindle', ''),
            "audible_price": prices.get('Audible Audiobook', ''),
            "paperback_price": prices.get('Paperback', '')
        }
