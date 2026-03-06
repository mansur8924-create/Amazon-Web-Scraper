import time
import random
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from curl_cffi import requests
from bs4 import BeautifulSoup
import warnings

"""
PROJECT: Retail Price Monitoring Pipeline
PURPOSE: Track top SSD products on Amazon Canada by price, rating, and reviews.
         Each run captures a snapshot for trend analysis over time.
AUTHOR: Mansur Mohammed
"""

# Suppress minor warnings for a clean console
warnings.simplefilter("ignore")

# Setup logging for progress updates
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)


class RetailPricePipeline:
    """
    Core pipeline to scrape Amazon SSD data and store it in Excel.
    """

    def __init__(self, output_file: str):
        self.output_file = Path(output_file)

        # Amazon Best Sellers for Internal SSDs
        self.best_sellers_url = (
            "https://www.amazon.ca/Best-Sellers-Electronics-Internal-Solid-State-Drives/"
            "zgbs/electronics/3312786011"
        )

        # Browser profiles to avoid bot detection
        self.browser_profiles = ["chrome110", "chrome120", "edge101", "safari15_3", "safari15_5"]

        # Backup URLs if the main page fails
        self.fallback_urls = [
            "https://www.amazon.ca/Samsung-990-PRO-SSD-2TB/dp/B0BHJJ9Y77/",
            "https://www.amazon.ca/WD_BLACK-SN850X-Internal-Gaming-Heatsink/dp/B0B7CKZHH9/",
            "https://www.amazon.ca/Crucial-Plus-PCIe-NAND-5000MB/dp/B0B25MJ1YT/",
            "https://www.amazon.ca/Sabrent-Internal-Extreme-Performance-SB-RKT4P-2TB/dp/B08P25PBJJ/"
        ]

    def get_top_products(self):
        """
        Retrieve the top 10 SSD product URLs from Amazon.
        Falls back to predefined URLs if scraping fails or is blocked.
        """
        logging.info("Loading Amazon best sellers page...")

        try:
            response = requests.get(
                self.best_sellers_url,
                impersonate=random.choice(self.browser_profiles),
                timeout=30
            )

            # Detect if a captcha blocked the request
            if "captcha" in response.text.lower():
                logging.warning("Captcha detected. Using fallback product URLs.")
                return self.fallback_urls

            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.find_all("div", {"id": "gridItemRoot"})

            urls = []
            for item in items[:10]:
                link = item.find("a", class_="a-link-normal")
                if link and "href" in link.attrs:
                    url = "https://www.amazon.ca" + link["href"]
                    urls.append(url.split("ref=")[0])  # clean URL

            return urls if urls else self.fallback_urls

        except Exception as e:
            logging.error(f"Failed to load best sellers page: {e}")
            return self.fallback_urls

    def save_results(self, data):
        """
        Save the latest product data into Excel.
        Appends to existing data if the file already exists.
        """
        if not data:
            return

        df_new = pd.DataFrame(data)

        if self.output_file.exists():
            df_old = pd.read_excel(self.output_file)
            df = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df = df_new

        df.to_excel(self.output_file, index=False)
        logging.info(f"Results saved to {self.output_file}")

    def run_scan(self):
        """
        Run a full scraping cycle: retrieve product data and save it.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        logging.info(f"Starting price scan at {timestamp}")

        urls = self.get_top_products()
        results = []

        for i, url in enumerate(urls, start=1):
            try:
                # Random delay to mimic human behavior
                delay = random.uniform(45, 90)
                logging.info(f"Waiting {delay:.1f}s before requesting product {i}")
                time.sleep(delay)

                response = requests.get(
                    url,
                    impersonate=random.choice(self.browser_profiles),
                    timeout=30
                )

                if "captcha" in response.text.lower():
                    logging.warning(f"Blocked by Amazon on product {i}, skipping.")
                    continue

                soup = BeautifulSoup(response.content, "html.parser")

                # Extract product info
                title = soup.find("span", {"id": "productTitle"})
                if not title:
                    continue
                name = title.get_text().strip()

                price_tag = soup.find("span", {"class": "a-offscreen"})
                price = price_tag.get_text().replace("$", "").replace(",", "") if price_tag else "N/A"

                rating_tag = soup.find("span", {"class": "a-icon-alt"})
                rating = rating_tag.get_text().split(" ")[0] if rating_tag else "N/A"

                review_tag = soup.find("span", {"id": "acrCustomerReviewText"})
                reviews = review_tag.get_text().split(" ")[0].replace(",", "") if review_tag else "0"

                results.append({
                    "Timestamp": timestamp,
                    "Product": name[:60],
                    "Price": price,
                    "Rating": rating,
                    "Reviews": reviews
                })

                logging.info(f"Collected product {i}: {name[:40]}")

            except Exception as e:
                logging.error(f"Error collecting product {i}: {e}")

        self.save_results(results)
        logging.info("Scan completed successfully.")


if __name__ == "__main__":
    OUTPUT_FILE = "SSD_Market_Master.xlsx"
    pipeline = RetailPricePipeline(OUTPUT_FILE)

    print("🚀 Retail price monitoring started.")

    try:
        while True:
            pipeline.run_scan()
            print("🛌 Scan complete. Sleeping for 3 hours before next run...")
            time.sleep(10800)  # 3 hours
    except KeyboardInterrupt:
        print("🛑 Monitoring stopped by user.")



