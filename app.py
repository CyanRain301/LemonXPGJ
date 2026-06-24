from email import message
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from io import BytesIO
import os
from pathlib import Path
import shutil
import atexit
from datetime import datetime

# 创建工作目录
PICS_DIR = Path(__file__).parent / 'pics'
PICS_DIR.mkdir(exist_ok=True)

# 创建Flask应用实例
app = Flask(__name__)

@app.route('/pics/<filename>')
def serve_pics(filename):
    return send_from_directory('pics', filename)

# 路由：处理根路径的GET请求，返回前端页面
@app.route('/')
def index():
    return render_template('index.html')

# 路由：处理导入图片按钮点击的POST请求
@app.route('/import-image', methods=['POST'])
def importImage():
    if request.is_json:
        data = request.get_json()  # 获取JSON数据
        print(f"收到导入图片请求: {data.get('path')}")
        # 获取导入图片路径
        current_dir = Path(data.get('path'))
        imageList = []
        #记录同名文件列表与相应的目录位置
        sameNameFile = []
        # 遍历目录及子目录下所有文件
        for file in current_dir.rglob('*'):
            #判断文件是不是图片文件
            if file.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                # 判断同名文件
                if (file.name in imageList):
                    rel_path = file.relative_to(current_dir)
                    print(f"已忽略同名文件: {file.name}，位于子目录{str(rel_path)}")
                    sameNameFile.append({'fileName': file.name, 'relativePath': str(rel_path)})
                    continue
                # 将file名记录在imageList中
                imageList.append(file.name)
                # 拷贝到 pics, 转换为扁平目录
                dest = PICS_DIR / file.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
                print(f" 已拷贝: {file.name}")

        # 按字母顺序排序（）
        imageList.sort()

        # 返回响应
        reply = {
            'status': 'success',
            'imageList': imageList,
            'sameNameFile': sameNameFile
        }
        print('发送回信' + str(reply))
        return jsonify(reply)
    else:
        print(f"接收数据错误，非JSON格式")
        reply = {
            'status': 'error',
            'imageList': str()
        }
        return jsonify(reply), 400

#路由：处理前端发送的导出图片POST请求
@app.route('/export-image', methods=['POST'])
def exportImage():
    if request.is_json:
        data = request.get_json()
        img_stack = data.get('imgStack', [])
        imgPath = Path(data.get('imgPath'))
        matchCls = data.get('matchCls')
        print(f'收到导出图片请求，共 {len(img_stack)} 张图片，目标地址 {imgPath}')
        #将目标目录下的所有文件名都记录在destFile列表中
        destFile = []
        sameNameFile = []
        exportSuccessFile = []
        for file in imgPath.iterdir():
            destFile.append(file.name)
        for img in img_stack:
            filename = img.get('filename', 'unknown')
            cls = img.get('cls', 'unknown')
            for file in PICS_DIR.iterdir():
                if file.name == filename and cls == matchCls:
                    # 检测目标目录是否有同名文件
                    if file.name not in destFile:
                        shutil.copy2(file, imgPath / filename)
                        exportSuccessFile.append(file.name)
                    else:
                        print(f'已跳过同名文件: {filename}')
                        sameNameFile.append({'fileName': file.name})
        print(f'已在目录{imgPath}下导出 {len(exportSuccessFile)} 张图片')
        reply = {
            'status': 'success',
            'message': f'已在目录{imgPath}下导出 {len(exportSuccessFile)} 张图片',
            'sameNameFile': sameNameFile,
            'exportSuccessFile': exportSuccessFile
        }
        return jsonify(reply)
    else:
        print('接收数据错误，非JSON格式')
        reply = {
            'status': 'error',
        }
        return jsonify(reply), 400

# 路由：处理导出选片表按钮点击的POST请求
@app.route('/export-sheet', methods=['POST'])
def exportSheet():
    if request.is_json:
        data = request.get_json()
        img_stack = data.get('imgStack', [])    #img_stack是一个列表
        imgPath = data.get('imgPath')
        print(f"收到导出选片表请求，共 {len(img_stack)} 张图片")

        # 生成文本内容
        lines = []
        lines.append("[LEMON's PHOTO SELECT TOOL]")

        for img in img_stack:
            # img是一个只能get的字典类似物
            filename = img.get('filename', 'unknown')
            cls = img.get('cls', 'unknown')
            # 提取状态（去掉 'image-item-' 前缀）
            status = cls.replace('image-item-', '') if cls.startswith('image-item-') else cls
            lines.append(f"{filename}\t\t{status}")

        # 添加结束位置
        lines.append("[END]")
        lines.append(f'Images initially imported from {imgPath}')

        # 生成文本内容
        content = "\n".join(lines)
        print(f"生成文本内容:\n{content}")
        # 创建文件对象
        file_obj = BytesIO()
        file_obj.write(content.encode('utf-8'))
        file_obj.seek(0)  # 重置指针到开头

        # 发送文件
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=f'选片表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mimetype='text/plain'
        )
    else:
        print(f"接收数据错误")
        return jsonify({
            'status': 'error',
            'message': ''
        }), 400

def cleanup_pics():
    """程序退出时删除 pics 目录下的图片文件"""
    if PICS_DIR.exists():
        try:
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            deleted_count = 0

            for file in PICS_DIR.iterdir():
                if file.is_file() and file.suffix.lower() in image_extensions:
                    file.unlink()
                    deleted_count += 1

            print(f"已删除 {deleted_count} 个图片文件")
        except Exception as e:
            print(f"清理失败: {e}")

atexit.register(cleanup_pics)

# 启动服务器
if __name__ == '__main__':
    # 允许所有IP访问
    print(f"Lemon的选片工具启动")
    app.run(debug=True, host='0.0.0.0', port=5000)