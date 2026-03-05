import time
import random
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from curl_cffi import requests
from bs4 import BeautifulSoup
import warnings

warnings.simplefilter(action='ignore')

# ---------------------------------------------------------
# 1. SETUP: The Robot's Diary
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# ---------------------------------------------------------
# 2. THE ENGINE: RetailIntelligencePipeline
# ---------------------------------------------------------
class RetailIntelligencePipeline:
    def __init__(self, target_excel: str):
        self.target_excel = Path(target_excel)
        
        # The URL where Amazon lists the most popular SSDs in real-time
        self.best_sellers_url = "https://www.amazon.ca/Best-Sellers-Electronics-Internal-Solid-State-Drives/zgbs/electronics/3312786011"
        
        # The Disguises
        self.browser_profiles = ["chrome110", "chrome120", "edge101", "safari15_3", "safari15_5"]
        
        # THE FALLBACK: If the Scout gets blocked, use these guaranteed links so the 3-hour cycle doesn't fail.
        self.fallback_urls = [
            "https://www.amazon.ca/Samsung-990-PRO-SSD-2TB/dp/B0BHJJ9Y77/",
            "https://www.amazon.ca/WD_BLACK-SN850X-Internal-Gaming-Heatsink/dp/B0B7CKZHH9/",
            "https://www.amazon.ca/Crucial-Plus-PCIe-NAND-5000MB/dp/B0B25MJ1YT/",
            "https://www.amazon.ca/Sabrent-Internal-Extreme-Performance-SB-RKT4P-2TB/dp/B08P25PBJJ/"
        ]

    def _deploy_scout(self) -> list:
        """Step 1: The Scout. Hunts down the current Top 10 URLs."""
        logging.info("🦅 Deploying Scout to discover the current Top 10 Best Sellers...")
        disguise = random.choice(self.browser_profiles)
        
        try:
            response = requests.get(self.best_sellers_url, impersonate=disguise, timeout=30)
            
            if "captcha" in response.text.lower() or "automated access" in response.text.lower():
                logging.warning("⚠️ Scout was blocked by Amazon Security. Switching to Fallback List.")
                return self.fallback_urls

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Amazon stores Best Sellers inside specific grid boxes
            items = soup.find_all('div', {'id': 'gridItemRoot'})
            top_10_urls = []

            for item in items[:10]: # Grab only the first 10
                link_tag = item.find('a', class_='a-link-normal')
                if link_tag and 'href' in link_tag.attrs:
                    raw_url = "https://www.amazon.ca" + link_tag['href']
                    # Clean the URL to remove tracking junk (cuts off everything after 'ref=')
                    clean_url = raw_url.split('ref=')[0]
                    top_10_urls.append(clean_url)

            if top_10_urls:
                logging.info(f"📍 Scout successfully mapped {len(top_10_urls)} dynamic targets.")
                return top_10_urls
            else:
                logging.warning("⚠️ Scout found the page, but couldn't read the links. Layout may have changed. Using Fallback.")
                return self.fallback_urls
                
        except Exception as e:
            logging.error(f"Scout encountered a critical error: {e}. Using Fallback List.")
            return self.fallback_urls

    def _save_and_format_excel(self, new_data: list[dict]) -> None:
        """The Builder and Painter for the Excel file."""
        if not new_data:
            return 

        df_new = pd.DataFrame(new_data)
        
        if self.target_excel.exists():
            df_existing = pd.read_excel(self.target_excel)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_excel(self.target_excel, index=False)

        try:
            from openpyxl import load_workbook
            from openpyxl.styles import Font, PatternFill, Alignment

            wb = load_workbook(self.target_excel)
            ws = wb.active

            header_fill = PatternFill(start_color="002060", end_color="002060", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            for cell in ws[1]: 
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")

            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                for cell in row:
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            for col in ws.columns:
                max_length = 0
                column_letter = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = max_length + 5

            wb.save(self.target_excel)
            print("🎨 SUCCESS: Dashboard dynamically formatted.")
        except PermissionError:
            logging.error("Could not paint: Please close Excel!")
        except Exception as e:
            logging.error(f"Formatting error: {e}")

    def run_stealth_scan(self) -> None:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        print(f"\n[{now}] 🚀 Initiating Dynamic Top-10 Market Scan...")
        print("-" * 80)

        # 1. Ask the Scout for the target URLs
        target_urls = self._deploy_scout()
        gathered_intelligence = []

        # 2. Extract data from the discovered targets
        for index, url in enumerate(target_urls, start=1):
            try:
                sleep_timer = random.uniform(25, 45)
                logging.info(f"Camouflage active. Loitering for {sleep_timer:.1f}s before approaching Target #{index}...")
                time.sleep(sleep_timer)

                disguise = random.choice(self.browser_profiles)
                response = requests.get(url, impersonate=disguise, timeout=30)
                
                if "captcha" in response.text.lower() or "automated access" in response.text.lower():
                    logging.error(f"🚨 HARD BLOCK: CAPTCHA triggered on Target #{index}. Skipping.")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                title_elem = soup.find("span", {"id": "productTitle"})
                if not title_elem:
                    logging.warning(f"⚠️ SOFT BLOCK: Blank page loaded for Target #{index}. Skipping.")
                    continue
                
                # THE UPGRADE: We now dynamically extract the official name directly from the page
                product_name = title_elem.get_text().strip()

                price_element = soup.find("span", {"class": "a-offscreen"})
                live_price = price_element.get_text().strip().replace('$', '').replace(',', '') if price_element else "N/A"

                orig_elem = soup.find("span", {"class": "a-price a-text-price"})
                if orig_elem and orig_elem.find("span", {"class": "a-offscreen"}):
                    orig_price = orig_elem.find("span", {"class": "a-offscreen"}).get_text().strip().replace('$', '').replace(',', '')
                else:
                    orig_price = live_price 

                rating_elem = soup.find("span", {"class": "a-icon-alt"})
                rating = rating_elem.get_text().strip().split(' ')[0] if rating_elem else "N/A"

                review_elem = soup.find("span", {"id": "acrCustomerReviewText"})
                if review_elem:
                    reviews = review_elem.get_text().strip().split(' ')[0].replace(',', '').replace('(', '').replace(')', '')
                else:
                    reviews = "0"

                avail_elem = soup.find("div", {"id": "availability"})
                availability = avail_elem.get_text().strip().replace('\n', ' ') if avail_elem else "Unknown"

                gathered_intelligence.append({
                    'Timestamp': now,
                    'Product': product_name[:60] + "...", # Cuts off massive Amazon titles to keep Excel clean
                    'Live Price': f"${live_price}" if live_price != "N/A" else "N/A",
                    'Original Price': f"${orig_price}" if orig_price != "N/A" else "N/A",
                    'Rating': rating,
                    'Total Reviews': reviews,
                    'Availability': availability
                })
                
                print(f"✅ ACQUIRED: Target #{index} | Price: ${live_price}")

            except Exception as error:
                logging.error(f"System failure on Target #{index}: {error}")
        
        if gathered_intelligence:
            self._save_and_format_excel(gathered_intelligence)

        print("-" * 80)
        print("🏁 Stealth Scan Complete.")

# ---------------------------------------------------------
# 3. EXECUTION: Starting the Engine
# ---------------------------------------------------------
if __name__ == "__main__":
    DEST = r'C:\Users\mansu\OneDrive\Desktop\Data Analyst Boot Camp\SSD_Market_Master.xlsx'
    pipeline = RetailIntelligencePipeline(target_excel=DEST)
    
    print("🤖 Stealth Retail Pipeline is ONLINE. Starting automated 3-hour cycles...")
    
    try:
        while True:
            pipeline.run_stealth_scan()
            
            print(f"\n⏳ Cycle complete. Entering 3-hour stealth hibernation...")
            print("   Press Ctrl + C in this terminal to safely stop the engine.")
            time.sleep(10800) # 10,800 seconds = 3 hours
            
    except KeyboardInterrupt:
        print("\n🛑 Manual Override: Pipeline safely shut down.")
        
              