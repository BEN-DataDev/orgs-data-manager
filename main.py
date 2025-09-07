import csv, json,logging, os
from datetime import datetime
from sqlalchemy import create_engine

from config_data.suburb_definitons import SuburbDefinitions
from web_worker.search_nsw_assoc_register import NSWAssociationScraper
from web_worker.search_anc_register import query_acnc_charities
from web_worker.search_abn_register import query_abn_register

pg13_conn_string = "postgresql://postgres:postgres@172.26.64.1:5433/community_mapping"
pg13_engine = create_engine(pg13_conn_string)

pg17_conn_string = "postgresql://postgres:postgres@172.26.64.1:5432/postgres"
pg17_engine = create_engine(pg17_conn_string)

# Timestamp and output path
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
output_dir = r"C:/python-projects/orgs-data-manager/data/raw"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

error_logger = logging.getLogger("suburb_errors")
error_log_path = os.path.join(output_dir, f"suburb_errors_{timestamp}.log")
error_handler = logging.FileHandler(error_log_path, mode="w", encoding="utf-8")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.WARNING)

def write_csv(filename, fieldnames, data):
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Results written to {filename}")
    except Exception as e:
        logging.error(f"Error writing {filename}: {e}")

def write_json(filename, data):
    try:
        with open(filename, mode="w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        logging.info(f"Missing data summary written to {filename}")
    except Exception as e:
        logging.error(f"Error writing JSON summary: {e}")

def main():
    all_scrape_results = []
    all_ckan_results = []
    all_abn_results = []
    missing_summary = []
    scraper = NSWAssociationScraper()

    # Gather unique postcodes and a mapping to state for ABN search
    postcode_state_map = {}
    
    for definition in SuburbDefinitions:
        suburb_info = {
            "suburb": definition.suburb,
            "state": definition.state,
            "postcode": definition.postcode
        }

        # Always keep the first observed state for a postcode (or update logic if needed)
        if definition.postcode not in postcode_state_map:
            postcode_state_map[definition.postcode] = definition.state

        logging.info(f"Scraping website for {suburb_info}")
        scrape_results = scraper.search_all(
            suburb=definition.suburb,
            postcode=definition.postcode,
            delay=4
        )
        if scrape_results:
            all_scrape_results.extend(scrape_results)
        else:
            error_logger.warning(f"No Fair Trading Incorporations results found for {suburb_info}")
            missing_summary.append({**suburb_info, "source": "fair trading incorporations register"})

        logging.info(f"Querying ACNC Charity Register for {suburb_info}")
        ckan_results = query_acnc_charities(
            town_city=definition.suburb,
            state=definition.state,
            postcode=definition.postcode
        )
        if ckan_results:
            all_ckan_results.extend(ckan_results)
        else:
            error_logger.warning(f"No ACNC charity results found for {suburb_info}")
            missing_summary.append({**suburb_info, "source": "acnc register"})

    # Now, call ABN register search once per unique postcode
    for postcode, state in postcode_state_map.items():
        suburb_info = {
            "suburb": "",  # Suburb not used for ABN, but left blank for summary consistency
            "state": state,
            "postcode": postcode
        }
        logging.info(f"Querying ABN Register for {suburb_info}")
        abn_results = query_abn_register(
            state=state,
            postcode=postcode
        )
        if abn_results:
            all_abn_results.extend(abn_results)
        else:
            error_logger.warning(f"No ABN register results found for {suburb_info}")
            missing_summary.append({**suburb_info, "source": "abn register"})

    logging.info(f"Total Fair Trading Incorporations results accumulated: {len(all_scrape_results)}")
    logging.info(f"Total ACNC results accumulated: {len(all_ckan_results)}")
    logging.info(f"Total ABN register results accumulated: {len(all_abn_results)}")

    if all_scrape_results:
        scrape_fieldnames = list(all_scrape_results[0].keys())
        scrape_filename = os.path.join(output_dir, f"fair_trading_incorporation_register_results_{timestamp}.csv")
        write_csv(scrape_filename, scrape_fieldnames, all_scrape_results)

    if all_ckan_results:
        ckan_fieldnames = list(all_ckan_results[0].keys())
        ckan_filename = os.path.join(output_dir, f"acnc_register_results_{timestamp}.csv")
        write_csv(ckan_filename, ckan_fieldnames, all_ckan_results)

    if all_abn_results:
        abn_fieldnames = list(all_abn_results[0].keys())
        abn_filename = os.path.join(output_dir, f"abn_register_results_{timestamp}.csv")
        write_csv(abn_filename, abn_fieldnames, all_abn_results)

    if missing_summary:
        summary_filename = os.path.join(output_dir, f"missing_results_summary_{timestamp}.json")
        write_json(summary_filename, missing_summary)

if __name__ == "__main__":
    main()