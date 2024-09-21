import random  # 导入随机数生成模块
import traceback  # 导入追踪错误的模块
import os  # 导入操作系统相关模块
import requests  # 导入发送HTTP请求的模块
import base64  # 导入base64编码模块
import tkinter as tk  # 导入tkinter模块用于创建GUI
from tkinter import messagebox, font  # 导入消息框和字体模块
import pyperclip  # 新增导入，用于操作剪切板

# 从文件中加载字符集
def load_characters_from_file(dir_path, file_name):
    try:
        # 构建文件路径
        file_path = os.path.join(dir_path, 'char_set', file_name)
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            characters = file.read().strip()  # 去除两端空白
        return characters  # 返回字符集
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在。")  # 文件未找到的错误提示
        return None  # 返回None表示加载失败
    except Exception as e:
        print(f"错误：读取文件 {file_path} 时发生错误。错误信息：{e}")  # 其他错误的提示
        return None  # 返回None表示加载失败

# 生成密码
def generate_password(length, characters):
    # 检查字符集是否有效
    if not characters or all(not char for char in characters.values()):
        print("错误：没有有效的字符集来生成密码。")  # 如果没有有效字符集
        return None  # 返回None表示生成失败
    password_list = []  # 存储生成的密码字符
    num_sets = len(characters)  # 字符集的数量
    set_length = length // num_sets  # 每个字符集应包含的字符数量
    for key, char_set in characters.items():
        if char_set:  # 如果字符集非空
            chosen_char = random.choice(char_set)  # 随机选择一个字符
            password_list.append(chosen_char)  # 添加到密码列表中
            if len(password_list) < length:  # 检查是否已达到所需长度
                # 添加其余字符
                password_list.extend([random.choice(char_set) for _ in range(set_length - 1)])
    # 如果密码长度仍不足
    while len(password_list) < length:
        for key, char_set in characters.items():
            if char_set:
                password_list.append(random.choice(char_set))  # 添加随机字符
                if len(password_list) == length:  # 达到所需长度后退出
                    break
    random.shuffle(password_list)  # 打乱密码列表
    return ''.join(password_list)  # 返回生成的密码

# 将密码保存到Markdown文件
def save_password_to_md(name, password):
    if not password:  # 检查密码是否为空
        print("错误：没有密码可以保存。")  # 提示信息
        return  # 返回
    try:
        with open('password.md', 'a', encoding='utf-8') as file:  # 以追加模式打开文件
            file.write(f'# {name}\n')  # 写入密码名称
            file.write(f'```\n{password}\n```\n\n')  # 写入密码内容
    except Exception as e:
        print(f"错误：写入文件 password.md 时发生错误。错误信息：{e}")  # 写入文件时的错误提示

# 备份文件到GitHub
def backup_to_github(file_path, commit_message, token, repo, branch):
    # 检查GitHub配置是否完整
    if not all([token, repo, branch]):
        print("错误：GitHub 配置信息不完整。")  # 提示信息
        return None  # 返回None表示备份失败

    with open(file_path, 'rb') as f:  # 以二进制模式打开文件
        file_content = base64.b64encode(f.read()).decode('utf-8')  # 读取文件并进行base64编码

    # GitHub API URL
    api_url = f"https://api.github.com/repos/{repo}/contents/{os.path.basename(file_path)}"
    headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json'}  # 设置请求头

    response = requests.get(api_url, headers=headers)  # 获取文件信息
    if response.status_code == 200:  # 如果文件已存在
        file_data = response.json()  # 获取文件信息
        payload = {  # 准备更新文件的payload
            'branch': branch,
            'message': commit_message,
            'content': file_content,
            'sha': file_data['sha']  # 文件的SHA值
        }
    else:  # 如果文件不存在
        payload = {  # 准备创建文件的payload
            'branch': branch,
            'message': commit_message,
            'content': file_content,
            'path': os.path.basename(file_path)  # 文件名
        }

    response = requests.put(api_url, json=payload, headers=headers)  # 发送请求更新或创建文件
    return response  # 返回请求响应

# 处理生成密码的逻辑
def on_generate():
    # 从输入框获取值
    name = entry_name.get()
    length_str = entry_length.get()
    token = entry_token.get()
    repo = entry_repo.get()
    branch = entry_branch.get()

    try:
        length = int(length_str)  # 将输入的长度转换为整数
    except ValueError:
        messagebox.showerror("输入错误", "长度必须是一个整数。")  # 提示输入错误
        return  # 返回

    # 加载字符集
    characters = {
        'uppercase': load_characters_from_file(dir_path, 'uppercase.txt'),
        'lowercase': load_characters_from_file(dir_path, 'lowercase.txt'),
        'symbols': load_characters_from_file(dir_path, 'symbols.txt'),
        'chinese': load_characters_from_file(dir_path, 'chinese.txt'),
        'tibetan': load_characters_from_file(dir_path, 'tibetan.txt')
    }

    if None in characters.values():  # 检查字符集是否加载成功
        messagebox.showerror("加载错误", "某些字符集未能加载。")  # 提示加载错误
        return  # 返回

    # 获取用户选择的字符集
    selected_characters = {
        'uppercase': var_uppercase.get(),
        'lowercase': var_lowercase.get(),
        'symbols': var_symbols.get(),
        'chinese': var_chinese.get(),
        'tibetan': var_tibetan.get()
    }

    # 更新选中的字符集
    for key in selected_characters.keys():
        selected_characters[key] = characters[key] if selected_characters[key] else ''

    password = generate_password(length, selected_characters)  # 生成密码

    if password:  # 如果生成成功
        save_password_to_md(name, password)  # 保存密码

        # 复制密码到剪切板
        pyperclip.copy(f"# {name}\n```\n{password}\n```\n")  # 复制密码格式化文本
        copy_message = "成功复制到剪切板。"  # 复制成功提示

        message = f"密码 '{name}' 已成功保存到 'password.md'。{copy_message}"  # 成功消息

        if var_backup_to_github.get():  # 如果选中备份到GitHub
            response = backup_to_github('password.md', f'Add password entry for {name}', token, repo, branch)
            if response and response.status_code == 200:  # 检查备份是否成功
                message += "\n并成功备份至GitHub。"  # 备份成功提示
            else:
                message += "\n备份至GitHub失败。"  # 备份失败提示
        messagebox.showinfo("成功", message)  # 显示成功消息
    else:
        messagebox.showerror("生成错误", "未能生成密码。")  # 提示生成密码失败

# 主程序入口
def main():
    global dir_path, entry_name, entry_length, entry_token, entry_repo, entry_branch
    global var_uppercase, var_lowercase, var_symbols, var_chinese, var_tibetan, var_backup_to_github

    dir_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件目录

    root = tk.Tk()  # 创建主窗口
    root.title("密码生成器")  # 设置窗口标题
    root.geometry("400x500")  # 设置窗口大小
    root.configure(bg="#f0f0f0")  # 设置背景颜色

    title_font = font.Font(size=16, weight="bold")  # 设置标题字体
    tk.Label(root, text="密码生成器", font=title_font, bg="#f0f0f0").pack(pady=10)  # 显示标题标签

    frame = tk.Frame(root, bg="#f0f0f0")  # 创建框架
    frame.pack(pady=10)  # 添加到主窗口

    # 创建输入框和标签
    tk.Label(frame, text="密码名字:", bg="#f0f0f0").grid(row=0, column=0, padx=10)
    entry_name = tk.Entry(frame)  # 密码名字输入框
    entry_name.grid(row=0, column=1, padx=10)

    tk.Label(frame, text="密码长度:", bg="#f0f0f0").grid(row=1, column=0, padx=10)
    entry_length = tk.Entry(frame)  # 密码长度输入框
    entry_length.grid(row=1, column=1, padx=10)

    tk.Label(frame, text="GitHub Token:", bg="#f0f0f0").grid(row=2, column=0, padx=10)
    entry_token = tk.Entry(frame)  # GitHub Token输入框
    entry_token.grid(row=2, column=1, padx=10)

    tk.Label(frame, text="GitHub Repo:", bg="#f0f0f0").grid(row=3, column=0, padx=10)
    entry_repo = tk.Entry(frame)  # GitHub Repo输入框
    entry_repo.grid(row=3, column=1, padx=10)

    tk.Label(frame, text="GitHub Branch:", bg="#f0f0f0").grid(row=4, column=0, padx=10)
    entry_branch = tk.Entry(frame)  # GitHub Branch输入框
    entry_branch.grid(row=4, column=1, padx=10)

    # 创建复选框选项
    var_uppercase = tk.BooleanVar()
    tk.Checkbutton(frame, text="包含大写字母", variable=var_uppercase, bg="#f0f0f0").grid(row=5, columnspan=2, sticky='w', padx=10)

    var_lowercase = tk.BooleanVar()
    tk.Checkbutton(frame, text="包含小写字母", variable=var_lowercase, bg="#f0f0f0").grid(row=6, columnspan=2, sticky='w', padx=10)

    var_symbols = tk.BooleanVar()
    tk.Checkbutton(frame, text="包含符号", variable=var_symbols, bg="#f0f0f0").grid(row=7, columnspan=2, sticky='w', padx=10)

    var_chinese = tk.BooleanVar()
    tk.Checkbutton(frame, text="包含中文字符", variable=var_chinese, bg="#f0f0f0").grid(row=8, columnspan=2, sticky='w', padx=10)

    var_tibetan = tk.BooleanVar()
    tk.Checkbutton(frame, text="包含泰语字符", variable=var_tibetan, bg="#f0f0f0").grid(row=9, columnspan=2, sticky='w', padx=10)

    var_backup_to_github = tk.BooleanVar()
    tk.Checkbutton(frame, text="备份到GitHub", variable=var_backup_to_github, bg="#f0f0f0").grid(row=10, columnspan=2, sticky='w', padx=10)

    btn_generate = tk.Button(root, text="生成密码", command=on_generate, bg="#4CAF50", fg="white", font=title_font)  # 创建生成密码按钮
    btn_generate.pack(pady=20)  # 添加到主窗口

    root.mainloop()  # 启动主循环

if __name__ == "__main__":  # 如果是主程序
    try:
        main()  # 调用主函数
    except Exception as e:
        print("程序运行时发生错误。")  # 提示错误信息
        print(traceback.format_exc())  # 打印详细错误信息
