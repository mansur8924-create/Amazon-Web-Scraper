"""
PROJECT: Automated Retail Intelligence Pipeline
PURPOSE: End-to-end web scraping and data persistence for market analysis.
FEATURES: 
    - Dynamic Target Discovery (Scout Strategy).
    - Deep-Stealth Loitering (Anti-Bot evasion).
    - Automated Excel Formatting (Executive Dashboarding).
AUTHOR: Mansur Mohammed
DATE: 2026-03-04
"""

import time
import random
import logging
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from curl_cffi import requests
from bs4 import BeautifulSoup
import warnings

# Suppress minor warnings to ensure a clean, professional console output
warnings.simplefilter(action='ignore')

# WHY: In professional environments, we need a chronological record of system 
# performance to identify bottlenecks or failures without manual monitoring.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class RetailIntelligencePipeline:
    def __init__(self, target_excel: str):
        """
        Initializes the pipeline, defining targets and stealth parameters.
        """
        # Relative Path handling ensures the project is portable across different OS.
        self.target_excel = Path(target_excel)
        
        # Target: Amazon Canada - Best Sellers in Internal SSDs
        self.best_sellers_url = "https://www.amazon.ca/Best-Sellers-Electronics-Internal-Solid-State-Drives/zgbs/electronics/3312786011"
        
        # 'The Disguises': Browser fingerprints to bypass security filters.
        self.browser_profiles = ["chrome110", "chrome120", "edge101", "safari15_3", "safari15_5"]
        
        # THE FALLBACK: Essential targets to ensure data continuity if dynamic discovery fails.
        self.fallback_urls = [
            "https://www.amazon.ca/Samsung-990-PRO-SSD-2TB/dp/B0BHJJ9Y77/",
            "https://www.amazon.ca/WD_BLACK-SN850X-Internal-Gaming-Heatsink/dp/B0B7CKZHH9/",
            "https://www.amazon.ca/Crucial-Plus-PCIe-NAND-5000MB/dp/B0B25MJ1YT/",
            "https://www.amazon.ca/Sabrent-Internal-Extreme-Performance-SB-RKT4P-2TB/dp/B08P25PBJJ/"
        ]

    def _deploy_scout(self) -> list:
        """
        Step 1: The Scout. Dynamically harvests the current Top 10 product URLs.
        WHY: Market leaders shift frequently; dynamic scouting maintains data accuracy.
        """
        logging.info("🦅 Deploying Scout to discover current Top 10 Market Leaders...")
        disguise = random.choice(self.browser_profiles)
        try:
            response = requests.get(self.best_sellers_url, impersonate=disguise, timeout=30)
            
            # Security Check: Identifying if the scraper has been flagged (Captcha).
            if "captcha" in response.text.lower() or "automated access" in response.text.lower():
                logging.warning("⚠️ Scout was blocked. Activating Fallback Protocol.")
                return self.fallback_urls

            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.find_all('div', {'id': 'gridItemRoot'})
            top_10_urls = []
            
            for item in items[:10]:
                link_tag = item.find('a', class_='a-link-normal')
                if link_tag and 'href' in link_tag.attrs:
                    raw_url = "https://www.amazon.ca" + link_tag['href']
                    # Sanitizing URL: Removing tracking parameters for a clean database.
                    top_10_urls.append(raw_url.split('ref=')[0])
                    
            return top_10_urls if top_10_urls else self.fallback_urls
        except Exception as error:
            logging.error(f"Scout Error: {error}. Utilizing Fallback targets.")
            return self.fallback_urls

    def _save_and_format_excel(self, new_data: list[dict]) -> None:
        """
        The Builder: Manages data persistence and applies professional UI formatting.
        WHY: A raw CSV is for machines; a formatted Excel report is for stakeholders.
        """
        if not new_data: return 
        
        df_new = pd.DataFrame(new_data)
        
        # Persistent Storage: Appending new observations to build a time-series history.
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
            
            # Dark Blue Header (Industry Standard for BI Reports)
            header_fill = PatternFill(start_color="002060", end_color="002060", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            
            for cell in ws[1]: 
                cell.fill, cell.font = header_fill, header_font
                cell.alignment = Alignment(horizontal="center")
            
            # Auto-Adjusting Column Widths: Ensures readability upon file opening.
            for col in ws.columns:
                max_len = max([len(str(cell.value)) for cell in col])
                ws.column_dimensions[col[0].column_letter].width = max_len + 5
                
            wb.save(self.target_excel)
            print("🎨 SUCCESS: Intelligence Dashboard formatted for distribution.")
        except Exception as e: 
            logging.error(f"Post-Processing Error: {e}")

    def run_stealth_scan(self) -> None:
        """
        Core Extraction Loop: Executes a randomized, high-stealth data harvest.
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        print(f"\n[{now}] 🚀 Initiating Deep-Stealth Market Intelligence Scan...")
        
        target_urls = self._deploy_scout()
        gathered_intelligence = []

        for index, url in enumerate(target_urls, start=1):
            try:
                # Deep Loitering: Randomized delays mimic natural human browsing behavior.
                sleep_timer = random.uniform(45, 90)
                logging.info(f"Stealth Mode Active ({sleep_timer:.1f}s) for Target #{index}...")
                time.sleep(sleep_timer)

                response = requests.get(url, impersonate=random.choice(self.browser_profiles), timeout=30)
                if "captcha" in response.text.lower() or "automated access" in response.text.lower():
                    logging.error(f"🚨 Target #{index} blocked. Proceeding to next target.")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                title_elem = soup.find("span", {"id": "productTitle"})
                if not title_elem: continue 
                
                name = title_elem.get_text().strip()
                price_tag = soup.find("span", {"class": "a-offscreen"})
                live_p = price_tag.get_text().strip().replace('$', '').replace(',', '') if price_tag else "N/A"
                
                rating_elem = soup.find("span", {"class": "a-icon-alt"})
                rating = rating_elem.get_text().strip().split(' ')[0] if rating_elem else "N/A"
                
                review_elem = soup.find("span", {"id": "acrCustomerReviewText"})
                revs = review_elem.get_text().strip().split(' ')[0].replace(',', '') if review_elem else "0"

                gathered_intelligence.append({
                    'Timestamp': now, 
                    'Product': name[:60] + "...", 
                    'Live Price': f"${live_p}",
                    'Rating': rating, 
                    'Total Reviews': revs, 
                    'Status': "In Stock"
                })
                print(f"✅ ACQUIRED: Target #{index} | Market Price: ${live_p}")
            except Exception as e: 
                logging.error(f"Extraction failed on Target #{index}: {e}")
        
        self._save_and_format_excel(gathered_intelligence)
        print("-" * 60 + "\n🏁 Cycle Complete. Data persistent in local database.")

if __name__ == "__main__":
    # PORTABLE PATH:
    # Using a relative path ensures the project is 'Plug-and-Play' for GitHub.
    DESTINATION = 'SSD_Market_Master.xlsx'
    
    pipeline = RetailIntelligencePipeline(target_excel=DESTINATION)
    
    print("🤖 Stealth Retail Pipeline ONLINE. Automated 3-hour refresh cycles active.")
    
    try:
        while True:
            pipeline.run_stealth_scan()
            # Hibernation: 10,800 seconds = 3 Hours
            print(f"\n⏳ Cycle finished at {datetime.now().strftime('%H:%M')}. Entering hibernation...")
            time.sleep(10800) 
    except KeyboardInterrupt:
        print("\n🛑 Manual Override: Pipeline successfully deactivated.")
              

