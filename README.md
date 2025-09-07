
# Python Modules Documentation

## main.py

This module automates suburban organization data collection from multiple public registers, including reporting and error logging, using defined suburb definitions and database connections.

### Overview

This **Python module** orchestrates the extraction and storage of organizational information for Australian suburbs from three major public sources: NSW Fair Trading Incorporations Register, ACNC Charity Register, and ABN Register.

### Features

- **Multi-source scraping:** Fetches results for each suburb from NSW, ACNC, and ABN registries.
- **Configurable suburb definitions:** Operates over a configurable list of suburb, state, and postcode definitions.
- **Error and event logging:** Uses Python's logging library for tracking and error reporting, including detailed error logs for missing data.[^1]
- **Deduplicated ABN lookups:** Searches the ABN register once per unique postcode for efficiency.
- **Flexible output:** Saves results as CSV files for each data source and logs any data gaps in JSON format for further inspection.

### How It Works

1. **Initialization:**
Loads suburb definitions, configures logging, and sets up database engines (PostgreSQL).
2. **Main Processing Loop:**
For each suburb definition:
    - Queries NSW Fair Trading Incorporations Register and ACNC Charity Register.
    - Aggregates missing results if any queries return no data.
    - Collects unique postcodes for ABN register lookup.
3. **ABN Register Query:**
For each unique postcode, queries the ABN register and tracks issues or missing entries.
4. **Export \& Logging:**
    - Exports results to timestamped CSV files.
    - Records missing data and errors to JSON and log files under a chosen output directory.

### Output Files

- **CSV:**
- `fair_trading_incorporation_register_results_<timestamp>.csv`
- `acnc_register_results_<timestamp>.csv`
- `abn_register_results_<timestamp>.csv`
- **JSON:**
- `missing_results_summary_<timestamp>.json` logs suburbs/postcodes with missing data.
- **Log:**
- `suburb_errors_<timestamp>.log` contains detailed error messages.

### Usage

Run the script as a standalone program:

```bash
python main.py
```

All configuration (e.g., suburb definitions, database connections) is handled in the supporting modules and environment settings.

### Requirements

- Python 3.x
- PostgreSQL server (with required databases)
- Supporting modules:
- `config_data.suburb_definitons`
- `web_worker.search_anc_register`
- `web_worker.search_abn_register`

### Notes

- Ensure the output directory specified exists and is writable.
- The script assumes correct setup of database connection strings and supporting module paths.
- Error logging will highlight any missing or problematic queries for manual follow-up.

***

**In summary:** The module is a data aggregation and export tool for suburban organizations, suitable for research, analysis, or registry monitoring.

## 1. search_abn_register.py

### Overview

A comprehensive Python module for searching and retrieving charity information from the Australian Business Register (ABR) using the official ABR XML Search API. This module provides structured access to business entity data including ABNs, entity status, charity endorsements, and address information.

### Key Features

- **ABR API Integration**: Direct integration with the official ABR XML Search web service
- **SOAP Client**: Uses Zeep library for robust SOAP web service communication
- **Charity-Specific Search**: Specialized functions for searching registered charities
- **Data Transformation**: Converts complex XML responses into structured Python dictionaries
- **Location Filtering**: Filters results by postcode and state to ensure accurate geographic matching
- **Error Handling**: Comprehensive retry logic and error handling for network requests
- **Rate Limiting**: Built-in delays to respect API usage guidelines
- **Maintenance Window Detection**: Automatic detection and handling of ABR service maintenance periods

### Main Components

#### ABRClient Class

- **Purpose**: Core client for interacting with ABR web services
- **Authentication**: Requires valid ABR GUID for API access
- **Transport**: Custom transport layer to capture raw XML responses
- **Methods**:
  - `search_charities()`: Search for charities by location
  - `_call_search_by_charity()`: Internal method for charity search API calls
  - `_lookup_abn_details()`: Retrieve detailed information for specific ABNs
  - `_check_maintenance()`: Verify service availability

#### Data Processing Functions

- **`etree_to_dict()`**: Converts XML ElementTree to nested Python dictionaries
- **`extract_business_entity()`**: Extracts business entity data from API responses
- **`format_record()`**: Transforms raw data into standardized output format

#### Output Format

Returns structured records containing:

- ABN and currency status
- Entity type and description
- ACNC registration status
- GST and DGR endorsement details
- Trading names (main and other)
- Physical address information
- Tax concession endorsements

### Usage Example

```python
from search_abn_register import query_abn_register

# Search for charities in specific location
charities = query_abn_register(state="NSW", postcode="2730", max_abns=50)
```

### Dependencies

- `zeep`: SOAP web service client
- `requests`: HTTP library
- `xml.etree.ElementTree`: XML parsing
- `python-dotenv`: Environment variable management

***

## 2. search_anc_register.py

### Overview

A Python module for querying the Australian Charities and Not-for-profits Commission (ACNC) Charity Register through the Australian Government's Open Data API. This module provides programmatic access to comprehensive charity registration data.

### Key Features

- **CKAN API Integration**: Uses the CKAN (Comprehensive Knowledge Archive Network) API
- **Flexible Search Parameters**: Supports filtering by town/city, state, and postcode
- **State Code Mapping**: Automatically handles both abbreviations (NSW) and full names (New South Wales)
- **Pagination Handling**: Automatically retrieves all results across multiple pages
- **Duplicate Prevention**: Ensures unique results by tracking ABN numbers
- **Multiple Filter Combinations**: Tests various combinations of location parameters for comprehensive results

### Main Functions

#### query_acnc_charities()

- **Purpose**: Primary function for searching ACNC charity register
- **Parameters**:
  - `town_city`: Municipality or city name (optional)
  - `state`: State code (NSW, VIC, etc.) or full name (optional)
  - `postcode`: Postal code (optional)
- **Returns**: List of charity records matching search criteria

### Search Strategy

The module employs a comprehensive search approach:

1. **Parameter Normalization**: Converts inputs to multiple formats (uppercase, title case)
2. **State Mapping**: Maps state codes to full names and vice versa
3. **Combination Testing**: Tests all combinations of normalized parameters
4. **Pagination**: Automatically handles large result sets with configurable page sizes
5. **Deduplication**: Prevents duplicate entries using ABN tracking

### Data Source

- **API Endpoint**: Australian Government Open Data Portal
- **Dataset**: ACNC Charity Register Data
- **Resource ID**: `eb1e6be4-5b13-4feb-b28e-388bf7c26f93`
- **Format**: JSON via CKAN datastore API

### Usage Example

```python
from search_anc_register import query_acnc_charities

# Search for charities in Sydney, NSW
charities = query_acnc_charities(town_city="SYDNEY", state="NSW", postcode="2000")
```

### Dependencies

- `ckanapi`: Python client for CKAN API
- `requests`: HTTP library for API communication
- `itertools`: For generating parameter combinations

***

## 3. search_nsw_assoc_register.py

### Overview

A web scraping module for extracting data from the NSW Fair Trading Association Register. This module provides automated access to incorporated association information in New South Wales through intelligent web scraping techniques.

### Key Features

- **Web Scraping**: Automated extraction from NSW Fair Trading website
- **Form Handling**: Manages complex ASP.NET forms with ViewState
- **Pagination Support**: Automatically navigates through multiple result pages
- **Detailed Information Retrieval**: Can fetch comprehensive details for individual organizations
- **Flexible Search Parameters**: Supports multiple search criteria combinations
- **Session Management**: Maintains persistent sessions for reliable scraping

### Main Components

#### NSWAssociationScraper Class

Comprehensive scraper with the following capabilities:

##### Core Methods

- **`search_all()`**: Main search function with multiple filter options
- **`fetch_org_details()`**: Retrieves detailed information for specific organizations
- **`_get_form_fields()`**: Extracts ASP.NET form fields and ViewState
- **`_parse_results()`**: Parses HTML search results into structured data
- **`_get_next_event_target()`**: Handles pagination navigation

##### Search Parameters

- `organisation_name`: Full or partial organization name
- `organisation_number`: Specific registration number
- `organisation_type`: Type of association/organization
- `suburb`: Location suburb
- `postcode`: Postal code
- `status`: Registration status (active, cancelled, etc.)

### Data Extraction

The module extracts comprehensive information including:

- **Basic Information**: Name, number, type, status
- **Registration Details**: Date registered, date removed
- **Location Data**: Registered office address
- **System Identifiers**: Internal organization IDs for detailed lookups

### Advanced Features

- **ASP.NET Compatibility**: Handles complex server-side form processing
- **Rate Limiting**: Configurable delays between requests to avoid overloading servers
- **Error Recovery**: Robust error handling for network issues and parsing problems
- **Progressive Results**: Displays progress information during multi-page scraping

### Usage Example

```python
from search_nsw_assoc_register import NSWAssociationScraper

scraper = NSWAssociationScraper()

# Search by location
results = scraper.search_all(suburb="BATLOW", postcode="2730")

# Get detailed information
if results and results[0]['organisation_id']:
    details = scraper.fetch_org_details(results[0]['organisation_id'])
```

### Technical Implementation

- **Session Persistence**: Maintains cookies and session state
- **HTML Parsing**: BeautifulSoup for robust HTML parsing
- **Regular Expressions**: Pattern matching for extracting JavaScript parameters
- **Form State Management**: Handles ASP.NET ViewState and EventTarget parameters

### Dependencies

- `requests`: HTTP session management and form submission
- `beautifulsoup4`: HTML parsing and navigation
- `time`: Rate limiting and delay management

###

## Module Integration Notes

These three modules are designed to work together as part of a comprehensive Australian organization search system:

1. **ABR Module**: Provides official business registration data with detailed entity information
2. **ACNC Module**: Focuses specifically on charity and not-for-profit organizations
3. **NSW Association Module**: Covers incorporated associations specific to New South Wales

Each module follows similar patterns for error handling, data formatting, and API interaction, making them suitable for integration into larger systems for comprehensive organizational research and compliance checking.
