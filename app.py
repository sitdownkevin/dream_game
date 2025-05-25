from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import asyncio
import json
import threading
import uuid
from workflow import Workflow
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储游戏会话
game_sessions = {}

@app.route('/')
def index():
    """游戏主页"""
    return render_template('index.html')

@app.route('/start_game')
def start_game():
    """开始新游戏"""
    game_id = str(uuid.uuid4())
    session['game_id'] = game_id
    game_sessions[game_id] = {
        'workflow': Workflow(verbose=False),
        'stage': 'initial',
        'data': {}
    }
    return redirect(url_for('game_stage', stage='loading'))

@app.route('/game/<stage>')
def game_stage(stage):
    """游戏各阶段页面"""
    game_id = session.get('game_id')
    if not game_id or game_id not in game_sessions:
        return redirect(url_for('index'))
    
    game_session = game_sessions[game_id]
    
    if stage == 'loading':
        return render_template('loading.html')
    elif stage == 'choice_a':
        return render_template('choice.html', 
                             stage='A',
                             situation=game_session['data'].get('situation_a'),
                             options=game_session['data'].get('situation_a_options'))
    elif stage == 'choice_b':
        return render_template('choice.html', 
                             stage='B',
                             situation=game_session['data'].get('situation_b'),
                             options=game_session['data'].get('situation_b_options'))
    elif stage == 'choice_c':
        return render_template('choice.html', 
                             stage='C',
                             situation=game_session['data'].get('situation_c'),
                             options=game_session['data'].get('situation_c_options'))
    elif stage == 'ending':
        return render_template('ending.html', 
                             data=game_session['data'])
    else:
        return redirect(url_for('index'))

@socketio.on('start_generation')
def handle_start_generation():
    """开始生成游戏内容"""
    game_id = session.get('game_id')
    if not game_id or game_id not in game_sessions:
        emit('error', {'message': '游戏会话不存在'})
        return
    
    # 在新线程中运行异步生成
    def run_generation():
        asyncio.run(generate_initial_content(game_id))
    
    thread = threading.Thread(target=run_generation)
    thread.start()

async def generate_initial_content(game_id):
    """生成初始游戏内容"""
    game_session = game_sessions[game_id]
    workflow = game_session['workflow']
    
    try:
        # 发送进度更新
        socketio.emit('progress_update', {'stage': '正在生成灵魂和主题...', 'progress': 10})
        await workflow.generate_personality_and_theme()
        
        socketio.emit('progress_update', {'stage': '正在生成背景故事...', 'progress': 20})
        await workflow.generate_background()
        
        socketio.emit('progress_update', {'stage': '正在生成角色...', 'progress': 30})
        await workflow.generate_character()
        
        socketio.emit('progress_update', {'stage': '正在生成梦境...', 'progress': 40})
        await workflow.generate_dreams()
        
        socketio.emit('progress_update', {'stage': '正在生成条件...', 'progress': 50})
        await workflow.generate_conditions()
        
        socketio.emit('progress_update', {'stage': '正在生成第一个情景...', 'progress': 60})
        await workflow.generate_situation()
        
        socketio.emit('progress_update', {'stage': '正在生成选项...', 'progress': 80})
        await workflow.generate_situation_options()
        
        # 更新游戏数据
        game_session['data'].update({
            'personality': workflow.personality,
            'theme': workflow.theme,
            'background': workflow.background,
            'character': workflow.character,
            'dream_true': workflow.dream_true,
            'dream_fake': workflow.dream_fake,
            'condition_true': workflow.condition_true,
            'condition_fake': workflow.condition_fake,
            'situation_a': workflow.situation_a,
            'situation_a_options': workflow.situation_a_options,
        })
        
        game_session['stage'] = 'choice_a'
        
        socketio.emit('progress_update', {'stage': '生成完成！', 'progress': 100})
        socketio.emit('generation_complete', {'redirect': '/game/choice_a'})
        
    except Exception as e:
        socketio.emit('error', {'message': f'生成过程中出现错误: {str(e)}'})

@app.route('/make_choice', methods=['POST'])
def make_choice():
    """处理玩家选择"""
    game_id = session.get('game_id')
    if not game_id or game_id not in game_sessions:
        return jsonify({'error': '游戏会话不存在'}), 400
    
    choice = request.json.get('choice')
    stage = request.json.get('stage')
    
    if not choice or not stage:
        return jsonify({'error': '无效的选择'}), 400
    
    # 在新线程中处理选择
    def process_choice():
        asyncio.run(handle_choice_async(game_id, choice, stage))
    
    thread = threading.Thread(target=process_choice)
    thread.start()
    
    return jsonify({'status': 'processing'})

async def handle_choice_async(game_id, choice, stage):
    """异步处理玩家选择"""
    game_session = game_sessions[game_id]
    workflow = game_session['workflow']
    
    try:
        if stage == 'A':
            await workflow.make_choice_for_situation(choice)
            await workflow.generate_situation_b()
            await workflow.generate_situation_b_options()
            
            game_session['data'].update({
                'situation_a_options_choice': workflow.situation_a_options_choice,
                'situation_a_result': workflow.situation_a_result,
                'situation_b': workflow.situation_b,
                'situation_b_options': workflow.situation_b_options,
            })
            
            socketio.emit('choice_processed', {'redirect': '/game/choice_b'})
            
        elif stage == 'B':
            await workflow.make_choice_for_situation_b(choice)
            await workflow.generate_situation_c()
            await workflow.generate_situation_c_options()
            
            game_session['data'].update({
                'situation_b_options_choice': workflow.situation_b_options_choice,
                'situation_b_result': workflow.situation_b_result,
                'situation_c': workflow.situation_c,
                'situation_c_options': workflow.situation_c_options,
            })
            
            socketio.emit('choice_processed', {'redirect': '/game/choice_c'})
            
        elif stage == 'C':
            await workflow.make_choice_for_situation_c(choice)
            await workflow.generate_ending()
            
            game_session['data'].update({
                'situation_c_options_choice': workflow.situation_c_options_choice,
                'situation_c_result': workflow.situation_c_result,
                'ending': workflow.ending,
            })
            
            socketio.emit('choice_processed', {'redirect': '/game/ending'})
            
    except Exception as e:
        socketio.emit('error', {'message': f'处理选择时出现错误: {str(e)}'})

@app.route('/restart')
def restart_game():
    """重新开始游戏"""
    game_id = session.get('game_id')
    if game_id and game_id in game_sessions:
        del game_sessions[game_id]
    session.pop('game_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 