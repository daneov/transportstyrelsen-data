# Scraping [Transportstyrelsen](https://www.transportstyrelsen.se/sv/vagtrafik/fordon/aga-kopa-eller-salja-fordon/import-och-export-av-fordon/fordonsimport-och-ursprungskontroll/)

## Transportstyrelsen

[Transportstyrelsen](https://www.transportstyrelsen.se/en) is the Swedish body responsible
for car registration, taxes and all of those things.  
When you send in your request, a case number gets assigned based on the received date.

As the estimated range within your case will be handled is quite broad, and no data 
accessible, I created a simple script that parses the date that Transportstyrelsen is
currently handling.

## What can this teach us?

Without knowing the number of cases that were handled, all this data does is give insight
into which dates took the longest to process. This could point to any of the possible
causes for something to go slow: a large number of cases, complex cases, understaffing, ...

Maybe over time this data gives us some generalizable results, who knows.

## How

This script has a `cron` schedule that triggers the scraping during what can be considered
working hours.

When triggered it:

1. Fetches the website
2. Parses the HTML for elements known to contain the date

    - This is the fragile part

3. Uses the case date to calculate the processing time
4. Enriches `transportstyrelsen_data.csv`
5. Pushes the updated csv
