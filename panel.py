import tkinter as tk
from tkinter import filedialog, messagebox
from steam_icon_fix import fix_icon

def select_directory(title):
    return filedialog.askdirectory(title=title)

def run_fix_icon(steam_path, desktop_path, start_menu_path):
    try:
        fix_icon(desktop_path=desktop_path, start_menu_path=start_menu_path, steam_path=steam_path)
        messagebox.showinfo("完成", "图标修复已完成！")
    except Exception as e:
        messagebox.showerror("错误", f"修复过程中出错：{e}")

def main_panel():
    root = tk.Tk()
    root.title("Steam 图标修复工具")
    root.geometry("470x250")
    root.resizable(False, False)

    steam_path_var = tk.StringVar()
    desktop_path_var = tk.StringVar()
    start_menu_path_var = tk.StringVar()

    # 标签和按钮
    def browse_steam():
        path = select_directory("选择 Steam 安装目录")
        if path:
            steam_path_var.set(path)

    def browse_desktop():
        path = select_directory("选择桌面目录")
        if path:
            desktop_path_var.set(path)

    def browse_start_menu():
        path = select_directory("选择开始菜单目录（可选）")
        if path:
            start_menu_path_var.set(path)

    def on_run():
        run_fix_icon(
            steam_path=steam_path_var.get() or None,
            desktop_path=desktop_path_var.get() or None,
            start_menu_path=start_menu_path_var.get() or None
        )

    tk.Label(root, text="Steam 路径：").pack(pady=5)
    steam_frame = tk.Frame(root)
    steam_frame.pack()
    tk.Entry(steam_frame, textvariable=steam_path_var, width=50).pack(side="left", padx=(0, 5))
    tk.Button(steam_frame, text="选择目录", command=browse_steam).pack(side="left")

    tk.Label(root, text="桌面路径：").pack(pady=5)
    desktop_frame = tk.Frame(root)
    desktop_frame.pack()
    tk.Entry(desktop_frame, textvariable=desktop_path_var, width=50).pack(side="left", padx=(0, 5))
    tk.Button(desktop_frame, text="选择目录", command=browse_desktop).pack(side="left")

    tk.Label(root, text="开始菜单路径（可选）：").pack(pady=5)
    start_menu_frame = tk.Frame(root)
    start_menu_frame.pack()
    tk.Entry(start_menu_frame, textvariable=start_menu_path_var, width=50).pack(side="left", padx=(0, 5))
    tk.Button(start_menu_frame, text="选择目录", command=browse_start_menu).pack(side="left")

    tk.Button(root, text="执行修复", command=on_run, bg="green", fg="white").pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main_panel()
