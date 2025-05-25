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


class SituationBResultLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()
        
    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)
    
    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(name="result", description="Paragragh that describes the result of the situation after the choice by the player")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)
    
    def get_prompt(self):
        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>

        <task>
        根据游戏信息(`game_information`)，描述NPC选择了使魔的对话选项后的即时结果或后果。
        这个结果应该自然地由所选选项引出，并暗示其对NPC实现愿望路径的影响。
        </task>
        
        <game_information>
            <theme>{theme}</theme>
            <background>{background}</background>
            <soul>{soul}</soul>
            <character>{character}</character>
            <dream_true>{dream_true}</dream_true>
            <dream_fake>{dream_fake}</dream_fake>
            <condition_true>{condition_true}</condition_true>
            <condition_fake>{condition_fake}</condition_fake>
            <prev_situation_description>{prev_situation_description}</prev_situation_description>
            <prev_situation_options_choice>{prev_situation_options_choice}</prev_situation_options_choice>
            <prev_situation_result>{prev_situation_result}</prev_situation_result>
            <current_situation_description>{current_situation_description}</current_situation_description>
            <current_situation_options_choice>{current_situation_options_choice}</current_situation_options_choice>
        </game_information>
        
        <constraints>
        1. 基于游戏信息(`game_information`)中的所有信息.
        2. 使用中文回答。
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """
        
        return PromptTemplate(
            template=prompt_template,
            input_variables=["theme", "background", "soul", "character", "dream_true", "dream_fake", "condition_true", "condition_fake", "prev_situation_description", "prev_situation_options_choice", "prev_situation_result", "current_situation_description", "current_situation_options_choice"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )
        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str, background: str, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str, current_situation_description: str, current_situation_options_choice: str):
        try:
            return self.chain.invoke({
                "theme": theme,
                "background": background,
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "prev_situation_description": prev_situation_description,
                "prev_situation_options_choice": prev_situation_options_choice,
                "prev_situation_result": prev_situation_result,
                "current_situation_description": current_situation_description,
                "current_situation_options_choice": current_situation_options_choice,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        
    
    async def arun(self, theme: str, background: str, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str, current_situation_description: str, current_situation_options_choice: str):
        try:
            return await self.chain.ainvoke({
                "theme": theme,
                "background": background,
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "prev_situation_description": prev_situation_description,
                "prev_situation_options_choice": prev_situation_options_choice,
                "prev_situation_result": prev_situation_result,
                "current_situation_description": current_situation_description,
                "current_situation_options_choice": current_situation_options_choice,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None
        

async def main():
    situation_b_result_llm = SituationBResultLLM()
    result = await situation_b_result_llm.arun(
        theme="科幻",
        background="未来世界",
        soul="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        character="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        dream_true="想要实现一个能够改变世界的愿望",
        dream_fake="想要实现一个能够改变世界的愿望",
        condition_true="想要实现一个能够改变世界的愿望",
        condition_fake="想要实现一个能够改变世界的愿望",
        prev_situation_description="NPC在游戏中遇到了一个使魔，使魔告诉NPC一个实现愿望的方法",
        prev_situation_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。",
        prev_situation_result="NPC选择了使魔的对话选项，使魔告诉NPC一个实现愿望的方法",
        current_situation_description="NPC在游戏中遇到了一个使魔，使魔告诉NPC一个实现愿望的方法",
        current_situation_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())