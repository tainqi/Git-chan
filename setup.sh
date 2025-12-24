#!/bin/bash
# Git-Chan 安装脚本

echo "正在安装 Git-Chan 电子宠物..."

# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装Python依赖
sudo apt install -y python3 python3-pip python3-venv git

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python包
pip install flask

# 安装Live2D模型 (示例模型)
echo "正在下载Live2D模型..."
cd static
mkdir -p models
cd models

# 下载免费的Live2D模型
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28.json -O git-chan.model.json
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28/28.physics.json
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28/28.moc3
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28/28.png
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28/28.mtn
wget https://raw.githubusercontent.com/alg-wiki/AzurLaneL2DViewer/master/model/28/expressions.json

cd ../..

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python app.py
EOF

chmod +x start.sh

# 创建systemd服务
sudo cat > /etc/systemd/system/git-chan.service << EOF
[Unit]
Description=Git-Chan Web Pet
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable git-chan
sudo systemctl start git-chan

echo "安装完成！"
echo "Git-Chan 已启动，访问 http://树莓派IP:5000"
echo ""
echo "管理命令:"
echo "启动服务: sudo systemctl start git-chan"
echo "停止服务: sudo systemctl stop git-chan"
echo "查看状态: sudo systemctl status git-chan"
echo "查看日志: sudo journalctl -u git-chan -f"
