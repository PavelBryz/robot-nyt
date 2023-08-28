from enum import Enum


class Currency(Enum):
    # RegEx - look for symbol and numbers or for numbers and then currency description
    DOLLAR = '(?:[$])(?:(?:\d+[.,]?)+(?:\.\d{1,2})?)|(?:(?:\d+[.,]?)+(?:\.\d{1,2})?) ?(?:[Dd]ollars?|USD|usd)'
    EURO = '(?:[€])(?:(?:\d+[.,]?)+(?:\.\d{1,2})?)|(?:(?:\d+[.,]?)+(?:\.\d{1,2})?) ?(?:EURO|EUR|eur)'
    POUND = '(?:[£])(?:(?:\d+[.,]?)+(?:\.\d{1,2})?)|(?:(?:\d+[.,]?)+(?:\.\d{1,2})?) ?(?:[pP]ounds?|GBP|gbp)'
