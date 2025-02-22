# config_handler.py
import configparser
import os

class ConfigHandler:
    """
    Reads and provides access to configuration parameters from 'config.ini'.
    """

    def __init__(self, config_file='config.ini'):
        """
        :param config_file: Path to the config file (default 'config.ini')
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found.")
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def get_search_url(self):
        """Retrieve the search URL from [DEFAULT]."""
        return self.config['DEFAULT'].get('search_url', '')

    def get_user_agent(self):
        """Retrieve the user agent from [DEFAULT]."""
        return self.config['DEFAULT'].get('user_agent', '')

    def get_headers(self):
        """
        Merge 'User-Agent' from [DEFAULT] with optional [HEADERS].
        Returns a dict that can be used in requests, if needed.
        """
        headers = {
            "User-Agent": self.get_user_agent()
        }
        if 'HEADERS' in self.config:
            for key, value in self.config['HEADERS'].items():
                headers[key] = value
        return headers
