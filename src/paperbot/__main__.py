# import math
import random
import time
import feedparser  # type: ignore
import ollama
from diskcache import Cache  # type: ignore
import os
import pickle
import subprocess
from datetime import datetime, timedelta

# INFO: Change the feeds if you want. You must change the command use in sayit, down towards the end of the script.

# Example RSS feeds for different categories. "Florida News" always has an error, so it's commented out.
FEEDS = {
    "National News": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
    # "Florida News": "https://www.orlandosentinel.com/arcio/rss/category/news/?query=display_date:%5Bnow-7d+TO+now%5D",
    "Boca Raton News": "https://www.bocaratontribune.com/feed/",
    "Science News": "https://www.sciencedaily.com/rss/top/science.xml",
    "Linux News": "https://www.phoronix.com/rss.php",
    "Consumer Economy": "https://www.npr.org/rss/rss.php?id=1017",
}

CACHE_FILE = "news_cache.pkl"
CACHE_EXPIRY = timedelta(hours=int(os.getenv("CACHE_EXPIRY_HOURS", 6)))

thecache = Cache("news_cache", size_limit=100 * 1024 * 1024)


# Load cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            print(
                f"Warning: Failed to load cache due to error: {e}. Cache will be reset."
            )
            return {}
    return {}


# Save cache
def save_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)


# Summarize using Ollama

# myprompt = (
#     "Summarize this text. Exclude any links, markdown, or formatting. "
#     + "Provide the summary as plain sentences with each sentence on a new line. "
#     + "Avoid combining multiple sentences into one line."
# )

myprompt = "Provide a clear, well-organized summary in 2 to 3 paragraphs. Avoid redundancy, ensure sentences are connected, and maintain logical flow. Exclude any links, markdown, or formatting."


@thecache.memoize(typed=True, expire=4 * 60 * 60, tag="summary")
def summarize_text(text, theprompt="Summarize this, without links or formatting."):
    response = ollama.chat(
        model="llama3:8b",
        messages=[
            {
                "role": "user",
                "content": f"{theprompt}:{text}",
            },
        ],
    )
    return response["message"]["content"].strip()


@thecache.memoize(typed=True, expire=4 * 60 * 60, tag="feed")
def getfeed(url: str) -> dict | None:
    if str is not None and len(url) > 7:
        try:
            return_value = feedparser.parse(url)
        except (feedparser.ParseError, Exception) as e:
            print(f"Error fetching {url}: {e}")
            print(f"[{e.__class__.__name__}] [{e.args}]")
            return None

        return return_value
    else:
        return None


# Fetch and summarize news with caching
def fetch_and_summarize_news() -> dict | None:
    cache = load_cache()
    summaries = {}
    current_time = datetime.now()

    sayit("One moment while I read the news...")
    for category, url in FEEDS.items():
        print(f"Fetching: {category}")
        if (
            category in cache
            and current_time - cache[category]["timestamp"] < CACHE_EXPIRY
        ):
            # print(f"Using cached data for {category}")
            summaries[category] = cache[category]["summaries"]
        else:
            # feed = feedparser.parse(url)
            hadException: bool = False
            keepTrying: bool = True
            attempt: int = 0
            max_attempts: int = 1

            while keepTrying:
                keepTrying = False
                attempt += 1
                try:
                    feed = getfeed(url)
                except Exception as e:
                    print(f"Error fetching category [{category}] at {url}: {e}")
                    print(f"[{e.__class__.__name__}] [{e.args}]")
                    sayit(
                        f"I seem to be having trouble reading the feed for {category}."
                    )
                    hadException = True
                    feed = None
                    pass
                else:
                    hadException = False

                if hadException:
                    if attempt <= max_attempts:
                        sayit("Let me check something. Diagnosing...")
                        print("Running a check on the cache...")
                        results = thecache.check(fix=True, retry=False)
                        print("Cache check results:", results)
                        if results is not None and len(results) > 0:
                            print(
                                "There was a cache problem. It might have been fixed."
                            )
                            sayit("There was a caching problem. I might have fixed it.")
                            sayit("Let me try summarizing again...")
                            keepTrying = True
                        else:
                            sayit("I couldn't find anything. Let's skip this article.")
                            keepTrying = False
                            continue

            if not hadException and feed is not None:
                summaries[category] = []

                print(f"Summarizing news for {category}")

                max_entry_index: int = int(min(len(feed.entries), 5))

                for entry in feed.entries[:max_entry_index]:
                    title = entry.get("title", "Ummm. I'm not sure the title.")
                    # print(f"prmt: {myprompt}")
                    hadException = False
                    keepTrying = True
                    attempt = 0
                    max_attempts = 1
                    summary = ""

                    while keepTrying:
                        keepTrying = False
                        attempt += 1
                        try:
                            summary = summarize_text(
                                entry.get("summary", "Nevermind. Next."), myprompt
                            )
                        except Exception as e:
                            print(f"Error summarizing text for {title} at {url}: {e}")
                            print(f"[{e.__class__.__name__}] [{e.args}]")
                            sayit(f"I had trouble summarizing text for {title}.")
                            hadException = True
                            pass
                        else:
                            hadException = False

                        if hadException:
                            if attempt <= max_attempts:
                                sayit("Let me see something. Diagnosing...")
                                print("Running check on the cache...")
                                results = thecache.check(fix=True, retry=False)
                                print(f"The results of the check were: {results}")
                                if results is not None and len(results) > 0:
                                    print(
                                        "There was a cache problem. It might have been fixed."
                                    )
                                    sayit(
                                        "There was a caching problem. I might have fixed it."
                                    )
                                    sayit("Let me try summarizing again...")
                                    keepTrying = True
                                else:
                                    sayit(
                                        "I couldn't find anything. Let's skip this article."
                                    )
                                    keepTrying = False
                                    continue
                        else:
                            keepTrying = False
                    if hadException:
                        continue

                    summaries[category].append(f"\n{title}\n\n{summary}")
                    print(f"Summary added for {title}")
                cache[category] = {
                    "summaries": summaries[category],
                    "timestamp": current_time,
                }
            else:
                # Dont say anything if we already processed an exception
                if not hadException:
                    print(f"Failed to fetch news for [{category}] from {url}")
                    sayit(
                        f"I seem to be unable to fetch the feed for [{category}] from {url}"
                    )
                    sayit(f"Failed to fetch the feed for [{category}].")
                    sayit("Continuing to the next feed.")

    # Moved from using pickle to diskcache
    # save_cache(cache)
    return summaries


# Send summaries to pipeup
def send_to_pipeup(summaries):
    # This random.choice keeps it from being predictable
    start2speak = sayit(
        random.choice(
            [
                "Here's the news.",
                "Now to the news update.",
                "These are the latest headlines.",
                "Today's news.",
                "Current events.",
                "Here are the updates.",
                "I found these top stories.",
                "Summarizing the news now.",
                "This is what's happening.",
                "Hear are the latest updates.",
                "Here are the latest news headlines.",
                "This is the latest news update.",
                "Check out these top stories.",
                "",
                "",
                "",
                "Ok",
                "Ready",
                "Proceeding",
            ]
        )
    )

    sayit(start2speak)
    time.sleep(1)

    for category in summaries.keys():
        sayit(f"Here are articles for {category}:")
        print(f"Here are the articles for {category}:")

        for article in summaries[category]:
            # print(f">>{article}<<\n")
            sayit(article)


def sayit(message: str):
    # INFO: You must change this to a program that works for you. A program that takes text as an argument and then plays it out loud.
    #
    # Place the program name as the first entry of a list, then follow with entries
    #   with each parameter to be passed to the program.
    #
    #   Example:
    #       subprocess.run(["text2speachProgram", "--optionWithValue", "the value", "normally quoted argument", "second"])
    #       subprocess.run(["edge-playback", "--text", "Testing 1, 2,  3. This is a test for proper enunciation of edge T.T.S.", "--voice", "en-US-EmmaNeural"])
    #
    subprocess.run(["pipeup", message], check=False)
    # subprocess.run(["edge-playback", "--text", message, "--voice", "en-US-EmmaNeural"])


# Main function
def main():
    summaries = fetch_and_summarize_news()
    send_to_pipeup(summaries)


if __name__ == "__main__":
    main()
