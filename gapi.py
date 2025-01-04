from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GumroadAPIDocScraper:
    def __init__(self):
        self.driver = self._initialize_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.api_docs = {}

    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scroll_to_element(self, element):
        """Scroll an element into view using JavaScript."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

    def get_sidebar_sections(self):
        """Extract links to documentation sections from the sidebar."""
        sections = []
        try:
            # Wait for the sidebar to load
            time.sleep(5)
            
            sidebar_links = self.driver.find_elements(By.XPATH, "//a[@href]")
            for link in sidebar_links:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and text and "gumroad.com" in href:
                    sections.append({"title": text, "url": href})
            
            return sections
        except Exception as e:
            logging.error(f"Error extracting sidebar sections: {e}")
            return []

    def extract_page_content(self):
        """Extract the title and content of the current page."""
        try:
            title = self.driver.title.strip()
            content = self.driver.find_element(By.TAG_NAME, "body").text.strip()
            return {"title": title, "content": content, "url": self.driver.current_url}
        except Exception as e:
            logging.error(f"Error extracting page content: {e}")
            return None

    def scrape_documentation(self):
        """Main scraping function."""
        try:
            # Open Gumroad API documentation page
            self.driver.get("https://app.gumroad.com/api")
            logging.info("Navigating to Gumroad API documentation")

            # Get sidebar sections
            sections = self.get_sidebar_sections()
            if not sections:
                logging.error("No sections found in the sidebar")
                return
            
            logging.info(f"Found {len(sections)} sections to scrape")

            # Iterate over each section
            for section in sections:
                try:
                    logging.info(f"Processing section: {section['title']}")
                    self.driver.get(section["url"])
                    time.sleep(2)  # Wait for the page to load

                    # Extract content
                    content = self.extract_page_content()
                    if content:
                        self.api_docs[section["title"]] = content
                        logging.info(f"Successfully scraped: {section['title']}")
                except Exception as e:
                    logging.error(f"Error processing section {section['title']}: {e}")
                    continue

            self.save_to_json()
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
        finally:
            self.driver.quit()

    def save_to_json(self):
        """Save scraped content to a JSON file."""
        try:
            if not self.api_docs:
                logging.warning("No content scraped!")
                return
            
            with open("gumroad_api_docs.json", "w", encoding="utf-8") as f:
                json.dump(self.api_docs, f, indent=4, ensure_ascii=False)
            
            logging.info("Scraped documentation saved to 'gumroad_api_docs.json'")
        except Exception as e:
            logging.error(f"Error saving to JSON: {e}")

def main():
    scraper = GumroadAPIDocScraper()
    scraper.scrape_documentation()

if __name__ == "__main__":
    main()
