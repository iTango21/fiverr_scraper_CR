1. Install required libraries:

    pip install scrapy
    pip install scraperapi-sdk
    pip install python-dotenv

...and all others that are not on your computer.


2. Create a file ".env" with the following content:

    SCRAPER_API_KEY=#####

!!! instead of "#####" insert your key!

3. To fire up a spider, ```cd``` into the folder ```fiverr```
   and run the following command in your terminal:

    scrapy crawl fiverr_spider_async