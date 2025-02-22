# crawler.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Crawler:
    """
    Helper class for configuring and managing the Selenium WebDriver.
    """
    def __init__(self, headless=True, user_agent=None, disable_images=True):
        """
        :param headless: Boolean to run Chrome headless (default True).
        :param user_agent: Optional user agent string. If None, Chrome's default is used.
        :param disable_images: Disable image loading to speed up page loads.
        """
        self.headless = headless
        self.user_agent = user_agent
        self.disable_images = disable_images
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """
        Set up the Selenium ChromeDriver with specified options.
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        if self.user_agent:
            chrome_options.add_argument(f"user-agent={self.user_agent}")

        # Some performance or debugging flags
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Disable images if requested
        if self.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)

        # Create driver via webdriver_manager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def get_driver(self):
        """
        Retrieve the Selenium WebDriver instance.
        """
        if not self.driver:
            self.setup_driver()
        return self.driver

    def quit(self):
        """Quit the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
