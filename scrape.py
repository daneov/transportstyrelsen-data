from dataclasses import dataclass
from datetime import datetime, timezone
from lxml import html
from zoneinfo import ZoneInfo
import csv
import json
import requests
import sys

@dataclass
class CaseDate:
    year: str
    month: str
    day: str
    timezone: ZoneInfo

    def to_iso8601(self):
        return self.__as_datetime().strftime("%Y-%m-%d")

    def processing_time(self, since):
        delta_days = (since - self.__as_datetime()).days
        proccessing_time_in_weeks = delta_days / 7 # Difference in weeks

        return proccessing_time_in_weeks

    def __as_datetime(self):
        return datetime(int(self.year), int(self.month), int(self.day), tzinfo=self.timezone)

class API:
    def get(self, url):
        # Fetch the page content
        response = requests.get(url, timeout=0.5)
        response.raise_for_status()

        return response.text

class SiteScraper:
    __month_map = {
        "januari": "01",
        "februari": "02",
        "mars": "03",
        "april": "04",
        "maj": "05",
        "juni": "06",
        "juli": "07",
        "augusti": "08",
        "september": "09",
        "oktober": "10",
        "november": "11",
        "december": "12"
    }

    def extract_date(self, data):
        tree = html.fromstring(data)

        # Use XPath to extract the day, month name, and year
        day_and_month = tree.xpath('normalize-space(//*[@id="page-alert-block"]/div/div/p/strong[1])')
        year = tree.xpath('normalize-space(//*[@id="page-alert-block"]/div/div/p/strong[2])')

        if not day_and_month or not year:
            raise ValueError("Could not find the expected elements on the page.")

        day, month_name = day_and_month.split()

        return year.strip(), self.__map_month(month_name.strip()), day.strip()

    def __map_month(self, original_month_name):
        month = self.__month_map.get(original_month_name.lower())

        if not month:
            raise ValueError(f"Unknown month name: {original_month_name}")

        return month

def append_to_csv(file_path, today, case_date, processing_time):
    # Specify the header
    headers = ["Date", "Evaluating cases", "Waiting period"]
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, dialect='unix')
            # Write the header only if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow({
                "Date": today,
                "Evaluating cases": case_date,
                "Waiting period": round(processing_time, 2)
            })
    except Exception as e:
        print(f"Error writing to CSV: {e}")

source_timezone = ZoneInfo("Europe/Stockholm")
url = "https://www.transportstyrelsen.se/sv/vagtrafik/fordon/aga-kopa-eller-salja-fordon/import-och-export-av-fordon/fordonsimport-och-ursprungskontroll/"
csv_file_path = "transportstyrelsen_data.csv"

def main():
    api = API()
    scraper = SiteScraper()
    now = datetime.now(timezone.utc)

    try:
        case_date = CaseDate(*scraper.extract_date(api.get(url)), timezone=source_timezone)
        append_to_csv(csv_file_path, now, case_date.to_iso8601(), case_date.processing_time(since=now))
        print("Written to disk")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stdout)
        sys.exit(64)

if __name__ == "__main__":
    main()
