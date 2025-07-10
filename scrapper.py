import json
from newspaper import Article
from newspaper import Config
import datetime
import os
import re
import requests

# Load the base JSON structure from the template file (we can hardcode this too if that ends up being better later)
with open('template.json', encoding='utf-8') as f:
    template = json.load(f)

def sanitize_filename(title):
    # Convert title into a safe ASCII-only filename (helps in case we name files after it or do other operations)
    if not title:
        return f"article_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    clean_title = re.sub(r'[^A-Za-z0-9 ]+', '', title)  # remove special characters
    return f"{clean_title[:50].strip().replace(' ', '_')}.json"

def sanitize_ascii(text):
    # Remove all non-ASCII characters from text
    return text.encode('ascii', errors='ignore').decode()

def scrape_article(url):
    # using newspaper3k to download/parse the article from the URL
    article = Article(url)
    try:
        article.download()  # Download the HTML from the page
        article.parse()     # Extract the article title, text, authors, etc.
    except requests.exceptions.Timeout:
        print(f"Article {url} timed out")
    except Exception as e:
        print(f"Failed to download/parse article: {e}")
        return None

    # Alert if the content has issues being parsed (i'm not checking the other less important fields like author, date, etc)
    if not article.text.strip():
        print("Warning: No content extracted from the article.")
        return None

    # duplicate the template (to be filled with new article data)
    data = template.copy()

    # Fill in fields using newspaper3k results (category/event cluster fields are left empty for now)
    data['title'] = sanitize_ascii(article.title or "")
    data['author'] = [{"name": sanitize_ascii(name)} for name in article.authors] if article.authors else [{"name": ""}]

    if not article.publish_date or not article.publish_date.year or  not article.publish_date.month or  not article.publish_date.day:
        return None
    else:
        data['publication_date'] = article.publish_date.isoformat()
        
    
    data['source'] = article.source_url or ""
    data['url'] = url
    data['bias'] = ""  # left empty for now
    data['content'] = sanitize_ascii(article.text)

    return data

def main():
    # Ensure the output directory exists (maybe replace storage with an appendage to the consolidated JSON)
    os.makedirs("scraped_articles", exist_ok=True)

    while True:
        # Prompt user for URL
        url = input("Enter news article URL (or 'q' to quit): ").strip()
        if url.lower() == 'q':
            break

        # scrape the article data using newspaper3k
        config = Config()
        config.request_timeout = 10
        data = scrape_article(url, config)
        if data:
            # print new json
            print("\nGenerated JSON Preview:\n")
            print(json.dumps(data, indent=4))

            # Create a safe filename from the article title (cleaned earlier)
            filename = sanitize_filename(data['title'])
            output_path = os.path.abspath(os.path.join("scraped_articles", filename))

            try:
                # Save the extracted article as a JSON file (ASCII-only!)
                with open(output_path, 'w', encoding='ascii') as f:
                    json.dump(data, f, ensure_ascii=True, indent=4)
                print(f"\nSaved to: {output_path}\n")
            except Exception as e:
                print(f"Error writing file: {e}")
        else:
            print("Skipped due to empty or failed content.\n")

# run
if __name__ == "__main__":
    main()