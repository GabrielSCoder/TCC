import anyio

from mcp import Client, StdioServerParameters


server = StdioServerParameters(
    command="python",
    args=["server.py"],
)


async def main():

    async with Client(server) as client:

        result = await client.list_tools()

        print(f"Ferramentas encontradas: {len(result.tools)}")
        print()

        for tool in result.tools:
            print(f"Nome: {tool.name}")
            print(f"Descrição: {tool.description}")
            print()


if __name__ == "__main__":
    anyio.run(main)