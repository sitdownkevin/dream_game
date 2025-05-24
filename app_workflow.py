import streamlit as st
import asyncio
import json
from llm.role.CharacLLM import CharacLLM
from llm.story.BackgroundLLM import BackgroundLLM
from llm.story.DreamLLM import DreamLLM
from llm.story.ConditionLLM import ConditionLLM
from llm.story.ThemeLLM import ThemeLLM
from llm.role.SoulLLM import SoulLLM
from llm.scene.SituationALLM import SituationALLM
from llm.scene.SituationAOptLLM import SituationAOptLLM


def init_session_state():
    """初始化 session state"""
    if 'soul' not in st.session_state:
        st.session_state.soul = None
    if 'theme' not in st.session_state:
        st.session_state.theme = None
    if 'background' not in st.session_state:
        st.session_state.background = None
    if 'character' not in st.session_state:
        st.session_state.character = None
    if 'dream_true' not in st.session_state:
        st.session_state.dream_true = None
    if 'dream_fake' not in st.session_state:
        st.session_state.dream_fake = None
    if 'condition_true' not in st.session_state:
        st.session_state.condition_true = None
    if 'condition_fake' not in st.session_state:
        st.session_state.condition_fake = None
    if 'situation' not in st.session_state:
        st.session_state.situation = None
    if 'situation_options' not in st.session_state:
        st.session_state.situation_options = None


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


async def generate_soul_and_theme():
    """生成灵魂和主题"""
    soul_llm = SoulLLM()
    theme_llm = ThemeLLM()
    
    with st.spinner("正在生成灵魂和主题..."):
        tasks = [
            soul_llm.arun(),
            theme_llm.arun(),
        ]
        soul, theme = await asyncio.gather(*tasks)
        
        st.session_state.soul = soul
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
            type='true',
            theme=st.session_state.theme,
            background=st.session_state.background,
            character=st.session_state.character
        )
        st.session_state.dream_true = dream_true
    
    with st.spinner("正在生成虚假梦境..."):
        dream_fake = await dream_llm.arun(
            type='fake',
            theme=st.session_state.theme,
            background=st.session_state.background,
            character=st.session_state.character,
            dream_true=dream_true
        )
        st.session_state.dream_fake = dream_fake
        st.success("梦境生成完成！")


async def generate_conditions():
    """生成条件"""
    condition_llm = ConditionLLM()
    
    with st.spinner("正在生成条件..."):
        tasks = [
            condition_llm.arun(
                type='true',
                theme=st.session_state.theme,
                background=st.session_state.background,
                character=st.session_state.character,
                dream=st.session_state.dream_true
            ),
            condition_llm.arun(
                type='fake',
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


async def generate_situation():
    """生成情境"""
    situation_llm = SituationALLM()
    
    with st.spinner("正在生成情境..."):
        situation = await situation_llm.arun(
            theme=st.session_state.theme['theme'],
            soul=st.session_state.soul['soul'],
            background=st.session_state.background['background'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
        )
        st.session_state.situation = situation
        st.success("情境生成完成！")


async def generate_situation_options():
    """生成情境选项"""
    situation_aopt_llm = SituationAOptLLM()
    
    with st.spinner("正在生成情境选项..."):
        situation_options = await situation_aopt_llm.arun(
            soul=st.session_state.soul['soul'],
            theme=st.session_state.theme['theme'],
            background=st.session_state.background['background'],
            character=st.session_state.character,
            dream_true=st.session_state.dream_true['dream'],
            dream_fake=st.session_state.dream_fake['dream'],
            condition_true=st.session_state.condition_true['condition'],
            condition_fake=st.session_state.condition_fake['condition'],
            current_situation_description=st.session_state.situation['description'],
        )
        st.session_state.situation_options = situation_options
        st.success("情境选项生成完成！")


def main():
    st.set_page_config(
        page_title="故事生成工作流",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 故事生成工作流")
    st.markdown("---")
    
    # 初始化 session state
    init_session_state()
    
    # 第一步：生成灵魂和主题
    st.header("1️⃣ 生成灵魂和主题")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎭 生成灵魂和主题", key="step1"):
            asyncio.run(generate_soul_and_theme())
    
    with col2:
        if st.session_state.soul and st.session_state.theme:
            st.success("✅ 已生成")
        else:
            st.info("⏳ 等待生成")
    
    # 显示结果
    col1, col2 = st.columns(2)
    with col1:
        display_json_content(st.session_state.soul, "灵魂")
    with col2:
        display_json_content(st.session_state.theme, "主题")
    
    st.markdown("---")
    
    # 第二步：生成背景
    st.header("2️⃣ 生成背景")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🌍 生成背景", key="step2", disabled=not (st.session_state.soul and st.session_state.theme)):
            asyncio.run(generate_background())
    
    with col2:
        if st.session_state.background:
            st.success("✅ 已生成")
        elif st.session_state.soul and st.session_state.theme:
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
        display_json_content(st.session_state.dream_fake, "虚假梦境")
    
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
        display_json_content(st.session_state.condition_fake, "虚假条件")
    
    st.markdown("---")
    
    # 第六步：生成情境
    st.header("6️⃣ 生成情境")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎬 生成情境", key="step6", disabled=not (st.session_state.condition_true and st.session_state.condition_fake)):
            asyncio.run(generate_situation())
    
    with col2:
        if st.session_state.situation:
            st.success("✅ 已生成")
        elif st.session_state.condition_true and st.session_state.condition_fake:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成条件")
    
    display_json_content(st.session_state.situation, "情境")
    
    st.markdown("---")
    
    # 第七步：生成情境选项
    st.header("7️⃣ 生成情境选项")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🎯 生成情境选项", key="step7", disabled=not st.session_state.situation):
            asyncio.run(generate_situation_options())
    
    with col2:
        if st.session_state.situation_options:
            st.success("✅ 已生成")
        elif st.session_state.situation:
            st.info("⏳ 可以生成")
        else:
            st.warning("⚠️ 需要先生成情境")
    
    display_json_content(st.session_state.situation_options, "情境选项")
    
    st.markdown("---")
    
    # 最终结果展示
    if st.session_state.situation_options:
        st.header("🎉 完整结果")
        with st.expander("查看完整生成数据", expanded=False):
            final_data = {
                'soul': st.session_state.soul['soul'] if st.session_state.soul else None,
                'theme': st.session_state.theme['theme'] if st.session_state.theme else None,
                'background': st.session_state.background['background'] if st.session_state.background else None,
                'character': st.session_state.character,
                'dream_true': st.session_state.dream_true['dream'] if st.session_state.dream_true else None,
                'dream_fake': st.session_state.dream_fake['dream'] if st.session_state.dream_fake else None,
                'condition_true': st.session_state.condition_true['condition'] if st.session_state.condition_true else None,
                'condition_fake': st.session_state.condition_fake['condition'] if st.session_state.condition_fake else None,
                'situation': st.session_state.situation['description'] if st.session_state.situation else None,
                'situation_options': st.session_state.situation_options,
            }
            st.json(final_data)
    
    # 重置按钮
    st.sidebar.header("🔄 操作")
    if st.sidebar.button("🗑️ 重置所有数据"):
        for key in ['soul', 'theme', 'background', 'character', 'dream_true', 'dream_fake', 
                   'condition_true', 'condition_fake', 'situation', 'situation_options']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()
