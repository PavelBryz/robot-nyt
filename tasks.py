from datetime import date, datetime

from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems, FileAdapter, EmptyQueue
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from helpers import add_months, get_date, UrlConstructor
from printers import Printer, CSVPrinter
from structures import Article

#
# There are API for searchin article. And it is better to use it,
# but since goal of this challenge was to demonstrate parsing skill I didn't use it at all.
#


# Initialize browser with Selenium library
browser_lib = Selenium()
browser_lib.open_available_browser()
# Since challenge requires usage of pure selenium I operate with driver directly
driver = browser_lib.browser_management.driver


class NoNewsException(Exception):
    """
    Raised when no news was found
    """
    pass

def open_the_search(url: str):
    """
    Navigate to the provided URL in the browser.
    :param url: URL to go to
    :return:
    """
    browser_lib.go_to(url)


def close_popup_window():
    """
    Close the compliance overlay popup if it exists.
    Does nothing if the popup is not found.
    :return:
    """
    try:
        WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="complianceOverlay"]/div/button')))
        driver.find_element(by=By.XPATH, value='//div[@id="complianceOverlay"]/div/button').click()
    except (NoSuchElementException, TimeoutException):
        pass


def select_sections(sections: list[str]):
    """
    Select sections for searching.
    If "All" is included in the sections list, no action is taken.
    :param sections: List of sections
    :return:
    """
    if "All" in sections:
        return
    driver.find_element(by=By.XPATH, value=r'//label[text()="Section"]').click()
    for section in sections:
        driver.find_element(by=By.XPATH, value=fr'//span[text()="{section}"]').click()
    driver.find_element(by=By.XPATH, value=r'//label[text()="Section"]').click()
    driver.refresh()


def select_types(types: list[str]):
    """
    Select types for searching.
    If "All" is included in the types list, no action is taken.
    :param types: List of types
    :return:
    """
    if "All" in types:
        return
    driver.find_element(by=By.XPATH, value=r'//label[text()="Type"]').click()
    for t in types:
        driver.find_element(by=By.XPATH, value=fr'//span[text()="{t}"]').click()
    driver.find_element(by=By.XPATH, value=r'//label[text()="Type"]').click()
    driver.refresh()


def scroll(max_date: datetime):
    """
    Scroll the search results until reaching the specified max_date.
    :param max_date:
    :return:
    """

    # Get last news article
    try:
        date_of_last_el = driver.find_element(by=By.XPATH,
                                              value=r'//li[@data-testid="search-bodega-result"][last()]/div/span')
    except NoSuchElementException:
        raise NoNewsException

    # if date of last news in  newer than max date, load next news
    while get_date(date_of_last_el.text) > max_date:
        # Button that loads next 10 records
        try:
            driver.find_element(by=By.XPATH, value=r'//button[@data-testid="search-show-more-button"]').click()
        except NoSuchElementException:
            return
        # Get last news article
        date_of_last_el = driver.find_element(by=By.XPATH,
                                              value=r'//li[@data-testid="search-bodega-result"][last()]/div/span')


def get_data(query: str, max_date: datetime) -> list[Article]:
    """
    Extract article data from the search results up to the specified max_date.
    :param query:
    :param max_date:
    :return:
    """
    articles = []
    # get all articles WebElements
    articles_elements = driver.find_elements(by=By.XPATH,
                                       value=r'//li[@data-testid="search-bodega-result"]')
    for el in articles_elements:

        # Since there might be news older than time limit, check for news date.
        # Since they are ordered in descending order by date, when one was found, cycle must be broken
        if get_date(el.find_element(by=By.XPATH, value=r'.//div/span').text) < max_date:
            break
        if [article for article in articles if article.link==el.find_element(by=By.XPATH, value=r'.//div/div/div/a').get_attribute('href').split('?')[0]]:
            continue
        article = Article()
        article.parse_date(el)
        article.save_image(r"output\img")

        articles.append(article)

    # To get full text of each article, open link to article and collect text
    # !!!Important!!! Paywall must be blocked before.
    for article in articles:
        browser_lib.go_to(article.link)
        try:
            article.full_description = driver.find_element(by=By.XPATH, value=r'//article/section').text.replace('\n', '')
        except NoSuchElementException:
            pass

    # Processing of text after it all was collected to find additional parameters
    for article in articles:
        article.search_for_currency()
        article.search_for_query(query)

    return articles

# This might be extended to block ads to save processors time and money as result
def block_pay_wall():
    """
    Block requests to specific URLs related to paywalls.
    :return:
    """
    browser_lib.browser_management.driver.execute_cdp_cmd('Network.setBlockedURLs', {
        "urls": ["meter-svc.nytimes.com/meter.js*", "https://samizdat-graphql.nytimes.com/*"]})
    browser_lib.browser_management.driver.execute_cdp_cmd('Network.enable', {})

def unblock_pay_wall():
    """
    Unlock requests to specific URLs related to paywalls.
    :return:
    """
    browser_lib.browser_management.driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": []})
    browser_lib.browser_management.driver.execute_cdp_cmd('Network.enable', {})


def main(printer: Printer):
    """
    Main function that orchestrates the scraping process:
    - Retrieve work item details
    - Construct search URL
    - Navigate to URL
    - Handle popups
    - Set search criteria
    - Scroll search results
    - Block paywall requests
    - Extract articles data
    - Print articles data to Excel
    :return:
    """
    try:
        wi = WorkItems()
        while True:
            try:
                wi.get_input_work_item()
            except EmptyQueue:
                break

            query = wi.get_work_item_variable("Query")
            sections = wi.get_work_item_variable("Sections")
            types = wi.get_work_item_variable("Types")
            month = int(wi.get_work_item_variable("Months"))

            max_date = add_months(date.today(), -month + 1) if month > 1 else add_months(date.today(), -1)

            # Original idea was to create url before
            url_constructor = UrlConstructor()
            url_constructor.generate_url_for_search(wi)

            open_the_search(url_constructor.url)
            close_popup_window()

            select_sections(sections)
            select_types(types)

            unblock_pay_wall()
            try:
                scroll(max_date)
            except NoNewsException:
                wi.create_output_work_item({"Query": query, 'Result': "No news"})
                wi.save_work_item()
                continue

            # Paywall block must be done only after all articles are loaded,
            # because same url is responsible for loading new news
            block_pay_wall()
            articles = get_data(query, max_date)

            if not articles:
                wi.create_output_work_item({"Query": query, 'Result': "No news"})
                wi.save_work_item()
                continue

            path_to_file = printer.print_to(articles, "output", query)
            wi.create_output_work_item({"Query": query, 'Result': "Success"}, [path_to_file])
            wi.save_work_item()

    finally:
        browser_lib.close_all_browsers()


if __name__ == "__main__":
    main(CSVPrinter())
