"""LinkedIn automation using Selenium"""
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict, List
import agent.infra.config as config


class LinkedInBot:
    """LinkedIn automation bot"""
    
    def __init__(self):
        self.driver = None
        self.logged_in = False
    
    def _random_delay(self):
        """Random delay to avoid detection"""
        time.sleep(random.uniform(config.LINKEDIN_DELAY_MIN, config.LINKEDIN_DELAY_MAX))
    
    def start_browser(self):
        """Start Chrome browser"""
        options = Options()
        
        if config.LINKEDIN_HEADLESS:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Browser started")
    
    def login(self) -> bool:
        """
        Login to LinkedIn
        
        Returns:
            True if successful
        """
        if not config.LINKEDIN_EMAIL or not config.LINKEDIN_PASSWORD:
            print("❌ LinkedIn credentials not configured")
            return False
        
        try:
            print("🔐 Logging into LinkedIn...")
            
            self.driver.get("https://www.linkedin.com/login")
            self._random_delay()
            
            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(config.LINKEDIN_EMAIL)
            self._random_delay()
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(config.LINKEDIN_PASSWORD)
            self._random_delay()
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(5)
            
            # Check if logged in
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                self.logged_in = True
                print("✅ Logged in successfully")
                return True
            else:
                print("❌ Login failed - check credentials")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def search_people(self, company_name: str, title: str = None) -> List[str]:
        """
        Search for people at a company
        
        Args:
            company_name: Company to search
            title: Job title to filter (optional)
            
        Returns:
            List of profile URLs
        """
        if not self.logged_in:
            print("❌ Not logged in")
            return []
        
        try:
            # Build search URL
            search_query = f'"{company_name}"'
            if title:
                search_query += f' "{title}"'
            
            url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            
            print(f"🔍 Searching LinkedIn for: {search_query}")
            self.driver.get(url)
            self._random_delay()
            
            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Get profile links
            profile_links = []
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link[href*='/in/']")
            
            for element in elements:
                href = element.get_attribute('href')
                if '/in/' in href and href not in profile_links:
                    profile_links.append(href.split('?')[0])  # Remove query params
            
            print(f"✅ Found {len(profile_links)} profiles")
            return profile_links[:10]  # Return top 10
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return []
    
    def send_connection_request(self, profile_url: str, message: Optional[str] = None) -> Dict:
        """
        Send connection request to a profile
        
        Args:
            profile_url: LinkedIn profile URL
            message: Optional custom message (Note: may require Premium)
            
        Returns:
            Result dictionary
        """
        if not self.logged_in:
            return {"success": False, "error": "Not logged in"}
        
        try:
            print(f"📤 Sending connection request: {profile_url}")
            
            self.driver.get(profile_url)
            self._random_delay()
            
            # Find and click Connect button
            connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Connect')]")
            
            if not connect_buttons:
                return {"success": False, "error": "Connect button not found (may already be connected)"}
            
            connect_buttons[0].click()
            self._random_delay()
            
            # If message provided and text area appears
            if message:
                try:
                    # Click "Add a note"
                    add_note_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Add a note')]")
                    add_note_button.click()
                    self._random_delay()
                    
                    # Enter message
                    message_field = self.driver.find_element(By.TAG_NAME, "textarea")
                    message_field.send_keys(message[:300])  # LinkedIn limit
                    self._random_delay()
                except:
                    print("⚠️ Could not add note (may require Premium)")
            
            # Click Send
            send_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Send')]")
            send_button.click()
            self._random_delay()
            
            print("✅ Connection request sent")
            return {"success": True, "profile_url": profile_url}
            
        except Exception as e:
            print(f"❌ Error sending request: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_message(self, profile_url: str, message: str) -> Dict:
        """
        Send a message to an existing connection
        
        Args:
            profile_url: LinkedIn profile URL
            message: Message to send
            
        Returns:
            Result dictionary
        """
        if not self.logged_in:
            return {"success": False, "error": "Not logged in"}
        
        try:
            print(f"💬 Sending message: {profile_url}")
            
            self.driver.get(profile_url)
            self._random_delay()
            
            # Find Message button
            message_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Message')]")
            
            if not message_buttons:
                return {"success": False, "error": "Message button not found (may not be connected)"}
            
            message_buttons[0].click()
            self._random_delay()
            
            # Find message input
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
            )
            
            message_input.send_keys(message)
            self._random_delay()
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
            send_button.click()
            self._random_delay()
            
            print("✅ Message sent")
            return {"success": True, "profile_url": profile_url}
            
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")


def linkedin_outreach(company_name: str, title: str, message: str, max_requests: int = 5) -> Dict:
    """
    Automated LinkedIn outreach workflow
    
    Args:
        company_name: Target company
        title: Job title to search for
        message: Connection request message
        max_requests: Max number of requests to send
        
    Returns:
        Summary of results
    """
    bot = LinkedInBot()
    
    try:
        # Start and login
        bot.start_browser()
        if not bot.login():
            return {"success": False, "error": "Login failed"}
        
        # Search for people
        profiles = bot.search_people(company_name, title)
        
        if not profiles:
            return {"success": False, "error": "No profiles found"}
        
        # Send connection requests
        results = {
            "success": True,
            "company": company_name,
            "searched_title": title,
            "profiles_found": len(profiles),
            "requests_sent": 0,
            "failed": 0
        }
        
        for i, profile_url in enumerate(profiles[:max_requests]):
            if i >= config.LINKEDIN_DAILY_LIMIT:
                print(f"⚠️ Daily limit reached ({config.LINKEDIN_DAILY_LIMIT})")
                break
            
            result = bot.send_connection_request(profile_url, message)
            
            if result['success']:
                results['requests_sent'] += 1
            else:
                results['failed'] += 1
            
            # Longer delay between requests
            time.sleep(random.uniform(10, 20))
        
        return results
        
    except Exception as e:
        return {"success": False, "error": str(e)}
        
    finally:
        bot.close()
