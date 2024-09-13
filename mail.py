import scrapy
import re
from scrapy_selenium import SeleniumRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class EmailtrackSpider(scrapy.Spider):
    name = 'emailtrack'

    def __init__(self, *args, **kwargs):
        super(EmailtrackSpider, self).__init__(*args, **kwargs)
        self.unique_emails = set()

    def start_requests(self):
        yield SeleniumRequest(
            url="https://webscraper.io/test-sites/e-commerce/scroll",
            wait_time=3,
            screenshot=True,
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        final_links = [str(link.url) for link in links]

        relevant_links = [link for link in final_links if any(keyword in link.lower() for keyword in ['contact', 'about'])]
        relevant_links.append(str(response.url))  

        if relevant_links:
            first_link = relevant_links.pop(0)
            yield SeleniumRequest(
                url=first_link,
                wait_time=3,
                screenshot=True,
                callback=self.parse_link,
                dont_filter=True,
                meta={'links': relevant_links}
            )

    def parse_link(self, response):
        links = response.meta['links']
        current_url = str(response.url)

        if not any(bad_word in current_url for bad_word in ['facebook', 'instagram', 'youtube', 'twitter', 'wiki', 'linkedin']):
            html_text = response.text
            email_list = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', html_text)
            self.unique_emails.update(email_list)

        if links:
            next_link = links.pop(0)
            yield SeleniumRequest(
                url=next_link,
                wait_time=3,
                screenshot=True,
                callback=self.parse_link,
                dont_filter=True,
                meta={'links': links}
            )
        else:
            yield SeleniumRequest(
                url=response.url,
                callback=self.parsed,
                dont_filter=True
            )

    def parsed(self, response):
        filtered_emails = [email for email in self.unique_emails if any(domain in email for domain in ['.in', '.com', 'info', 'org'])]
        
        print("\n\nEmails scraped:", filtered_emails, "\n\n")
