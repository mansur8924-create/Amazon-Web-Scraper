# Amazon-Web-Scraper
 Project Overview

This project addresses the challenge of real-time market monitoring. I developed a custom Python-based web scraper to automate the collection of product data (specifically SSDs) from Amazon. By extracting pricing trends, ratings, and product specifications, this tool provides the foundational data needed for competitive market analysis.

Tools & Technologies

Python: The core language for building the scraping logic.

BeautifulSoup & Requests: Utilized for parsing HTML content and handling HTTP requests to extract specific data points.

Pandas: Used to structure the raw scraped data into a clean, tabular format.

CSV/Excel: Final data is exported into structured files (SSD_Market_Master.xlsx) for business use.

 Project Structure

Extraction Engine (amazon ssd.py): The primary script that navigates product pages and captures titles, prices, and reviews.

Data Export (import csv.py): A utility script focused on ensuring the data is correctly appended to the master database without duplication.

Market Database: The final output file containing gathered market intelligence on SSD products.

 Key Features

Automation: The script can be scheduled to run at specific intervals to track price fluctuations over time.

Scalability: The logic is designed to be easily adapted for other product categories beyond SSDs.

Data Integrity: Includes error handling to manage cases where product information might be missing or formatted inconsistently on the live web.

 How to Use

Clone the repository: Download the scripts to your local machine.

Configure Headers: Ensure the User-Agent in the Python script matches your browser to prevent being blocked by the site's security.

Run the Scraper: Execute python "amazon ssd.py" to begin the data collection process.

Review Output: Open SSD_Market_Master.xlsx to see the newly collected data.
