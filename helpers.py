from calendar import monthrange
from datetime import date, datetime
from typing import Optional

from RPA.Robocorp.WorkItems import WorkItems

# Define date formats to be used for date parsing
DATE_FORMATS = ('%b. %d', '%b. %d, %Y', '%B %d', '%B %d, %Y')


def get_date(article_date: str):
    """
    Get the parsed date from the input article_date string.
    Handles multiple date formats defined in DATE_FORMATS.
    :param article_date: Parsed date of article
    :return:
    """
    article_date = article_date.replace("Sept", "Sep")
    for date_format in DATE_FORMATS:
        try:
            parsed_date = datetime.strptime(article_date, date_format)
            # If there is no year, replace it with the current year
            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=datetime.today().year)
            return parsed_date
        except ValueError:
            pass
    # If no valid date format is found, raise a ValueError
    return datetime.now()



def add_months(start_date: date, months: int) -> datetime:
    """
    Add a given number of months to a date.
    :param start_date: Base date
    :param months: Amount of months
    :return: Returns a new date.
    """
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    day = min(start_date.day, monthrange(year, month)[1])
    return datetime(year, month, day)


class UrlConstructor:
    """
    UrlConstructor class for creating and modifying URLs for New York Times search.
    It was part of original idea to create search query prior to search.
    I was trying to do that because It will save from additional
    resource spending and UI elements change (DOM hierarchy, names and so on).
    Sadly It didn't work because:
        Date filtration didn't work
        To filter sections all full names of sections must be found,
            but I didn't find way to find it for whole 100+ sections. Request returns only 10, connected to query
        I didn't do types filtration because since it is so similar with sections filtration,
            they should share the same approach

    However, It still generates request with query, dates (in case it start working) and sorting.
    """
    def __init__(self, base_url: Optional[str] = "https://www.nytimes.com/search?"):
        """
        Initialize with a base URL, defaulting to NYTimes search page.
        :param base_url:
        """
        self.__url = base_url + "sort=newest"

    @property
    def url(self) -> str:
        return self.__url

    def generate_url_for_search(self, work_item: WorkItems):
        """
        Generate the final URL based on the provided WorkItems object.
        :param work_item:
        :return:
        """
        self._add_query(work_item.get_work_item_variable("Query"))
        self._add_months(work_item.get_work_item_variable("Months"))

    def _add_query(self, query: str):
        self.__url += f"&query={query}"

    def _add_date(self, date_from: date, date_to: date):
        self.__url += f"&startDate={date_from.strftime('%Y-%m-%d')}"
        self.__url += f"&endDate={date_to.strftime('%Y-%m-%d')}"

    def _add_months(self, months_count: str):
        """
        Add a given number of months for filtering search results based on date.

        :param months_count:
        :return:
        """
        months_count = int(months_count)
        if months_count > 1:
            self._add_date(date_from=date.today(),
                           date_to=add_months(date.today(), -months_count + 1))
        else:
            self._add_date(date_from=date.today(),
                           date_to=add_months(date.today(), -1))
