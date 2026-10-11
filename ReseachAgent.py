import requests


def search_papers(topic, limit=5, open_access_only=False):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,authors,year,citationCount,url,openAccessPdf",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching from API: {e}")
        return None
    return []


def clean_papers(papers_data, open_access_only=False):
    
    if not papers_data:
        return []

    cleaned = []
    for item in papers_data:
        pdf_info = item.get("openAccessPdf")
        pdf_url = pdf_info.get("url") if pdf_info else None

        if open_access_only and not pdf_url:
            continue

        authors_list = item.get("authors", [])
        authors_str = (
            ", ".join([a.get("name", "") for a in authors_list])
            if authors_list
            else "Unknown Authors"
        )

        citation_count = item.get("citationCount")
        citation_count = int(citation_count) if citation_count is not None else 0

        year_val = item.get("year")
        year_val = year_val if year_val is not None else "N/A"

        cleaned.append(
            {
                "title": item.get("title") or "No Title Available",
                "authors": authors_str,
                "year": year_val,
                "citationCount": citation_count,
                "url": item.get("url") or "#",
                "openAccessPdf": pdf_url,
            }
        )
    return cleaned



def find_most_cited(papers):
    if not papers:
        return None
    return max(papers, key=lambda p: p.get("citationCount", 0))


def find_least_cited(papers):
    if not papers:
        return None
    return min(papers, key=lambda p: p.get("citationCount", 0))


def find_newest(papers):
    if not papers:
        return None
    valid = [p for p in papers if isinstance(p.get("year"), int)]
    return max(valid, key=lambda p: p.get("year")) if valid else papers[0]


def find_oldest(papers):
    if not papers:
        return None
    valid = [p for p in papers if isinstance(p.get("year"), int)]
    return min(valid, key=lambda p: p.get("year")) if valid else papers[0]


def count_papers(papers):
    return len(papers)


def average_citations(papers):
    if not papers:
        return 0
    return round(
        sum(p.get("citationCount", 0) for p in papers) / len(papers), 1
    )




def llm_choose_tool(question):
    if not question:
        return "MOST_CITED"
    q = question.lower()
    if any(w in q for w in ["oldest", "old", "earliest", "first"]):
        return "OLDEST"
    elif any(w in q for w in ["newest", "latest", "recent", "new"]):
        return "NEWEST"
    elif any(w in q for w in ["least", "lowest", "fewest", "minimum"]):
        return "LEAST_CITED"
    elif any(
        w in q
        for w in ["most", "highest", "top", "influential", "popular", "maximum"]
    ):
        return "MOST_CITED"
    return "MOST_CITED"


def run_tool(tool_name, papers):
    if not papers:
        return None
    if tool_name in ["find_most_cited", "MOST_CITED"]:
        return find_most_cited(papers)
    elif tool_name in ["find_least_cited", "LEAST_CITED"]:
        return find_least_cited(papers)
    elif tool_name in ["find_newest", "NEWEST"]:
        return find_newest(papers)
    elif tool_name in ["find_oldest", "OLDEST"]:
        return find_oldest(papers)
    elif tool_name == "count_papers":
        return count_papers(papers)
    elif tool_name == "average_citations":
        return average_citations(papers)
    else:
        return find_most_cited(papers)