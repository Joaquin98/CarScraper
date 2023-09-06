# Program README

## Introduction

This Python program is designed for web scraping data from the AutoTrader website. It collects information about cars listed for sale, including details such as the car's name, engine specifications, dealer name, location, colors available, and more. The program utilizes the Selenium web scraping library to navigate and extract data from web pages.

## Prerequisites

Before running the program, make sure you have the following prerequisites installed:

- Python 3.x
- Selenium library
- Undetected Chromedriver
- Google Chrome (for Chromedriver)

You can install the required Python libraries using pip:

```bash
pip install -r requirements.txt
```

## Program Structure

The program consists of a Python class named `Bot`, which encapsulates the web scraping logic. Here's an overview of the program's structure and key components:

- `selectors_dict`: This dictionary contains XPath selectors for various elements on the web page, such as car names, engine details, and more. These selectors are used to locate and extract specific information.

- `get_brands` Method: This method starts the web scraping process by navigating to AutoTrader's search page and extracting a list of car brands. It iterates through the brands and years, collecting car links for each combination.

- `thread_function` Method: This method defines the behavior of individual threads when running in parallel. It is used to scrape car data concurrently.

- `start_parallel` Method: This method coordinates the parallel execution of data scraping using multiple threads.

- `get_car_info` Method: This method scrapes and extracts detailed information about a single car listing, including its name, engine details, dealer name, location, and color options.

- `get_car_info_parrallel` Method: Similar to `get_car_info`, this method scrapes car information in parallel using a separate WebDriver instance for each thread.

- `start_files` Method: This method initializes the program by creating necessary directories and files for data storage.

- `get_id_from_links` Method: This method extracts unique car IDs from car links and stores them for further processing.

## Usage

To use the program, follow these steps:

1. Install the required libraries using `pip` as mentioned in the "Prerequisites" section.

2. Run the program using the following command:

   ```bash
   python auto_trader_bot.py
   ```

3. Choose one of the following options:
   - Option 1: Get post IDs. This option collects car IDs by scraping the AutoTrader website.
   - Option 2: Get data from stored post IDs. This option extracts detailed car information from the collected car IDs.

5. The program will start scraping data or processing stored car IDs based on your choice.

## Data Storage

- The program stores collected car links in a CSV file named `./bot_data/links.csv`.

- Extracted car information is saved in a CSV file named `./data/cars.csv`.

## Notes

- The program may require adjustments to work with the specific layout and structure of the AutoTrader website, as website structures can change over time.

- Ensure that you have the appropriate permissions to scrape data from websites, and be respectful of website terms of service and usage policies.

- The program's behavior can be further customized and extended to collect additional data or perform specific actions as needed.

- Make sure to periodically update your Chrome browser and Chromedriver to avoid compatibility issues.

## Disclaimer

This program is provided for educational and demonstration purposes only. Always abide by website terms of service and legal regulations when conducting web scraping activities. Use this program responsibly and ensure that your web scraping activities comply with applicable laws and regulations.