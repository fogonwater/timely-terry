from datetime import datetime
import json
import time
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

import config


def tstamp():
    """ Return string representation of current timestamp """
    return datetime.now().strftime("%H:%M:%S")


def tag_visible(element):
    """ Filter updates of elements """
    # Ignore non-visible text tags, like script and style
    if element.parent.name in config.IGNORE_ELEMENTS:
        return False
    # Also HTML comments
    if isinstance(element, Comment):
        return False
    return True


def retrieve_page_text(url, user_agent):
    """
    Requests content from a URL. On 200 success, returns a stripped
    text of visible page elements. Failure returns None.
    """
    # Set the headers for the user agent
    headers = {"User-Agent": user_agent}
    # Request content from url
    try:
        response = requests.get(url, headers=headers)
    # If request breaks, print error and return None
    except Exception as e:
        print("{} * {}".format(tstamp(), e))
        print("Terry was unable to retrieve: {}".format(url))
        return None
    # Also bail on a clean response where status code is not 200
    if response.status_code != 200:
        print(
            "{} * Got {} response from: {}".format(tstamp(), response.status_code, url)
        )
        return None
    # On a 200 response, transform into beautiful soup object and extract visible text
    soup = BeautifulSoup(response.text, "html.parser")
    soup_text = soup.find_all(text=True)
    visible_text = filter(tag_visible, soup_text)
    return " ".join(t.strip().lower() for t in visible_text if t.strip())


class Terry:
    """ Bot who can scan pages and notify Slack channel of changes """

    def __init__(self):
        self.user_agent = config.USER_AGENT
        self.check_frequency = config.CHECK_FREQUENCY
        self.pages = {}
        for page in config.PAGES:
            self.add_page(page["label"], page["url"])

    def add_page(self, label, url):
        """ Add a new page for scanning """
        # TODO - Fix Terry from breaking if there is an issue when first adding pages
        original = retrieve_page_text(url, self.user_agent)
        print("'{}' reference page has {} characters.".format(label, len(original)))
        self.pages[label] = {
            "label": label,
            "url": url,
            "original": original,
            "has_changed": False,
        }

    def count_changed_pages(self):
        """ Count number of pages that have changed since scanning began. """
        return len([p for p in self.pages.values() if p["has_changed"]])

    def update_slack(self, page):
        """ Send message to Slack channel about updated page. """
        label = page["label"]
        message = "I found a change on '{}'. Visit: {}".format(label, page["url"])
        r = requests.post(
            config.SLACK_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"text": message}),
        )
        print(
            "{} Sent Slack an update about {}. Got back {} status.".format(
                tstamp(), label, r.status_code
            )
        )
        # If we successfully update Slack, set this page's has_changed to True
        if r.status_code == 200:
            print("    Updating has_changed to True")
            self.pages[label]["has_changed"] = True
            return True
        else:
            print("    Terry could not update Slack, so will try again soon.")
            return False

    def scan(self):
        """ Go into scanning mode. Keep scanning until all pages updated. """
        while True:
            for page in self.pages.values():
                # If this page has changed, skip it
                if page["has_changed"] == True:
                    continue
                # Get a copy of current page. Skip on bad response from source.
                current = retrieve_page_text(page["url"], self.user_agent)
                if not current:
                    continue
                # Compare current text with original reference text
                if current and current != page["original"]:
                    print("{} {} updated!".format(tstamp(), page["label"]))
                    print("    New content has {} characters.".format(len(current)))
                    self.update_slack(page)
                else:
                    print("{} '{}' no update.".format(tstamp(), page["label"]))
            # Update the console with how many pages have changed.
            print(
                "Terry has detected {} page changes to date.".format(
                    self.count_changed_pages()
                )
            )
            # If all pages have changed, exit scan mode.
            if self.count_changed_pages() == len(self.pages):
                break
            # Otherwise, sleep until it's time to check again
            time.sleep(self.check_frequency)
        print("All pages have changed. Terry is knocking off work.")

    def test_message(self, message="Terry is ready and working."):
        """ Send a test message to Slack channel via your webhook. """
        r = requests.post(
            config.SLACK_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"text": message}),
        )
        print(
            "{} Sent Slack a test message. Received {} status.".format(
                tstamp(), r.status_code
            )
        )


def main():
    terry = Terry()
    # terry.test_message()
    terry.scan()


if __name__ == "__main__":
    main()
