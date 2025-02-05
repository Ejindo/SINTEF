import requests
import os

def find_melanoma_paper():
    """
    Query EuropePMC for a single open-access melanoma research paper.
    Returns the PMID if found, otherwise returns None.
    """
    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        'query': 'melanoma AND OPEN_ACCESS:Y',
        'format': 'json',
        'pageSize': 1
    }
    
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    results = data.get('resultList', {}).get('result', [])
    if not results:
        print("No melanoma papers found.")
        return None
    
    paper = results[0]
    pmid = paper.get('pmid')
    if not pmid:
        print("No PMID found for the paper.")
        return None
    
    print(f"Found melanoma paper with PMID: {pmid}")
    return pmid

def save_xml(pmid, folder="data", encoding="ascii", source="pmcoa"):
    """
    Fetch the full-text XML for a given PMID using the BioC API
    and save it to a local folder.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"{pmid}_{encoding}_{source}.xml"
    file_path = os.path.join(folder, filename)
    
    if os.path.exists(file_path):
        print(f"XML file already exists: {file_path}")
        return 1
    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/{source}.cgi/BioC_xml/{pmid}/{encoding}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        text = response.text
        if len(text) < 50:
            print(f"Fetched XML is too short for PMID {pmid}: {text}")
            return 0
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved XML for PMID {pmid} to {file_path}")
        return 1
    except Exception as e:
        print(f"Error fetching XML for PMID {pmid}: {e}")
        return 0

def main():
    pmid = find_melanoma_paper()
    if pmid:
        save_xml(pmid)

if __name__ == "__main__":
    main()