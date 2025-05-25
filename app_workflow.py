import streamlit as st
import asyncio
import json
from llm.role.Charac import CharacLLM
from llm.story.Background import BackgroundLLM
from llm.story.Dream import DreamLLM
from llm.story.Condition import ConditionLLM
from llm.story.Theme import ThemeLLM
from llm.role.Personality import PersonalityLLM
from llm.scene.SituationA import SituationALLM
from llm.scene.SituationAOpt import SituationAOptLLM
from llm.scene.SituationAResult import SituationAResultLLM
from llm.scene.SituationB import SituationBLLM
from llm.scene.SituationBOpt import SituationBOptLLM
from llm.scene.SituationBResult import SituationBResultLLM
from llm.scene.SituationC import SituationCLLM
from llm.scene.SituationCOpt import SituationCOptLLM
from llm.scene.SituationCResult import SituationCResultLLM
from llm.story.Ending import EndingLLM


def init_session_state():
    """初始化 session state"""
    session_vars = [
        'personality', 'theme', 'background', 'character', 'dream_true', 'dream_fake',
        'condition_true', 'condition_fake', 'situation_a', 'situation_a_options',
        'situation_a_options_choice', 'situation_a_result', 'situation_b', 
        'situation_b_options', 'situation_b_options_choice', 'situation_b_result',
        'situation_c', 'situation_c_options', 'situation_c_options_choice', 
        'situation_c_result', 'ending'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = None


def display_json_content(data, title):
    """显示 JSON 格式的内容"""
    if data:
        st.subheader(f"✅ {title}")
        if isinstance(data, dict):
            st.json(data)
        else:
            st.text(data)
    else:
        st.subheader(f"⏳ {title}")
        st.info("等待生成...")


async def generate_personality_and_theme():
    """生成灵魂和主题"""
    personality_llm = PersonalityLLM()
    theme_llm = ThemeLLM()
    
    with st.spinner("正在生成灵魂和主题..."):
        tasks = [
            personality_llm.arun(),
            theme_llm.arun(),
        ]
        personality, theme = await asyncio.gather(*tasks)
        
        st.session_state.personality = personality
        st.session_state.theme = theme
        
        st.success("灵魂和主题生成完成！")


async def generate_background():
    """生成背景"""
    background_llm = BackgroundLLM()
    
    with st.spinner("正在生成背景..."):
        background = await background_llm.arun(theme=st.session_state.theme)
        st.session_state.background = background
        st.success("背景生成完成！")


async def generate_character():
    """生成角色"""
    charac_llm = CharacLLM()
    
    with st.spinner("正在生成角色..."):
        character = await charac_llm.arun(
            theme=st.session_state.theme, 
            background=st.session_state.background
        )
        st.session_state.character = character
        st.success("角色生成完成！")


async def generate_dreams():
    """生成梦境"""
    dream_llm = DreamLLM()
    
    with st.spinner("正在生成真实梦境..."):
        dream_true = await dream_llm.arun(
            type='TRUE',
            theme=st.session_state.theme,
            background=st.session_state.background,
            character=st.session_state.character
        )
        st.session_state.dream_true = dream_true
    
    with st.spinner("正在生成表面梦境..."):
        dream_fake = await dream_llm.arun(
            type='FAKE',
            theme=st.session_state.theme,
            background=st.session_state.background,
            character=st.session_state.character,
            dream_true=dream_true
        )
        st.session_state.dream_fake = dream_fake
        st.success("梦境生成完成！")


async def generate_conditions():
    """生成条件"""
    condition_llm_true = ConditionLLM(type='TRUE')
    condition_llm_fake = ConditionLLM(type='FAKE')
    
    with st.spinner("正在生成条件..."):
        tasks = [
            condition_llm_true.arun(
                theme=st.session_state.theme,
                background=st.session_state.background,
                character=st.session_state.character,
                dream=st.session_state.dream_true
            ),
            condition_llm_fake.arun(
                theme=st.session_state.theme,
                background=st.session_state.background,
                character=st.session_state.character,
                dream=st.session_state.dream_fake
            ),
        ]
        condition_true, condition_fake = await asyncio.gather(*tasks)
        
        st.session_state.condition_true = condition_true
        st.session_state.condition_fake = condition_fake
        st.success("条件生成完成！")


async def generate_situation_a():
    """生成情境A"""
    situation_llm = SituationALLM()
    
    with st.spinner("正在生成情境A..."):
        situation = await situation_llm.arun(
            theme=st.session_state.theme['theme'],
            personality=st.session_state.personality['personality'],
            background=st.session_state.background['background'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
        )
        st.session_state.situation_a = situation
        st.success("情境A生成完成！")


async def generate_situation_a_options():
    """生成情境A选项"""
    situation_aopt_llm = SituationAOptLLM()
    
    with st.spinner("正在生成情境A选项..."):
        situation_options = await situation_aopt_llm.arun(
            personality=st.session_state.personality['personality'],
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            current_situation_description=st.session_state.situation_a['description'],
        )
        st.session_state.situation_a_options = situation_options
        st.success("情境A选项生成完成！")


async def make_choice_for_situation_a(choice):
    """为情境A做出选择并生成结果"""
    st.session_state.situation_a_options_choice = st.session_state.situation_a_options[choice]
    
    situation_result_llm = SituationAResultLLM()
    
    with st.spinner("正在生成情境A结果..."):
        situation_result = await situation_result_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            current_situation_description=st.session_state.situation_a['description'],
            current_situation_options_choice=st.session_state.situation_a_options_choice,
        )
        st.session_state.situation_a_result = situation_result
        st.success("情境A结果生成完成！")


async def generate_situation_b():
    """生成情境B"""
    situation_b_llm = SituationBLLM()
    
    with st.spinner("正在生成情境B..."):
        situation_b = await situation_b_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_a['description'],
            prev_situation_options_choice=st.session_state.situation_a_options_choice,
            prev_situation_result=st.session_state.situation_a_result['result'],
        )
        st.session_state.situation_b = situation_b
        st.success("情境B生成完成！")


async def generate_situation_b_options():
    """生成情境B选项"""
    situation_b_opt_llm = SituationBOptLLM()
    
    with st.spinner("正在生成情境B选项..."):
        situation_b_options = await situation_b_opt_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_a['description'],
            prev_situation_options_choice=st.session_state.situation_a_options_choice,
            prev_situation_result=st.session_state.situation_a_result['result'],
            current_situation_description=st.session_state.situation_b['description'],
        )
        st.session_state.situation_b_options = situation_b_options
        st.success("情境B选项生成完成！")


async def make_choice_for_situation_b(choice):
    """为情境B做出选择并生成结果"""
    st.session_state.situation_b_options_choice = st.session_state.situation_b_options[choice]
    
    situation_b_result_llm = SituationBResultLLM()
    
    with st.spinner("正在生成情境B结果..."):
        situation_b_result = await situation_b_result_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_a['description'],
            prev_situation_options_choice=st.session_state.situation_a_options_choice,
            prev_situation_result=st.session_state.situation_a_result['result'],
            current_situation_description=st.session_state.situation_b['description'],
            current_situation_options_choice=st.session_state.situation_b_options_choice,
        )
        st.session_state.situation_b_result = situation_b_result
        st.success("情境B结果生成完成！")


async def generate_situation_c():
    """生成情境C"""
    situation_c_llm = SituationCLLM()
    
    with st.spinner("正在生成情境C..."):
        situation_c = await situation_c_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_b['description'],
            prev_situation_options_choice=st.session_state.situation_b_options_choice,
            prev_situation_result=st.session_state.situation_b_result['result'],
        )
        st.session_state.situation_c = situation_c
        st.success("情境C生成完成！")


async def generate_situation_c_options():
    """生成情境C选项"""
    situation_c_opt_llm = SituationCOptLLM()
    
    with st.spinner("正在生成情境C选项..."):
        situation_c_options = await situation_c_opt_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_b['description'],
            prev_situation_options_choice=st.session_state.situation_b_options_choice,
            prev_situation_result=st.session_state.situation_b_result['result'],
            current_situation_description=st.session_state.situation_c['description'],
        )
        st.session_state.situation_c_options = situation_c_options
        st.success("情境C选项生成完成！")


async def make_choice_for_situation_c(choice):
    """为情境C做出选择并生成结果"""
    st.session_state.situation_c_options_choice = st.session_state.situation_c_options[choice]
    
    situation_c_result_llm = SituationCResultLLM()
    
    with st.spinner("正在生成情境C结果..."):
        situation_c_result = await situation_c_result_llm.arun(
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            prev_situation_description=st.session_state.situation_b['description'],
            prev_situation_options_choice=st.session_state.situation_b_options_choice,
            prev_situation_result=st.session_state.situation_b_result['result'],
            current_situation_description=st.session_state.situation_c['description'],
            current_situation_options_choice=st.session_state.situation_c_options_choice,
        )
        st.session_state.situation_c_result = situation_c_result
        st.success("情境C结果生成完成！")


async def generate_ending():
    """生成结局"""
    ending_llm = EndingLLM(type="NORMAL")
    
    with st.spinner("正在生成故事结局..."):
        ending = await ending_llm.arun(
            personality=st.session_state.personality['personality'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            situation_a_description=st.session_state.situation_a['description'],
            situation_a_options_choice=st.session_state.situation_a_options_choice,
            situation_a_result=st.session_state.situation_a_result['result'],
            situation_b_description=st.session_state.situation_b['description'],
            situation_b_options_choice=st.session_state.situation_b_options_choice,
            situation_b_result=st.session_state.situation_b_result['result'],
            situation_c_description=st.session_state.situation_c['description'],
            situation_c_options_choice=st.session_state.situation_c_options_choice,
            situation_c_result=st.session_state.situation_c_result['result'],
        )
        st.session_state.ending = ending
        st.success("故事结局生成完成！")


def render_choice_interface(situation_options, situation_key, step_name):
    """渲染选择界面"""
    if situation_options:
        st.subheader(f"🎯 {step_name} - 请做出选择")
        
        choice_a = situation_options.get('CHOICE_A', '')
        choice_b = situation_options.get('CHOICE_B', '')
        choice_c = situation_options.get('CHOICE_C', '')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**选项A:**")
            # 处理字典或字符串格式
            if isinstance(choice_a, dict):
                st.write(choice_a.get('description', '无描述'))
            else:
                st.write(choice_a if choice_a else '无描述')
            if st.button(f"选择A", key=f"{situation_key}_choice_a"):
                return 'CHOICE_A'
        
        with col2:
            st.markdown("**选项B:**")
            # 处理字典或字符串格式
            if isinstance(choice_b, dict):
                st.write(choice_b.get('description', '无描述'))
            else:
                st.write(choice_b if choice_b else '无描述')
            if st.button(f"选择B", key=f"{situation_key}_choice_b"):
                return 'CHOICE_B'
        
        with col3:
            st.markdown("**选项C:**")
            # 处理字典或字符串格式
            if isinstance(choice_c, dict):
                st.write(choice_c.get('description', '无描述'))
            else:
                st.write(choice_c if choice_c else '无描述')
            if st.button(f"选择C", key=f"{situation_key}_choice_c"):
                return 'CHOICE_C'
    
    return None


def main():
    st.set_page_config(
        page_title="故事生成工作流",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 完整故事生成工作流")
    st.markdown("---")
    
    # 初始化 session state
    init_session_state()
    
    # 第一步：生成灵魂和主题
    st.header("1️⃣ 生成灵魂和主题")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎭 生成灵魂和主题", key="step1"):
            asyncio.run(generate_personality_and_theme())
    
    with col2:
        if st.session_state.personality and st.session_state.theme:
            st.success("✅ 已生成")
        else:
            st.info("⏳ 等待生成")
    
    # 显示结果
    col1, col2 = st.columns(2)
    with col1:
        display_json_content(st.session_state.personality, "灵魂")
    with col2:
        display_json_content(st.session_state.theme, "主题")
    
    st.markdown("---")
    
    # 第二步：生成背景
    st.header("2️⃣ 生成背景")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🌍 生成背景", key="step2", disabled=not (st.session_state.personality and st.session_state.theme)):
            asyncio.run(generate_background())
    
    with col2:
        if st.session_state.background:
            st.success("✅ 已生成")
        elif st.session_state.personality and st.session_state.theme:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成灵魂和主题")
    
    display_json_content(st.session_state.background, "背景")
    
    st.markdown("---")
    
    # 第三步：生成角色
    st.header("3️⃣ 生成角色")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("👤 生成角色", key="step3", disabled=not st.session_state.background):
            asyncio.run(generate_character())
    
    with col2:
        if st.session_state.character:
            st.success("✅ 已生成")
        elif st.session_state.background:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成背景")
    
    display_json_content(st.session_state.character, "角色")
    
    st.markdown("---")
    
    # 第四步：生成梦境
    st.header("4️⃣ 生成梦境")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("💭 生成梦境", key="step4", disabled=not st.session_state.character):
            asyncio.run(generate_dreams())
    
    with col2:
        if st.session_state.dream_true and st.session_state.dream_fake:
            st.success("✅ 已生成")
        elif st.session_state.character:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成角色")
    
    # 显示结果
    col1, col2 = st.columns(2)
    with col1:
        display_json_content(st.session_state.dream_true, "真实梦境")
    with col2:
        display_json_content(st.session_state.dream_fake, "表面梦境")
    
    st.markdown("---")
    
    # 第五步：生成条件
    st.header("5️⃣ 生成条件")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📋 生成条件", key="step5", disabled=not (st.session_state.dream_true and st.session_state.dream_fake)):
            asyncio.run(generate_conditions())
    
    with col2:
        if st.session_state.condition_true and st.session_state.condition_fake:
            st.success("✅ 已生成")
        elif st.session_state.dream_true and st.session_state.dream_fake:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成梦境")
    
    # 显示结果
    col1, col2 = st.columns(2)
    with col1:
        display_json_content(st.session_state.condition_true, "真实条件")
    with col2:
        display_json_content(st.session_state.condition_fake, "表面条件")
    
    st.markdown("---")
    
    # 第六步：生成情境A
    st.header("6️⃣ 生成情境A")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎬 生成情境A", key="step6", disabled=not (st.session_state.condition_true and st.session_state.condition_fake)):
            asyncio.run(generate_situation_a())
    
    with col2:
        if st.session_state.situation_a:
            st.success("✅ 已生成")
        elif st.session_state.condition_true and st.session_state.condition_fake:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成条件")
    
    display_json_content(st.session_state.situation_a, "情境A")
    
    st.markdown("---")
    
    # 第七步：生成情境A选项
    st.header("7️⃣ 生成情境A选项")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎯 生成情境A选项", key="step7", disabled=not st.session_state.situation_a):
            asyncio.run(generate_situation_a_options())
    
    with col2:
        if st.session_state.situation_a_options:
            st.success("✅ 已生成")
        elif st.session_state.situation_a:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成情境A")
    
    display_json_content(st.session_state.situation_a_options, "情境A选项")
    
    # 第八步：情境A选择
    if st.session_state.situation_a_options and not st.session_state.situation_a_result:
        st.header("8️⃣ 情境A选择")
        choice = render_choice_interface(st.session_state.situation_a_options, "situation_a", "情境A")
        if choice:
            asyncio.run(make_choice_for_situation_a(choice))
            st.rerun()
    
    if st.session_state.situation_a_options_choice:
        st.subheader("✅ 情境A选择")
        if isinstance(st.session_state.situation_a_options_choice, dict):
            st.json(st.session_state.situation_a_options_choice)
        else:
            st.write(st.session_state.situation_a_options_choice)
        display_json_content(st.session_state.situation_a_result, "情境A结果")
    
    st.markdown("---")
    
    # 第九步：生成情境B
    if st.session_state.situation_a_result:
        st.header("9️⃣ 生成情境B")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎬 生成情境B", key="step9", disabled=not st.session_state.situation_a_result):
                asyncio.run(generate_situation_b())
        
        with col2:
            if st.session_state.situation_b:
                st.success("✅ 已生成")
            elif st.session_state.situation_a_result:
                st.info("⏳ 可以生成")
        
        display_json_content(st.session_state.situation_b, "情境B")
    
    # 第十步：生成情境B选项
    if st.session_state.situation_b:
        st.header("🔟 生成情境B选项")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎯 生成情境B选项", key="step10", disabled=not st.session_state.situation_b):
                asyncio.run(generate_situation_b_options())
        
        with col2:
            if st.session_state.situation_b_options:
                st.success("✅ 已生成")
            elif st.session_state.situation_b:
                st.info("⏳ 可以生成")
        
        display_json_content(st.session_state.situation_b_options, "情境B选项")
        
        # 情境B选择
        if st.session_state.situation_b_options and not st.session_state.situation_b_result:
            st.header("1️⃣1️⃣ 情境B选择")
            choice = render_choice_interface(st.session_state.situation_b_options, "situation_b", "情境B")
            if choice:
                asyncio.run(make_choice_for_situation_b(choice))
                st.rerun()
        
        if st.session_state.situation_b_options_choice:
            st.subheader("✅ 情境B选择")
            if isinstance(st.session_state.situation_b_options_choice, dict):
                st.json(st.session_state.situation_b_options_choice)
            else:
                st.write(st.session_state.situation_b_options_choice)
            display_json_content(st.session_state.situation_b_result, "情境B结果")
    
    # 第十二步：生成情境C
    if st.session_state.situation_b_result:
        st.header("1️⃣2️⃣ 生成情境C")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎬 生成情境C", key="step12", disabled=not st.session_state.situation_b_result):
                asyncio.run(generate_situation_c())
        
        with col2:
            if st.session_state.situation_c:
                st.success("✅ 已生成")
            elif st.session_state.situation_b_result:
                st.info("⏳ 可以生成")
        
        display_json_content(st.session_state.situation_c, "情境C")
    
    # 第十三步：生成情境C选项
    if st.session_state.situation_c:
        st.header("1️⃣3️⃣ 生成情境C选项")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎯 生成情境C选项", key="step13", disabled=not st.session_state.situation_c):
                asyncio.run(generate_situation_c_options())
        
        with col2:
            if st.session_state.situation_c_options:
                st.success("✅ 已生成")
            elif st.session_state.situation_c:
                st.info("⏳ 可以生成")
        
        display_json_content(st.session_state.situation_c_options, "情境C选项")
        
        # 情境C选择
        if st.session_state.situation_c_options and not st.session_state.situation_c_result:
            st.header("1️⃣4️⃣ 情境C选择")
            choice = render_choice_interface(st.session_state.situation_c_options, "situation_c", "情境C")
            if choice:
                asyncio.run(make_choice_for_situation_c(choice))
                st.rerun()
        
        if st.session_state.situation_c_options_choice:
            st.subheader("✅ 情境C选择")
            if isinstance(st.session_state.situation_c_options_choice, dict):
                st.json(st.session_state.situation_c_options_choice)
            else:
                st.write(st.session_state.situation_c_options_choice)
            display_json_content(st.session_state.situation_c_result, "情境C结果")
    
    # 第十五步：生成结局
    if st.session_state.situation_c_result:
        st.header("1️⃣5️⃣ 生成故事结局")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎊 生成故事结局", key="step15", disabled=not st.session_state.situation_c_result):
                asyncio.run(generate_ending())
        
        with col2:
            if st.session_state.ending:
                st.success("✅ 已生成")
            elif st.session_state.situation_c_result:
                st.info("⏳ 可以生成")
        
        display_json_content(st.session_state.ending, "故事结局")
    
    st.markdown("---")
    
    # 最终结果展示
    if st.session_state.ending:
        st.header("🎉 完整故事")
        with st.expander("查看完整生成数据", expanded=False):
            final_data = {
                'personality': st.session_state.personality['personality'] if st.session_state.personality else None,
                'theme': st.session_state.theme['theme'] if st.session_state.theme else None,
                'background': st.session_state.background['background'] if st.session_state.background else None,
                'character': st.session_state.character,
                'dream_true': st.session_state.dream_true['dream'] if st.session_state.dream_true else None,
                'dream_fake': st.session_state.dream_fake['dream'] if st.session_state.dream_fake else None,
                'condition_true': st.session_state.condition_true['condition'] if st.session_state.condition_true else None,
                'condition_fake': st.session_state.condition_fake['condition'] if st.session_state.condition_fake else None,
                'situation_a': st.session_state.situation_a['description'] if st.session_state.situation_a else None,
                'situation_a_choice': st.session_state.situation_a_options_choice,
                'situation_a_result': st.session_state.situation_a_result['result'] if st.session_state.situation_a_result else None,
                'situation_b': st.session_state.situation_b['description'] if st.session_state.situation_b else None,
                'situation_b_choice': st.session_state.situation_b_options_choice,
                'situation_b_result': st.session_state.situation_b_result['result'] if st.session_state.situation_b_result else None,
                'situation_c': st.session_state.situation_c['description'] if st.session_state.situation_c else None,
                'situation_c_choice': st.session_state.situation_c_options_choice,
                'situation_c_result': st.session_state.situation_c_result['result'] if st.session_state.situation_c_result else None,
                'ending': st.session_state.ending['ending'] if st.session_state.ending else None,
            }
            st.json(final_data)
    
    # 重置按钮
    st.sidebar.header("🔄 操作")
    if st.sidebar.button("🗑️ 重置所有数据"):
        session_vars = [
            'personality', 'theme', 'background', 'character', 'dream_true', 'dream_fake',
            'condition_true', 'condition_fake', 'situation_a', 'situation_a_options',
            'situation_a_options_choice', 'situation_a_result', 'situation_b', 
            'situation_b_options', 'situation_b_options_choice', 'situation_b_result',
            'situation_c', 'situation_c_options', 'situation_c_options_choice', 
            'situation_c_result', 'ending'
        ]
        for key in session_vars:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()
