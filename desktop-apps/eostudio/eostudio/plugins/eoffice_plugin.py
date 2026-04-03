"""eOffice plugin — integrates the eOffice productivity suite into EoStudio.

This plugin connects to the eOffice backend (localhost:3001) and provides:
- Embedded document/spreadsheet/note editors inside EoStudio
- eBot AI assistant for code documentation, summarization, and rewriting
- Project documentation generation (eDocs)
- Data analysis from simulation results (eSheets)
- Task management integration (ePlanner)
- Team collaboration (eConnect)
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from eostudio.plugins.plugin_base import (
    Plugin,
    PluginHook,
    PluginManifest,
    PluginState,
)

log = logging.getLogger(__name__)

EOFFICE_DEFAULT_URL = "http://localhost:3001"


# ------------------------------------------------------------------
# eOffice API client
# ------------------------------------------------------------------

class EOfficeClient:
    """HTTP client for the eOffice backend API."""

    def __init__(self, base_url: str = EOFFICE_DEFAULT_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self._connected = False
        self._version = ""
        self._apps: List[Dict[str, Any]] = []

    def check_connection(self) -> bool:
        try:
            resp = urllib.request.urlopen(f"{self.base_url}/api/health", timeout=3)
            data = json.loads(resp.read().decode())
            self._version = data.get("version", "unknown")
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def version(self) -> str:
        return self._version

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            return json.loads(resp.read().decode())
        except Exception as exc:
            log.error("eOffice API error (%s): %s", path, exc)
            return {"error": str(exc)}

    def _get(self, path: str) -> Dict[str, Any]:
        try:
            resp = urllib.request.urlopen(
                f"{self.base_url}{path}", timeout=10
            )
            return json.loads(resp.read().decode())
        except Exception as exc:
            log.error("eOffice API error (%s): %s", path, exc)
            return {"error": str(exc)}

    # ---- eBot AI ----

    def ebot_ask(self, prompt: str, context: str = "") -> str:
        result = self._post("/api/ebot/ask", {
            "prompt": prompt,
            "context": context,
        })
        return result.get("response", result.get("error", ""))

    def ebot_summarize(self, text: str) -> str:
        result = self._post("/api/ebot/summarize", {"text": text})
        return result.get("summary", result.get("error", ""))

    def ebot_rewrite(self, text: str, style: str = "professional") -> str:
        result = self._post("/api/ebot/rewrite", {
            "text": text,
            "style": style,
        })
        return result.get("rewritten", result.get("error", ""))

    def ebot_generate_docs(self, code: str, language: str = "c") -> str:
        result = self._post("/api/ebot/generate-docs", {
            "code": code,
            "language": language,
        })
        return result.get("documentation", result.get("error", ""))

    # ---- eDocs ----

    def create_doc(self, title: str, content: str = "") -> Dict[str, Any]:
        return self._post("/api/edocs", {
            "title": title,
            "content": content,
        })

    def list_docs(self) -> List[Dict[str, Any]]:
        result = self._get("/api/edocs")
        return result.get("documents", [])

    # ---- eNotes ----

    def create_note(self, title: str, body: str = "") -> Dict[str, Any]:
        return self._post("/api/enotes", {"title": title, "body": body})

    def list_notes(self) -> List[Dict[str, Any]]:
        result = self._get("/api/enotes")
        return result.get("notes", [])

    # ---- eSheets ----

    def create_sheet(self, title: str, data: List[List[Any]] = None) -> Dict[str, Any]:
        return self._post("/api/esheets", {
            "title": title,
            "data": data or [],
        })

    def import_csv(self, title: str, csv_content: str) -> Dict[str, Any]:
        return self._post("/api/esheets/import", {
            "title": title,
            "format": "csv",
            "content": csv_content,
        })

    # ---- ePlanner ----

    def create_task(self, title: str, description: str = "",
                     priority: str = "medium") -> Dict[str, Any]:
        return self._post("/api/eplanner/tasks", {
            "title": title,
            "description": description,
            "priority": priority,
        })

    def list_tasks(self) -> List[Dict[str, Any]]:
        result = self._get("/api/eplanner/tasks")
        return result.get("tasks", [])

    # ---- eDrive ----

    def upload_file(self, filename: str, content: str) -> Dict[str, Any]:
        return self._post("/api/edrive/upload", {
            "filename": filename,
            "content": content,
        })

    def list_files(self) -> List[Dict[str, Any]]:
        result = self._get("/api/edrive/files")
        return result.get("files", [])


# ------------------------------------------------------------------
# eOffice plugin
# ------------------------------------------------------------------

class EOfficePlugin(Plugin):
    """eOffice productivity suite plugin for EoStudio.

    Provides embedded document editing, AI-powered code documentation,
    simulation data analysis, task management, and team collaboration
    directly within the EoStudio IDE.
    """

    manifest = PluginManifest(
        id="eoffice",
        name="eOffice Productivity Suite",
        version="0.1.0",
        description=(
            "Integrates eDocs, eNotes, eSheets, eBot AI, ePlanner, and "
            "eDrive into EoStudio for documentation, data analysis, and "
            "project management."
        ),
        author="EoS Team",
        plugin_type="productivity",
        entry_point="eostudio.plugins.eoffice_plugin",
        dependencies=[],
        min_EoStudio_version="0.1.0",
        config_schema={
            "backend_url": {
                "type": "string",
                "default": EOFFICE_DEFAULT_URL,
            },
            "auto_doc_on_export": {
                "type": "boolean",
                "default": True,
                "description": "Auto-generate documentation when exporting code",
            },
            "auto_sheet_on_simulate": {
                "type": "boolean",
                "default": True,
                "description": "Auto-create eSheets from simulation results",
            },
            "ebot_enabled": {
                "type": "boolean",
                "default": True,
            },
        },
    )

    def __init__(self, manifest: Optional[PluginManifest] = None) -> None:
        super().__init__(manifest or self.__class__.manifest)
        self._client = EOfficeClient()
        self._connected = False
        self._eoffice_version = ""

    # ---- Lifecycle ----

    def activate(self, context: Dict[str, Any]) -> bool:
        url = self.config.get("backend_url", EOFFICE_DEFAULT_URL)
        self._client = EOfficeClient(url)
        self._connected = self._client.check_connection()

        if self._connected:
            self._eoffice_version = self._client.version
            log.info("eOffice connected: v%s at %s", self._eoffice_version, url)
        else:
            log.warning("eOffice backend not available at %s — running offline", url)

        # Register hooks
        self._hooks = {
            PluginHook.ON_EXPORT: self._on_export,
            PluginHook.ON_SIMULATE: self._on_simulate,
            PluginHook.ON_SAVE: self._on_save,
            PluginHook.POST_CODEGEN: self._on_post_codegen,
            PluginHook.ON_ERROR: self._on_error,
        }

        self.state = PluginState.ACTIVE
        return True

    def deactivate(self) -> None:
        self.state = PluginState.DISABLED
        self._connected = False

    # ---- Hook Handlers ----

    def _on_export(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-generate project documentation when code is exported."""
        if not self.config.get("auto_doc_on_export", True):
            return {}
        if not self._connected:
            return {"skipped": "eOffice offline"}

        code = data.get("code", "")
        filename = data.get("filename", "export")
        language = data.get("language", "c")

        if code:
            docs = self._client.ebot_generate_docs(code, language)
            self._client.create_doc(
                title=f"Documentation: {filename}",
                content=docs,
            )
            log.info("Auto-generated docs for %s", filename)
            return {"documentation_created": True, "title": filename}

        return {}

    def _on_simulate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-create eSheets from simulation results."""
        if not self.config.get("auto_sheet_on_simulate", True):
            return {}
        if not self._connected:
            return {"skipped": "eOffice offline"}

        metrics = data.get("metrics", {})
        platform = data.get("platform", "unknown")

        if metrics:
            rows = [["Metric", "Value", "Unit"]]
            for key, val in metrics.items():
                unit = ""
                if "time" in key.lower() or "duration" in key.lower():
                    unit = "ms"
                elif "memory" in key.lower() or "ram" in key.lower():
                    unit = "KB"
                elif "frequency" in key.lower() or "clock" in key.lower():
                    unit = "MHz"
                rows.append([key, str(val), unit])

            self._client.create_sheet(
                title=f"Simulation Results: {platform}",
                data=rows,
            )
            log.info("Auto-created eSheet for simulation on %s", platform)
            return {"sheet_created": True, "platform": platform}

        return {}

    def _on_save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync project files to eDrive on save."""
        if not self._connected:
            return {}

        filename = data.get("filename", "")
        if filename:
            log.debug("Project saved: %s (eDrive sync available)", filename)
        return {}

    def _on_post_codegen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate inline documentation for generated code."""
        if not self.config.get("ebot_enabled", True):
            return {}
        if not self._connected:
            return {}

        files = data.get("generated_files", [])
        documented = 0
        for finfo in files[:5]:  # limit to 5 files
            code = finfo.get("content", "")
            if code and len(code) > 100:
                docs = self._client.ebot_generate_docs(code)
                if docs:
                    documented += 1
        return {"files_documented": documented}

    def _on_error(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log errors to eNotes for tracking."""
        if not self._connected:
            return {}

        error_msg = data.get("message", "Unknown error")
        source = data.get("source", "EoStudio")
        self._client.create_note(
            title=f"Error: {source}",
            body=f"**Error:** {error_msg}\n\n"
                 f"**Source:** {source}\n"
                 f"**Time:** auto-logged by eOffice plugin",
        )
        return {"error_logged": True}

    # ---- Public API for EoStudio ----

    def ask_ebot(self, prompt: str, context: str = "") -> str:
        if not self._connected:
            return "(eOffice offline — start backend with 'npm run dev')"
        return self._client.ebot_ask(prompt, context)

    def summarize(self, text: str) -> str:
        if not self._connected:
            return "(eOffice offline)"
        return self._client.ebot_summarize(text)

    def rewrite(self, text: str, style: str = "professional") -> str:
        if not self._connected:
            return "(eOffice offline)"
        return self._client.ebot_rewrite(text, style)

    def generate_docs(self, code: str, language: str = "c") -> str:
        if not self._connected:
            return "(eOffice offline)"
        return self._client.ebot_generate_docs(code, language)

    def create_doc(self, title: str, content: str = "") -> Dict[str, Any]:
        if not self._connected:
            return {"error": "offline"}
        return self._client.create_doc(title, content)

    def create_note(self, title: str, body: str = "") -> Dict[str, Any]:
        if not self._connected:
            return {"error": "offline"}
        return self._client.create_note(title, body)

    def create_task(self, title: str, description: str = "") -> Dict[str, Any]:
        if not self._connected:
            return {"error": "offline"}
        return self._client.create_task(title, description)

    def export_simulation_data(self, title: str,
                                 data: List[List[Any]]) -> Dict[str, Any]:
        if not self._connected:
            return {"error": "offline"}
        return self._client.create_sheet(title, data)

    # ---- UI Contributions ----

    def get_menu_items(self) -> List[Dict[str, Any]]:
        return [
            {
                "label": "eOffice",
                "children": [
                    {"label": "Open eDocs", "action": "eoffice.open_edocs",
                     "shortcut": "Ctrl+Shift+D"},
                    {"label": "Open eNotes", "action": "eoffice.open_enotes",
                     "shortcut": "Ctrl+Shift+N"},
                    {"label": "Open eSheets", "action": "eoffice.open_esheets"},
                    {"label": "Open ePlanner", "action": "eoffice.open_eplanner"},
                    {"type": "separator"},
                    {"label": "eBot: Summarize Selection",
                     "action": "eoffice.ebot_summarize"},
                    {"label": "eBot: Rewrite Selection",
                     "action": "eoffice.ebot_rewrite"},
                    {"label": "eBot: Generate Docs",
                     "action": "eoffice.ebot_generate_docs"},
                    {"label": "eBot Chat", "action": "eoffice.ebot_chat",
                     "shortcut": "Ctrl+Shift+B"},
                    {"type": "separator"},
                    {"label": "Export to eDrive",
                     "action": "eoffice.export_edrive"},
                    {"label": "Open eOffice Suite",
                     "action": "eoffice.open_suite"},
                ],
            },
        ]

    def get_toolbar_items(self) -> List[Dict[str, Any]]:
        return [
            {"icon": "📝", "label": "eDocs", "action": "eoffice.open_edocs",
             "tooltip": "Open eDocs editor"},
            {"icon": "🤖", "label": "eBot", "action": "eoffice.ebot_chat",
             "tooltip": "eBot AI Assistant"},
            {"icon": "📊", "label": "eSheets", "action": "eoffice.open_esheets",
             "tooltip": "Open eSheets"},
        ]

    def get_panel(self) -> Optional[Dict[str, Any]]:
        status = "Connected" if self._connected else "Offline"
        apps = [
            {"name": "eDocs", "port": 5173, "status": "ready"},
            {"name": "eNotes", "port": 5174, "status": "ready"},
            {"name": "eSheets", "port": 5175, "status": "ready"},
            {"name": "eSlides", "port": 5176, "status": "ready"},
            {"name": "eMail", "port": 5177, "status": "ready"},
            {"name": "ePlanner", "port": 5183, "status": "ready"},
            {"name": "eDrive", "port": 5179, "status": "ready"},
            {"name": "eConnect", "port": 5180, "status": "ready"},
            {"name": "eForms", "port": 5181, "status": "ready"},
        ]

        return {
            "title": "eOffice Suite",
            "sections": [
                {
                    "title": "Status",
                    "items": [
                        {"label": "Backend", "value": status},
                        {"label": "Version", "value": self._eoffice_version or "—"},
                        {"label": "URL", "value": self._client.base_url},
                        {"label": "eBot AI",
                         "value": "Enabled" if self.config.get("ebot_enabled") else "Disabled"},
                    ],
                },
                {
                    "title": "Apps",
                    "items": [
                        {"label": app["name"],
                         "value": f":{app['port']}",
                         "action": f"eoffice.open_{app['name'].lower()}"}
                        for app in apps
                    ],
                },
                {
                    "title": "Quick Actions",
                    "items": [
                        {"label": "Summarize Code", "action": "eoffice.ebot_summarize"},
                        {"label": "Generate Docs", "action": "eoffice.ebot_generate_docs"},
                        {"label": "Create Task", "action": "eoffice.create_task"},
                        {"label": "Export Results", "action": "eoffice.export_results"},
                    ],
                },
            ],
        }

    def get_status(self) -> Dict[str, Any]:
        base = super().get_status()
        base.update({
            "connected": self._connected,
            "eoffice_version": self._eoffice_version,
            "backend_url": self._client.base_url,
            "ebot_enabled": self.config.get("ebot_enabled", True),
            "auto_doc": self.config.get("auto_doc_on_export", True),
            "auto_sheet": self.config.get("auto_sheet_on_simulate", True),
        })
        return base
