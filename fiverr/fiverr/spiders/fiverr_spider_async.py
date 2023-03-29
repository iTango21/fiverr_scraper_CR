# Load the packages
import scrapy
# from fiverr.spiders.fiverr_spider_sync import custom_settings_dict
# from fiverr.spiders.fiverr_spider_sync import client
from scraper_api import ScraperAPIClient
from dotenv import load_dotenv
import os
import re

from bs4 import BeautifulSoup
import lxml

# Load the environment variables
load_dotenv()

# Get the scraper API key
client = ScraperAPIClient(api_key=os.getenv("SCRAPER_API_KEY"))

# Define the dictionary that contains the custom settings of the spiders. This will be used in all other spiders
custom_settings_dict = {
    "FEED_EXPORT_ENCODING": "utf-8",  # UTF-8 deals with all types of characters
    "RETRY_TIMES": 10,  # Retry failed requests up to 10 times (10 instead of 3 because Fiverr is a hard site to scrape)
    "AUTOTHROTTLE_ENABLED": False,
    # Disables the AutoThrottle extension (recommended to be used with proxy services unless the website is tough to crawl)
    "RANDOMIZE_DOWNLOAD_DELAY": False,
    # If enabled, Scrapy will wait a random amount of time (between 0.5 * DOWNLOAD_DELAY and 1.5 * DOWNLOAD_DELAY) while fetching requests from the same website
    "CONCURRENT_REQUESTS": 5,
    # The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader
    "DOWNLOAD_TIMEOUT": 60  # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
}


# Define the spider class
class FiverrSpiderAsync(scrapy.Spider):
    name = 'fiverr_spider_async'  # Name of the spider
    allowed_domains = ['fiverr.com']  # Allowed domains to crawl
    custom_settings = custom_settings_dict  # Standard custom settings of the spider
    custom_settings["FEEDS"] = {"gig_data_async.json": {"format": "json",
                                                        "overwrite": True}}  # Export to a JSON file with an overwrite functionality
    # master_url = "https://www.fiverr.com/categories/data/data-processing/data-mining-scraping?source=pagination&page={}&offset=-16"
    master_url = 'https://www.fiverr.com/categories/programming-tech/ai-applications?source=pagination&page={}&offset=-16'

    """
                client.scrapyGet(url=FiverrSpiderAsync.master_url.format(i), country_code="us", render=True,
                                 premium=False),
    """

    def start_requests(self):
        for i in range(1, 2):
            yield scrapy.Request(
                client.scrapyGet(url=FiverrSpiderAsync.master_url.format(i),
                                 country_code="us",
                                 render=True,
                                 premium=True),
                callback=self.parse,
                dont_filter=True
            )

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')

        with open('___gig.txt', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        #
        # # open the file in w mode
        # # set encoding to UTF-8
        # with open("___gig1.txt", "w", encoding='utf-8') as file:
        #     # prettify the soup object and convert it into a string
        #     file.write(str(soup.prettify()))
        #
        # soup2 = response.xpath('/html').extract()
        #
        # with open('___gig2.txt', 'w', encoding='utf-8') as f:
        #     f.write(soup2)

        sellers = response.xpath("//div[contains(@class, 'gig-wrapper')]")

        print(f'\t\t=============>>>   Sellers = {len(sellers)}')

        for gig in sellers:

            # Some gigs are without reviews, so we need to handle that case
            try:
                gig_rating = float(gig.css("div.content-info > div.rating-wrapper").xpath(
                    "./span[contains(@class, 'gig-rating')]/text()").get())
            except TypeError:
                gig_rating = None

            print(f'\t\t1   =============>>>   gig_rating = {gig_rating}')

            try:
                num_reviews = gig.css("div.content-info > div.rating-wrapper").xpath(
                    "./span[contains(@class, 'gig-rating')]/span/text()").get().replace("(", "").replace(")", "")
                # Num reviews should be integer, but some gigs have num_reviews in a string format (e.g., 1k+). Change any num_reviews with a string format to integer
                if num_reviews == "1k+":
                    num_reviews = "1000"  # Assume the seller has 1000 reviews so that we can change the format to integer later
                else:
                    pass
                # Change the format of num_reviews to integer
                num_reviews = int(num_reviews)
            except:
                num_reviews = None

            print(f'\t\t2   =============>>>   num_reviews = {num_reviews}')

            # Price points before and after the decimal point are shown separately. We treat this case here
            #
            # gig_starting_price_before_decimal = re.findall(pattern="\d+", string=gig.css("footer > div.price-wrapper > a > span::text").get())[0]
            tmp_pr1 = gig.css("footer > a > span::text").get()
            gig_starting_price_before_decimal = re.findall("\d+", tmp_pr1)[0]

            gig_starting_price_after_decimal = gig.css("footer > a > span > sup::text").get()
            gig_starting_price = float(gig_starting_price_before_decimal + "." + gig_starting_price_after_decimal)

            print(f'\t\t3   =============>>>   gig_starting_price = {gig_starting_price}')

            # Create the data dictionary
            data_dict = {
                "seller_name": gig.xpath("./div[contains(@class, 'seller-info')]").css(
                    "div.inner-wrapper > div.seller-identifiers > div.seller-name-and-country > div.seller-name > a::text").get(),
                "seller_url": "https://www.fiverr.com" + gig.css("h3 > a::attr(href)").get(),
                "seller_level": gig.xpath("./div[contains(@class, 'seller-info')]").css(
                    "div.inner-wrapper > div.seller-identifiers").xpath(
                    "./span[contains(@class, 'level')]//span/text()").get(),
                "gig_title": gig.css("h3 > a::attr(title)").get(),
                "gig_rating": gig_rating,
                "num_reviews": num_reviews,
                "gig_starting_price": gig_starting_price
            }

            # Return the data
            yield data_dict
