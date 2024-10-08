import os
import logging
import uuid
import subprocess
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, render_template_string, url_for

app = Flask(__name__)

logging.basicConfig(filename='log/app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

IMAGE_LIST = os.environ.get("IMAGE_LIST", ".png, .jpg, .jpeg")

LANGUAGE = os.environ.get("LANGUAGE", "chi_sim+eng")


# 定义一个路由，指定支持的请求方法为GET
@app.route('/')
def upload():
    # 渲染上传页面
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='static/favicon.ico')


# 定义一个路由，指定支持的请求方法为POST
@app.route('/ocr', methods=['POST'])
def ocr_main():
    uploaded_file = request.files.get('file', None)
    file_name = uploaded_file.filename
    image_extensions = tuple(ext.strip() for ext in IMAGE_LIST.split(','))
    if not file_name.lower().endswith(image_extensions):
        return "请上传图片"
    ocr_status, ocr_result = exec_ocr(uploaded_file)
    if not ocr_status:
        return ocr_result
    else:
        html_content = render_xml(ocr_result)
        return render_template_string(html_content)


def exec_ocr(png_file):
    file_name = f"{uuid.uuid4()}.png"  # 可以改为 .jpg
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    # 确保 data 目录存在
    os.makedirs(data_dir, exist_ok=True)

    # 文件保存路径
    file_path = os.path.join(data_dir, file_name)
    with open(file_path, 'wb') as f:
        f.write(png_file.read())  # 这里可以写入你想要保存的内容
    app.logger.info(f'文件路径:{file_path}')
    command = ["tesseract", file_path, "-", "-l", LANGUAGE, "hocr"]
    try:
        # 执行命令并获取输出
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return True, result.stdout  # 返回标准输出
    except subprocess.CalledProcessError as e:
        app.logger.error(f"错误: {e.stderr}")  # 打印错误信息
        return False, "ocr识别错误"


def render_xml(xml_content):
    app.logger.info(f'xml内容:\n{xml_content}')
    root = ET.fromstring(xml_content)
    html_content = ET.tostring(root, encoding='unicode', method='html')
    app.logger.info(f'html内容:\n{html_content}')
    return html_content


if __name__ == '__main__':
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5001)
