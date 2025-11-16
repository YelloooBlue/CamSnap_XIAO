from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# 图片保存目录（自动创建）
SAVE_DIR = "Backend/files"
os.makedirs(SAVE_DIR, exist_ok=True)

# 允许的请求头和内容类型（适配 ESP32 直传）
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/jpg"]

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        # 1. 验证请求内容类型（必须是 JPEG 二进制数据）
        content_type = request.content_type
        if content_type not in ALLOWED_CONTENT_TYPES:
            return jsonify({
                "status": "error",
                "message": f"不支持的内容类型：{content_type}，仅允许 {ALLOWED_CONTENT_TYPES}"
            }), 415  # 415 = 不支持的媒体类型

        # 2. 读取二进制图片数据（ESP32 直接 POST 的 fb->buf 数据）
        image_data = request.data
        if not image_data:
            return jsonify({"status": "error", "message": "未接收到图片数据"}), 400

        # 3. 生成唯一文件名（时间戳+jpg后缀，避免覆盖）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # 精确到微秒，确保唯一
        save_filename = f"esp32_capture_{timestamp}.jpg"
        save_path = os.path.join(SAVE_DIR, save_filename)

        # 4. 写入文件（二进制模式保存 JPEG）
        with open(save_path, "wb") as f:
            f.write(image_data)

        app.logger.info(f"图片保存成功：{save_path}（大小：{len(image_data)} 字节）")

        # 5. 返回成功响应（ESP32 可解析 status 判断结果）
        return jsonify({
            "status": "success",
            "message": "图片上传成功",
            "filename": save_filename,
            "file_size": len(image_data)
        }), 200

    except Exception as e:
        app.logger.error(f"上传失败：{str(e)}")
        return jsonify({
            "status": "error",
            "message": f"服务器错误：{str(e)}"
        }), 500

if __name__ == "__main__":
    # 运行服务：允许局域网访问（ESP32 需和电脑在同一WiFi）
    app.run(host="0.0.0.0", port=8501, debug=False)  # 生产环境关闭 debug