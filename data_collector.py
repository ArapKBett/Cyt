# data_collector.py
import requests
from bs4 import BeautifulSoup
import re
from loguru import logger
from config import Config
import time
from typing import List, Dict

class DataCollector:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self._setup_logging()

    def _setup_logging(self):
        logger.add(Config.LOG_FILE, level=Config.LOG_LEVEL, rotation="10 MB")

    def _rate_limit_handler(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"Rate limit hit, sleeping for {retry_after} seconds")
            time.sleep(retry_after)
            return True
        return False

    def fetch_github_repos(self, query: str) -> List[Dict]:
        try:
            url = f"{Config.GITHUB_API}/search/repositories"
            params = {"q": query, "per_page": Config.MAX_REPOS}
            response = requests.get(url, headers=self.headers, params=params)
            
            if self._rate_limit_handler(response):
                return self.fetch_github_repos(query)
            
            response.raise_for_status()
            repos = response.json()["items"]
            return [
                {
                    "type": "repository",
                    "title": repo["name"],
                    "description": repo["description"] or "No description",
                    "url": repo["html_url"],
                    "source": "GitHub"
                } for repo in repos
            ]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch GitHub repos: {e}")
            return []

    def fetch_serpapi_results(self, query: str) -> List[Dict]:
        try:
            params = {
                "api_key": Config.SERPAPI_KEY,
                "q": query,
                "num": 10
            }
            response = requests.get(Config.SERPAPI_URL, params=params)
            response.raise_for_status()
            results = response.json().get("organic_results", [])
            return [
                {
                    "type": "search_result",
                    "title": result["title"],
                    "description": result.get("snippet", "No snippet"),
                    "url": result["link"],
                    "source": "SerpApi"
                } for result in results
            ]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch SerpApi results: {e}")
            return []

    def scrape_hacktricks(self, url: str) -> List[Dict]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            commands = []
            for code_block in soup.find_all("code"):
                command = code_block.text.strip()
                if command:
                    commands.append({
                        "type": "command",
                        "title": f"Command: {command[:30]}...",
                        "description": command,
                        "url": url,
                        "source": "HackTricks"
                    })
            return commands
        except requests.RequestException as e:
            logger.error(f"Failed to scrape HackTricks: {e}")
            return []

    def validate_code_snippet(self, code: str) -> bool:
        # Basic validation to avoid malicious code
        dangerous_patterns = [
            r"rm\s+-rf", r"exec\s*\(", r"eval\s*\(", r"os\.system\s*\("
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"Potentially dangerous code detected: {code[:50]}...")
                return False
        return True

    def collect_all(self) -> List[Dict]:
        resources = []
        for query in Config.SEARCH_QUERIES:
            resources.extend(self.fetch_github_repos(query))
            resources.extend(self.fetch_serpapi_results(query))
        
        for url in Config.SCRAPE_URLS:
            resources.extend(self.scrape_hacktricks(url))
        
        # Example: Add a validated code snippet
        sample_code = """
        import socket
        def scan_port(ip, port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return port if result == 0 else None
        """
        if self.validate_code_snippet(sample_code):
            resources.append({
                "type": "code",
                "title": "Simple Port Scanner",
                "description": sample_code,
                "url": "N/A",
                "source": "Custom"
            })
        
        logger.info(f"Collected {len(resources)} resources")
        return resources
