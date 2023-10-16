import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers_param = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
}


def scrape_page(url, cards):
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
        location = None
        author = None

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

            if newUrl.startswith("https://www.eeas.europa.eu/delegation"):
                insidePage = requests.get(newUrl, headers=headers_param)
                insidePage.raise_for_status()  # Check for HTTP errors
                info = insidePage.content
                soup_2 = BeautifulSoup(info, "html.parser")
                try:
                    location = soup_2.find("div", {
                        "class": "field field--name-field-location-text field--type-string field--label-hidden field__item"}).text.strip()
                except AttributeError:
                    location = "NOT DEFINED"
                try:
                    author = soup_2.find("div", {"class": "node__meta"}).a.text.strip()
                except AttributeError:
                    author = "NOT DEFINED"
                try:
                    content_1 = soup_2.find("div", {
                        "class": "clearfix text-formatted field field--name-field-text-teaser field--type-text-long field--label-hidden field__item"}).text.strip()
                except AttributeError:
                    content_1 = "no info"
                try:
                    content = soup_2.find("div", {
                        "class": "clearfix text-formatted field field--name-field-text field--type-text-long field--label-hidden field__item"}).text.strip()
                except AttributeError:
                    content = "No Content for eeas"
                if content != "No Content" and content_1 != "no info":
                    content = content_1 + content
                elif content == "No Content" and content_1 != "no info":
                    content = content_1
                elif content == "No Content" and content_1 == "no info":
                    content = "Nothing about content"
            elif newUrl.startswith("https://www.eeas.europa.eu/eeas") and newUrl != url:
                #it gives error when you do not add newUrl != url because the base url starts with eeas.europa
                driver = webdriver.Chrome()
                try:
                    driver.get(newUrl)
                    location_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             '.field.field--name-field-location-text.field--type-string.field--label-hidden.field__item')))
                    title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.text-box-header .field--name-title')))
                    content_frame = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, '#block-eeas-website-content article div.text-formatted')))
                    content = driver.execute_script("return arguments[0].textContent.trim();", content_frame)
                    author = "EEAS"
                    location = location_element.text.strip()
                    title = title_element.text.strip()

                finally:
                    driver.quit()
            elif newUrl.startswith("https://www.consilium.europa.eu") or newUrl.startswith("consilium.europa.eu"):
                driver = webdriver.Chrome()
                try:
                    driver.get(newUrl)
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                    author_elements = driver.find_elements(By.CSS_SELECTOR, '.tag-institution-meta.tag-ceu')
                    author = author_elements[0].text.strip() if author_elements else "Author not found"
                    title_elements = driver.find_elements(By.CSS_SELECTOR,
                                                          '.padding-bottom-0.margin-bottom-20.no-bb h1')
                    title = title_elements[0].text.strip() if title_elements else "Title not found"
                    content_elements = driver.find_elements(By.CSS_SELECTOR,
                                                            '.col-md-9.council-left-content-basic.council-flexify p')
                    content = '\n'.join([paragraph.text.strip() for paragraph in content_elements])
                    location = "Not Specified"
                finally:
                    driver.quit()
            elif newUrl.startswith("https://ec.europa"):
                driver = webdriver.Chrome()
                try:
                    driver.get(newUrl)
                    title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, '.ecl-heading.ecl-heading--h1.ecl-u-color-white'))
                    )
                    title = title_element.text.strip()
                    content_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.ecl-paragraph'))
                    )
                    content = content_element.text.strip()
                    location_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, '.ecl-meta.ecl-meta--header .ecl-meta__item:last-child'))
                    )
                    location = location_element.text.strip()

                except Exception as e:
                    print(f"An error occurred: {e}")

                finally:
                    driver.quit()
            else:
                location = "NOT SUPPORTED FOR NOW"
                author = "NOT SUPPORTED FOR NOW"
                content = "NOT SUPPORTED FOR NOW"
            print("last one: ", title)
            cards.append([subtitle, title, date, newUrl, location, author, content, location_tag.text.strip(),
                          topic_tag.text.strip()])
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


cards = []
topics = []
#put the topic txt file path here
with open("/Users/denizterziler/PycharmProjects/WebScrapingCodePython/ukrain_topics.txt", "r") as file:
    for topic_tag in file:
        topics.append(topic_tag.strip())
for topic in topics:
    print("topic_url:", topic)
    page = 0
    while True:
        #from 01.01.2015 to 01.07.2023
        url = f"https://www.eeas.europa.eu/eeas/press-material_en?fulltext=&created_from=2015-01-01&created_to=2023-07-01&f%5B0%5D=pm_tag{topic}&page={page}"

        scrape_page(url, cards)

        if not next_page_exists(url):
            break

        page += 1

    print("Finished scraping for topic_tag:", topic.strip())
data = pd.DataFrame(cards,
                    columns=['Subtitle', 'Title', 'Date', 'URL', 'Location', 'Author', 'Content', 'Location_Tag',
                             'Topic_Tag'])
data.to_csv('data_set.csv')
