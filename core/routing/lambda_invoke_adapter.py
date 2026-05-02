# core/routing/lambda_invoke_adapter.py
#
# boto3-backed Lambda invoke adapter for YoAiRuntime.
#
# Injected into YoAiRuntime.tools["lambda_invoke"] at platform bootstrap.
# YoAiRuntime never imports boto3 directly — this keeps the runtime
# testable without AWS credentials by swapping in a stub adapter.
#
# Invocation type: RequestResponse (synchronous).
# The calling Lambda waits for the target to complete and return its
# API Gateway proxy response before returning to the caller.
#
# Usage in platform_bootstrap.py:
#   from core.routing.adapters.lambda_invoke_adapter import make_lambda_invoke_fn
#   tools = {"lambda_invoke": make_lambda_invoke_fn()}
#   runtime = YoAiRuntime(capability_map=capability_map, tools=tools)
#
# Usage in tests (stub):
#   async def stub_invoke(function_name: str, payload: bytes) -> bytes:
#       return json.dumps({"statusCode": 200, "body": "{}"}).encode()
#   tools = {"lambda_invoke": stub_invoke}

from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Callable, Awaitable

from core.observability.logging.platform_logger import get_platform_logger

LOG = get_platform_logger("lambda_invoke_adapter")


def make_lambda_invoke_fn(
    region_name: str | None = None,
) -> Callable[[str, bytes], Awaitable[bytes]]:
    # Returns an async callable that invokes a Lambda function synchronously
    # and returns the response payload as bytes.
    #
    # region_name: AWS region. None = boto3 default (from env / IAM role).
    #
    # boto3 is imported here, not at module level, so the adapter module
    # can be imported in test environments without boto3 installed — tests
    # inject a stub instead of calling make_lambda_invoke_fn().
    import boto3

    client = boto3.client("lambda", region_name=region_name)

    async def invoke(function_name: str, payload: bytes) -> bytes:
        # boto3 is synchronous — run in a thread pool to avoid blocking
        # the asyncio event loop.
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                partial(
                    client.invoke,
                    FunctionName=function_name,
                    InvocationType="RequestResponse",  # synchronous
                    Payload=payload,
                ),
            )
        except Exception as exc:
            # Surface boto3 errors (NoCredentialsError, ClientError, etc.)
            # as a structured error payload so YoAiRuntime._invoke_lambda()
            # can wrap them in a JSON-RPC error envelope.
            LOG.write(
                event_type="lambda_invoke_adapter.InvokeError",
                payload={"function_name": function_name, "error": str(exc)},
                context=None,
            )
            raise

        # response["Payload"] is a StreamingBody — read it fully
        raw = response["Payload"].read()

        # FunctionError is set when the Lambda itself raised an unhandled
        # exception (distinct from the function returning an error response).
        if response.get("FunctionError"):
            LOG.write(
                event_type="lambda_invoke_adapter.FunctionError",
                payload={
                    "function_name":  function_name,
                    "function_error": response["FunctionError"],
                    "response":       raw.decode("utf-8", errors="replace"),
                },
                context=None,
            )
            # Return the raw error payload — YoAiRuntime will parse it and
            # surface it as a JSON-RPC -32603 error envelope.

        return raw

    return invoke


def make_stub_invoke_fn(
    response_body: dict | None = None,
    status_code: int = 200,
) -> Callable[[str, bytes], Awaitable[bytes]]:
    # Test stub — returns a fixed API Gateway proxy response.
    # Use this in unit tests instead of make_lambda_invoke_fn().
    #
    # Example:
    #   stub = make_stub_invoke_fn({"result": {"output": "ok"}})
    #   tools = {"lambda_invoke": stub}
    #   runtime = YoAiRuntime(capability_map=cap_map, tools=tools)

    fixed_response = json.dumps({
        "statusCode": status_code,
        "body": json.dumps(response_body or {"result": {}, "status": "stub"}),
    }).encode("utf-8")

    async def stub(function_name: str, payload: bytes) -> bytes:
        LOG.write(
            event_type="lambda_invoke_adapter.StubInvoke",
            payload={
                "function_name": function_name,
                "payload_size":  len(payload),
            },
            context=None,
        )
        return fixed_response

    return stub
