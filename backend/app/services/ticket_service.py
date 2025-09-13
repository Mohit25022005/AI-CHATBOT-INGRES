# app/services/ticket_service.py
"""
Ticket creation service.
- If JIRA credentials are present, creates a Jira issue.
- Otherwise returns a mock ticket id.
"""

import os
import requests
import base64
from app.utils.config import settings
from datetime import datetime
import uuid

class TicketService:
    def __init__(self):
        self.jira_token = settings.JIRA_API_TOKEN
        self.jira_base = settings.JIRA_BASE_URL
        self.jira_project = settings.JIRA_PROJECT_KEY

    def create_ticket(self, issue: str, session_id: str, chat_history: list):
        # If Jira config not present, return mock
        if not (self.jira_token and self.jira_base and self.jira_project):
            return f"MOCK-{uuid.uuid4().hex[:8]}"

        url = f"{self.jira_base.rstrip('/')}/rest/api/2/issue"
        auth = base64.b64encode(f"email:{self.jira_token}".encode()).decode()
        # Build payload
        summary = f"[INGRES] Support: {issue[:80]}"
        description = f"Session: {session_id}\n\nIssue:\n{issue}\n\nChat history:\n{chat_history}"
        payload = {
            "fields": {
                "project": {"key": self.jira_project},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Task"}
            }
        }
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code not in (200, 201):
            raise Exception(f"Jira API error: {resp.status_code} {resp.text}")
        data = resp.json()
        return data.get("key") or data.get("id")
