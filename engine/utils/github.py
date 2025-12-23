import os
import requests

def post_comment(url, body):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    requests.post(url, headers=headers, json={"body": body})
