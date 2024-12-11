import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import json
import csv
from lxml import html

def scrape_website(url):
    try:
        # Fetch the page content
        response = requests.get(url, timeout=0.5)
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to fetch page: HTTP {response.status_code}"
            }

        year, month, day = extract_date(response.text)
        combined, case_date_iso, today, weeks_waiting_period = calculate_fields(year, month, day)

        return {
            "status": "success",
            "today": today,
            "case_date_iso": case_date_iso,
            "waiting_period": weeks_waiting_period
        }
    except ValueError as e:
        return {
            "status": "error",
            "error_message": f"An exception occurred: {str(e)}"
        }

def extract_date(content):
    tree = html.fromstring(content)
    
    # Use XPath to extract the day, month name, and year
    day_month = tree.xpath('normalize-space(//*[@id="page-alert-block"]/div/div/p/strong[1])')
    year = tree.xpath('normalize-space(//*[@id="page-alert-block"]/div/div/p/strong[2])')
    
    if not day_month or not year:
        raise ValueError("Could not find the expected elements on the page.")

    day, month_name = day_month.split()

    return year.strip(), map_month(month_name.strip()), day.strip()

def map_month(original_month_name):
    month_map = {
        "januari": "01", "februari": "02", "mars": "03", "april": "04",
        "maj": "05", "juni": "06", "juli": "07", "augusti": "08",
        "september": "09", "oktober": "10", "november": "11", "december": "12"
    }
    month = month_map.get(original_month_name.lower())
    
    if not month:
        raise ValueError(f"Unknown month name: {original_month_name}")

    return month
    
def calculate_fields(year, month, day):
    # Format date to ISO8601 format
    stockholm_timezone = ZoneInfo("Europe/Stockholm")
    case_date = datetime(int(year), int(month), int(day), tzinfo=stockholm_timezone)
    case_date_iso = case_date.strftime("%Y-%m-%d")
    
    # Get today's date and time in ISO8601 format
    today = datetime.now(tz=stockholm_timezone)
    # Calculate the difference in days and weeks
    delta_days = (today - case_date).days
    delta_weeks = delta_days / 7
    
    return case_date.strftime('%d %B'), case_date_iso, today.isoformat(), delta_weeks

def append_to_csv(file_path, data):
    # Specify the header
    headers = ["Date", "Evaluating cases", "Waiting period"]
    # Check if the file exists to write the header
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, dialect='unix')
            # Write the header only if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow({
                "Date": data["today"],
                "Evaluating cases": data["case_date_iso"],
                "Waiting period": round(data["waiting_period"], 2)
            })
    except Exception as e:
        print(f"Error writing to CSV: {e}")


url = "https://www.transportstyrelsen.se/sv/vagtrafik/fordon/aga-kopa-eller-salja-fordon/import-och-export-av-fordon/fordonsimport-och-ursprungskontroll/"
result = scrape_website(url)

# Return result
if result["status"] == "success":
    csv_file_path = "transportstyrelsen_data.csv"
    append_to_csv(csv_file_path, result)
    sys.stdout.write("Written to disk")
else:
    sys.stdout.write(f"Error: {result['error_message']}")
