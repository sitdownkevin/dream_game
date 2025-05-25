import os
import asyncio
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = 1.0


class CharacLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE, model_kwargs={"top_p": 0.9})

    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(
                name="name", description="The name of the character", type="string"),
            ResponseSchema(
                name="role", description="The role of the character", type="string"),
            ResponseSchema(
                name="age", description="The age of the character", type="integer"
            ),
            ResponseSchema(
                name="description", description="A short description of the character", type="string"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)

    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        <format_instructions>{format_instructions}</format_instructions>
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <personality description="NPC特性">{personality}</personality>
        </game_information>
        <task>
        基于`game_information`中的信息，给出一个浮夸的NPC设定.
        </task>
        <constraints>
        1. NPC设定包括名字、年龄、角色、描述.
        2. NPC设定的名字要有想象力，不能和世面已有的游戏角色重名.
        3. NPC设定的名字不能学习原神、魔兽的风格.
        4. NPC 设定的名字不能包含'璃'、'星'字.
        5. 使用中文回答.
        6. Return the result in the format of `format_instructions`.
        </constraints>
        """

        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "personality"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(
                ),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser

    def run(self, theme: str = None, background: str = None, personality: str = None):
        try:
            return self.chain.invoke({"theme": theme, "background": background, "personality": personality})
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def arun(self, theme: str = None, background: str = None, personality: str = None):
        try:
            return await self.chain.ainvoke({"theme": theme, "background": background, "personality": personality})
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    charac_llm = CharacLLM()
    result = await charac_llm.arun(
        theme='科幻',
        background='未来世界',
        personality='善良和美丽的角色，但同时具有一个正面的性格特性和高度负面的性格特性'
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
