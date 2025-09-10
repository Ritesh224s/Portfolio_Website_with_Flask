from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os, json, time, sqlite3, re
import requests
from urllib.parse import quote_plus
import config

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

os.makedirs("data", exist_ok=True)

def _now(): return int(time.time())

def read_cache():
    if not os.path.exists(config.CACHE_FILE):
        return {}
    try:
        with open(config.CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_cache(payload):
    with open(config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def fetch_repos():
    """Fetch repos from GitHub with 1-hour cache and offline fallback."""
    cache = read_cache()
    if cache.get("fetched_at") and _now() - cache["fetched_at"] < config.CACHE_TTL_SECONDS:
        return cache.get("repos", [])

    url = f"https://github.com/Ritesh224s"
    try:
        r = requests.get(url, timeout=10, headers={"Accept":"application/vnd.github+json"})
        r.raise_for_status()
        raw = r.json()
        repos = []
        for repo in raw:
            if repo.get("fork"):  # skip forks
                continue
            repos.append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "description": repo.get("description") or "",
                "language": repo.get("language") or "Other",
                "stars": repo.get("stargazers_count", 0),
                "updated": repo.get("updated_at", ""),
                "topics": repo.get("topics", []),
            })
        # pin first
        def pin_rank(r):
            try:
                return config.PINNED.index(r["name"])
            except ValueError:
                return 999
        repos.sort(key=lambda r: (pin_rank(r), -r["stars"], r["name"].lower()))

        write_cache({"fetched_at": _now(), "repos": repos})
        return repos
    except Exception:
        # offline fallback from cache
        return cache.get("repos", [])

def ensure_db():
    con = sqlite3.connect(config.DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    con.commit()
    con.close()

ensure_db()

def is_valid_email(s):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s or ""))

@app.route("/")
def home():
    repos = fetch_repos()[:8]  # show highlights
    return render_template("index.html", repos=repos, gh_user=config.GITHUB_USERNAME)

@app.route("/projects")
def projects():
    q = (request.args.get("q") or "").strip().lower()
    lang = (request.args.get("lang") or "").strip()
    repos = fetch_repos()

    if q:
        repos = [r for r in repos if q in (r["name"] + " " + (r["description"] or "")).lower()]
    if lang:
        repos = [r for r in repos if (r["language"] or "").lower() == lang.lower()]

    languages = sorted({(r["language"] or "Other") for r in fetch_repos()})
    return render_template("projects.html", repos=repos, languages=languages, q=q, lang=lang)

@app.route("/api/projects")
def api_projects():
    return jsonify(fetch_repos())

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject", "")
        message = request.form.get("message")

        if not name or not is_valid_email(email) or not message:
            flash("Please provide a valid name, email, and message.", "error")
            return redirect(url_for("contact"))

        con = sqlite3.connect(config.DB_FILE)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO messages(name,email,subject,message,created_at) VALUES(?,?,?,?,?)",
            (name, email, subject, message, _now()),
        )
        con.commit()
        con.close()
        flash("Thanks! Your message has been received.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)