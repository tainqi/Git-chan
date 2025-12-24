from flask import Flask, render_template, request, jsonify
import json
import os
import re
from datetime import datetime, timedelta
import random
import threading
import time

app = Flask(__name__)

# 宠物数据
class GitChanPet:
    def __init__(self):
        self.data_file = 'pet_data.json'
        self.load_data()
        
        # 启动后台状态更新线程
        self.update_thread = threading.Thread(target=self.background_update, daemon=True)
        self.update_thread.start()
    
    def load_data(self):
        default_data = {
            'name': 'Git-Chan',
            'hunger': 50,
            'happiness': 80,
            'energy': 70,
            'level': 1,
            'exp': 0,
            'total_fed': 0,
            'last_fed': None,
            'status': 'happy',
            'messages': ['你好！我是Git-Chan，用Git链接喂养我吧！🚀']
        }
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保所有字段都存在
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                return data
        except:
            return default_data
    
    def save_data(self, data):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def background_update(self):
        """后台自动更新状态"""
        while True:
            time.sleep(60)  # 每分钟更新一次
            data = self.load_data()
            
            # 随时间变化
            data['hunger'] = min(100, data['hunger'] + 0.5)
            data['energy'] = max(0, data['energy'] - 0.3)
            
            # 更新状态
            if data['hunger'] > 80:
                data['status'] = 'hungry'
            elif data['energy'] < 20:
                data['status'] = 'tired'
            elif data['happiness'] > 70:
                data['status'] = 'happy'
            else:
                data['status'] = 'normal'
            
            self.save_data(data)

pet = GitChanPet()

# Git链接验证
def validate_git_url(url):
    patterns = [
        r'^https?://github\.com/',
        r'^https?://gitlab\.com/',
        r'^https?://gitee\.com/',
        r'^https?://bitbucket\.org/',
        r'^git@',
        r'\.git$',
        r'github\.io',
        r'git',
    ]
    url_lower = url.lower()
    return any(re.search(pattern, url_lower) for pattern in patterns)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(pet.load_data())

@app.route('/api/feed', methods=['POST'])
def feed():
    data = pet.load_data()
    url = request.json.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'message': '请输入链接'})
    
    if not validate_git_url(url):
        return jsonify({'success': False, 'message': '请输入有效的Git链接'})
    
    # 计算喂养量
    feed_amount = min(25, len(url) // 4)
    feed_amount = max(5, feed_amount)
    
    # 更新状态
    data['hunger'] = max(0, data['hunger'] - feed_amount)
    data['happiness'] = min(100, data['happiness'] + 8)
    data['total_fed'] += 1
    data['last_fed'] = datetime.now().isoformat()
    data['exp'] += feed_amount
    
    # 升级检查
    if data['exp'] >= data['level'] * 100:
        data['level'] += 1
        data['exp'] = 0
        data['messages'].append(f'🎉 升级到 {data["level"]} 级！')
    
    # 随机消息
    messages = [
        f'🍴 感谢投喂！恢复了 {feed_amount} 点饥饿度',
        f'💾 链接 "{url[:30]}..." 很美味！',
        f'⚡ 获得 {feed_amount} 点能量！',
        f'❤️  这个仓库看起来不错！',
        f'🚀 继续用更多Git链接喂养我吧！'
    ]
    data['messages'].append(random.choice(messages))
    
    # 限制消息数量
    if len(data['messages']) > 8:
        data['messages'] = data['messages'][-8:]
    
    pet.save_data(data)
    
    return jsonify({
        'success': True,
        'message': data['messages'][-1],
        'feed_amount': feed_amount,
        'data': data
    })

@app.route('/api/play', methods=['POST'])
def play():
    data = pet.load_data()
    
    if data['energy'] > 15:
        data['happiness'] = min(100, data['happiness'] + 15)
        data['energy'] = max(0, data['energy'] - 15)
        data['messages'].append('🎮 玩得好开心！')
    else:
        data['messages'].append('😴 我有点累了...')
    
    pet.save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/sleep', methods=['POST'])
def sleep():
    data = pet.load_data()
    data['energy'] = min(100, data['energy'] + 40)
    data['messages'].append('💤 睡了个好觉！')
    pet.save_data(data)
    return jsonify({'success': True, 'data': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
