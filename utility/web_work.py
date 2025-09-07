def parse_suburb_filter(entry: str) -> dict:
    parts = entry.rsplit(" ", 2)
    suburb = parts[0]
    state = parts[1]
    postcode = parts[2]
    return {"suburb": suburb, "state": state, "postcode": postcode}