import re
from typing import List, Optional
from bs4 import BeautifulSoup
import pandas as pd

class DataCleaner:
    def filter_text(self, text: str, keywords: List[str]) -> Optional[str]:
        """
        Filters the text based on a list of keywords. Returns the text if any keyword is found.
        """
        if any(re.search(rf'\b{word}\b', text.lower()) for word in keywords):
            return text
        return None

    def get_urls(self, texts: List[str], filter: Optional[str] = None) -> List[str]:
        """
        Extracts URLs from a list of texts. Optionally filters them based on a keyword or pattern.
        """
        urls = []
        for text in texts:
            found_urls = re.findall(r'http[s]?://\S+', text)
            if filter:
                found_urls = [url for url in found_urls if filter in url]
            urls.extend(found_urls)
        return urls

    def extract_countries(self, content: str, countries: List[str]) -> List[str]:
        """
        Extracts mentions of countries from the content based on a predefined list of countries.
        """
        return [country for country in countries if country in content]

    def extract_bitcoin_resistance_levels(self, content: str) -> List[float]:
        """
        Extracts Bitcoin resistance levels from the content using a regular expression.
        """
        resistance_levels = re.findall(r'resistance at \$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', content, re.IGNORECASE)
        return [float(level.replace(',', '')) for level in resistance_levels]

    def extract_images(self, html_content: str, keyword: Optional[str] = None) -> List[str]:
        """
        Extracts image URLs from the HTML content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        images = soup.find_all('img')
        image_urls = [img['src'] for img in images if 'src' in img.attrs]
        return image_urls

    def clean_html(self, html_content: str) -> dict:
        """
        Cleans raw HTML content by removing unnecessary tags, scripts, and styles,
        leaving only the relevant text and returning a dictionary that maps HTML tags
        to their corresponding text content or attributes.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Dictionary to hold the cleaned content with tag names
        content_dict = {}

        # Iterate through all tags and extract text or other relevant attributes
        for tag in soup.find_all(True):  # True finds all tags
            tag_name = tag.name
            if tag_name in ['a', 'img', 'source', 'link']:  # Special handling for certain tags
                if tag_name == 'a':
                    content_dict.setdefault(tag_name, []).append({
                        "text": tag.get_text(separator=' ').strip(),
                        "href": tag.get('href', '')
                    })
                elif tag_name == 'img':
                    content_dict.setdefault(tag_name, []).append(tag.get('src', ''))
                elif tag_name == 'source':
                    content_dict.setdefault(tag_name, []).append(tag.get('src', ''))
                elif tag_name == 'link':
                    content_dict.setdefault(tag_name, []).append(tag.get('href', ''))
            else:
                text = tag.get_text(separator=' ').strip()
                if text:  # Only add non-empty text
                    content_dict.setdefault(tag_name, []).append(text)

        return content_dict



    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarizes a large body of text to capture the key points. 
        """
        sentences = text.split('. ')
        summary = '. '.join(sentences[:max_length])
        if len(sentences) > max_length:
            summary += '...'
        return summary



if __name__ == "__main__":
    pass