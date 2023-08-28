# NYTimes Parser Challenge

## About

This project presents a parser specifically designed for extracting news articles from the New York Times. The parser aims to automate various tasks related to news articles retrieval, filtration, and data extraction.

## Features

### Parse Data from WorkItems

The parser is capable of scraping article details like title, date of publication, description, and more directly from web elements in the New York Times website.

### Create URL for Search

The project includes a `UrlConstructor` class that assists in dynamically creating and modifying URLs for searching articles on the New York Times.

### Bypass Paywall

The parser has the capability to block and unblock the paywall for a seamless scraping experience.

### Filter News

You can filter out articles based on various criteria like date and keywords, though the date filter is currently under improvement.

### Full Text Extraction

This parser also has the ability to retrieve the full text of an article, providing more contextual information beyond headlines and summaries.

### Search for Various Currencies

The parser can automatically detect mentions of various currencies like USD, EURO, and GBP within the article text.

### Export Functionality

After parsing, the data can be exported in either CSV or Excel formats for further analysis.



