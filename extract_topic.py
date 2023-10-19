"""
You need to provide a 'topics.txt' file to run this code.
Visit the EEAS Press Material page, copy the HTML containing topics, and save it to the 'topics.txt' file.
-*-*-
Bu kodu çalıştırmak için bir 'topics.txt' dosyası sağlamanız gerekiyor.
EEAS Press Material sayfasını ziyaret edin, konuları içeren HTML'yi kopyalayın ve 'topics.txt' dosyasına kaydedin.
-*-*-
https://www.eeas.europa.eu/eeas/press-material_en?fulltext=&created_from=2019-01-01&created_to=2023-01-07
"""

from bs4 import BeautifulSoup


def extract():
    with open("topics.txt", "r") as topics_file:
        topics_file_contents = topics_file.read()
    topics = []
    html = topics_file_contents
    data = BeautifulSoup(html, "lxml")
    topic_options = data.find_all("li", {"class": "select2-results__option"})
    for topic_option in topic_options:
        data_select2_id = topic_option.get("data-select2-id")
        parts = data_select2_id.split("=pm_tag")
        if len(parts) > 1:
            topics.append(parts[1])
    with open("deneme.txt", "w") as output_file:
        for topic in topics:
            output_file.write(topic + "\n")


if __name__ == '__main__':
    extract()
