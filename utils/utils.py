def extract_body_type(transport_summary):
    for line in transport_summary.split('\n'):
        if "Тип кузова:" in line:
            return line.split("Тип кузова:")[1].strip()
    return ""

def extract_city(address):
    parts = address.split(',')
    if len(parts) >= 2:
        return parts[-2].strip()
    return parts[-1].strip()