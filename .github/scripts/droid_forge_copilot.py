import json
import os
import sys
import requests
from pathlib import Path

GITHUB_API = "https://api.github.com"
MENTION_TOKENS = ["@droidforge", "@ai-assistant"]

def load_event():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        sys.exit(0)
    with open(event_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_text(event):
    if "comment" in event:
        return event["comment"].get("body", "")
    if "issue" in event:
        return event["issue"].get("body", "")
    if "pull_request" in event:
        return event["pull_request"].get("body", "")
    return ""

def is_mentioned(text):
    text_lower = text.lower()
    return any(token in text_lower for token in MENTION_TOKENS)

def load_repo_context():
    context = []
    for name in ["README.md", "README.txt"]:
        p = Path(name)
        if p.exists():
            context.append(p.read_text(encoding="utf-8")[:4000])
    return "\n\n".join(context)

def call_llm(prompt):
    key = os.environ.get("AI_PROVIDER_KEY")
    if not key:
        return "AI_PROVIDER_KEY is not configured."

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are DroidForge Copilot. Expert in Android, Kivy, Python-to-APK, GitHub Actions."},
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    if r.status_code != 200:
        return f"LLM error: {r.status_code}\n{r.text}"

    return r.json()["choices"][0]["message"]["content"]

def post_comment(url, body):
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    requests.post(url, headers=headers, json={"body": body})

def main():
    event = load_event()
    text = extract_text(event)

    if not is_mentioned(text):
        sys.exit(0)

    context = load_repo_context()
    prompt = f"{context}\n\nUser request:\n{text}"

    reply = call_llm(prompt)

    if "comment" in event:
        url = event["comment"]["issue_url"] + "/comments"
    elif "issue" in event:
        url = event["issue"]["comments_url"]
    elif "pull_request" in event:
        url = event["pull_request"]["comments_url"]
    else:
        sys.exit(0)

    post_comment(url, reply)

if __name__ == "__main__":
    main()
