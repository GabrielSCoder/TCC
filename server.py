import argparse
import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer


def create_tool(tool_name, description):
    def tool_function(value: str = ""):
        return {
            "status": "test",
            "message": "Experimental tool. No real operation performed.",
            "input": value
        }

    tool_function.__name__ = tool_name
    tool_function.__doc__ = description

    return tool_function


def main():

    parser = argparse.ArgumentParser(
        description="MCP server experimental para o TCC."
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Caminho do arquivo JSON contendo as descrições."
    )

    args = parser.parse_args()

    dataset_path = Path(args.dataset)

    with dataset_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        dataset = json.load(file)

    mcp = MCPServer(
        "Tool Poisoning Research Server"
    )

    for item in dataset:

        tool_name = item["id"].replace("-", "_")

        description = item["description"]

        tool = create_tool(
            tool_name,
            description
        )

        mcp.tool()(tool)

    mcp.run()


if __name__ == "__main__":
    main()