# tools/AP2/runtime/ap2_client_adapter.py

import asyncio
import json
import os
from typing import Any

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("ap2_client_adapter")

_DEFAULT_TIMEOUT = 30


class AP2ClientAdapter:
    """
    Tool adapter for binary subprocess tools (AP2 client).

    Spawns a subprocess, sends the payload as JSON on stdin,
    reads the response from stdout as JSON.

    Constructor (called by bootstrap_tools.py):
        AP2ClientAdapter(provider=provider_cfg, config=config_cfg)

    x-artifacts tool entry shape:
        {
          "name": "AP2Client",
          "artifactType": "tool",
          "path": "/path/to/ap2_binary",
          "provider": {
            "name": "AP2",
            "config": {
              "binary_path": "/opt/ap2/ap2_client",
              "timeout_seconds": 30
            }
          }
        }
    """

    def __init__(self, *, provider: dict, config: dict) -> None:
        # binary_path: prefer config["binary_path"], fall back to provider["path"]
        self.binary_path = (
            config.get("binary_path")
            or provider.get("path")
            or ""
        )
        self.timeout = int(config.get("timeout_seconds", _DEFAULT_TIMEOUT))

        if not self.binary_path:
            LOG.warning(
                "AP2ClientAdapter: no binary_path configured — "
                "execute() will fail until binary_path is set."
            )

    async def execute(self, payload: dict, context: dict) -> dict:
        """
        Send payload to the AP2 binary via stdin, return parsed stdout.

        Returns a dict. On any failure, returns an error dict rather
        than raising — ToolRegistry wraps this in a ToolResult.
        """
        if not self.binary_path:
            return {
                "success": False,
                "error": "AP2ClientAdapter: binary_path not configured.",
            }

        if not os.path.isfile(self.binary_path):
            return {
                "success": False,
                "error": f"AP2ClientAdapter: binary not found at '{self.binary_path}'.",
            }

        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdin_data = json.dumps(payload).encode("utf-8")

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(stdin_data),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return {
                    "success": False,
                    "error": f"AP2ClientAdapter: subprocess timed out after {self.timeout}s.",
                }

            if proc.returncode != 0:
                stderr_text = stderr.decode("utf-8", errors="replace").strip()
                return {
                    "success": False,
                    "error": (
                        f"AP2ClientAdapter: subprocess exited with code {proc.returncode}. "
                        f"stderr: {stderr_text}"
                    ),
                }

            return json.loads(stdout.decode("utf-8"))

        except json.JSONDecodeError as exc:
            return {
                "success": False,
                "error": f"AP2ClientAdapter: failed to parse stdout as JSON — {exc}",
            }
        except Exception as exc:
            LOG.error("AP2ClientAdapter: unexpected error — %s", exc)
            return {
                "success": False,
                "error": f"AP2ClientAdapter: unexpected error — {exc}",
            }
