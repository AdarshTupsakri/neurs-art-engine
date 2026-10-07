#!/usr/bin/env python3
"""
Automated GitHub Repository Creation and Git Push Script for NEURS.
Creates remote repo 'neurs-art-engine', commits codebase, tags 'v1.0.0-final', and pushes.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

GITHUB_USERNAME = "AdarshTupsakri"
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD", "Adarshmedha1922$")
REPO_NAME = "neurs-art-engine"

def create_github_repo(username: str, token_or_pass: str, repo_name: str) -> str:
    """
    Creates a new GitHub repository using GitHub REST API v3.
    """
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": "NEURS Art Engine - Step-by-step interactive AI visual art tutorial engine (Woxsen University)",
        "private": False,
        "auto_init": False
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "NEURS-Deployer-Agent",
            "Accept": "application/vnd.github.v3+json"
        },
        method="POST"
    )

    # Basic Auth header or Bearer Token header
    if token_or_pass.startswith("ghp_") or token_or_pass.startswith("github_pat_"):
        req.add_header("Authorization", f"Bearer {token_or_pass}")
    else:
        import base64
        auth_str = f"{username}:{token_or_pass}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        req.add_header("Authorization", f"Basic {encoded_auth}")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"Successfully created GitHub repository: {data.get('html_url')}")
            return data.get("clone_url")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"Repository '{repo_name}' already exists on GitHub.")
            return f"https://github.com/{username}/{repo_name}.git"
        else:
            print(f"GitHub API Error {e.code}: {e.read().decode('utf-8')}")
            sys.exit(1)

def run_cmd(cmd: list[str], cwd: str = ".") -> str:
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing command: {res.stderr}")
    return res.stdout

def setup_git_repository(clone_url: str):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Git init
    run_cmd(["git", "init"], cwd=root_dir)
    run_cmd(["git", "config", "user.name", "Adarsh Tupsakri"], cwd=root_dir)
    run_cmd(["git", "config", "user.email", "adarsh.tupsakri@woxsen.edu.in"], cwd=root_dir)

    # 2. Checkout main
    run_cmd(["git", "checkout", "-B", "main"], cwd=root_dir)

    # 3. Add all files
    run_cmd(["git", "add", "."], cwd=root_dir)

    # 4. Initial commit
    run_cmd(["git", "commit", "-m", "feat: initial production release v1.0.0-final - NEURS Art Engine"], cwd=root_dir)

    # 5. Tag release
    run_cmd(["git", "tag", "-a", "v1.0.0-final", "-m", "NEURS Art Engine Production Release v1.0.0-final"], cwd=root_dir)

    # 6. Set remote origin
    auth_clone_url = clone_url.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_PASSWORD}@")
    run_cmd(["git", "remote", "remove", "origin"], cwd=root_dir)
    run_cmd(["git", "remote", "add", "origin", auth_clone_url], cwd=root_dir)

    # 7. Push to origin main and tags
    push_out = run_cmd(["git", "push", "-u", "origin", "main", "--tags"], cwd=root_dir)
    print("Git push completed successfully!")

if __name__ == "__main__":
    print("Initializing GitHub repository creation for NEURS...")
    clone_url = create_github_repo(GITHUB_USERNAME, GITHUB_PASSWORD, REPO_NAME)
    setup_git_repository(clone_url)
