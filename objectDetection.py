# Thư viện sử dụng
import os
import torch
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Load YOLO model -> Sẽ thực hiện tải về và lưu vào .cache
model = torch.hub.load('ultralytics/yolov5', 'yolov5m', pretrained="true") #'yolov5m' - small, medium

# Hàm tìm ảnh đầu tiên có trong folder
def getFirstImagePath(folder_path):
    # Danh sách các phần mở rộng
    image_extensions = ['.png', '.jpg', '.jpeg']
    
    # Lấy danh sách tất cả các file trong thư mục
    files = os.listdir(folder_path)
    
    # Tìm file ảnh đầu tiên
    for file in files:
        if os.path.splitext(file)[1].lower() in image_extensions:
            return os.path.join(folder_path, file)
    
    return None  # Không tìm thấy ảnh

# Hàm xóa tất cả các tập tin trong thư mục
def clrFolder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Hàm resize image sử dụng cv2
def resizeImagecv2(image_path, size=(800, 600)):
    # Đọc ảnh từ file
    img = cv2.imread(image_path)
    
    # Thay đổi kích thước ảnh
    resized_img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    # Lưu ảnh đã thay đổi kích thước
    cv2.imwrite(image_path, resized_img)

# Định nghĩa route tới index.html
@app.route('/')
def index():
    return render_template('index.html')

# Định nghĩa route khi một file được upload lên, phương thức sử dụng là HTTP POST
@app.route('/upload', methods=['POST'])
# Hàm này được gọi khi có yêu cầu POST tới URL '/upload'
def upload_file():
    # Kiểm tra có tệp được tải lên không
    if 'file' not in request.files:
        return redirect(request.url)
    # Kiểm tra xem người dùng có tải file hợp lệ không
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    # Nếu có file ảnh
    if file:
        # Đảm bảo tính an toàn khi thực hiện upload file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath) # png
        
        # Xóa tất cả file trong folder result
        clrFolder(app.config['RESULT_FOLDER'])

        # Thực hiện phát hiện đối tượng trong ảnh
        results = model(filepath)
        # Lưu kết quả vào thư mục mong muốn
        results.save(save_dir=app.config['RESULT_FOLDER'], exist_ok=True) # jpg

        # Xóa tất cả file trong folder upload
        clrFolder(app.config['UPLOAD_FOLDER'])

        # Lấy ảnh đầu tiên
        result_img_path = getFirstImagePath(app.config['RESULT_FOLDER'])
        # Sửa size
        resizeImagecv2(result_img_path, size=(800, 600))
        # Render
        return render_template('index.html', result_img=result_img_path)

# Main
if __name__ == '__main__':
    app.run(debug=True)