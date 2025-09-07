import requests
import json
import itertools
from ckanapi import RemoteCKAN

def query_acnc_charities(town_city=None, state=None, postcode=None):
    """
    Queries the ACNC Charity Register Data API based on provided filters.
    [function docstring remains the same]
    """
    rc = RemoteCKAN('https://data.gov.au/data/', apikey='')
    RESOURCE_ID = "eb1e6be4-5b13-4feb-b28e-388bf7c26f93"

    all_found_records = []
    seen_abns = set()
    PAGE_SIZE = 1000

    # --- Prepare filter value options ---
    possible_town_cities = [None]
    if town_city:
        possible_town_cities = list(set([
            town_city.upper(),
            town_city.title()
        ]))

    possible_states = [None]
    if state:
        state_mapping = {
            "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
            "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
            "NT": "Northern Territory", "ACT": "Australian Capital Territory"
        }
        possible_states = list(set([
            state.upper(),
            state_mapping.get(state.upper(), None)
        ]))
        possible_states = [s for s in possible_states if s is not None]

    possible_postcodes = [None]
    if postcode:
        possible_postcodes = [postcode.upper()]

    filter_combinations = itertools.product(
        possible_town_cities, possible_states, possible_postcodes
    )

    for tc_val, s_val, pc_val in filter_combinations:
        current_filters = {}
        if tc_val is not None:
            current_filters["Town_City"] = tc_val
        if s_val is not None:
            current_filters["State"] = s_val
        if pc_val is not None:
            current_filters["Postcode"] = pc_val
        if not current_filters:
            continue

        offset = 0
        while True:
            params = {
                "resource_id": RESOURCE_ID,
                "limit": PAGE_SIZE,
                "offset": offset,
                "filters": current_filters
            }
            try:
                data = rc.action.datastore_search(**params)
                if data.get("records"):
                    records = data["records"]
                    for record in records:
                        abn = record.get('ABN')
                        if abn and abn not in seen_abns:
                            all_found_records.append(record)
                            seen_abns.add(abn)
                    if len(records) < PAGE_SIZE:
                        break
                    else:
                        offset += PAGE_SIZE
                else:
                    break
            except Exception as e:
                print(f"API error for filters {current_filters}, offset {offset}: {e}")
                break

    return all_found_records

# (Optional) CLI/test mode
if __name__ == "__main__":
    sample = query_acnc_charities(town_city="SYDNEY", state="NSW", postcode="2000")
    print(f"Found {len(sample)} records.")
    for i, rec in enumerate(sample[:3]):  # Print only first 3, for brevity
        print(f"\nRecord {i+1}:")
        print(rec)
