import requests
from flask import Flask, render_template, request
import ReseachAgent

app = Flask(__name__)

def get_visitor_info():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=2)
        if res.status_code == 200:
            data = res.json()
            return {
                "ip": data.get("ip", "127.0.0.1"),
                "city": data.get("city", "Amman"),
                "country": data.get("country_name", "Jordan"),
                "timezone": data.get("timezone", "Asia/Amman"),
                "currency": data.get("currency", "JOD"),
                "organization": data.get("org", "Local Network")
            }
    except Exception:
        pass
    return {
        "ip": "127.0.0.1",
        "city": "Amman",
        "country": "Jordan",
        "timezone": "Asia/Amman",
        "currency": "JOD",
        "organization": "Local Network"
    }

@app.route("/", methods=["GET", "POST"])
def home():
    visitor_info = get_visitor_info()
    topic = ""
    question = ""
    selected_tool = None
    tool_result = None
    papers = []
    error_message = None

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        question = request.form.get("question", "").strip()
        sort_by = request.form.get("sort_by", "most_cited")
        limit = int(request.form.get("limit", 5))
        open_access = True if request.form.get("open_access") else False

        if not topic:
            error_message = "Please enter a research topic."
        elif not question:
            error_message = "Please enter a question."
        else:
            raw_papers = ReseachAgent.search_papers(topic, limit=limit, open_access_only=open_access)
            clean_results = ReseachAgent.clean_papers(raw_papers, open_access_only=open_access)

            if not clean_results:
                error_message = "No papers were found. Try another research topic."
            else:
                if sort_by == "most_cited":
                    clean_results.sort(key=lambda p: p.get("citationCount", 0), reverse=True)
                elif sort_by == "least_cited":
                    clean_results.sort(key=lambda p: p.get("citationCount", 0))
                elif sort_by == "newest":
                    clean_results.sort(key=lambda p: p.get("year") if isinstance(p.get("year"), int) else 0, reverse=True)
                elif sort_by == "oldest":
                    clean_results.sort(key=lambda p: p.get("year") if isinstance(p.get("year"), int) else 9999)

                papers = clean_results
                selected_tool = ReseachAgent.llm_choose_tool(question)
                tool_result = ReseachAgent.run_tool(selected_tool, papers)

    return render_template(
        "index.html",
        topic=topic,
        question=question,
        selected_tool=selected_tool,
        tool_result=tool_result,
        papers=papers,
        visitor_info=visitor_info,
        error_message=error_message
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")

if __name__ == "__main__":
    app.run(debug=True)