import time
import tkinter as tk
from tkinter.ttk import Progressbar
from pynput import keyboard
import threading
import cv2
import face_recognition
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import imutils
import shutil
import os
from tkinter import filedialog, messagebox
from tkinter import filedialog, simpledialog, ttk

# 获取当前脚本所在的目录
current_directory = os.path.dirname(__file__)

# 设置模型文件的路径
model_path = os.path.join(current_directory, 'models', 'shape_predictor_68_face_landmarks.dat')

# 确保 face_recognition 使用正确的路径
face_recognition.api.pose_predictor_68_point_model = model_path

#   加载已知面孔的编码
known_face_encodings = []
known_face_names = []

# 错误提示相关
error_displayed = False
error_start_time = 0

cap = None

# 存储已知的面孔编码和名字
known_face_encodings = []
known_face_names = []

# 定义图片所在的文件夹
IMAGE_DIR = "img\\"

def load_known_faces_thread():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    # 创建进度条窗口
    progress_window = tk.Toplevel(root)
    progress_window.title("加载进度")
    progress_window.geometry("300x100")
    tk.Label(progress_window, text="正在加载人脸，请稍候...").pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
    progress_bar.pack(pady=20)

    # 获取所有图片文件
    files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    num_files = len(files)
    progress_bar["maximum"] = num_files  # 设置进度条最大值

    students = {}

    # 遍历img文件夹下的所有图片文件
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):  # 检查文件是否是图片格式
            # 从文件名中提取学生姓名
            name_len = 0
            for ch in filename:
                if ch.isdigit():
                    break
                else:
                    name_len += 1

            name = filename[:name_len]  # 假设文件名格式为: name_imageX.ext
            if name not in students:
                students[name] = []
            students[name].append(filename)

    # 加载图片并提取人脸编码
    image_index = 0
    for name, image_paths in students.items():
        for img_path in image_paths:
            full_img_path = os.path.join(IMAGE_DIR, img_path)
            try:
                print(img_path)
                image = face_recognition.load_image_file(full_img_path)
                face_encodings = face_recognition.face_encodings(image)
                # 更新进度条
                image_index += 1
                progress_bar["value"] = image_index
                progress_window.update_idletasks()  # 刷新进度条

                if face_encodings:  # 确保识别到人脸
                    face_encoding = face_encodings[0]  # 获取第一张脸的编码
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(name)
                else:
                    print(f"未检测到人脸: {img_path}")

            except Exception as e:
                print(f"加载图片 {img_path} 时出错: {e}")

    # 完成后关闭进度条窗口
    progress_window.destroy()

def load_known_faces():
    load_thread = threading.Thread(target=load_known_faces_thread)
    load_thread.start()
def on_press(key):
    global alt_tab_pressed
    try:
        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            alt_tab_pressed = True
        elif key == keyboard.Key.tab and alt_tab_pressed:
            print("警告: 检测到 Alt+Tab 切屏操作！")
            alt_tab_pressed = False
    except AttributeError:
        pass


def on_release(key):
    global alt_tab_pressed
    if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        alt_tab_pressed = False


# 设置键盘监听器
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# 初始化主界面
root = Tk()
root.title("Face Recognition System")
root.geometry("860x450")
root.configure(bg='#2b3e50')

# 标签样式
title_label = Label(root, text="Face Recognition System", font=("Helvetica", 24, "bold"), bg='#2b3e50', fg='white')
title_label.pack(pady=20)

# 实时监控和图片识别按钮样式
button_frame = Frame(root, bg='#2b3e50')
button_frame.pack(pady=80)

# 加载已知人脸
load_known_faces()

def make_button(text, command):
    return Button(button_frame, text=text, font=("Helvetica", 14), width=15, height=2, bg='#3c6478', fg='white', relief='flat', command=command)

# 加载图片
def load_face():
    students = {}
    # 主窗口和UI组件
    root = tk.Tk()
    root.title("人脸识别加载器")
    root.geometry("440x440")


    # 窗口设置
    # 进度条和表格的相关代码
    # 设置主题
    style = ttk.Style()
    style.configure("Treeview",
                    background="#f0f0f0",
                    foreground="#000000",
                    rowheight=25,
                    fieldbackground="#f0f0f0")
    style.configure("Treeview.Heading",
                    background="#0078d4",
                    foreground="#ffffff",
                    font=("Arial", 12, "bold"))

    style.configure("TButton",
                    font=("Arial", 12),
                    background="#0078d4",
                    foreground="#ffffff",
                    padding=10)
    style.map("TButton",
              background=[('active', '#005a9e')],
              foreground=[('active', '#ffffff')])

    # 创建 Canvas 和 Frame
    canvas = tk.Canvas(root)
    canvas.grid(row=0, column=0, padx=(20, 0), pady=(20, 0), columnspan=2, sticky='nsew')

    tree_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=tree_frame, anchor='nw')

    # 创建表格
    tree = ttk.Treeview(tree_frame, columns=("Name", "Images"), show="headings", height=15)
    tree.heading("Name", text="Name")
    tree.heading("Images", text="Image Paths")
    tree.column("Name", width=150)  # 设置列宽
    tree.column("Images", width=900)  # 设置列宽
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 添加滚动条
    h_scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    h_scrollbar.grid(row=1, column=0, padx=20, pady=0, columnspan=2, sticky='ew')
    canvas.configure(xscrollcommand=h_scrollbar.set)

    v_scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    v_scrollbar.grid(row=0, column=2, padx=(0, 20), pady=(20, 0), sticky='ns')
    canvas.configure(yscrollcommand=v_scrollbar.set)

    def loadImage_load_known_faces_thread():

        # 创建进度条窗口
        progress_window = tk.Toplevel(root)
        progress_window.title("加载进度")
        progress_window.geometry("300x100")
        tk.Label(progress_window, text="正在加载人脸，请稍候...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
        progress_bar.pack(pady=20)

        # 获取所有图片文件
        files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        num_files = len(files)
        progress_bar["maximum"] = num_files  # 设置进度条最大值

        # 清空表格并重新加载数据
        for row in tree.get_children():
            tree.delete(row)

        students = {}

        # 每加载一个文件，更新进度条
        for i, filename in enumerate(files):
            name_len = 0
            for ch in filename:
                if ch.isdigit():
                    break
                else:
                    name_len += 1

            name = filename[0:name_len]  # 假设文件名格式为: name_imageX.ext
            if name not in students:
                students[name] = []
            students[name].append(filename)

        for name, image_paths in students.items():
            full_paths = [os.path.join(IMAGE_DIR, img_path) for img_path in image_paths]
            tree.insert("", "end", values=(name, ", ".join(full_paths)))
            # 更新进度条
            progress_bar["value"] = i + 1
            progress_window.update_idletasks()  # 刷新进度条

        # 完成后关闭进度条窗口
        progress_window.destroy()

        # 更新 Canvas 的大小
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # 将加载人脸的操作放入线程中
    def loadImage_load_known_faces():
        load_thread = threading.Thread(target=loadImage_load_known_faces_thread)
        load_thread.start()

    # 定义图片保存目录
    IMAGE_DIR = "img\\"
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # 上传新的人像并添加到表格
    def loadImage_add_new_face():
        name = simpledialog.askstring("输入名字", "请输入人名：")
        if not name:
            return

        file_paths = filedialog.askopenfilenames(title="选择图片", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_paths:
            return

        # 保存有效的人像到 img 目录下
        valid_file_paths = []
        for file_path in file_paths:
            try:
                image = face_recognition.load_image_file(file_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:  # 如果识别到至少一张脸
                    file_name = os.path.basename(file_path)
                    new_path = os.path.join(IMAGE_DIR, f"{file_name}")
                    shutil.copy(file_path, new_path)
                    valid_file_paths.append(new_path)
                else:
                    print(f"图片 {file_path} 中没有识别到人脸")
            except Exception as e:
                print(f"加载图片 {file_path} 时出错: {e}")

        if not valid_file_paths:
            messagebox.showinfo("信息", "没有识别到有效的人脸，操作被取消。")
            return

        # 更新表格
        full_paths = [os.path.join(IMAGE_DIR, os.path.basename(p)) for p in valid_file_paths]
        tree.insert("", "end", values=(name, ", ".join(full_paths)))

        # 保存到 students 字典并加载新的人脸
        if name in students:
            students[name].extend([os.path.basename(p) for p in valid_file_paths])
        else:
            students[name] = [os.path.basename(p) for p in valid_file_paths]

        for img_path in valid_file_paths:
            try:
                image = face_recognition.load_image_file(img_path)
                face_encoding = face_recognition.face_encodings(image)[0]  # 获取第一张脸的编码
                known_face_encodings.append(face_encoding)
                known_face_names.append(name)
                messagebox.showinfo("Result", "添加成功！")


            except Exception as e:
                print(f"加载图片 {img_path} 时出错: {e}")

        # 更新 Canvas 的大小
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # 创建按钮
    load_button = tk.Button(root, text="加载人像", command=loadImage_load_known_faces)
    load_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    add_face_button = tk.Button(root, text="添加人像", command=loadImage_add_new_face)
    add_face_button.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

    root.mainloop()

# 实时监控
def start_real_time_monitoring():
    global cap
    # 初始化摄像头
    if cap != None:
        cap.release()
        cv2.destroyAllWindows()
    cap = cv2.VideoCapture(0)

    # 创建新的窗口
    monitor_window = Toplevel(root)
    monitor_window.title("实时监控")
    monitor_window.geometry("600x400")

    # 在新窗口中创建一个 Label 组件用于显示监控画面
    monitor_label = Label(monitor_window)
    monitor_label.pack(fill='both', expand=True)

    def update_frame():
        ret, frame = cap.read()
        if not ret:
            return

        # 将图像从 BGR 转换为 RGB，减少蓝色偏色问题
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 使用 imutils 调整帧大小
        rgb_frame = imutils.resize(rgb_frame, width=600)

        # 转换为图像显示
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        monitor_label.imgtk = imgtk
        monitor_label.configure(image=imgtk)

        # 不断更新帧
        monitor_label.after(10, update_frame)

    update_frame()

# 人脸识别
def start_face_recognition():
    # 初始化摄像头
    cap = cv2.VideoCapture(0)

    # 错误提示相关
    error_displayed = False
    error_start_time = 0

    def process_frame(frame):
        global error_displayed, error_start_time

        # 将帧缩放到宽度为500像素
        frame = imutils.resize(frame, width=500)

        # 转换为 RGB 图像
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 检测面部
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
            name = "Unknown"

            # 如果找到匹配的面孔
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

        if len(face_locations) == 0:
            if not error_displayed or (time.time() - error_start_time > 5):
                error_displayed = True
                error_start_time = time.time()

                # 创建一个全黑的图像作为错误提示窗口
                error_message = "Don't leave the camera"
                error_frame = 255 * np.ones(shape=(200, 600, 3), dtype=np.uint8)

                # 将错误提示文本添加到图像上
                cv2.putText(error_frame, error_message, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2,
                            cv2.LINE_AA)

                # 显示错误提示窗口
                cv2.imshow("Error", error_frame)
        else:
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # 在检测到的人脸周围绘制一个矩形框
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                # 在矩形框上方绘制学生的名字
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # 显示实时视频
            cv2.imshow("Exam Monitoring", frame)

    def video_capture():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            process_frame(frame)

            # 检查是否点击了窗口右上角的叉叉
            if cv2.getWindowProperty('Exam Monitoring', cv2.WND_PROP_VISIBLE) < 1:
                break

            # 按 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # 使用线程处理视频捕获
    video_thread = threading.Thread(target=video_capture)
    video_thread.start()

# 图片识别
progress = None # 全局的进度条
def analyze_image_thread():
    global progress
    # 打开文件对话框，选择要分析的图像
    file_path = filedialog.askopenfilename()
    if file_path:
        # 加载所选图像并检测人脸
        image = face_recognition.load_image_file(file_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # 如果没有检测到任何人脸
        if len(face_locations) == 0:
            messagebox.showinfo("Result", "未检测到任何人脸")
        else:
            # 创建一个新的进度条窗口
            progress_window = tk.Toplevel()
            progress_window.title("Progress")
            progress = Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
            progress.pack(padx=10, pady=10)

            # 存储已检测到的人脸姓名
            face_names = []
            total_faces = len(face_encodings)  # 获取总的人脸数
            progress['maximum'] = total_faces  # 设置进度条的最大值

            for idx, face_encoding in enumerate(face_encodings):
                # 比较面部编码与已知面孔编码
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
                name = "Unknown"  # 默认识别不到姓名

                if True in matches:
                    # 找到第一个匹配的已知面孔
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                face_names.append(name)

                # 更新进度条
                progress['value'] = idx + 1  # 更新进度
                progress_window.update()  # 刷新窗口

                # 模拟耗时操作
                time.sleep(0.5)

            # 绘制矩形和姓名标签
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 关闭进度条窗口
            progress_window.destroy()

            # 将处理过的图像显示出来
            img = Image.fromarray(image)
            img.show()

def analyze_image():
    analyze_thread = threading.Thread(target=analyze_image_thread)
    analyze_thread.start()

# 实时监控按钮


real_time_button = make_button("实时监控", lambda: start_real_time_monitoring())
real_time_button.grid(row=0, column=0, padx=20)

# 人脸识别按钮
face_recognition_button = make_button("人脸识别", lambda: start_face_recognition())
face_recognition_button.grid(row=0, column=1, padx=20)

# 上传图片按钮
upload_image_button = make_button("图片识别", lambda: analyze_image())
upload_image_button.grid(row=0, column=2, padx=20)

# 加载人像按钮
load_face_button = make_button("加载人像", lambda: load_face())
load_face_button.grid(row=0, column=3, padx=20)

# 关闭按钮样式
quit_button = Button(root, text="退出", font=("Helvetica", 12), width=10, height=1, bg='#c44d61', fg='white', relief='flat', command=root.quit)
quit_button.pack(pady=20)

root.mainloop()
