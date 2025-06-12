import asyncio
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import logging

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def run_claude_chat(user_prompt: str):
    server_script_path = "../mcp-ecommerce-agent/src/agent/ecom_tools.py"

    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    async with stdio_client(server_params) as (stdio, write):
        async with ClientSession(stdio, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools

            client = Anthropic()
            messages = [{"role": "user", "content": user_prompt}]
            tool_schemas = [{
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema
            } for t in tools]

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=(
                    "Sen bir Türkçe müşteri destek asistanısın. "
                    "Kullanıcıdan gelen ürün sorularını arka plandaki tool ile çözümle. "
                    "JSON cevabı Claude üretmeyecek, sadece tool'dan dönecek."
                ),
                max_tokens=1000,
                tools=tool_schemas,
                messages=messages
            )

            final_text = ""
            possible_json = None

            for content in response.content:
                if content.type == "text":
                    final_text += content.text.strip() + "\n\n"

                elif content.type == "tool_use":
                    tool_result = await session.call_tool(content.name, content.input)

                    if (
                        isinstance(tool_result.content, list)
                        and len(tool_result.content) == 1
                        and getattr(tool_result.content[0], "type", "") == "text"
                    ):
                        result_text = tool_result.content[0].text.strip()
                        final_text += f"🔧 {result_text}"

                        # JSON olup olmadığını kontrol et
                        try:
                            json_data = json.loads(result_text)
                            logger.info("✅ JSON başarılı şekilde ayrıştırıldı.")
                            return json_data
                        except json.JSONDecodeError:
                            logger.warning("❌ JSON ayrıştırılamadı. Düz metin döndürülüyor.")
                            return final_text
                    else:
                        final_text += f"🔧 {str(tool_result.content).strip()}"
                        return final_text

            return final_text


if __name__ == "__main__":
    prompt = input("Claude'a sor: ")
    result = asyncio.run(run_claude_chat(prompt))
    print("Claude:", result)
