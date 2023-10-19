import urllib
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from urllib.parse import unquote


def for_every_country(url):
    browser = webdriver.Chrome()
    browser.get(url)
    browser.fullscreen_window()
    browser.execute_script("window.scrollBy(0, 500);")
    time.sleep(2)

    try:
        element = browser.find_element(By.XPATH, '(//*[@id="-content"]/div/span)[3]')
        element.click()
        time.sleep(5)

        parent_span = browser.find_element(By.XPATH, '//*[@id="top"]/span')
        li_elements = parent_span.find_elements(By.XPATH, './/li')

        with open("parsed_portion.txt", "a") as file:
            for li in li_elements:
                href_attribute = li.get_attribute('id')
                pm_tag_index = href_attribute.find("pm_tag")

                if pm_tag_index != -1:
                    portion_after_pm_tag = href_attribute[pm_tag_index + len("pm_tag"):]
                    encoded_portion = urllib.parse.quote(portion_after_pm_tag, safe='')
                    decoded_portion = urllib.parse.unquote(encoded_portion)  # Decode the URL-encoded portion
                    file.write(decoded_portion + "\n")


    except Exception as e:
        print(f"Error processing URL: {url}. Exception: {e}")

    browser.quit()


if __name__ == '__main__':
    with open("location_url.txt", "r") as url_file:
        urls = url_file.readlines()

    for url in urls:
        url = "https://www.eeas.europa.eu/eeas/press-material_en?fulltext=&created_from=2019-01-01&created_to=2023-07-01&f%5B0%5D=press_site" + url.strip()
        print(url)
        for_every_country(url)
        time.sleep(5)
