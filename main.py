from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

# Supabase Configuration
SUPABASE_URL = "https://xrogtywyggbgulnyaqqa.supabase.co"  # Replace with your Supabase project URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhyb2d0eXd5Z2diZ3VsbnlhcXFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczMzY1MzMsImV4cCI6MjA1MjkxMjUzM30.2wFFIjgT-DtbPRBFgcqNg7n2vyNNaBcKXaq5Q8PRLs0"  # Replace with your Supabase anon key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#Tool used to pull funding articles from businesswire using playwright and pushing the most recent articles to a supabase
#database to be used with openAI LLm to extra the specific information needed for the funding articles(company name, funding amount
#, investers, date, source).  
#
#(__This Tool Is Set to the last Two Days And Can be adjusted On line 15 and 67__}
def scrape_recent_articles(days=2):
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the target URL
        page.goto("https://www.businesswire.com/portal/site/home/news/subject/?vnsId=31355")

        # Wait for the articles to load
        page.wait_for_selector(".bwTitleLink")

        # Locate all article links and timestamps
        articles = page.locator(".bwTitleLink")
        timestamps = page.locator(".bwTimestamp time")
        count = articles.count()

        # Calculate the cutoff date (as an offset-aware datetime)
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=days)

        for i in range(count):
            # Extract the title, link, and date
            title = articles.nth(i).locator("span").text_content().strip()
            link = articles.nth(i).get_attribute("href")
            full_link = f"https://www.businesswire.com{link}" if link.startswith("/") else link

            # Parse and filter by date (as an offset-aware datetime)
            date_str = timestamps.nth(i).get_attribute("datetime")
            article_date = datetime.fromisoformat(date_str) if date_str else None

            if article_date and article_date >= cutoff_date:
                # Save to Supabase
                save_to_supabase(title, full_link)

        # Close the browser
        browser.close()

def save_to_supabase(title, link):
    # Insert data into Supabase
    data = {
        "title": title,
        "link": link
    }
    response = supabase.table("articles").insert(data).execute()

    # Check if the response is successful
    if response.data:
        print(f"Article saved: {title}")
    else:
        print(f"Failed to save article: {response}")

# Run the scraper
scrape_recent_articles(days=2)

#Code test#

#rows = int(input("how many rows: "))
#columns = int(input("how many columns: "))
#symbol = input("enter a symbol to use: 
# import asyncio
# from crawl4ai import AsyncWebCrawler, CacheMode

# async def main():
#     async with AsyncWebCrawler(verbose=True) as crawler:
#         # We'll add our crawling code here
#         pass

# if __name__ == "__main__":
#     asyncio.run(main())

#     async def main():
#      async with AsyncWebCrawler(verbose=True) as crawler:
#         result = await crawler.arun(url="https://www.businesswire.com/portal/site/home/news/subject/?vnsId=31355")
#         print(f"Basic crawl result: {result.markdown[:5000]}")  # Print first 500 characters

# asyncio.run(main())

