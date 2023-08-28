import re
import urllib.request
from dataclasses import dataclass, field
from datetime import date

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from enums import Currency
from helpers import get_date


@dataclass
class Article:
    # Add link to article. It is reasonable to have it for future,
    # if after requirement changes and we will need to collect some extra data
    # we would not need to do whole work from scratch
    link: str = ''
    title: str = ''
    date: date = ''
    description: str = ''  # Short article description from search
    full_description: str = ''  # Full text of article
    picture_link: str = ''
    picture_name: str = ''
    # it might be interesting to analise words not only how many query phrase in whole text
    # but in title, description and full text separately
    phrase_count: dict[str, int] = field(default_factory=dict)
    # there are more than one currency, so I made it to search for several
    money: dict[str, bool] = field(default_factory=dict)

    def parse_date(self, element: WebElement):
        """
        Method to populate article properties from a WebElement object
        :param element:
        :return:
        """
        self.link = element.find_element(by=By.XPATH, value=r'.//div/div/div/a').get_attribute('href').split('?')[0]
        self.title = element.find_element(by=By.XPATH, value=r'.//div/div/div/a/h4').text
        self.date = get_date(element.find_element(by=By.XPATH, value=r'.//div/span').text)
        self.description = element.find_element(by=By.XPATH, value=r'.//div/div/div/a/p[1]').text
        try:
            self.picture_link = element.find_element(by=By.XPATH, value='.//div/div/figure/div/img').get_attribute(
                'src')
            self.picture_name = re.search(r"/.*/(.*?)\?", self.picture_link, re.MULTILINE).group(1)
        except NoSuchElementException:
            pass

    def save_image(self, path: str):
        """
        Method to save the article's image to a given path.
        :param path:
        :return:
        """
        if self.picture_link:
            urllib.request.urlretrieve(self.picture_link, fr"{path}\{self.picture_name}")

    def search_for_currency(self):
        """
        Method to check if the article mentions any currency from currency enum and
        updates the money dictionary accordingly
        :return:
        """
        united_string = self.title + self.description + self.full_description
        for cur in Currency:
            if re.search(cur.value, united_string, re.MULTILINE):
                self.money[cur.name] = True

    def search_for_query(self, query: str):
        """
        Method to search for a query string in various parts of the article and update the phrase_count dictionary
        :param query:
        :return:
        """
        united_string = self.title + self.description + self.full_description
        self.phrase_count["combined"] = united_string.count(query)
        self.phrase_count["title"] = self.title.count(query)
        self.phrase_count["description"] = self.description.count(query)
        self.phrase_count["full_description"] = self.full_description.count(query)
