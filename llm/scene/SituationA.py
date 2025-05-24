from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable

import asyncio
import os


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("DEFAULT_OPENAI_TEMPERATURE", 0.3))


class SituationALLM:
    def __init__(self, system_prompt: str = None, verbose: bool = False):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
        self.verbose = verbose
        self.data = None
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="description", description="Description of the situation")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>
        {format_instructions}
        </format_instructions>
        
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <soul description="游戏主角的灵魂">{soul}</soul>
            <background description="游戏背景">{background}</background>
            <character description="游戏主角">{character}</character>
            <dream_true description="游戏主角的真实愿望">{dream_true}</dream_true>
            <dream_fake description="游戏主角的虚假愿望">{dream_fake}</dream_fake>
            <condition_true description="游戏主角达成真实愿望的条件">{condition_true}</condition_true>
            <condition_fake description="游戏主角达成虚假愿望的条件">{condition_fake}</condition_fake>
        </game_information>
        
 
        <task>
        描述主角与一个神秘使魔首次相遇的情境。使魔的出现应该与主角的愿望和背景有微妙的联系，暗示一个潜在的转折点。
        </task>
 
        <background>
        "公主魔法"设定: 无条件让人物获得召唤男使魔的能力。据说他能够超越时空，帮召唤者实现愿望。然而，并没有可靠的依据。
        </background>

        <constraints>
        1. 基于主题(`theme`)、背景(`background`)、人物设定(`character`)、达成真实愿望的条件(`condition_true`)、达成虚假愿望的条件(`condition_fake`)，描述主角与一个神秘使魔首次相遇的情境。
        2. 使用中文回答。
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "character", "dream_true", "dream_fake", "condition_true", "condition_fake"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str, soul: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str):
        try:
            return self.chain.invoke({
                "theme": theme,
                "soul": soul,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str, soul: str, background: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str):
        try:
            return await self.chain.ainvoke({
                "theme": theme,
                "soul": soul,
                "background": background,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def aget_information(self):
        import sys, os
        # Add the project root to the path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(project_root)
        from llm.role.Soul import SoulLLM
        from llm.story.Theme import ThemeLLM
        from llm.story.Background import BackgroundLLM
        from llm.role.Charac import CharacLLM
        from llm.story.Dream import DreamLLM
        from llm.story.Condition import ConditionLLM
        
        print("Generating theme and soul...")
        theme_llm = ThemeLLM()
        soul_llm = SoulLLM()
        tasks = [
            theme_llm.arun(),
            soul_llm.arun(),
        ]
        data = await asyncio.gather(*tasks)
        theme, soul = data
        if self.verbose:
            print(theme)
            print(soul)

        print("Generating background...")
        background_llm = BackgroundLLM()
        background = await background_llm.arun(theme=theme)
        if self.verbose:
            print(background)
        
        print("Generating character...")
        character_llm = CharacLLM()
        character = await character_llm.arun(theme=theme, background=background)
        if self.verbose:
            print(character)
        
        print("Generating dream...")
        dream_llm = DreamLLM()
        dream_true = await dream_llm.arun(type='true', theme=theme, background=background, character=character)
        if self.verbose:
            print(dream_true)
        dream_fake = await dream_llm.arun(type='fake', theme=theme, background=background, character=character, dream_true=dream_true)
        if self.verbose:
            print(dream_fake)
        
        print("Generating condition...")
        condition_llm = ConditionLLM()
        condition_true = await condition_llm.arun(type='true', theme=theme, background=background, character=character, dream=dream_true)
        if self.verbose:
            print(condition_true)
        condition_fake = await condition_llm.arun(type='fake', theme=theme, background=background, character=character, dream=dream_fake)
        if self.verbose:
            print(condition_fake)
            
        self.data = {
            "theme": theme['theme'],
            "soul": soul['soul'],
            "background": background['background'],
            "character": character,
            "dream_true": dream_true['dream'],
            "dream_fake": dream_fake['dream'],
            "condition_true": condition_true['condition'],
            "condition_fake": condition_fake['condition'],
        }
        
        return self.data
    

    async def agenerate_situation(self):
        try:
            await self.aget_information()
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        try:
            result = await self.arun(
                theme=self.data['theme'],
                soul=self.data['soul'],
                background=self.data['background'],
                character=self.data['character'],
                dream_true=self.data['dream_true'],
                dream_fake=self.data['dream_fake'],
                condition_true=self.data['condition_true'],
                condition_fake=self.data['condition_fake'],
            )
        
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    situation_llm = SituationALLM(verbose=False)
    result = await situation_llm.agenerate_situation()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())