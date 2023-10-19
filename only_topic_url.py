"""
parsed_portion.txt kullan!!!
satır 75
-*-her bir haber url için topicleri eşleştirir.-*-
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers_param = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
}


def scrape_page(url, cards, topics):
    try:
        pressMaterialPage = requests.get(url, headers=headers_param)
        pressMaterialPage.raise_for_status()  # Check for HTTP errors
        time.sleep(1)
        news = pressMaterialPage.content
        soup = BeautifulSoup(news, "html.parser")
        allTheCard = soup.find_all("div", {"role": "article", "class": "card"})
        location_topic_tags = soup.find_all("span", {"class": "facet-pills__pill__link"})
        location_tag = None
        topic_tag = None

        if len(location_topic_tags) >= 2:
            location_tag = location_topic_tags[0]
            topic_tag = location_topic_tags[1]
            print("topic_tag:", topic_tag.text.strip())
            print("location_tag: ", location_tag.text.strip())
        for oneCard in allTheCard:
            subtitle = oneCard.find("h6", {"class": "card-subtitle"}).text.strip()
            title = oneCard.find("h5", {"class": "card-title"}).text.strip()
            date = oneCard.find("div", {"class": "card-footer small node__meta"}).text.strip()
            newUrl = oneCard.find("a")['href']
            if newUrl[0] == "/":
                newUrl = "https://www.eeas.europa.eu" + newUrl

            url_exists = any(card[3] == newUrl for card in cards)

            if url_exists:
                existing_row = next(card for card in cards if card[3] == newUrl)
                if topic_tag.text.strip() not in existing_row[-1]:
                    existing_row[-1] += f", {topic_tag.text.strip()}"
            else:
                cards.append([subtitle, title, date, newUrl, location_tag.text.strip(), topic_tag.text.strip()])
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making a request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return cards


def next_page_exists(url):
    pressMaterialPage = requests.get(url, headers=headers_param)
    news = pressMaterialPage.content
    soup = BeautifulSoup(news, "html.parser")
    next_page_button = soup.find('a', {'title': 'Go to next page'})
    if next_page_button:
        print("True condition", next_page_button)
        return True
    else:
        print("False condition", next_page_button)
        return False


def url_topic():
    cards = []
    topics = []

    with open("/Users/denizterziler/PycharmProjects/WebScrapingCodePython/parsed_portion.txt", "r") as file:
        for topic_tag in file:
            topics.append(topic_tag.strip())

    for topic in topics:
        print("topic_url:", topic)
        page = 0
        while True:
            # From 01.01.2019 to 01.07.2023
            url = f"https://www.eeas.europa.eu/eeas/press-material_en?fulltext=&created_from=2019-01-01&created_to=2023-07-01&f%5B0%5D=pm_tag{topic}&page={page}"

            scrape_page(url, cards, topics)

            if not next_page_exists(url):
                break

            page += 1

        print("Finished scraping for topic_tag:", topic.strip())

    data = pd.DataFrame(cards,
                        columns=['Subtitle', 'Title', 'Date', 'URL', 'Location_Tag', 'Topic_Tag'])
    data.to_csv('data_set_first.csv')


if __name__ == '__main__':
    url_topic()
