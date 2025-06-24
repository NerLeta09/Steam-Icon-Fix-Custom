import os
import sys
import ctypes
import shutil
import requests
import configparser
import winreg
from glob import glob
from pathlib import Path
from urllib.parse import urlparse

# 设置控制台颜色
def set_color(color):
    ctypes.windll.kernel32.SetConsoleTextAttribute(ctypes.windll.kernel32.GetStdHandle(-11), color)

def logui(msg): set_color(11); print(msg); set_color(7)
def logsuc(msg): set_color(10); print(msg); set_color(7)
def logwrn(msg): set_color(14); print(msg); set_color(7)
def logerr(msg): set_color(12); print(msg); set_color(7)

# 获取 Steam 安装目录
def get_steam_path():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
            val, _ = winreg.QueryValueEx(key, "InstallPath")
            return val
    except Exception:
        return None

# 获取快捷方式目录
def get_special_folder(folder_name):
    from win32com.shell import shell, shellcon
    try:
        return shell.SHGetFolderPath(0, getattr(shellcon, folder_name), None, 0)
    except:
        return None

# 查找 .url 文件
def find_url_files(paths):
    files = []
    for path in paths:
        if path and os.path.exists(path):
            files += glob(os.path.join(path, "*.url"))
    return files

# 下载文件
def download_file(url, path):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(path, 'wb') as f:
                f.write(resp.content)
            return True
        return resp.status_code
    except Exception as e:
        logerr(f"下载失败: {e}")
        return -1

# 删除图标缓存
def flush_icon_cache():
    os.system("taskkill /f /im explorer.exe")
    paths = [
        os.path.expandvars(r"%userprofile%\AppData\Local\IconCache.db"),
        os.path.expandvars(r"%userprofile%\AppData\Local\Microsoft\Windows\Explorer")
    ]
    for path in paths:
        if os.path.isdir(path):
            for file in os.listdir(path):
                if file.startswith("thumbcache") or file.endswith(".db"):
                    try: os.remove(os.path.join(path, file))
                    except: pass
        elif os.path.isfile(path):
            try: os.remove(path)
            except: pass
    os.system("start explorer")

# 主程序入口
def main(steam_path=None, desktop_path=None):
    set_color(11)
    print("========Steam Icon Fix (CLI)========")
    set_color(6)

    # 手动输入路径
    steam_path = input("请输入 Steam 图标目录路径（留空则自动检测）: ").strip()
    desktop_path = input("请输入桌面路径（留空则使用默认桌面）: ").strip()

    if not steam_path:
        steam_path = None  # 后续用注册表自动检测
    if not desktop_path:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # 默认从注册表获取
    default_steam_path = get_steam_path()
    if default_steam_path:
        steam_path = os.path.join(default_steam_path, "steam", "games")
        logsuc(f"找到 Steam 图标目录: {steam_path}")
    else:
        logwrn("找不到 Steam 注册信息，使用默认路径")

    # 获取快捷方式目录
    start_menu = get_special_folder("CSIDL_PROGRAMS")
    start_menu_path = os.path.join(start_menu, "Steam") if start_menu else None

    files = find_url_files([desktop_path, start_menu_path])
    if not files:
        logerr("未找到任何 .url 快捷方式")
        sys.exit(1)

    cdn = input("选择 CDN [0=akamai, 1=cloudflare]（默认0）：").strip()
    cdn = "cloudflare" if cdn == "1" else "akamai"
    logui(f"当前使用 CDN: {cdn}")

    icon_url_tpl = f"http://cdn.{cdn}.steamstatic.com/steamcommunity/public/images/apps"

    for file in files:
        config = configparser.ConfigParser(interpolation=None)
        config.read(file)

        try:
            url = config["InternetShortcut"]["URL"]
            icon_file = config["InternetShortcut"]["IconFile"]
        except KeyError:
            logwrn(f"无效 .url 文件: {file}")
            continue

        if not url.startswith("steam://"):
            continue

        appid = url.split("/")[-1]
        icon_filename = os.path.basename(icon_file)
        download_url = f"{icon_url_tpl}/{appid}/{icon_filename}"
        save_path = os.path.join(steam_path, icon_filename)

        print(f"\n处理 {os.path.basename(file)} | AppID: {appid}")
        print(f"- 下载: {download_url}")
        res = download_file(download_url, save_path)
        if res is True:
            logsuc("- 下载成功并保存")

            # 修改 .url 文件中的 IconFile 路径
            config.set("InternetShortcut", "IconFile", save_path)

            # 保存回文件（注意写回编码）
            with open(file, "w", encoding="utf-8") as f:
                config.write(f, space_around_delimiters=False)
            logsuc("- 快捷方式已更新 IconFile 路径")
            
        elif isinstance(res, int) and 400 <= res < 600:
            logwrn(f"- 跳过，HTTP错误: {res}")
        else:
            logerr("- 下载失败，终止")
            if os.path.exists(save_path):
                os.remove(save_path)
            sys.exit(1)

    logui("图标处理完成，刷新缓存中...")
    flush_icon_cache()
    logsuc("全部完成！")
    os.system("pause")

if __name__ == "__main__":
    main()
