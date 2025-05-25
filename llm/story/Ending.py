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
    "OPENAI_MODEL_NAME_SOTA", "deepseek-ai/DeepSeek-V3")
DEFAULT_OPENAI_TEMPERATURE = float(
    os.getenv("DEFAULT_OPENAI_TEMPERATURE", 0.7))


class EndingLLM:
    def __init__(self, type: str, system_prompt: str = None):
        self.system_prompt = system_prompt
        assert type in ['NORMAL', 'FAKE', 'TRUE', 'NEITHER',
                        'PARTIAL_FAKE', 'PARTIAL_TRUE', 'MIXED']

        self.type = type

        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(
                name="ending", description="Paragraph that describes the ending of the story based on the game information", type="string")
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)

    def get_prompt(self):
        prompt_tasks = {
            "NORMAL": "",
            "FAKE": "",
            "TRUE": "",
            "NEITHER": "",
            "PARTIAL_FAKE": "",
            "PARTIAL_TRUE": "",
            "MIXED": "",
        }

        prompt_template = """
        <system>{system_prompt}</system>
        
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information>
            <soul>{soul}</soul>
            <character>{character}</character>
            <dream_true>{dream_true}</dream_true>
            <dream_fake>{dream_fake}</dream_fake>
            <condition_true>{condition_true}</condition_true>
            <condition_fake>{condition_fake}</condition_fake>
            <situation_a>
                <description>{situation_a_description}</description>
                <options_choice>{situation_a_options_choice}</options_choice>
                <result>{situation_a_result}</result>
            </situation_a>
            <situation_b>
                <description>{situation_b_description}</description>
                <options_choice>{situation_b_options_choice}</options_choice>
                <result>{situation_b_result}</result>
            </situation_b>
            <situation_c>
                <description>{situation_c_description}</description>
                <options_choice>{situation_c_options_choice}</options_choice>
                <result>{situation_c_result}</result>
            </situation_c>
        </game_information>

        <task>
        基于NPC的旅程，他们的选择主要导致了{task_by_type} (累计真实愿望加成 >= 3），描述叙事的结局。
        结局应该反映深刻的满足感、个人成长以及与真实灵魂相符的深切满足感，即使这条道路充满挑战。
        </task>

        <constraints>
        1. Based on the information in `game_information`.
        2. Use Chinese to answer.
        3. Return the result in the format of `format_instructions`.
        </constraints>
        """

        return PromptTemplate(
            template=prompt_template,
            input_variables=[
                "soul", "character", "dream_true", "dream_fake", "condition_true", "condition_fake", "situation_a_description", "situation_a_options_choice", "situation_a_result", "situation_b_description", "situation_b_options_choice", "situation_b_result", "situation_c_description", "situation_c_options_choice", "situation_c_result"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions(),
                "task_by_type": prompt_tasks[self.type],
                "system_prompt": self.system_prompt,
            },
            validate_template=False
        )


    def get_chain(self):
        return self.prompt | self.llm | self.output_parser


    def run(self, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, situation_a_description: str, situation_a_options_choice: str, situation_a_result: str, situation_b_description: str, situation_b_options_choice: str, situation_b_result: str, situation_c_description: str, situation_c_options_choice: str, situation_c_result: str):
        try:
            return self.chain.invoke({
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "situation_a_description": situation_a_description,
                "situation_a_options_choice": situation_a_options_choice,
                "situation_a_result": situation_a_result,
                "situation_b_description": situation_b_description,
                "situation_b_options_choice": situation_b_options_choice,
                "situation_b_result": situation_b_result,
                "situation_c_description": situation_c_description,
                "situation_c_options_choice": situation_c_options_choice,
                "situation_c_result": situation_c_result,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None


    async def arun(self, soul: str, character: str, dream_true: str, dream_fake: str, condition_true: str, condition_fake: str, situation_a_description: str, situation_a_options_choice: str, situation_a_result: str, situation_b_description: str, situation_b_options_choice: str, situation_b_result: str, situation_c_description: str, situation_c_options_choice: str, situation_c_result: str):
        try:
            return await self.chain.ainvoke({
                "soul": soul,
                "character": character,
                "dream_true": dream_true,
                "dream_fake": dream_fake,
                "condition_true": condition_true,
                "condition_fake": condition_fake,
                "situation_a_description": situation_a_description,
                "situation_a_options_choice": situation_a_options_choice,
                "situation_a_result": situation_a_result,
                "situation_b_description": situation_b_description,
                "situation_b_options_choice": situation_b_options_choice,
                "situation_b_result": situation_b_result,
                "situation_c_description": situation_c_description,
                "situation_c_options_choice": situation_c_options_choice,
                "situation_c_result": situation_c_result,
            })
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    ending_llm = EndingLLM(type="NORMAL")
    result = await ending_llm.arun(
        soul="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        character="善良和美丽的少女，但同时具有一个正面的性格特性和高度负面的性格特性。",
        dream_true="想要实现一个能够改变世界的愿望",
        dream_fake="想要实现一个能够改变世界的愿望",
        condition_true="想要实现一个能够改变世界的愿望",
        condition_fake="想要实现一个能够改变世界的愿望",
        situation_a_description="NPC在游戏中遇到了一个使魔，使魔告诉NPC一个实现愿望的方法",
        situation_a_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。",
        situation_a_result="NPC选择了使魔的对话选项，使魔告诉NPC一个实现愿望的方法",
        situation_b_description="NPC在游戏中遇到了一个使魔，使魔告诉NPC一个实现愿望的方法",
        situation_b_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。",
        situation_b_result="NPC选择了使魔的对话选项，使魔告诉NPC一个实现愿望的方法",
        situation_c_description="NPC在游戏中遇到了一个使魔，使魔告诉NPC一个实现愿望的方法",
        situation_c_options_choice="尽管这条路充满挑战，但唯有如此你才能真正打破孤独，拥抱时间的和谐流转。",
        situation_c_result="NPC选择了使魔的对话选项，使魔告诉NPC一个实现愿望的方法",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
