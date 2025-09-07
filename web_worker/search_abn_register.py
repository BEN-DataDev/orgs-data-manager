import os
import time
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from requests import Session
from requests.exceptions import RequestException
import zeep
from zeep.transports import Transport
import xml.etree.ElementTree as ET

load_dotenv()
ABN_GUID: str = os.getenv("PRIVATE_ABN_SEARCH_GUID", "")
if not ABN_GUID:
    raise ValueError("PRIVATE_ABN_SEARCH_GUID environment variable is not set.")

NAMESPACE = {'ns': 'http://abr.business.gov.au/ABRXMLSearch/'}

class ABRClient:
    def __init__(self, guid: str):
        self.guid = guid
        self.session = Session()
        self.transport = CustomTransport(session=self.session)
        self.client = zeep.Client(
            'https://abr.business.gov.au/ABRXMLSearch/AbrXmlSearch.asmx?WSDL',
            transport=self.transport
        )
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._check_maintenance()

    def _check_maintenance(self):
        windows = [
            {'start': '2025-08-02 21:00:00+10:00', 'end': '2025-08-03 14:00:00+10:00'},
            {'start': '2025-08-09 21:00:00+10:00', 'end': '2025-08-10 10:00:00+10:00'}
        ]
        now = datetime.now(timezone(timedelta(hours=10)))
        for w in windows:
            start = datetime.strptime(w['start'], '%Y-%m-%d %H:%M:%S%z')
            end = datetime.strptime(w['end'], '%Y-%m-%d %H:%M:%S%z')
            if start <= now <= end:
                raise RuntimeError(f"ABR Service under maintenance until {end.strftime('%Y-%m-%d %H:%M AEST')}")

    def search_charities(self, postcode, state, max_abns=None) -> List[Dict]:
        search_params = {
            'postcode': postcode,
            'state': '',
            'charityTypeCode': '',
            'concessionTypeCode': '',  # blank for all charity types
            'authenticationGuid': self.guid
        }
        self.logger.info(f"Searching for charities in postcode {postcode}")

        abns = self._call_search_by_charity(search_params, max_abns)
        charities = []

        for abn in abns:
            parsed_details = self._lookup_abn_details(abn)
            if not parsed_details:
                continue

            be = extract_business_entity(parsed_details)

            # Only include those whose main location matches search
            main_addr = be.get("mainBusinessPhysicalAddress")
            postcode_val = None
            state_code = None
            if main_addr:
                postcode_val = main_addr.get("postcode")
                state_code = (main_addr.get("stateCode") or '').upper()
            if state_code == state.upper() and postcode_val == postcode:
                charities.append(format_record(be))
            time.sleep(0.4)
        self.logger.info(f"Returning {len(charities)} charity results")
        return charities

    def _call_search_by_charity(self, params, limit) -> List[str]:
        max_retries = 3
        content = None        
        for attempt in range(max_retries):
            try:
                self.client.service.SearchByCharity(**params)
                if not self.transport.last_response:
                    raise RuntimeError("No response from SearchByCharity")
                content = self.transport.last_response.content
                break
            except RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

        if content is None:
            raise RuntimeError("Failed to get response content after all retries")

        if isinstance(content, bytes):
            result = content.decode('utf-8')
        else:
            result = content
            
        root = ET.fromstring(result)
        abn_list = root.findall('.//ns:abn', namespaces=NAMESPACE)
        abns = [abn.text for abn in abn_list if abn.text]
        if limit is not None:
            abns = abns[:limit]
        return abns

    def _lookup_abn_details(self, abn) -> Optional[Any]:
        """
        Returns all values from the response XML as a nested dict (or text/None).
        """
        max_retries = 3
        params = dict(
            searchString=abn,
            includeHistoricalDetails='N',
            authenticationGuid=self.guid
        )
        res = None

        for attempt in range(max_retries):
            try:
                self.client.service.SearchByABNv201408(**params)
                if not self.transport.last_response:
                    raise RuntimeError(f"No response for ABN {abn}")
                res = self.transport.last_response.content
                break
            except RequestException as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed SearchByABNv201408 for ABN {abn} after {max_retries} attempts: {e}")
                    return None
                time.sleep(2 ** attempt)

        if res is None:
            logging.error(f"No response content received for ABN {abn}")
            return None

        if isinstance(res, bytes):
            res = res.decode('utf-8')

        root = ET.fromstring(res)
        # Extract the entire response
        return etree_to_dict(root)

class CustomTransport(Transport):
    def __init__(self, session=None):
        super().__init__(session=session)
        self.last_response = None
    def post(self, address, message, headers):
        response = super().post(address, message, headers)
        self.last_response = response
        return response

def etree_to_dict(elem) -> Any:
    """
    Recursively convert an xml.etree.ElementTree.Element into a dict or a text value.
    """
    d = {}
    children = list(elem)
    if children:
        child_dict = {}
        for child in children:
            tag = child.tag
            ns_idx = tag.find('}')
            if ns_idx != -1:
                tag = tag[ns_idx + 1:]
            child_value = etree_to_dict(child)
            if tag in child_dict:
                if isinstance(child_dict[tag], list):
                    child_dict[tag].append(child_value)
                else:
                    child_dict[tag] = [child_dict[tag], child_value]
            else:
                child_dict[tag] = child_value
        d.update(child_dict)
    text = (elem.text or '').strip()
    if text and not children:
        return text
    elif text:
        d['value'] = text
    return d

def extract_business_entity(details: dict) -> dict:
    """
    Returns the businessEntity201408 dictionary from parsed ABR XML.
    """
    response = (
        details.get("Body", {})
        .get("SearchByABNv201408Response", {})
        .get("ABRPayloadSearchResults", {})
        .get("response", {})
    )
    return response.get("businessEntity201408", {})

def format_record(be: dict) -> dict:
    """
    Formats a businessEntity201408 dict into the requested flat record structure.
    """
    def get_path(node, *path):
        curr = node
        for key in path:
            if isinstance(curr, list):
                curr = curr[0] if curr else None
            if not isinstance(curr, dict):
                return None
            curr = curr.get(key)
        if isinstance(curr, dict) or isinstance(curr, list):
            return curr
        return curr

    abn = get_path(be, "ABN", "identifierValue")
    is_current = get_path(be, "ABN", "isCurrentIndicator")
    replaced_from = get_path(be, "ABN", "replacedFrom")
    entity_status = get_path(be, "entityStatus", "entityStatusCode")
    effective_from = get_path(be, "entityStatus", "effectiveFrom")
    effective_to = get_path(be, "entityStatus", "effectiveTo")
    entity_type_code = get_path(be, "entityType", "entityTypeCode")
    entity_type_description = get_path(be, "entityType", "entityDescription")
    acnc_status = get_path(be, "ACNCRegistration", "status")
    acnc_status_from = get_path(be, "ACNCRegistration", "effectiveFrom")
    acnc_status_to = get_path(be, "ACNCRegistration", "effectiveTo")
    record_last_updated = be.get("recordLastUpdatedDate")

    gst = json.dumps(be.get("goodsAndServicesTax")) if be.get("goodsAndServicesTax") is not None else None
    dgr = json.dumps(be.get("dgrEndorsement")) if be.get("dgrEndorsement") is not None else None
    main_trading_names = json.dumps(be.get("mainTradingName")) if be.get("mainTradingName") is not None else None
    other_trading_names = json.dumps(be.get("otherTradingName")) if be.get("otherTradingName") is not None else None
    main_business_physical_address = json.dumps(be.get("mainBusinessPhysicalAddress")) if be.get("mainBusinessPhysicalAddress") is not None else None
    tax_concession_endorsements = json.dumps(be.get("taxConcessionCharityEndorsement")) if be.get("taxConcessionCharityEndorsement") is not None else None

    return {
        "abn": abn,
        "isCurrent": is_current,
        "replacedFrom": replaced_from,
        "entityStatus": entity_status,
        "effectiveFrom": effective_from,
        "effectiveTo": effective_to,
        "entityTypeCode": entity_type_code,
        "entityDescription": entity_type_description,
        "acnc_status": acnc_status,
        "acnc_status_from": acnc_status_from,
        "acnc_status_to": acnc_status_to,
        "record_last_updated": record_last_updated,
        "gst": gst,
        "dgr": dgr,
        "main_trading_names": main_trading_names,
        "other_trading_names": other_trading_names,
        "main_business_physical_address": main_business_physical_address,
        "tax_concession_endorsements": tax_concession_endorsements,
    }

def query_abn_register(state, postcode, max_abns=None) -> List[Dict]:
    """
    Top-level function to query ABR register just like scrape_website or query_acnc_charities.
    Returns a list of dict records in the output structure.
    """
    client = ABRClient(ABN_GUID)
    try:
        return client.search_charities(postcode=postcode, state=state, max_abns=max_abns)
    finally:
        if hasattr(client, 'session'):
            client.session.close()

def main():
    client = ABRClient(ABN_GUID)
    try:
        charities = client.search_charities("BATLOW", "2730", "NSW")
        print(f"\nFound {len(charities)} charities:\n")
        for charity in charities:
            for k, v in charity.items():
                print(f"{k}: {v}")
            print("------")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if hasattr(client, 'session'):
            client.session.close()

if __name__ == "__main__":
    main()