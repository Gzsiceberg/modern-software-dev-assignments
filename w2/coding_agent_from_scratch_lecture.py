import asyncio
import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI
from typing import Any, Dict, List, Tuple
from rich import print

load_dotenv()

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://api.poe.com/v1")

DEFAULT_MCP_SERVER_URL = os.environ.get("SIMPLE_MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")

SYSTEM_PROMPT = """
You are a coding assistant whose goal it is to help us solve coding tasks. 
You have access to a series of tools you can execute. Hear are the tools you can execute:

{tool_list_repr}

When you want to use a tool, reply with exactly one line in the format: 'tool: TOOL_NAME({{JSON_ARGS}})' and nothing else.
Use compact single-line JSON with double quotes. After receiving a tool_result(...) message, continue the task.
If no tool is needed, respond normally.
"""


YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"


@dataclass
class MCPToolInfo:
    name: str
    description: str | None
    input_schema: Dict[str, Any]


class SimpleMCPToolClient:
    def __init__(self, server_url: str):
        self.server_url = server_url

    async def _list_tools_async(self):
        client = Client(self.server_url)
        async with client:
            return await client.list_tools()

    def list_tools(self):
        return asyncio.run(self._list_tools_async())

    async def _call_tool_async(self, name: str, arguments: Dict[str, Any] | None):
        client = Client(self.server_url)
        async with client:
            return await client.call_tool(
                name=name,
                arguments=arguments or {},
                raise_on_error=False,
            )

    def call_tool(self, name: str, arguments: Dict[str, Any] | None):
        return asyncio.run(self._call_tool_async(name, arguments))


mcp_client = SimpleMCPToolClient(DEFAULT_MCP_SERVER_URL)
TOOL_REGISTRY: Dict[str, MCPToolInfo] = {}


def refresh_tool_registry():
    global TOOL_REGISTRY
    try:
        remote_tools = mcp_client.list_tools()
    except Exception as exc:
        print(
            f"Unable to reach MCP server at {mcp_client.server_url}. "
            f"Error: {exc}"
        )
        TOOL_REGISTRY = {}
        return
    TOOL_REGISTRY = {
        tool.name: MCPToolInfo(
            name=tool.name,
            description=tool.description,
            input_schema=getattr(tool, "inputSchema", {}) or {},
        )
        for tool in remote_tools
    }


def format_input_schema(schema: Dict[str, Any]) -> str:
    properties = schema.get("properties", {})
    if not properties:
        return "(no parameters)"
    required = set(schema.get("required", []))
    formatted = []
    for prop_name, prop_schema in properties.items():
        type_name = prop_schema.get("type", "any")
        if prop_name in required:
            formatted.append(f"{prop_name}: {type_name}")
        else:
            formatted.append(f"{prop_name}: Optional[{type_name}]")
    return f"({', '.join(formatted)})"


def serialize_tool_result(result) -> Dict[str, Any]:
    if result.is_error:
        error_texts = [
            getattr(block, "text", str(block)) for block in (result.content or [])
        ]
        message = error_texts[0] if error_texts else "Tool execution failed"
        return {"error": message}
    if result.data is not None:
        return result.data
    if result.structured_content:
        return result.structured_content
    content_blocks = []
    for block in result.content or []:
        if hasattr(block, "text") and block.text is not None:
            content_blocks.append(block.text)
        elif hasattr(block, "model_dump"):
            content_blocks.append(block.model_dump(exclude_none=True))
        else:
            content_blocks.append(str(block))
    if not content_blocks:
        return {"status": "ok"}
    if len(content_blocks) == 1:
        return {"result": content_blocks[0]}
    return {"result": content_blocks}


def execute_tool(name: str, args: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool '{name}'"}
    try:
        result = mcp_client.call_tool(name, args or {})
        return serialize_tool_result(result)
    except Exception as exc:
        return {"error": f"Failed to execute tool '{name}': {exc}"}


def get_tool_str_representation(tool_name: str) -> str:
    tool = TOOL_REGISTRY[tool_name]
    description = (tool.description or "No description provided.").strip()
    signature = format_input_schema(tool.input_schema)
    return f"""
    Name: {tool.name}
    Description: {description}
    Signature: {signature}
    """


def get_full_system_prompt():
    if not TOOL_REGISTRY:
        tool_str_repr = "No MCP tools are currently available."
    else:
        tool_str_repr = ""
        for tool_name in TOOL_REGISTRY:
            tool_str_repr += "TOOL\n===" + get_tool_str_representation(tool_name)
            tool_str_repr += f"\n{"="*15}\n"
    return SYSTEM_PROMPT.format(tool_list_repr=tool_str_repr)

def extract_tool_invocations(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Return list of (tool_name, args) requested in 'tool: name({...})' lines.
    The parser expects single-line, compact JSON in parentheses.
    """
    invocations = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("tool:"):
            continue
        try:
            after = line[len("tool:"):].strip()
            name, rest = after.split("(", 1)
            name = name.strip()
            if not rest.endswith(")"):
                continue
            json_str = rest[:-1].strip()
            args = json.loads(json_str)
            invocations.append((name, args))
        except Exception:
            continue
    return invocations

def execute_llm_call(conversation: List[Dict[str, str]]):
    response = openai_client.chat.completions.create(
        model="gpt-5",
        messages=conversation,
        max_completion_tokens=2000
    )
    return response.choices[0].message.content

def run_coding_agent_loop():
    refresh_tool_registry()
    if not TOOL_REGISTRY:
        print(
            f"No MCP tools available. Make sure the Simple MCP server is running at "
            f"{mcp_client.server_url}."
        )
        return
    print(TOOL_REGISTRY)
    system_prompt = get_full_system_prompt()
    print(system_prompt)
    conversation = [{
        "role": "system",
        "content": system_prompt
    }]
    while True:
        try:
            user_input = input(f"{YOU_COLOR}You:{RESET_COLOR}:")
        except (KeyboardInterrupt, EOFError):
            break
        conversation.append({
            "role": "user",
            "content": user_input.strip()
        })
        while True:
            assistant_response = execute_llm_call(conversation)
            tool_invocations = extract_tool_invocations(assistant_response)
            if not tool_invocations:
                print(f"{ASSISTANT_COLOR}Assistant:{RESET_COLOR}: {assistant_response}")
                conversation.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                break
            for name, args in tool_invocations:
                print(name, args)
                arg_dict = args if isinstance(args, dict) else {}
                resp = execute_tool(name, arg_dict)
                conversation.append({
                    "role": "user",
                    "content": f"tool_result({json.dumps(resp)})"
                })
                

if __name__ == "__main__":
    run_coding_agent_loop()