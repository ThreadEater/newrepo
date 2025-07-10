import feedparser
import scrapper
import os
import json
import logging as lg
from func_timeout import func_timeout, FunctionTimedOut

FEEDS = [
    'http://feeds.abcnews.com/abcnews/usheadlines',
    'http://rss.cnn.com/rss/cnn_topstories.rss',
    'http://www.cbsnews.com/latest/rss/main',
    'http://www.nytimes.com/services/xml/rss/nyt/National.xml',
    'http://online.wsj.com/xml/rss/3_7085.xml',
    'http://content.usatoday.com/marketing/rss/rsstrans.aspx?feedId=news2',
    'http://rss.csmonitor.com/feeds/usa',
    'http://feeds.nbcnews.com/feeds/topstories',
    'http://feeds.nbcnews.com/feeds/worldnews',
    'http://feeds.reuters.com/Reuters/worldNews',
    'http://feeds.reuters.com/Reuters/domesticNews',
    'http://hosted.ap.org/lineups/USHEADS.rss',
    'http://hosted.ap.org/lineups/WORLDHEADS.rss',
    'http://www.huffingtonpost.com/feeds/verticals/world/index.xml',
    'http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
    'http://news.yahoo.com/rss/us',
    'http://rss.news.yahoo.com/rss/world',
    'http://www.newsweek.com/rss',
    'http://feeds.feedburner.com/thedailybeast/articles',
    'http://qz.com/feed',
    'http://www.theguardian.com/world/usa/rss',
    'http://www.politico.com/rss/politicopicks.xml',
    'http://www.newyorker.com/feed/news',
    'http://feeds.feedburner.com/NationPBSNewsHour',
    'http://feeds.feedburner.com/NewshourWorld',
    'http://www.usnews.com/rss/news',
    'http://www.npr.org/rss/rss.php?id=1003',
    'http://www.npr.org/rss/rss.php?id=1004',
    'http://feeds.feedburner.com/AtlanticNational',
    'http://feeds.feedburner.com/TheAtlanticWire',
    'http://www.latimes.com/nation/rss2.0.xml',
    'http://www.latimes.com/world/rss2.0.xml',
    'http://api.breakingnews.com/api/v1/item/?format=rss',
    'https://news.vice.com/rss',
    'http://talkingpointsmemo.com/feed/livewire',
    'http://www.salon.com/category/news/feed/rss/',
    'http://time.com/newsfeed/feed/',
    'http://feeds.foxnews.com/foxnews/latest?format=xml',
    'http://mashable.com/us-world/rss/'
]

LINKFILE = "links.txt"
TIMEOUT = 10
lg.basicConfig(
    filename="scraper.log",
    filemode="a",  
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=lg.DEBUG  
)

def parse_rss_feeds(feed: str, linkfile: str) -> None:
    try:
        os.makedirs("scraped_articles", exist_ok=True)
        lg.info("Running 'feedparser.parse()'")
        rss = func_timeout(timeout=TIMEOUT, func=feedparser.parse, args=(feed,))
        lg.info("Ran 'feedparser.parse()'")
        for item in rss.entries:
            link = item.link
            if not in_linkfile(link, linkfile):
                lg.info("Running 'scrapper.scrape_article()'")
                data = func_timeout(timeout=TIMEOUT, func=scrapper.scrape_article, args=(link,))
                lg.info("Ran 'scrapper.scrape_article()'")
                if data:
                    filename = scrapper.sanitize_filename(data['title'])
                    output_path = os.path.abspath(os.path.join("scraped_articles", filename))
                    with open(output_path, 'w', encoding='ascii') as f:
                        json.dump(data, f, ensure_ascii=True, indent=4)

    except FunctionTimedOut:
        print("Function timed out")
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise

def in_linkfile(link: str, linkfile: str) -> bool:
    try:
        with open(linkfile, 'a+') as f:
            links = f.readlines()
            if link in links:
                return True
            else:
                f.write(f"{link}\n")
        return False
    
    except Exception as e:
        print(f"ERROR: {e}")
        raise

def aggregate_json_files() -> None:
    try:
        articles = []
        os.makedirs("scraped_articles", exist_ok=True)
        for article in os.scandir(os.path.abspath("scraped_articles")):
            with open(article.path, "r") as f:
                articles.append(json.load(f))

        with open("articles.json", "w") as f:
            json.dump(articles, f, ensure_ascii=True, indent=4)

    except Exception as e:
        print(f"ERROR: {e}")
        raise
    


try:
    for feed in FEEDS:
        parse_rss_feeds(feed, LINKFILE)
    aggregate_json_files()

except Exception as e:
    print(f"ERROR: {e}")
    raise