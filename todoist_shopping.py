#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# todoist_shopping.py - Fetch Todoist "Einkaufsliste" and format for Signal
# Copyright (C) 2026 #B4mad Industries
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Fetch the Todoist 'Einkaufsliste' shopping list and output a formatted list."""

import subprocess
import sys
from collections import defaultdict

import requests

API_BASE = "https://api.todoist.com/api/v1"
PROJECT_NAME = "Einkaufsliste"


def get_api_token() -> str:
    """Retrieve the Todoist API token from gopass."""
    try:
        result = subprocess.run(
            ["gopass", "show", "openclaw/todoist-api-token"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"❌ Failed to retrieve API token from gopass: {e}", file=sys.stderr)
        sys.exit(1)


def api_get(endpoint: str, token: str, params: dict | None = None) -> dict:
    """Make an authenticated GET request to the Todoist API."""
    resp = requests.get(
        f"{API_BASE}/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def find_project(token: str) -> str | None:
    """Find the Einkaufsliste project and return its ID."""
    data = api_get("projects", token)
    for project in data.get("results", []):
        if project["name"] == PROJECT_NAME:
            return project["id"]
    return None


def get_sections(token: str, project_id: str) -> dict[str, str]:
    """Return a mapping of section_id -> section_name."""
    data = api_get("sections", token, {"project_id": project_id})
    return {s["id"]: s["name"] for s in data.get("results", [])}


def get_tasks(token: str, project_id: str) -> list[dict]:
    """Fetch all active tasks for a project."""
    data = api_get("tasks", token, {"project_id": project_id})
    return [t for t in data.get("results", []) if not t.get("checked")]


def format_shopping_list(tasks: list[dict], sections: dict[str, str]) -> str:
    """Format tasks into a clean shopping list grouped by section."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        section = sections.get(task.get("section_id", ""), "")
        grouped[section].append(task["content"])

    lines = ["🛒 *Einkaufsliste*", ""]

    # Unsectioned items first
    if "" in grouped:
        for item in sorted(grouped[""]):
            lines.append(f"• {item}")
        if len(grouped) > 1:
            lines.append("")

    # Sectioned items
    for section_name in sorted(k for k in grouped if k):
        lines.append(f"📦 *{section_name}*")
        for item in sorted(grouped[section_name]):
            lines.append(f"  • {item}")
        lines.append("")

    if not tasks:
        lines.append("✅ Liste ist leer — nichts zu kaufen!")

    return "\n".join(lines).rstrip()


def main():
    token = get_api_token()

    project_id = find_project(token)
    if not project_id:
        print(f"❌ Project '{PROJECT_NAME}' not found.", file=sys.stderr)
        sys.exit(1)

    sections = get_sections(token, project_id)
    tasks = get_tasks(token, project_id)
    print(format_shopping_list(tasks, sections))


if __name__ == "__main__":
    main()
