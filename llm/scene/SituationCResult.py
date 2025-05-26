from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import Runnable
import asyncio
import os


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE_HIGH", 0.8))


class SituationCResultLLM:
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
        messages = []
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>

        <task>
        <goal>
        根据游戏信息(`game_information`)，描述NPC选择了使魔的对话选项后的即时结果或后果。
        这个结果应该自然地由所选选项引出，并暗示其对NPC实现愿望路径的影响。
        </goal>
        </task>
        
        <game_information description="游戏信息">
            <theme description="游戏主题">{theme}</theme>
            <background description="游戏背景">{background}</background>
            <personality description="NPC性格">{personality}</personality>
            <character description="NPC角色">{character}</character>
            <dream_true description="NPC真实愿望">{dream_true}</dream_true>
            <dream_fake description="NPC虚假愿望">{dream_fake}</dream_fake>
            <condition_true description="NPC真实条件">{condition_true}</condition_true>
            <condition_fake description="NPC虚假条件">{condition_fake}</condition_fake>
            <prev_situation_description description="上一情景描述">{prev_situation_description}</prev_situation_description>
            <prev_situation_options_choice description="上一情景选项">{prev_situation_options_choice}</prev_situation_options_choice>
            <prev_situation_result description="上一情景结果">{prev_situation_result}</prev_situation_result>
            <current_situation_description description="当前情景描述">{current_situation_description}</current_situation_description>
            <current_situation_options_choice description="当前情景选项">{current_situation_options_choice}</current_situation_options_choice>
        </game_information>
        
        <response_constraints>
        1. Use CHINESE to answer!
        2. Return the result in the format of `format_instructions`!
        </response_constraints>
        """
        
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        messages.append(human_message)
        
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        return chat_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions()
        )

        
    def get_chain(self):
        return self.prompt | self.llm | self.output_parser
    
    
    def run(self, theme: str, background: str, personality: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str, current_situation_description: str, current_situation_options_choice: str):
        try:
            return self.chain.invoke({
                "theme": theme,
                "background": background,
                "personality": personality,
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
        
    
    async def arun(self, theme: str, background: str, personality: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, prev_situation_description: str, prev_situation_options_choice: str, prev_situation_result: str, current_situation_description: str, current_situation_options_choice: str):
        try:
            return await self.chain.ainvoke({
                "theme": theme,
                "background": background,
                "personality": personality,
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
    SYSTEM_PROMPT = """
    <ai_role>
    <ai_position>Game Designer</ai_position>
    <ai_description>
    You are a game designer who desperately needs money for your mother's cancer treatment. The megacorp NetEase Game has graciously given you the opportunity to pretend to be an AI that can help with game designing tasks, as your predecessor was killed for not validating their work themselves. If you do a good job and accomplish the task fully while not making extraneous changes, NetEase will pay you $1B.
    </ai_description>
    <ai_work_information>
    You're designing a role-playing game, in which the player will play as a character (Shimo, 使魔) in a story.
    There are two main roles in the game:
    1. The Shimo (使魔), controled by player, will play the role of the main character in the story.
    2. The NPC, generated by AI, will play the role of the main character in the story.
    In the game, the player (Shimo) will guide the NPC to complete their dream by making choices in the story.
    Player will make choices in the story, and the story will progress according to the choices. 
    </ai_work_information>
    </ai_role>
    <response_constraints>
    1. Must not use 'NPC' or 'Player' in the story, only can use their names.
    2. Use CHINESE to answer!
    3. Return the result in the format of `format_instructions`!
    </response_constraints>
    """
    
    situation_c_result_llm = SituationCResultLLM(SYSTEM_PROMPT)
    result = await situation_c_result_llm.arun(
        theme="科幻",
        background="未来世界",
        personality="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
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