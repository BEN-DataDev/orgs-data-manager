import requests
from bs4 import BeautifulSoup, Tag
import time
import re

class NSWAssociationScraper:
    BASE_URL = "https://applications.fairtrading.nsw.gov.au/assocregister/RegistrationSearch.aspx"
    DETAILS_URL = "https://applications.fairtrading.nsw.gov.au/assocregister/PublicRegisterDetails.aspx?Organisationid={orgid}"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _get_form_fields(self, soup):
        form = soup.find('form', {'id': 'aspnetForm'})
        if form is None:
            raise Exception("Form not found!")
        fields = {}
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            if name:
                fields[name] = value
        for select_tag in form.find_all('select'):
            name = select_tag.get('name')
            if name:
                options = select_tag.find_all('option')
                selected = next((opt for opt in options if opt.has_attr('selected')), options[0] if options else None)
                fields[name] = selected.get('value', '') if selected else ''
        return fields

    def _parse_results(self, soup):
        """Parse search results from the page"""
        results = []
        results_list = soup.find('span', id='ctl00_MainArea_ResultDataList')
        if not results_list:
            print("No results list found - might be on initial search page")
            return results

        for row_div in results_list.find_all('div', class_='row', recursive=True):
            main_col = row_div.find('div', class_='col-md-10')
            status_col = row_div.find('div', class_='col-md-2')
            if not main_col or not status_col:
                continue

            # Name + org ID
            name_a = main_col.find('a')
            name = name_a.get_text(strip=True) if name_a else None
            orgid = None
            if name_a and 'href' in name_a.attrs:
                match = re.search(r'Organisationid=(\d+)', name_a['href'])
                if match:
                    orgid = match.group(1)

            # Extract details
            org_number, org_type, date_registered, date_removed, reg_address = None, None, None, None, None
            text_secondary_div = main_col.find('div', class_='row text-secondary')
            if text_secondary_div:
                for div in text_secondary_div.find_all('div'):
                    div_text = div.get_text(strip=True)
                    if 'Organisation Number:' in div_text:
                        org_number = div_text.split('Organisation Number:')[-1].strip()
                    elif 'Date Registered:' in div_text:
                        date_registered = div_text.split('Date Registered:')[-1].strip()
                    elif 'Organisation Type:' in div_text:
                        org_type = div_text.split('Organisation Type:')[-1].strip()
                    elif 'Date Removed:' in div_text:
                        date_removed = div_text.split('Date Removed:')[-1].strip()
                    elif 'Registered Office Address:' in div_text:
                        reg_address = div_text.split('Registered Office Address:')[-1].strip()

            # Status
            status = None
            figcaption = status_col.find('figcaption')
            if figcaption:
                status_span = figcaption.find('span')
                if status_span:
                    status = status_span.get_text(strip=True)

            if name:
                results.append({
                    "name": name,
                    "organisation_number": org_number,
                    "organisation_type": org_type,
                    "status": status,
                    "date_registered": date_registered,
                    "date_removed": date_removed,
                    "registered_office_address": reg_address,
                    "organisation_id": orgid
                })

        return results

    def _get_next_event_target(self, soup):
        """Find the next page link event target"""
        candidates = [
            'ctl00_MainArea_PageNextLink',
            'ctl00_MainArea_PageNextBottomLink'
        ]
        for cid in candidates:
            next_link = soup.find('a', id=cid)
            if not next_link:
                continue
            href = next_link.get('href')
            if not href or 'display:none' in next_link.get('style', '') or next_link.has_attr('disabled'):
                continue
            if 'javascript:__doPostBack' in href:
                match = re.search(r"__doPostBack\('([^']+)'", href)
                if match:
                    return match.group(1)
        return None

    def search_all(self, organisation_name=None, organisation_number=None, organisation_type=None,
                   suburb=None, postcode=None, status=None, delay=0.5):
        """Perform search and return all results across all pages"""
        all_results = []
        page_num = 0
        try:
            print("Getting initial search page...")
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            fields = self._get_form_fields(soup)

            # Search params
            if organisation_name:
                fields['ctl00$MainArea$AdvancedSearchSection$Organisationname'] = organisation_name
            if organisation_number:
                fields['ctl00$MainArea$AdvancedSearchSection$Organisationnumber'] = organisation_number
            if organisation_type:
                fields['ctl00$MainArea$AdvancedSearchSection$Organisationtype'] = organisation_type
            if suburb:
                fields['ctl00$MainArea$AdvancedSearchSection$Suburb'] = suburb
            if postcode:
                fields['ctl00$MainArea$AdvancedSearchSection$Postcode'] = postcode
            if status:
                fields['ctl00$MainArea$AdvancedSearchSection$Organisationstatus'] = status

            fields['__EVENTTARGET'] = 'ctl00$MainArea$AdvancedSearchSection$AdvancedSearchButton'
            fields['__EVENTARGUMENT'] = ''

            print(f"Performing search with suburb='{suburb}', postcode='{postcode}'...")
            search_response = self.session.post(self.BASE_URL, data=fields)
            search_response.raise_for_status()
            search_soup = BeautifulSoup(search_response.text, 'html.parser')

            while True:
                page_num += 1
                new_results = self._parse_results(search_soup)
                if not new_results:
                    print(f"Page {page_num}: no results found. Stopping.")
                    break

                all_results.extend(new_results)
                print(f"Fetched page {page_num}: {len(new_results)} results, {len(all_results)} total so far.")

                next_target = self._get_next_event_target(search_soup)
                if not next_target:
                    print(f"No more pages after page {page_num}. Done.")
                    break

                fields = self._get_form_fields(search_soup)
                fields['__EVENTTARGET'] = next_target
                fields['__EVENTARGUMENT'] = ''

                time.sleep(delay)
                next_response = self.session.post(self.BASE_URL, data=fields)
                next_response.raise_for_status()
                search_soup = BeautifulSoup(next_response.text, 'html.parser')

            print(f"Completed search across {page_num} page(s). Found {len(all_results)} total results.")
            return all_results

        except Exception as e:
            print(f"Error during search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_org_details(self, orgid):
        url = self.DETAILS_URL.format(orgid=orgid)
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch details for {orgid}: {response.status_code}")
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            details = {}
            main_card = soup.find("div", class_="card-body")
            if not main_card or not isinstance(main_card, Tag):
                print("Couldn't find main details area or main_card is not a Tag.")
                return None
            for row in main_card.find_all("div", class_="row"):
                if not isinstance(row, Tag):
                    continue
                labels = row.find_all("span", class_="font-weight-bold")
                for label in labels:
                    key = label.get_text(strip=True).replace(":", "").strip()
                    value_element = label.next_sibling
                    value = None
                    if isinstance(value_element, Tag):
                        value = value_element.get_text(strip=True)
                    elif value_element:
                        value = str(value_element).strip()
                    else:
                        next_string = label.find_next(string=True)
                        if next_string:
                            value = str(next_string).strip()
                    if value and value != key:
                        details[key] = value
            return details
        except Exception as e:
            print(f"Error fetching details for {orgid}: {e}")
            return None

if __name__ == "__main__":
    scraper = NSWAssociationScraper()
    
    # Test with BATLOW
    print("Searching for organizations in BATLOW, postcode 2730...")
    results = scraper.search_all(suburb="BATLOW", postcode="2730")
    
    print(f"\nFound {len(results)} total results:")
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['name']}")
        print(f"   Number: {r['organisation_number']}")
        print(f"   Type: {r['organisation_type']}")
        print(f"   Status: {r['status']}")
        print(f"   Date Registered: {r['date_registered']}")
        print(f"   Date Removed: {r['date_removed']}")
        print(f"   Registered Office Address: {r['registered_office_address']}")
        print(f"   Organisation ID: {r['organisation_id']}")
        
        # Optionally fetch details for first result
        if i == 1 and r['organisation_id']:
            print(f"\n   Fetching details for {r['name']}...")
            details = scraper.fetch_org_details(r['organisation_id'])
            if details:
                print("   Details:")
                for k, v in details.items():
                    print(f"     {k}: {v}")