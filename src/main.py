# -*- coding: utf-8 -*-
# --------------------
# This program is part of the Little Tree Wallpaper project
# main.py is the program's entry file.
# 本程序是小树壁纸项目的组成部分
# main.py 是本程序的入口文件
# --------------------
# Little Tree Wallpaper is a free and open-source program released under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007 license.
# Please abide by the content of this agreement, otherwise we have the right to pursue legal responsibility.
# 小树壁纸是基于 GNU Affero 通用公共许可证第三版（2007年11月19日发布）(AGPLv3) 发布的自由的免费开源程序
# 请遵守该协议内容，否则我们有权追究您法律责任。
# --------------------
# If you make any changes to this code or use any code of this program, please open source the code of your program and keep the copyright information of the Little Tree Wallpaper
# 如果您对本代码产生任何改动或使用了本程序任何代码，请您将您程序的代码开源，并保留小树壁纸的版权信息。
# --------------------
# Copyright © 2023-2025 Little Tree Wallpaper Project Group. Some rights reserved.
# 版权所有 © 2023-2025 小树壁纸项目组。保留部分权利。
# Copyright © 2022-2025 Little Tree Studio. Some rights reserved.
# 版权所有 © 2023-2025 小树工作室。保留部分权利。
# Copyright © 2021-2025 Xiaoshu. Some rights reserved.
# 版权所有 © 2021-2025 小树。保留部分权利。
# !部分代码正在重构，不建议在当前版本对代码修改或使用！

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 导入
# 功能: 导入库
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# 标准库
import sys
import queue
import traceback
import datetime
import mimetypes
import random
import subprocess
import threading
import io
import os
import logging
import time
import json
import math
import re
import webbrowser
import shutil
import platform
import argparse
import hashlib

# 非标准库
import magic.magic
import pycurl
import pystray
import requests
import concurrent
import magic
import ltwpAPI.image
import ltwpAPI.wallpaper
import ltwpAPI.config
import maliang
import maliang.animation as animation
import maliang.core.configs as configs
import maliang.theme as theme
import maliang.toolbox as toolbox
import tkinter.filedialog as filedialog
from concurrent.futures import ThreadPoolExecutor
from plyer import notification
from PIL import Image, ImageFile
from colorama import Fore, Style
from functools import lru_cache
from importlib.util import find_spec
from urllib.parse import urlparse, unquote

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 库设置
# 功能: 定义库的一些设置
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


ImageFile.LOAD_TRUNCATED_IMAGES = True #? 解决图片加载问题
configs.Font.size = -24 #? 设置字体大小


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 常量定义
# 功能: 定义一些常量
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

DEBUG_MODE = True #?是否开启调试模式
DEBUG_MODE_NO_LOADING_IMAGE = False #?是否不加载图片

VER = "v6.0.0-rc.2" #? 主版本号
INSIDE_VER = "6.0.0.rc.2.t23" #? 内部版本号
BUILD_VER = "PY.TK.CORE.20250405001" #? 构建版本号

IS_PUBLIC = False #? 是否为公开版本
IS_TEST_VERSION = True #? 是否为测试版本

#? 下载 UserAgent(UA) 设置
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"

#? 日志设置
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [行:%(lineno)d] - [消息]%(message)s" #? 日志格式
LOG_FILE = f'./logs/log_{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.log' #? 日志文件

#? 路径设置
if sys.platform == "win32":
    USER_PATH = os.environ['USERPROFILE'] #? 用户路径
    CONFIG_PATH = f"{USER_PATH}\\.xiaoshu\\XiaoshuWallpaper\\Config\\Config.toml" #? 配置文件路径
    WALLPAPER_PATH = f"{USER_PATH}\\.xiaoshu\\XiaoshuWallpaper\\Wallpaper\\" #? 壁纸文件路径
    TEMP = os.path.expandvars("%TEMP%") #? 临时文件路径
else:
    USER_PATH = os.path.expanduser('~') #? 用户路径
    CONFIG_PATH = f"{USER_PATH}/.xiaoshu/XiaoshuWallpaper/Config/Config.toml" #? 配置文件路径
    WALLPAPER_PATH = f"{USER_PATH}/.xiaoshu/XiaoshuWallpaper/Wallpaper/" #? 壁纸文件路径
    TEMP = os.path.expandvars("$TMPDIR") #? 临时文件路径

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 初始化变量
# 功能: 初始化一些变量
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

occupied_file_list=[] #? 缓存/日志清理排除文件列表

is_choose = None #? 按钮选择
is_load_main: bool = False #? 是否已经加载主界面
is_have_update: bool = False #? 是否有更新
is_checked_update: bool = False #? 是否已经检查更新
is_load_index_wallpaper_detail: bool = False #? 是否已经加载壁纸详情界面

update_check_result: dict = None #? 检查更新结果

API_Core: dict = {
    "Wallpaper":{
        "Bing" : "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=7&mkt=zh-CN",
        "Spotlight" : "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&bcnt=4&country=zh&locale=zh-cn&fmt=json",
    },
    "Update":{
        "Update 1" : "https://raw.kkgithub.com/shu-shu-1/API/main/xiaoshu%20wallpaper/v2/update.json",
        "Update 2" : "https://fastly.jsdelivr.net/gh/shu-shu-1/API@main/xiaoshu%20wallpaper/v2/update.json",
    },
    "Web":{
        "Bing_test" : "https://www.bing.com/hp/api/v1/trivia",
        "Official" : "https://xiao-shu.us.kg/wallpaper/"
    }
} #? 核心API
API_Source: dict = {
    "Wallhaven源": {
        "随机": "https://api.nguaduot.cn/wallhaven/random",
        "每日": "https://api.nguaduot.cn/wallhaven/today"
    },
    "风景源": {
        "缙哥哥接口": "https://api.dujin.org/pic/fengjing",
        "远方接口": "https://tu.ltyuanfang.cn/api/fengjing.php"
    },
    "二次元源": {
        "保罗源": {
            "sm.ms-白底动漫": "https://api.paugram.com/wallpaper/?source=sm",
            "github.io-白底动漫": "https://api.paugram.com/wallpaper/?source=github"
        },
        "次元源": {
            "原神": "https://t.mwm.moe/ysz",
            "随机": "https://t.mwm.moe/pc",
            "AI生成": "https://t.mwm.moe/ai",
            "风景": "https://t.mwm.moe/fj",
            "小狐狸": "https://t.mwm.moe/xhl",
            "萌图": "https://t.mwm.moe/moe"
        },
        "其他源": {
            "[忆云]随机": "https://api.imlcd.cn/bg/acg.php",
            "[PAULZZH]东方": "https://img.paulzzh.com/touhou/random",
            "[樱花]随机": "https://www.dmoe.cc/random.php",
            "[Anosu]Pixiv精选": "https://image.anosu.top/pixiv/direct",
            "[个人收集]饿殍：明末千里行": [
                "https://i.postimg.cc/zf2yRGXj/image.jpg",
                "https://i.postimg.cc/ZRjVN3vQ/image.jpg",
                "https://i.postimg.cc/FRVG56y8/4b290f6e-b886-effb-b9b1-4a97bbeea0fe.jpg",
                "https://i.postimg.cc/3RZMSndJ/a3cde8b4-0197-1ad3-3760-9cb95dbc6517.jpg",
                "https://i.postimg.cc/02RWMpQV/ea0ff1ca-0358-4fca-b2bb-5b3a51706bdc.jpg",
                "https://i.postimg.cc/qRttT6HK/f5fd0dc2722faf65c455943574b087863546706878663505.jpg",
                "https://i.postimg.cc/0NZ9J3vB/ss-f1ba762ccb2918909b05051891316f27ecbbb245-1920x1080.jpg"
            ]
        }
    }
} #? 壁纸源API

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 输入参数处理
# 功能: 输入参数处理，获取命令行参数、环境变量、默认值等
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


parser = argparse.ArgumentParser(description='Xiaoshu Wallpaper')
parser.add_argument('-v', '--version', action='version', version=f'Xiaoshu Wallpaper {VER}')
parser.add_argument('-s', '--startup', action='store_true', help='Start using the startup mode. (test)')


console_args = parser.parse_args(sys.argv[1:])

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 启动检查和环境处理
# 功能: 检查系统环境并给出提示/导入库
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

if platform.system() == "Windows" and find_spec("win32clipboard") is None and find_spec("win32gui") is None and find_spec("win32api") is None and find_spec("win32con") is None:
    print(Fore.RED + "[启动检查不通过]缺少pywin32库，请安装后重试！" + Style.RESET_ALL)
    maliang.dialogs.TkMessage("您当前使用的是Windows平台，但是您未安装pywin32库，请安装后重试！",detail="如果您是在构建后的程序(下载版)中遇到此问题，请联系开发团队。",title="小树壁纸-启动检查",icon="error")
if platform.system() == "Windows":
    print(platform.win32_ver()[0])
    if not (platform.win32_ver()[0] == "10" or platform.win32_ver()[0] == "11"):
        print(Fore.RED + "[启动检查不通过]小树壁纸目前不支持版本低于10的Windows系统，请更换系统后重试！" + Style.RESET_ALL)
        maliang.dialogs.TkMessage("小树壁纸目前不支持版本低于10的Windows系统，请更换系统后重试！",detail="如果您是在构建后的程序(下载版)中遇到此问题，请联系开发团队。",title="小树壁纸-启动检查",icon="error")
        sys.exit(1)
# 检测资源完整性
if not os.path.exists("./assets/"):
    print(Fore.RED + "[启动检查不通过]资源文件丢失，请重新下载程序！" + Style.RESET_ALL)
    maliang.dialogs.TkMessage("资源文件丢失，请重新下载程序！",title="小树壁纸-启动检查",icon="error")
    exit(1)
if platform.system() == "Windows":
    import win32gui
    import win32con
    import win32api
    import win32clipboard
print(Fore.GREEN + f"[启动检查通过]当前系统环境为{platform.system()} {platform.release()} {platform.version()}" + Style.RESET_ALL)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 测试版处理
# 功能: 测试版警告信息、单独设置
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

if IS_PUBLIC and IS_TEST_VERSION:
    print(f"{Fore.YELLOW}警告")
    print(f"{Fore.YELLOW}-----------------------------------------------")
    print(f"{Fore.YELLOW}当前是开发版本，请谨慎使用！")
    print(f"{Fore.YELLOW}测试版本不能代表最终品质，请以正式版为准！")
    print(f"{Fore.YELLOW}-----------------------------------------------")
    print(f"{Style.RESET_ALL}")
elif IS_TEST_VERSION:
    print(f"{Fore.YELLOW}警告")
    print(f"{Fore.YELLOW}-----------------------------------------------")
    print(f"{Fore.YELLOW}当前是{Style.RESET_ALL}{Fore.RED}内部未公开{Style.RESET_ALL}{Fore.YELLOW}的开发版本，请谨慎使用！")
    print(f"{Fore.YELLOW}内部测试版本不能代表最终品质，请勿外泄，请以正式版为准！")
    print(f"{Fore.YELLOW}-----------------------------------------------")
    print(f"{Style.RESET_ALL}")
if not IS_PUBLIC:
    maliang.dialogs.TkMessage(title="警告", message="当前是内部测试版本，请勿外泄，请以正式版为准！", icon="warning", option="ok")
if not DEBUG_MODE:
    sys.stdout = open(os.devnull, 'w')


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 功能函数
# 功能: 定义一些功能函数
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def new_folder(folder_name: str) -> None:
    """
    创建一个新文件夹，如果文件夹已存在则记录信息而不重复创建。

    Args:
    folder_name (str): 要创建的文件夹的名称或路径。

    如果指定的文件夹名称在文件系统中已经存在，则会记录一条信息并返回，
    不进行任何操作。如果文件夹不存在，则会创建该文件夹，并记录一条成功创建的信息。
    """
    if os.path.exists(folder_name):
        logging.info(f"文件夹“{folder_name}”已存在")
        return
    else:
        os.makedirs(folder_name)
        logging.info(f"创建文件夹“{folder_name}”成功")


def get_executable_directory() -> str:
    """
    获取可执行文件的目录路径。

    如果当前脚本已经打包成可执行文件，则返回该可执行文件所在的目录路径。
    如果当前脚本是未打包的普通Python脚本，则返回该脚本文件所在的目录路径。

    Returns:
        str: 可执行文件或脚本文件所在的目录路径。
    """
    if getattr(sys, 'frozen', False):
        # 如果脚本是冻结的（即打包后的可执行文件）
        return os.path.dirname(sys.executable)
    else:
        # 如果脚本是普通的Python脚本
        return os.path.dirname(os.path.abspath(__file__))

def extract_filename(path: str) -> list:
    """
    提取文件名和扩展名。

    Args:
    path (str): 文件路径。

    Returns:
    list: 包含文件名和扩展名的列表。
    """
    head, tail = os.path.split(path.rstrip(os.sep))
    return [head if head else None,tail if tail else None]

def check_api_accessibility_and_latency(api_dict : dict):
    """
    检查API端点的可访问性和延迟。

    Args:
        api_dict (dict): 包含API来源及其对应端点URL的字典。格式如下：
            {
                "来源1": {
                    "端点1": "URL1",
                    "端点2": ["URL2", "备用URL2"]
                },
                "来源2": {
                    "端点3": "URL3"
                }
            }

    Returns:
        dict: 检查结果字典，包含每个API来源及其端点的可访问性、延迟和状态码或错误信息。格式如下：
            {
                "来源1": {
                    "端点1": {"可访问": True/False, "延迟": float, "状态码": int},
                    "端点2": {"可访问": True/False, "延迟": float, "状态码": int, "错误": "错误信息"}
                },
                "来源2": {
                    "端点3": {"可访问": True/False, "延迟": float, "状态码": int}
                }
            }

    Notes:
        - 如果端点URL是列表，将使用列表中的第一个URL进行检查。
        - 对于每个端点，通过发送GET请求来检查其可访问性，并计算请求的延迟。
        - 如果请求成功（状态码200），则记录可访问性为True，延迟为请求所用时间，并记录状态码。
        - 如果请求失败，则记录可访问性为False，延迟为None，并记录错误信息。
    """
    results = {}

    def check_endpoint(source, endpoint_name, endpoint_url):
        if isinstance(endpoint_url, list):
            endpoint_url = endpoint_url[0]  # 如果URL是列表，取第一个

        headers = {
            'User-Agent': UA
        }

        try:
            start_time = time.time()
            response = requests.get(endpoint_url, headers=headers, timeout=10)
            end_time = time.time()

            latency = end_time - start_time
            status = response.status_code

            return {
                "可访问": status == 200,
                "延迟": latency,
                "状态码": status
            }
        except requests.RequestException as e:
            return {
                "可访问": False,
                "延迟": None,
                "错误": str(e)
            }

    def recursive_check(current_dict, current_source):
        if current_source not in results:
            results[current_source] = {}

        for key, value in current_dict.items():
            if isinstance(value, dict):
                recursive_check(value, key)
            else:
                results[current_source][key] = check_endpoint(current_source, key, value)

    for source, endpoints in api_dict.items():
        recursive_check(endpoints, source)

    return results


def get_file_count(folder_path) -> int:
    """
        获取文件夹下的文件数量
        Args:
            folder_path (str): 文件夹路径
        Returns:
            int: 文件数量
    """
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        file_count += len(filenames)
    return file_count
def get_folder_size(folder_path) -> int:
    """
        获取文件夹大小
        Args:
            folder_path (str): 文件夹路径
        Returns:
            int: 文件夹大小（MB）
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size / (1024 * 1024)
def run_installer(installer_path) -> None:
    """
    运行安装程序。
    Args:
        installer_path (str): 安装程序路径。
    """


    if sys.platform == 'win32':
        installer_path = installer_path
        arguments = [
            "/FORCECLOSEAPPLICATIONS",
            "/RESTARTAPPLICATIONS",
            "/SILENT"
        ]

        # 合并路径和参数为一个列表
        command = [installer_path] + arguments

        # 使用 subprocess.Popen() 启动安装程序
        subprocess.Popen(command)
    else:
        subprocess.call(['chmod', '+x', installer_path])
        subprocess.call(['open', installer_path])
def resize_image(image_path: str, new_height: int) -> maliang.PhotoImage:
    """
    调整图片大小并保持原始宽高比，返回处理后的PhotoImage对象。

    使用Lanczos重采样算法进行高质量的下采样处理。调整后的图片宽度会根据目标高度
    自动按比例计算。

    Args:
        image_path: 待处理图片的完整文件路径
        new_height: 调整后的目标高度（像素），必须为正整数

    Returns:
        maliang.PhotoImage: 包含调整尺寸后图片数据的对象，可直接用于界面显示

    Raises:
        FileNotFoundError: 当指定图片路径不存在时引发
        PIL.UnidentifiedImageError: 当图片文件损坏或格式不支持时引发
        ValueError: 当输入高度小于等于0时引发

    Example:
        >>> img = resize_image("wallpaper.jpg", 600)
        >>> canvas.draw_image(img, 0, 0)

    Note:
        实际输出宽度为原始宽高比乘以目标高度的计算结果（向下取整）
        建议目标高度不超过原图高度的10倍以防止过度插值
    """
    # 参数校验
    if new_height <= 0:
        raise ValueError("目标高度必须为正值")

    # 打开图片并获取尺寸
    original_image = Image.open(image_path)
    width, height = original_image.size

    # 计算等比缩放后的宽度
    new_width = int(width * new_height / height)

    # 执行缩放操作
    resized_image = original_image.resize(
        (new_width, new_height),
        resample=Image.Resampling.LANCZOS
    )

    return maliang.PhotoImage(resized_image)

def copy_and_set_wallpaper(image_path,*args) -> None:
    """
    复制图片到指定路径，并设置壁纸

    Args:
        image_path (str): 图片路径
        *args: 可选参数，用于传递给set_wallpaper函数

    Returns:
        None
    """
    shutil.copyfile(image_path, f"{WALLPAPER_PATH}{os.path.basename(image_path)}")
    set_wallpaper(f"{WALLPAPER_PATH}{os.path.basename(image_path)}")

def set_wallpaper(filelink) -> None:
    """
    设置壁纸。

    Args:
        filelink (str): 图片文件路径。

    Returns:
        None
    """
    set_wallpaper_class=ltwpAPI.wallpaper.WallpaperChanger()
    set_wallpaper_class.set_wallpaper(filelink)

def compare_versions(version1, version2) -> int:
    """
    比较两个语义版本字符串，考虑预发布版本和构建元数据。

    该函数遵循语义版本 2.0.0 规范（semver.org），比较版本时支持 major.minor.patch 核心版本、预发布标签和构建元数据。
    版本字符串可选地以 'v' 或 'V' 开头，这些前缀在解析期间会被忽略。

    参数:
        version1 (str): 要比较的第一个版本字符串。
        version2 (str): 要比较的第二个版本字符串。

    返回值:
        int: 如果 version1 比 version2 新，返回 1；
             如果 version1 比 version2 旧，返回 -1；
             如果版本相同，返回 0。
    """

    def parse_core_version(version):
        version_clean = version.lstrip('vV')
        core_part = version_clean.split('+')[0].split('-')[0]
        parts = list(map(int, core_part.split('.')))
        while len(parts) < 3:
            parts.append(0)
        return parts[:3]

    def parse_pre_release(version):
        version_clean = version.lstrip('vV')
        parts = version_clean.split('+')[0].split('-')
        if len(parts) > 1:
            return parts[1].split('.')
        return None

    def compare_identifiers(a, b):
        a_is_num = isinstance(a, int)
        b_is_num = isinstance(b, int)

        if a_is_num and b_is_num:
            return (a > b) - (a < b)
        if a_is_num:
            return -1
        if b_is_num:
            return 1
        return (a > b) - (a < b)

    v1_core = parse_core_version(version1)
    v2_core = parse_core_version(version2)
    core_comparison = (v1_core > v2_core) - (v1_core < v2_core)
    if core_comparison != 0:
        return core_comparison

    v1_pre = parse_pre_release(version1)
    v2_pre = parse_pre_release(version2)

    if v1_pre is None and v2_pre is None:
        return 0
    if v1_pre is None:
        return 1
    if v2_pre is None:
        return -1

    def convert_identifier(identifier):
        try:
            if identifier.startswith('0') and len(identifier) > 1:
                raise ValueError("Numeric identifier with leading zero")
            return int(identifier)
        except ValueError:
            return identifier

    v1_ids = [convert_identifier(id) for id in v1_pre]
    v2_ids = [convert_identifier(id) for id in v2_pre]

    min_length = min(len(v1_ids), len(v2_ids))
    for i in range(min_length):
        comparison = compare_identifiers(v1_ids[i], v2_ids[i])
        if comparison != 0:
            return comparison

    return (len(v1_ids) > len(v2_ids)) - (len(v1_ids) < len(v2_ids))

def copy_image_to_clipboard(image_path) -> None:
    """
    将图片文件复制到剪贴板。

    Args:
        image_path (str): 图片文件路径。

    Returns:
        None
    """
    try:
        # 打开图片并转换为RGB模式
        img = Image.open(image_path).convert('RGB')

        # 跨平台处理：根据操作系统选择合适的剪贴板操作
        if sys.platform == "win32":
            # Windows 平台使用 ImageGrab 和 Clipboard API
            from io import BytesIO

            output = BytesIO()
            img.save(output, format='BMP')
            data = output.getvalue()[14:]  # BMP 文件头需要去掉前14字节
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

        elif sys.platform == "darwin":
            # macOS 平台使用 pbcopy
            import subprocess
            from tempfile import NamedTemporaryFile

            with NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                img.save(tmp_file.name, format="PNG")
                subprocess.run(["pbcopy", tmp_file.name], check=True)

        else:
            # Linux 平台使用 xclip 或 xsel
            import subprocess
            from tempfile import NamedTemporaryFile

            with NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                img.save(tmp_file.name, format="PNG")
                try:
                    # 尝试使用 xclip
                    subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", tmp_file.name], check=True)
                except FileNotFoundError:
                    # 如果 xclip 不可用，尝试使用 xsel
                    subprocess.run(["xsel", "--clipboard", "--input", "--type", "image/png", "<", tmp_file.name], check=True, shell=True)

    except Exception as e:
        logging.error(f"复制图片到剪贴板失败: {e}")



def get_my_pictures_path() -> str:
    """
    获取用户图片文件夹路径。

    Returns:
        str: 用户图片文件夹路径。
    """
    logging.info("调用读取图片文件夹路径函数")

    if sys.platform == "linux":
        try:
            # 方案1: 通过 xdg-user-dir 命令获取（需安装 xdg-utils）
            result = subprocess.run(
                ['xdg-user-dir', 'PICTURES'],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
                stderr=subprocess.DEVNULL
            )
            path = result.stdout.strip()
            path = os.path.expanduser(path)  # 处理 ~ 扩展
            if not os.path.isabs(path):
                path = os.path.abspath(path)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 方案2: 回退到环境变量或默认路径
            path = os.environ.get("XDG_PICTURES_DIR", "")
            if path:
                path = os.path.expandvars(path)  # 处理 $VAR 变量
                path = os.path.expanduser(path)  # 再次处理 ~ 扩展
                return os.path.abspath(path)
            else:
                # 方案3: 最终回退到 ~/Pictures
                return os.path.expanduser("~/Pictures")
        except Exception as e:
            logging.error(f"Linux 平台未知错误: {e}")

            maliang.dialogs.TkMessage(
                icon="error",
                title="路径错误",
                message="无法确定图片目录",
                detail="请检查是否安装 xdg-utils 或设置环境变量"
            )
            raise RuntimeError("无法获取图片目录")

    else:  # Windows 平台
        try:
            import winreg
            # 原有注册表读取逻辑
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            my_pictures_path, _ = winreg.QueryValueEx(key, "My Pictures")
            winreg.CloseKey(key)
            # 展开可能的环境变量（如 %USERPROFILE%）
            return os.path.expandvars(my_pictures_path)
        except OSError as error:
            logging.error(f"注册表读取错误: {error}")
            print(f"错误: {error.strerror}")
            maliang.dialogs.TkMessage(
                icon="error",
                title="注册表错误",
                message="读取图片路径失败",
                detail="请尝试以管理员权限运行程序"
            )
            raise
        except Exception as e:
            logging.error(f"未知错误: {e}")

            maliang.dialogs.TkMessage(
                icon="error",
                title="系统错误",
                message="发生意外错误",
                detail="请查看日志文件"
            )
            raise
def validate_image_file(path):
    try:
        with Image.open(path) as img:
            img.verify()  # 轻量验证
            if img.format == "JPEG":
                # 检查EXIF头部
                with open(path, 'rb') as f:
                    f.seek(0x1000)  # 跳转至EXIF区域
                    exif_data = f.read(0x200)
                    if exif_data.count(b'\x00') > 100:  # 简单检测异常填充
                        raise ValueError("可疑的EXIF结构")
        return True
    except Exception as e:
        logging.error(f"无效图片: {str(e)}")
        return False
def determine_image_format(image_path: str) -> str:
    """
    获取图片文件的格式。

    :param image_path: 图片文件的路径
    :return: 图片文件的格式（如 'PNG'）
    """
    try:
        validate_image_file(image_path)
    except Exception as e:
        logging.error(f"无效图片: {str(e)}")
        return None

    try:
        with Image.open(image_path) as img:
            format = img.format
            logging.info(f"图片格式为{format}")
            return format
    except IOError:
        logging.error(f"无法打开图片文件: {image_path}")

        return None

def change_file_extension(file_path, new_extension):
    """
    更改给定文件路径的文件扩展名。

    :param file_path: 文件的完整路径
    :param new_extension: 新的扩展名（包括点，例如 '.jpg'）
    :return: 更改后的文件路径
    """
    # 获取文件的目录和基础名（不带扩展名）
    file_dir = os.path.dirname(file_path)
    file_base = os.path.splitext(os.path.basename(file_path))[0]

    # 构建新的文件路径
    new_file_path = os.path.join(file_dir, file_base + "." + new_extension.lower())

    # 重命名文件
    try:
        os.rename(file_path, new_file_path)
        # print(f"File renamed to {new_file_path}")
        logging.info(f"{file_path}文件重命名为{new_file_path}".replace("\\","/"))
        return new_file_path
    except OSError as e:
        logging.error(f"无法重命名文件: {e}")

        return None

def clean_filename(filename):
    """
    清理文件名中的无效字符。

    该函数接收一个文件名字符串，替换其中的无效字符（如<>:"/\\|?*）为下划线，并移除末尾的"&pid=hp"。
    返回清理后的文件名字符串。

    :param filename: 原始文件名字符串。
    :type filename: str
    :return: 清理后的文件名字符串。
    :rtype: str
    :details: 该函数会执行以下操作：
        - 使用正则表达式替换文件名中的<>:"/\\|?*字符为下划线。
        - 移除文件名末尾的"&pid=hp"字符串。
    """
    # 替换无效字符
    return re.sub(r'[<>:"/\\|?*]', '_', filename).removesuffix("&pid=hp")

def get_bing_image() -> list:
    """
    从必应壁纸API获取图片信息。

    该函数向必应的API发送请求，获取最近7天的壁纸信息。
    返回一个包含壁纸版权信息、日期、原始图片链接、图片链接、标题和版权链接的列表。
    如果请求失败或发生异常，则返回False。

    :return: 包含壁纸信息的列表，或False表示请求失败。
    :rtype: list or bool
    :details: 返回的列表中的每个元素是一个字典，包含以下键值对：
        - 'copyright': 图片的版权信息。
        - 'date': 图片的结束日期，格式为 'YYYY-MM-DD'。
        - 'urlbase': 图片的基础URL，可用于生成不同分辨率的图片链接。
        - 'url': 图片的完整URL。
        - 'title': 图片的标题。
        - 'copyrightlink': 图片版权的链接。
    """
    try:
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',  # 不是必须
        }
        response = requests.get(
            "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=7&mkt=zh-CN",
            headers=headers,  # 请求头
            timeout=5,  # 设置请求超时时间
        )
        response = json.loads(response.text)  # 转化为json
        imgList = []
        for item in response['images']:
            imgList.append({
                'copyright': item['copyright'],  # 版权
                'date': item['enddate'][0:4] + '-' + item['enddate'][4:6] + '-' + item['enddate'][6:],  # 时间
                'urlbase': 'https://cn.bing.com' + item['urlbase'],  # 原始图片链接
                'url': 'https://cn.bing.com' + item['url'],  # 图片链接
                'title': item['title'],  # 标题
                'copyrightlink': item['copyrightlink'],  # 版权链接
            })
        return imgList  # 返回一个数据数组
    except Exception:
        return False

def get_spotlight_image() -> list:
    """
    从Windows Spotlight API获取图片信息。

    该函数向Microsoft的API发送请求，获取Windows Spotlight的图片信息。
    返回一个包含图片链接、标题、版权、日期和版权链接的列表。
    如果请求失败或发生异常，则返回False。

    :return: 包含Spotlight图片信息的列表，或False表示请求失败。
    :rtype: list or bool
    :details: 返回的列表中的每个元素是一个字典，包含以下键值对：
        - 'url': 图片的横屏（landscape）版本的URL。
        - 'portrait_image': 图片的竖屏（portrait）版本的URL。
        - 'title': 图片的标题。
        - 'copyright': 图片的版权信息。
        - 'date': 图片的获取日期，格式为 'YYYY-MM-DD'。
        - 'copyrightlink': 图片版权的链接。
    """
    try:
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'user-agent': UA
        }
        response = requests.get(
            "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&bcnt=4&country=zh&locale=zh-cn&fmt=json",
            headers=headers,  # 请求头
            timeout=5,  # 设置请求超时时间
        )

        image_links = []

        for item in response.json()['batchrsp']['items']:
            item_data = json.loads(item['item'])  # 再次解析 item
            ad_data = item_data['ad']

            landscape_image = ad_data['landscapeImage']['asset']
            portrait_image = ad_data['portraitImage']['asset']
            title = ad_data['title']
            copyright = ad_data['copyright']
            cta_url = ad_data['ctaUri']

            image_links.append({
                'url': landscape_image,
                'portrait_image': portrait_image,
                'title': title,
                'copyright': copyright,
                'date': f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}",
                'copyrightlink': cta_url,
            })
        return image_links  # 返回一个数据数组
    except Exception as e:
        raise Exception(f'Windows Spotlight API获取失败: {e}')

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 文件夹
# 功能: 新建一些必须的文件夹
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

new_folder("logs")
new_folder("temp")
new_folder(WALLPAPER_PATH)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 日志
# 功能: 初始化日志记录器
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# 关闭默认的日志记录器
logging.getLogger().handlers.clear()
# 创建日志记录器
logger = logging.getLogger()
# 设置日志级别
logger.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
# 创建控制台处理器
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter(LOG_FORMAT)
# 将格式化器添加到处理器
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write(f"""{"-"*50}
    小树壁纸日志信息
    小树壁纸 | 当前版本: {VER} 内部版本: {INSIDE_VER} 构建版本: {BUILD_VER}
    运行平台信息: {platform.platform()}
    Python版本: {platform.python_version()}
    日志文件: {LOG_FILE}
{"-"*50}
""")
logging.info("日志初始化成功")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 主窗口
# 功能: 初始化主窗口
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

root = maliang.Tk(title=f"小树壁纸{VER}_{BUILD_VER}")
root.center()

logging.info("初始化窗口成功")



# 加载字体
if toolbox.load_font("./assets/fonts/LXGWWenKai-Regular.ttf"):
    configs.Font.family = "霞鹜文楷"
    logging.info("文本字体1加载成功")
if toolbox.load_font("./assets/fonts/MiSans-Regular.ttf"):
    logging.info("文本字体2加载成功")
if toolbox.load_font("./assets/fonts/SEGOEICONS.TTF"):
    logging.info("图标字体加载成功")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 脚本引擎
# 功能: 小树壁纸脚本的执行引擎
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class WallpaperScriptEngine:
    def __init__(self, api):
        self.vars = {}
        self.api = api  # 壁纸操作API接口
        self.functions = {
            'set_wallpaper': self._api_set_wallpaper,
            'download': self._api_download,
            'sleep': self._api_sleep,
            'log': self._api_log
        }

    def _api_set_wallpaper(self, args):
        """设置壁纸接口: set_wallpaper("url")"""
        if len(args) != 1:
            raise ValueError("set_wallpaper 需要1个参数")
        return self.api.set_wallpaper(args[0])

    def _api_download(self, args):
        """下载文件接口: download("url", "save_path")"""
        if len(args) < 2:
            raise ValueError("download 需要至少2个参数")
        if len(args) > 3:
            raise ValueError("download 最多3个参数")
        if len(args) == 2:
            return self.api.download_file(args[0], args[1])
        else:
            return self.api.download_file(args[0], args[1], args[2])

    def _api_sleep(self, args):
        """延时接口: sleep(seconds)"""
        if len(args) != 1 or not isinstance(args[0], (int, float)):
            raise ValueError("sleep 需要1个数字参数")
        time.sleep(args[0])

    def _api_log(self, args):
        """日志接口: log("message")"""
        if len(args) != 1:
            raise ValueError("log 需要1个参数")
        logging.info(f"[脚本日志] {args[0]}")

    def execute(self, script):
        """执行脚本代码"""
        for line in script.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            self._execute_line(line)


    def _eval_expr(self, expr):
        """解析数学表达式，包含详细的错误信息"""
        try:
            return eval(expr, {}, self.vars)
        except Exception as e:
            # 添加当前变量信息到错误提示
            available_vars = ", ".join(self.vars.keys())
            raise ValueError(
                f"表达式解析错误: '{expr}' "
                f"(可用变量: {available_vars}) - {str(e)}"
            )

    def _parse_args(self, args_str):
        """解析函数参数，支持字符串、变量和表达式"""
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if not arg:
                continue
            if arg.startswith('"') and arg.endswith('"'):
                args.append(arg[1:-1])  # 字符串字面量
            else:
                try:
                    # 评估表达式
                    value = self._eval_expr(arg)
                    args.append(value)
                except Exception as e:
                    raise NameError(f"参数解析错误: '{arg}' - {str(e)}")
        return args

    def _execute_line(self, line):
        line = line.strip()
        if not line:
            return

        # 处理for循环（增强range参数解析）
        if line.startswith('for '):
            # 提取循环结构：for i in range(...) { ... }
            import re
            match = re.match(r'for\s+(\w+)\s+in\s+range$(.*)$\s*\{(.*)\}', line, re.DOTALL)
            if not match:
                raise SyntaxError("无效的循环语法")

            var_name = match.group(1)
            range_args_str = match.group(2).strip()
            block = match.group(3).strip()

            # 解析range参数
            range_args = self._parse_args(range_args_str)

            # 根据参数数量生成range参数
            if len(range_args) == 1:
                start, end, step = 0, range_args[0], 1
            elif len(range_args) == 2:
                start, end, step = range_args[0], range_args[1], 1
            elif len(range_args) == 3:
                start, end, step = range_args
            else:
                raise ValueError("range()参数最多3个")

            # 执行循环
            for i in range(start, end, step):
                self.vars[var_name] = i
                # 执行循环体内的每一条语句
                for stmt in re.split(r';\s*', block):
                    if stmt:
                        self._execute_line(stmt)
            return

### ✨ 脚本管理器
def script_thread(script):
    logging.info(f"[新脚本线程 | ID{threading.get_ident()}] 开始执行脚本")
    api = ScriptAPI()
    engine = WallpaperScriptEngine(api)
    try:
        engine.execute(script)
        logging.info(f"[脚本线程 | ID{threading.get_ident()}] 脚本执行完成")
        notification.notify(
            title="脚本执行完成",
            message="壁纸脚本已成功执行",
            app_name="小树壁纸"
        )
    except Exception as e:
        logging.error(f"[脚本线程 | ID{threading.get_ident()}] 脚本执行错误: {e}")

        notification.notify(
            title="脚本执行错误",
            message=f"错误详情：{str(e)}",
            app_name="小树壁纸"
        )

class ScriptAPI:
    """提供给脚本引擎的API接口"""
    def set_wallpaper(self, url):
        return set_wallpaper(url)

    def download_file(self, url, path = None, file_name = None):
        if not path:
            path = os.path.join(os.getcwd(), "temp")
        if file_name:
            return download_file(url, path, file_name)
        try:
            file_path = extract_filename(path)

            if file_path[1]:

                print(file_path)
                return download_file(url, file_path[0], file_path[1])

            return download_file(url, path)
        except Exception:

            return download_file(url, path)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 命令行调试工具
# 功能: 提供命令行调试工具
# !警告: 部分功能因界面库限制，暂时无法正常使用！
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def command_line_debug_tool():
    """
    命令行调试工具线程函数。
    """
    while True:
        user_input = input()
        if user_input.lower() == 'exit':
            os._exit(0)
        elif user_input.lower() == 'clean':
            os.system('cls')
        elif user_input.lower() == 'test':
            print("测试消息！")
        elif user_input.lower() == 'checkapi':
            results = check_api_accessibility_and_latency(API_Core)

            # 打印结果
            for source, endpoints in results.items():
                print(f"源: {source}")
                for endpoint_name, result in endpoints.items():
                    print(f"  接口: {endpoint_name}")
                    print(f"    可访问: {result['可访问']}")
                    print(f"    延迟: {result['延迟']} 秒")
                    if '状态码' in result:
                        print(f"    状态码: {result['状态码']}")
                    if '错误' in result:
                        print(f"    错误: {result['错误']}")
            results = check_api_accessibility_and_latency(API_Source)

            # 打印结果
            for source, endpoints in results.items():
                print(f"源: {source}")
                for endpoint_name, result in endpoints.items():
                    print(f"  接口: {endpoint_name}")
                    print(f"    可访问: {result['可访问']}")
                    print(f"    延迟: {result['延迟']} 秒")
                    if '状态码' in result:
                        print(f"    状态码: {result['状态码']}")
                    if '错误' in result:
                        print(f"    错误: {result['错误']}")
        elif user_input.startswith("ssp"):
            start_panel()
        elif user_input.startswith("theme"):
            try:
                theme_name = user_input.split(" ")[1]
            except IndexError:
                theme_name = "list"
            match theme_name:
                case "light":
                    theme.set_color_mode("light")
                case "dark":
                    theme.set_color_mode("dark")
                case "acrylic":
                    theme.apply_theme(root, "acrylic")
                    theme.set_color_mode("dark")
                # case "粉雕玉琢":
                #     style.set_theme_map(light_theme=粉雕玉琢)
                #     style.set_color_mode("light")
                # case "原木秋色":
                #     style.set_theme_map(light_theme=原木秋色)
                #     style.set_color_mode("light")
                # case "国行公祭":
                #     style.set_theme_map(light_theme=国行公祭)
                #     style.set_color_mode("light")
                # case "粉花春色":
                #     style.set_theme_map(light_theme=粉花春色)
                #     style.set_color_mode("light")
                # case "中秋月下":
                #     style.set_theme_map(light_theme=中秋月下)
                #     style.set_color_mode("light")
                # case "欢庆春节":
                #     style.set_theme_map(light_theme=欢庆春节)
                #     style.set_color_mode("light")
                # case "清明祭扫":
                #     style.set_theme_map(light_theme=清明祭扫)
                #     style.set_color_mode("light")
                # case "黄昏蓝调":
                #     style.set_theme_map(light_theme=黄昏蓝调)
                #     style.set_color_mode("light")
                case "list":
                    print("可选主题：")
                    print("light dark acrylic")
                case _:
                    print(f"{Style.RESET_ALL}{Fore.RED}不存在的主题：{theme_name}{Style.RESET_ALL}")
        else:
            print(f"{Style.RESET_ALL}{Fore.RED}不存在的命令：{user_input}{Style.RESET_ALL}")

command_line_debug_tool_thread = threading.Thread(target=command_line_debug_tool)
command_line_debug_tool_thread.daemon = True
command_line_debug_tool_thread.start()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 配置文件管理
# 功能: 读取/初始化配置文件
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

logging.info("配置文件路径："+os.path.abspath(CONFIG_PATH))
if os.path.exists(CONFIG_PATH) is not True:
    logging.warning("未检测到配置文件, 尝试创建配置文件...")
    if os.path.exists(os.path.dirname(CONFIG_PATH)) is not True:
        logging.info("未检测到配置文件目录, 尝试创建配置文件目录...")
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH))
            logging.info("创建配置文件目录成功")
        except Exception as e:
            logging.error(f"创建配置文件目录失败, 错误: {e}")

            maliang.dialogs.TkMessage(icon="error",title="严重错误：创建配置文件目录失败",message="详细错误信息请查看日志",detail="你可以向作者反馈此问题")
            webbrowser.open("https://github.com/shu-shu-1/Xiaoshu-Wallpaper/issues/new?labels=bug")
            os._exit(0)
    with open(CONFIG_PATH,"w+") as f:
        logging.info("创建空配置文件成功")
        f.read()
        f.close()
    cog = ltwpAPI.config.ConfigManager(CONFIG_PATH)
    cog.reset_config()
    logging.info("已载入默认配置")
else:
    try:
        cog = ltwpAPI.config.ConfigManager(CONFIG_PATH)
    except Exception as e:
        logging.error(f"载入配置文件失败, 错误: {e}")

        maliang.dialogs.TkMessage(icon="error",title="严重错误：载入配置文件失败",message="详细错误信息请查看日志",detail="你可以向作者反馈此问题(前提是你未手动修改配置文件)或删除配置文件")
        webbrowser.open("https://github.com/shu-shu-1/Xiaoshu-Wallpaper/issues/new?labels=bug")
        os._exit(0)
    logging.info("已载入配置文件")
    try:
        cog.get_value("info.version")
    except KeyError:
        logging.warning("配置文件版本过低或为空, 重置配置文件...")
        cog.reset_config()
    if compare_versions(cog.get_value("info.version"), "2.0.0") > 0:
        logging.warning("配置文件版本过高, 请确认是否使用过高版本程序")
        maliang.dialogs.TkMessage(icon="warning",title="配置文件版本过高",message="配置文件版本过高，请确认是否使用过高版本程序",detail="配置文件版本过高，可能导致程序运行异常。建议使用最新版本程序或重新创建配置文件。")

if cog.get_value("data.download_path") == "":
    logging.warning("下载路径未设置, 尝试设置默认下载路径...")
    # TODO : 更改默认下载路径
    cog.set_value("data.download_path", get_my_pictures_path())



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 窗口默认样式
# 功能: 设置窗口默认样式
# ?提示: 该模块仅设置窗口默认样式，具体的窗口布局由各个模块自行完成
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


root.iconbitmap(default=cog.get_value("display.window_icon_path"))
root.resizable(width=False, height=False)



### ✨ 页面切换
def clean_page():
    canvas_index.place_forget()
    canvas_test.place_forget()
    canvas_setting.place_forget()
    canvas_about.place_forget()
    canvas_egg.place_forget()
    canvas_detail.place_forget()
    canvas_download.place_forget()
    canvas_wallpaper.place_forget()
    canvas_wallpaper_detail.place_forget()
    canvas_wallpaper_more_360_download.pack_forget()

def test_info():
    canvas_loading.place_forget()
    canvas_test.place(width=1280, height=720, x=640, y=360, anchor="center")

def egg():
    # maliang.dialogs.TkMessage(icon="info",title="彩蛋",message="你发现了一个彩蛋！",detail="你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！\n\n你发现了一个彩蛋！")
    canvas_index.delete("all")

    canvas_index.place_forget()
    canvas_egg.place(width=1280, height=720, x=640, y=360, anchor="center")

def wallpaper():
    wallpaper_wallhaven()
    canvas_index.delete("all")

    canvas_index.place_forget()
    canvas_wallpaper_detail.place_forget()
    canvas_wallpaper.place(width=1280, height=720, x=640, y=360, anchor="center")


def setting():
    canvas_index.delete("all")

    canvas_index.place_forget()
    canvas_setting.place(width=1280, height=720, x=640, y=360, anchor="center")

    canvas_setting.update_idletasks()
    canvas_setting.zoom()



def about():
    canvas_index.delete("all")
    canvas_index.place_forget()

    canvas_about.place(width=1280, height=720, x=640, y=360, anchor="center")
    canvas_about.update_idletasks()
    canvas_about.zoom()



def more_bing(*args):
    global canvas_detail
    canvas_detail.place(width=1280, height=720, x=0, y=0)
    canvas_download.delete("all")
    canvas_download.place_forget()
    canvas_index.delete("all")
    canvas_index.place_forget()
    # canvas_detail.update_idletasks()
    # canvas_detail.zoom()
    # canvas_index._zoom_children()
    # canvas_index._zoom_self()

def main():
    global canvas_index
    # global last
    # if is_load_main is not True:
    #     index_window()
    canvas_index.destroy()
    canvas_index = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
    # canvas_index.zoom()

    index_window()
    # canvas_index.zoom()
    canvas_index.place(x=0, y=-720, width=1280, height=720)
    animation.MoveTkWidget(canvas_index, (0, 720), 100, fps=60, controller=animation.smooth).start(delay=100)

    time.sleep(1)
    canvas_test.place_forget()
    canvas_setting.place_forget()
    canvas_about.place_forget()
    canvas_egg.place_forget()
    canvas_detail.place_forget()
    canvas_download.place_forget()
    canvas_wallpaper.place_forget()
    canvas_wallpaper_detail.place_forget()
    canvas_wallpaper_more_360_download.pack_forget()

    # canvas_index.update_idletasks()
    # canvas_index.zoom()
### ✨ 测试信息
canvas_test = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
maliang.Text(canvas_test, (50, 50), text="测试信息", fontsize=40, anchor="nw")
test_info_text="""感谢您参与小树壁纸SSP(自启动面板)的测试！
如果您有任何意见或建议，欢迎您在Github上提出issue或PR。
同时也欢迎您关注我们的其他版本：

- 小树壁纸Next：https://github.com/shu-shu-1/Xiaoshu-Wallpaper-Next
- 小树壁纸Future (C#开发)：敬请期待
"""
maliang.Text(canvas_test, (50, 100), text=test_info_text, fontsize=25, anchor="nw")
maliang.Button(canvas_test, (50, 600), text="开始测试", command=main)
# maliang.Text(canvas_test, (1280, 720), text=xf"版本：{VER} 内部版本：{software_VER} 构建信息：{BUILD_VER}", fontsize=20, anchor="se")
canvas_test.create_text(1280, 720, text=f"小树壁纸 版本：{VER} 内部版本：{INSIDE_VER} 构建信息：{BUILD_VER}", font=("MiSans",20),anchor="se", fill="gray")
### ✨ 启动加载


canvas_loading = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)

### ✨ 更新
canvas_index = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_update = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_update_download = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)

def fetch_latest_release(
    ty: str = cog.get_value("update.channel"),
    api_endpoints: list = [
        "https://raw.kkgithub.com/shu-shu-1/API/main/xiaoshu%20wallpaper/v2/update.json",
        "https://fastly.jsdelivr.net/gh/shu-shu-1/API@main/xiaoshu%20wallpaper/v2/update.json"
    ]
):
    """检查软件更新，支持多API端点轮询

    Args:
        ty: 更新渠道类型
        api_endpoints: 可自定义的API端点列表，按顺序尝试直至成功
    """
    logging.info(f"开始检查更新，渠道类型：{ty}")

    # 测试渠道特殊处理
    if ty == "Test":
        logging.info("检测到测试更新配置")
        return {
            "status": "test_update",
            "version": "V0.1.0 Next",
            "update_note": "小树壁纸 Next α 测试已开始\n\n感谢你参与本次测试！(≧∇≦)ﾉ\n\t\t\t\t-更新提示测试-",
            "download_url": None,
            "file_format": None
        }

    # 轮询API端点
    update_web_json = None
    for idx, api in enumerate(api_endpoints, 1):
        try:
            logging.info(f"尝试第{idx}个API端点: {api}")
            response = requests.get(api, timeout=10)
            response.raise_for_status()
            update_web_json = json.loads(response.text)
            break  # 成功获取后跳出循环
        except Exception as e:
            logging.warning(f"API端点{idx}请求失败: {str(e)}")
            continue

    # 所有API请求失败处理
    if not update_web_json:
        error_msg = f"所有{len(api_endpoints)}个API端点请求均失败"
        logging.error(error_msg)
        return {
            "status": "error",
            "error_message": error_msg
        }

    # 解析版本信息
    try:
        channel_data = update_web_json["update_channels"][ty]
        web_ver = channel_data["version"]
        web_download_url = channel_data["download_link"]
        web_update_note = channel_data["update_content"]
        web_file_format = channel_data["file_format"]

        if compare_versions(web_ver, VER) == 1:
            logging.info(f"发现新版本 {web_ver}")
            return {
                "status": "update_available",
                "version": web_ver,
                "update_note": web_update_note,
                "download_url": web_download_url,
                "file_format": web_file_format
            }
        else:
            logging.info(f"当前已是最新版本 ({web_ver})")
            return {"status": "no_update"}

    except KeyError as e:
        error_msg = f"JSON字段解析失败: {str(e)}"
        logging.error(error_msg)

        return {
            "status": "error",
            "error_message": error_msg
        }
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        logging.error(error_msg)

        return {
            "status": "error",
            "error_message": error_msg
        }





### ✨ 启动面板





def download_file(url, save_path="./temp", custom_filename=None, timeout=30, max_retries=3, headers=None):
    """
    使用pycurl高效下载文件并根据多种情况自动判断文件格式和文件名
    本函数已在V6.0.0 RC2重构
    
    参数:
        url (str): 要下载的文件URL
        save_path (str, optional): 保存文件的路径，如果没有指定则保存在temp目录
        custom_filename (str, optional): 手动指定的文件名，如果包含扩展名则使用该扩展名
        timeout (int, optional): 请求超时时间(秒)
        chunk_size (int, optional): 每次读取的数据块大小
        max_retries (int, optional): 最大重试次数
        headers (dict, optional): 自定义请求头信息
        
    返回:
        str: 保存的文件的完整路径，如果下载失败则返回None
    """
    
    # 设置默认请求头
    default_headers = {
        'User-Agent': UA,
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    if headers:
        default_headers.update(headers)

    
    # 处理手动指定的文件名
    filename = None
    extension = None
    custom_extension = None
    
    if custom_filename:
        filename = custom_filename
        # 检查是否包含扩展名
        if '.' in custom_filename and not custom_filename.endswith('.'):
            name_parts = custom_filename.rsplit('.', 1)
            if len(name_parts) > 1 and name_parts[1].strip():
                custom_extension = '.' + name_parts[1].strip()
    
    # 重试逻辑
    for attempt in range(max_retries):
        temp_path = None
        try:
            # 初始化pycurl
            c = pycurl.Curl()
            
            # 1. 首先获取头部信息
            header_buffer = io.BytesIO()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.NOBODY, 1)  # HEAD请求
            c.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
            c.setopt(pycurl.CONNECTTIMEOUT, timeout)
            c.setopt(pycurl.TIMEOUT, timeout)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            
            # 设置请求头
            header_list = [f"{k}: {v}" for k, v in default_headers.items()]
            c.setopt(pycurl.HTTPHEADER, header_list)
            
            c.perform()
            http_code = c.getinfo(pycurl.HTTP_CODE)
            
            if http_code != 200:
                raise pycurl.error(f"HTTP状态码: {http_code}")
            
            # 解析头部信息
            headers_text = header_buffer.getvalue().decode('utf-8', errors='ignore')
            headers_dict = {}
            for line in headers_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers_dict[key.strip()] = value.strip()
            
            # 如果没有手动指定文件名，尝试自动获取
            if not filename:
                # 1. 从Content-Disposition获取文件名
                if 'Content-Disposition' in headers_dict:
                    content_disposition = headers_dict['Content-Disposition']
                    filename_match = re.search(r'filename=["\'](.*)["\']', content_disposition)
                    if filename_match:
                        filename = unquote(filename_match.group(1))
                    else:
                        filename_match = re.search(r'filename=([^;]+)', content_disposition)
                        if filename_match:
                            filename = unquote(filename_match.group(1).strip())
                
                # 2. 从URL路径获取文件名
                if not filename:
                    parsed_url = urlparse(url)
                    if parsed_url.path:
                        filename = unquote(os.path.basename(parsed_url.path))
                        # 检查是否是有效的文件名
                        if not filename or filename.endswith('/') or '.' not in filename:
                            filename = None
            
            # 如果没有自定义扩展名，尝试从Content-Type获取
            content_type = headers_dict.get('Content-Type', '').lower().split(';')[0].strip()
            if not custom_extension and content_type and content_type != 'application/octet-stream':
                guessed_extension = mimetypes.guess_extension(content_type)
                if guessed_extension:
                    extension = guessed_extension
            
            # 如果没有获取到文件名，使用URL的MD5哈希值作为文件名
            if not filename:
                hash_object = hashlib.md5(url.encode())
                filename = hash_object.hexdigest()
            
            # 确定临时保存路径用于判断文件类型
            temp_dir = os.path.dirname(os.path.abspath(save_path)) if save_path else os.getcwd()
            temp_path = os.path.join(temp_dir, f"temp_{filename}")
            
            # 2. 下载文件内容
            logging.info(f"开始下载: {url}")
            
            # 重置curl对象
            c.reset()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.CONNECTTIMEOUT, timeout)
            c.setopt(pycurl.TIMEOUT, timeout)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.HTTPHEADER, header_list)
            
            # 设置写入文件和进度回调
            with open(temp_path, 'wb') as f:
                c.setopt(pycurl.WRITEDATA, f)
                
                # 进度回调函数
                def progress_callback(download_total, downloaded, upload_total, uploaded):
                    # if download_total > 0:
                    #     progress = (downloaded / download_total) * 100
                    #     logging.info(f"下载进度: {progress:.2f}% ({downloaded} / {download_total})")
                    pass
                
                c.setopt(pycurl.NOPROGRESS, 0)
                c.setopt(pycurl.PROGRESSFUNCTION, progress_callback)
                
                c.perform()
            
            http_code = c.getinfo(pycurl.HTTP_CODE)
            if http_code != 200:
                raise pycurl.error(f"下载失败，HTTP状态码: {http_code}")
            
            # 文件类型检测
            if not custom_extension:
                mime_type = magic.magic.Magic(mime=True).from_file(temp_path)
                file_type = magic.magic.Magic().from_file(temp_path)
                logging.info(f"检测到的MIME类型: {mime_type}")
                logging.info(f"检测到的文件类型: {file_type}")
                
                # 根据检测到的MIME类型获取扩展名
                if not extension:
                    guessed_extension = mimetypes.guess_extension(mime_type)
                    if guessed_extension:
                        extension = guessed_extension
                
                # 确保文件名有正确的扩展名
                if extension:
                    name_parts = filename.rsplit('.', 1)
                    if len(name_parts) > 1 and name_parts[1].lower() in mimetypes.types_map.keys():
                        # 已有合适的扩展名，保持不变
                        pass
                    else:
                        # 添加或替换扩展名
                        filename = name_parts[0] + extension
            else:
                # 使用自定义扩展名
                logging.info(f"使用自定义扩展名: {custom_extension}")
                name_parts = filename.rsplit('.', 1)
                filename = name_parts[0] + custom_extension
            
            # 确定最终保存路径
            if save_path:
                if os.path.isdir(save_path):
                    full_path = os.path.join(save_path, filename)
                else:
                    # 如果提供的是完整路径，使用它
                    full_path = save_path
            else:
                full_path = filename
            
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
            
            # 将临时文件移动到最终位置
            shutil.move(temp_path, full_path)
            
            logging.info(f"文件下载完成: {full_path.replace('\\','/')}")
            return full_path
            
        except pycurl.error as e:
            errno, errmsg = e.args if len(e.args) == 2 else (None, str(e))
            logger.error(f"下载尝试 {attempt + 1}/{max_retries} 失败: {errmsg} (errno: {errno})")
            if attempt == max_retries - 1:
                logger.error(f"下载失败，已达到最大重试次数: {url}")
                # 清理临时文件
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
            continue
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
            # 清理临时文件
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return None
        finally:
            if 'c' in locals():
                c.close()
            
    return None

def ssp_bing_loading():
    global bing_data, bing_img_temp, bing_img_view
    try:
        logging.info("开始加载快捷面板Bing壁纸")
        bing_loading_text.set("加载中...1/3")
        bing_data=get_bing_image()
        logging.info("Bing壁纸服务器数据获取成功")
        bing_loading_text.set("加载中...2/3")
        bing_img_temp=download_file(bing_data[0]["url"], custom_filename="bing")
        occupied_file_list.append(bing_img_temp)
        logging.info("Bing壁纸图片下载成功")
        bing_loading_text.set("加载中...3/3")
        bing_img_view=maliang.Image(canvas_ssp, (20,100), image=maliang.PhotoImage(ltwpAPI.image.RoundedImage(15).round_corners(ltwpAPI.image.ImageScaler(Image.open(bing_img_temp)).scale_by_size(new_height=200))))
        logging.info("Bing壁纸图片加载成功")
        sbb.forget(False)
        vb.forget(False)
        bing_loading_text.forget()
    except Exception as e:
        logging.error(f"加载Bing壁纸失败：{e}")

        bing_loading_text.set("加载出现错误，请查看日志了解详情。")
    # spotlight_data=get_spotlight_image()
def ssp_spotlight_loading():
    global spotlight_data, spotlight_img_temp1, spotlight_img_temp2, spotlight_img_temp3, spotlight_img_temp4, spotlight_img_view1, spotlight_img_view2, spotlight_img_view3, spotlight_img_view4
    try:
        logging.info("开始加载快捷面板Spotlight壁纸")
        spotlight_loading_text.set("加载中...1/5")
        spotlight_data=get_spotlight_image()
        logging.info("Spotlight壁纸服务器数据获取成功")
        spotlight_loading_text.set("加载中...2/5")
        spotlight_img_temp1=download_file(spotlight_data[0]["url"], custom_filename="spotlight1")
        occupied_file_list.append(spotlight_img_temp1)
        spotlight_img_view1=maliang.Image(canvas_ssp, (25,360), image=maliang.PhotoImage(ltwpAPI.image.RoundedImage(10).round_corners(ltwpAPI.image.ImageScaler(Image.open(spotlight_img_temp1)).scale_by_size(new_height=110))))
        logging.info("Spotlight壁纸图片1下载成功")
        spotlight_loading_text.set("加载中...3/5")
        spotlight_img_temp2=download_file(spotlight_data[1]["url"], custom_filename="spotlight2")
        occupied_file_list.append(spotlight_img_temp2)
        spotlight_img_view2=maliang.Image(canvas_ssp, (225,360), image=maliang.PhotoImage(ltwpAPI.image.RoundedImage(10).round_corners(ltwpAPI.image.ImageScaler(Image.open(spotlight_img_temp2)).scale_by_size(new_height=110))))
        logging.info("Spotlight壁纸图片2下载成功")
        spotlight_loading_text.set("加载中...4/5")
        spotlight_img_temp3=download_file(spotlight_data[2]["url"], custom_filename="spotlight3")
        occupied_file_list.append(spotlight_img_temp3)
        spotlight_img_view3=maliang.Image(canvas_ssp, (25,480), image=maliang.PhotoImage(ltwpAPI.image.RoundedImage(10).round_corners(ltwpAPI.image.ImageScaler(Image.open(spotlight_img_temp3)).scale_by_size(new_height=110))))
        logging.info("Spotlight壁纸图片3下载成功")
        spotlight_loading_text.set("加载中...5/5")
        spotlight_img_temp4=download_file(spotlight_data[3]["url"], custom_filename="spotlight4")
        occupied_file_list.append(spotlight_img_temp4)
        spotlight_img_view4=maliang.Image(canvas_ssp, (225,480), image=maliang.PhotoImage(ltwpAPI.image.RoundedImage(10).round_corners(ltwpAPI.image.ImageScaler(Image.open(spotlight_img_temp4)).scale_by_size(new_height=110))))
        logging.info("Spotlight壁纸图片4下载成功")
        logging.info("Spotlight壁纸图片加载成功")
        svb.forget(False)
        spotlight_loading_text.forget()
    except Exception as e:
        logging.error(f"加载Spotlight壁纸失败：{e}")

        spotlight_loading_text.set("加载出现错误，请查看日志了解详情。")
def show_root():
    root.deiconify()
def hide_root():
    root.withdraw()
root.protocol("WM_DELETE_WINDOW", hide_root)
def start_panel():
    global ssp_loading_bing_thread,ssp_loading_spotlight_thread

    ssp_loading_bing_thread = threading.Thread(target=ssp_bing_loading)
    ssp_loading_spotlight_thread = threading.Thread(target=ssp_spotlight_loading)
    ssp()
def ssp():
    global panel,bing_loading_text,canvas_ssp,spotlight_loading_text,sbb,vb,svb
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    # screen_height = panel.winfo_screenheight()

    # 设置窗口宽度和高度
    window_width = 450
    window_height = 650

    # 计算窗口右上角的位置
    x_position = screen_width - window_width - 40
    y_position = 20
    # 设置窗口位置
    panel = maliang.Toplevel(title="SSP test",size=[window_width,window_height],position=[x_position,y_position])
    panel.topmost(True)
    panel.resizable(False,False)
    panel.toolwindow(True)
    theme.customize_window(
        panel,
        # style="acrylic",
        hide_title_bar=True,
        # hide_button="maxmin",
        border_type="smallround",
    )
    def hide_panel():
        panel.withdraw()
    panel.protocol("WM_DELETE_WINDOW", hide_panel)
    def show_panel():
        panel.deiconify()
    def open_bing_detail():
        if is_load_main:

            clean_page()
            more_bing()
            root.deiconify()
        else:
            maliang.dialogs.TkMessage(icon="info",title="提示",message="请等待主窗口加载完成后再打开Bing壁纸详情。")
    def spotlight_detail():
        ...
    menu = (
        pystray.MenuItem('显示主窗口', show_root, default=True),
        pystray.MenuItem('显示快捷面板', show_panel),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('退出', lambda: os._exit(0)))
    threading.Thread(target=pystray.Icon("icon", Image.open(cog.get_value("display.window_icon_path")), "小树壁纸", menu).run, daemon=True).start()

    canvas_ssp = maliang.Canvas(panel, auto_zoom=True, keep_ratio="min", free_anchor=True)
    canvas_ssp.place(width=470, height=800, x=0, y=0, anchor="nw")

    maliang.Text(canvas_ssp, (20, 20), text="快捷面板", family="MiSans", fontsize=25)
    maliang.Text(canvas_ssp, (20, 60), text="Bing每日壁纸", family="MiSans", fontsize=20)
    bing_loading_text = maliang.Text(canvas_ssp, (150, 65), text="加载中...", family="MiSans", fontsize=15)
    maliang.Text(canvas_ssp, (20, 320), text="Windows 聚焦", family="MiSans", fontsize=20)
    spotlight_loading_text = maliang.Text(canvas_ssp, (165, 325), text="加载中...", family="MiSans", fontsize=15)
    maliang.Button(canvas_ssp, (425, 20), text="—", command=lambda:hide_panel(), family="MiSans", fontsize=15,size=[30,30],weight="bold")
    sbb=maliang.Button(canvas_ssp, (390, 100), text="设为壁纸", command=lambda:copy_and_set_wallpaper(bing_img_temp), family="MiSans", fontsize=15)
    vb=maliang.Button(canvas_ssp, (390, 150), text="查看详情", command=lambda:open_bing_detail(), family="MiSans", fontsize=15)
    svb=maliang.Button(canvas_ssp, (377, 600), text="详情", command=lambda:spotlight_detail(), family="MiSans", fontsize=15)
    sbb.forget()
    vb.forget()
    svb.forget()
    ssp_loading_bing_thread.start()
    ssp_loading_spotlight_thread.start()
    panel.mainloop()

### ✨ 主界面
# 全局样式配置字典
STYLE_CONFIG = {
    "default": {
        "meta": {
            "display_name": "经典主题",
            "author": "系统内置"
        },
        "background": {
            "enable": True,
            "position": (0, 0),
            "resize": (720, 720),
            "anchor": "nw"
        },
        "elements": [
            {
                "type": "icon_button",
                "name": "设置按钮",
                "position": (50, 670),
                "size": (40, 50),
                "symbol": "",
                "fontsize": 40,
                "commands": {"<Button-1>": "setting"}
            },
            {
                "type": "icon_button",
                "name": "关于按钮",
                "position": (100, 670),
                "size": (40, 53),
                "symbol": "",
                "fontsize": 43,
                "commands": {
                    "<Button-1>": "about",
                    "<Button-2>": "about",
                    "<Button-3>": "egg"
                }
            },
            {
                "type": "icon_button",
                "name": "壁纸入口",
                "position": (1230, 670),
                "size": (40, 50),
                "symbol": "",
                "fontsize": 40,
                "commands": {"<Button-1>": "wallpaper"}
            },
            {
                "type": "text",
                "content": "主页",
                "position": (50, 70),
                "fontsize": 40,
                "anchor": "w"
            },
            {
                "type": "text",
                "content": "小树壁纸6.0 RC 预发行版",
                "position": (50, 110),
                "fontsize": 25,
                "anchor": "w"
            },
            {
                "type": "image_panel",
                "position": (640, 320),
                "anchor": "center",
                "info_position": (640, 100),
                "detail_position": (640, 440),
                "more_info": {
                    "position": (640, 490),
                    "size": (40, 50),
                    "symbol": "",
                    "fontsize": 40
                }
            }
        ]
    },
    "next": {
        "meta": {
            "display_name": "现代主题",
            "author": "设计团队"
        },
        "background": {
            "enable": True,
            "position": (0, 0),
            "resize": (720, 720),
            "anchor": "nw"
        },
        "elements": [
            {
                "type": "icon_button",
                "name": "设置按钮",
                "position": (60, 670),
                "size": (40, 50),
                "symbol": "",
                "fontsize": 30,
                "commands": {"<Button-1>": "setting"}
            },
            {
                "type": "icon_button",
                "name": "关于按钮",
                "position": (60, 620),
                "size": (40, 53),
                "symbol": "",
                "fontsize": 33,
                "commands": {
                    "<Button-1>": "about",
                    "<Button-2>": "about",
                    "<Button-3>": "egg"
                }
            },
            {
                "type": "icon_button",
                "name": "壁纸入口",
                "position": (60, 170),
                "size": (40, 50),
                "symbol": "\ue93c",
                "fontsize": 30,
                "commands": {"<Button-1>": "wallpaper"}
            },
            {
                "type": "text",
                "content": "主页",
                "position": (100, 70),
                "fontsize": 35,
                "anchor": "w"
            },
            {
                "type": "text",
                "content": "小树壁纸6.0 RC 预发行版",
                "position": (100, 110),
                "fontsize": 25,
                "anchor": "w"
            },
            {
                "type": "image_panel",
                "position": (100, 230),
                "anchor": "nw",
                "info_position": (100, 140),
                "more_info": {
                    "position": (60, 130),
                    "size": (40, 40),
                    "symbol": "\uf738",
                    "fontsize": 30
                }
            },
            # {
            #     "type": "icon_button",
            #     "name": "新增功能按钮",
            #     "position": (60, 270),
            #     "size": (40, 40),
            #     "symbol": "\ueb4c",
            #     "fontsize": 28,
            #     "commands": {"<Button-1>": "new_feature"}
            # }
        ]
    },
    "test": {
        "meta": {
            "display_name": "测试主题",
            "author": "测试团队"
        },
        "background": {
            "enable": True,
            "position": (0, 0),
            "resize": (720, 720),
            "anchor": "nw"
        },
        "elements": [
            {
                "type": "icon_button",
                "name": "设置按钮",
                "position": (50, 670),
                "size": (40, 50),
                "symbol": "",
                "fontsize": 40,
                "commands": {"<Button-1>": "setting"}
            },
            {
                "type": "text",
                "position": (75, 665),
                "fontsize": 20,
                "content": "设置"
            },
            {
                "type": "icon_button",
                "name": "关于按钮",
                "position": (50, 600),
                "size": (40, 53),
                "symbol": "",
                "fontsize": 43,
                "commands": {
                    "<Button-1>": "about",
                    "<Button-2>": "about",
                    "<Button-3>": "egg"
                }
            },
            {
                "type": "text",
                "position": (75, 595),
                "fontsize": 20,
                "content": "关于"
            },
            {
                "type": "icon_button",
                "name": "壁纸入口",
                "position": (1175, 670),
                "size": (40, 50),
                "symbol": "",
                "fontsize": 40,
                "commands": {"<Button-1>": "wallpaper"}
            },
            {
                "type": "text",
                "position": (1200, 665),
                "fontsize": 20,
                "content": "壁纸源"
            },
            {
                "type": "text",
                "content": "主页",
                "position": (50, 70),
                "fontsize": 40,
                "anchor": "w"
            },
            {
                "type": "text",
                "content": "小树壁纸6.0 RC 预发行版 | 测试主界面",
                "position": (50, 110),
                "fontsize": 25,
                "anchor": "w"
            },
            {
                "type": "image_panel",
                "position": (50, 220),
                "anchor": "nw",
                "content": {
                    "main_image": {
                        "anchor": "nw",
                        "crop": True
                    },
                    "info": {
                        "position": (50, 140),
                        "anchor": "nw",
                        "lines": [
                            {"content": "今日{source}", "fontsize": 30, "weight": "bold"},
                            {"content": "{title}", "fontsize": 24, "position": (50, 175)}
                        ]
                    },
                    "copyright": {
                        "position": (50, 430),
                        "anchor": "nw",
                        "content": "{copyright}",
                        "fontsize": 20
                    },
                    "more_info": {
                        "icon": {
                            "position": (1050, 370),
                            "anchor": "nw",
                            "size": (40, 50),
                            "symbol": "",
                            "fontsize": 40,
                            "command": "detail"
                        },
                        "text": {
                            "position": (1140, 385),
                            "anchor": "n",
                            "content": "更多信息",
                            "fontsize": 20
                        }
                    }
                }
            }
        ]
    }
}

def create_ui_element(parent, element_config):
    """支持多行文本和深度锚点配置的UI元素创建"""
    try:
        elem_type = element_config.get("type")

        # 文本元素处理
        if elem_type == "text":
            # 公共配置解析
            base_position = element_config.get("position", (0, 0))
            base_anchor = element_config.get("anchor", "nw")
            global_justify = element_config.get("justify")
            fontsize = element_config.get("fontsize", 12)
            weight = element_config.get("weight", "normal")

            # 智能推断对齐方式
            if not global_justify:
                anchor = element_config.get("anchor", "center")
                justify_defaults = {
                    "nw": "left", "w": "left", "sw": "left",
                    "ne": "right", "e": "right", "se": "right",
                    "n": "center", "s": "center", "center": "center"
                }
                global_justify = justify_defaults.get(anchor, "left")

            maliang.Text(
                parent,
                base_position,
                text=element_config["content"].format(
                    source=home_page_assets_data['source'],
                    title=home_page_assets_data['detail']['title'],
                    copyright=home_page_assets_data['detail']['copyright']
                ),
                fontsize=fontsize,
                anchor=base_anchor,
                justify=global_justify,
                weight=weight
            )



        # 图标按钮处理
        elif elem_type == "icon_button":
            canvas = maliang.Canvas(
                parent,
                auto_zoom=True,
                keep_ratio="min",
                free_anchor=True
            )
            canvas.place(
                x=element_config["position"][0],
                y=element_config["position"][1],
                width=element_config["size"][0],
                height=element_config["size"][1],
                anchor=element_config.get("anchor", "center")
            )

            # 图标绘制
            vertical_offset = 10 if element_config["size"][1] >= 50 else 4
            maliang.Text(
                canvas,
                (0, vertical_offset),
                text=element_config["symbol"],
                fontsize=element_config["fontsize"],
                family="Segoe Fluent lcons",
                anchor="nw"
            )

            # 事件绑定
            for event, command in element_config.get("commands", {}).items():
                canvas.bind(event, lambda e, cmd=command: COMMAND_MAP[cmd]())

        # 图片面板处理
        elif elem_type == "image_panel":
            # 主图片处理
            img_config = element_config.get("content", {})
            main_img_config = img_config.get("main_image", {})

            # 根据配置选择裁剪或缩放
            if main_img_config.get("crop", True):
                img = process_image(home_page_assets_path)
            else:
                img = process_image(
                    home_page_assets_path,
                    target_size=main_img_config.get("target_size")
                )

            # 绘制主图片
            maliang.Image(
                parent,
                element_config["position"],
                image=img,
                anchor=element_config.get("anchor", "center")
            )

            # 信息区块
            info_config = img_config.get("info")
            if info_config:
                for line in info_config.get("lines", []):
                    maliang.Text(
                        parent,
                        line.get("position", info_config["position"]),
                        text=line["content"].format(
                            source=home_page_assets_data['source'],
                            title=home_page_assets_data['detail']['title']
                        ),
                        fontsize=line.get("fontsize", 20),
                        anchor=line.get("anchor", info_config["anchor"]),
                        weight=line.get("weight", info_config.get("weight", "normal")),
                    )

            # 版权信息
            copyright_config = img_config.get("copyright")
            if copyright_config:
                maliang.Text(
                    parent,
                    copyright_config["position"],
                    text=copyright_config["content"].format(
                        copyright=home_page_assets_data['detail']['copyright']
                    ),
                    fontsize=copyright_config.get("fontsize", 12),
                    anchor=copyright_config.get("anchor", "nw")
                )

            # 更多信息区块
            more_info_config = img_config.get("more_info")
            if more_info_config:
                # 图标部分
                icon_config = more_info_config.get("icon")
                if icon_config:
                    icon_canvas = maliang.Canvas(parent, auto_zoom=True)
                    icon_canvas.place(
                        x=icon_config["position"][0],
                        y=icon_config["position"][1],
                        width=icon_config["size"][0],
                        height=icon_config["size"][1],
                        anchor=icon_config.get("anchor", "nw")
                    )
                    maliang.Text(
                        icon_canvas,
                        (0, 10),
                        text=icon_config["symbol"],
                        fontsize=icon_config["fontsize"],
                        family="Segoe Fluent lcons",
                        anchor="nw"
                    )
                    icon_canvas.bind(
                        "<Button-1>",
                        lambda e: COMMAND_MAP[icon_config.get("command", "more_bing")]()
                    )

                # 文本部分
                text_config = more_info_config.get("text")
                if text_config:
                    maliang.Text(
                        parent,
                        text_config["position"],
                        text=text_config["content"],
                        fontsize=text_config["fontsize"],
                        anchor=text_config.get("anchor", "n")
                    )

        # 图标按钮
        elif elem_type == "icon_button":
            canvas = maliang.Canvas(
                parent,
                auto_zoom=True,
                keep_ratio="min",
                free_anchor=True
            )
            canvas.place(
                x=element_config["position"][0],
                y=element_config["position"][1],
                width=element_config["size"][0],
                height=element_config["size"][1],
                anchor=element_config.get("anchor", "center")
            )

            # 图标绘制
            vertical_offset = 10 if element_config["size"][1] >= 50 else 4
            maliang.Text(
                canvas,
                (0, vertical_offset),
                text=element_config["symbol"],
                fontsize=element_config["fontsize"],
                family="Segoe Fluent lcons",
                anchor="nw"
            )

            # 事件绑定
            for event, command in element_config.get("commands", {}).items():
                canvas.bind(event, lambda e, cmd=command: COMMAND_MAP[cmd]())

        # 增强型图片面板
        elif elem_type == "image_panel":
            # 主图片处理
            img_config = element_config.get("content", {})
            main_img_config = img_config.get("main_image", {})

            # 根据配置选择裁剪或缩放
            if main_img_config.get("crop", True):
                img = process_image(home_page_assets_path)
            else:
                img = process_image(
                    home_page_assets_path,
                    target_size=main_img_config.get("target_size")
                )

            # 绘制主图片
            maliang.Image(
                parent,
                element_config["position"],
                image=img,
                anchor=element_config.get("anchor", "center")
            )

            # 信息区块
            info_config = img_config.get("info")
            if info_config:
                for line in info_config.get("lines", []):
                    maliang.Text(
                        parent,
                        line.get("position", info_config["position"]),
                        text=line["content"].format(
                            source=home_page_assets_data['source'],
                            title=home_page_assets_data['detail']['title']
                        ),
                        fontsize=line.get("fontsize", 20),
                        anchor=line.get("anchor", info_config["anchor"]),
                        weight=line.get("weight", "normal")
                    )

            # 版权信息
            copyright_config = img_config.get("copyright")
            if copyright_config:
                maliang.Text(
                    parent,
                    copyright_config["position"],
                    text=copyright_config["content"].format(
                        copyright=home_page_assets_data['detail']['copyright']
                    ),
                    fontsize=copyright_config.get("fontsize", 12),
                    anchor=copyright_config.get("anchor", "nw")
                )

            # 更多信息区块
            more_info_config = img_config.get("more_info")
            if more_info_config:
                # 图标部分
                icon_config = more_info_config.get("icon")
                if icon_config:
                    icon_canvas = maliang.Canvas(parent, auto_zoom=True)
                    icon_canvas.place(
                        x=icon_config["position"][0],
                        y=icon_config["position"][1],
                        width=icon_config["size"][0],
                        height=icon_config["size"][1],
                        anchor=icon_config.get("anchor", "nw")
                    )
                    maliang.Text(
                        icon_canvas,
                        (0, 10),
                        text=icon_config["symbol"],
                        fontsize=icon_config["fontsize"],
                        family="Segoe Fluent lcons",
                        anchor="nw"
                    )
                    icon_canvas.bind(
                        "<Button-1>",
                        lambda e: COMMAND_MAP[icon_config.get("command", "more_bing")]()
                    )

                # 文本部分
                text_config = more_info_config.get("text")
                if text_config:
                    maliang.Text(
                        parent,
                        text_config["position"],
                        text=text_config["content"],
                        fontsize=text_config["fontsize"],
                        anchor=text_config.get("anchor", "n")
                    )

    except Exception as e:
        logging.error(f"UI元素创建失败: {str(e)}")

        traceback.print_exc()

# 优化后的图片处理函数（支持动态锚点）
@lru_cache(maxsize=32)
def process_image(image_path, target_size=None, crop_area=None):
    """支持多种处理模式的图片处理"""
    try:
        img = Image.open(image_path)

        if target_size:  # 缩放模式
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            return maliang.PhotoImage(img)

        if crop_area:  # 自定义裁剪
            return maliang.PhotoImage(img.crop(crop_area))

        # 默认裁剪逻辑
        width, height = img.size
        left = (width - (width // 2 - 10)) // 2
        upper = max((height - 300) // 2, 0)
        return maliang.PhotoImage(img.crop((
            left,
            upper,
            left + width//2 + 10,
            upper + 200
        )))

    except Exception as e:
        logging.error(f"图片处理失败: {str(e)}")

        return maliang.PhotoImage(Image.new('RGB', (100, 100), color='gray'))

def index_window(*args):
    global is_load_main
    is_load_main = True

    current_style = cog.get_value("home_page.style")
    config = STYLE_CONFIG.get(current_style, STYLE_CONFIG["default"])

    # 加载背景
    bg_config = config["background"]
    if bg_config["enable"] and cog.get_value("display.window_background_image_path"):
        bg_image = process_image(
            cog.get_value("display.window_background_image_path"),
            bg_config["resize"]
        )
        maliang.Image(
            canvas_index,
            bg_config["position"],
            image=bg_image,
            anchor=bg_config["anchor"]
        )

    # 创建所有UI元素
    for element in config["elements"]:
        create_ui_element(canvas_index, element)

    # 更新提示
    if is_have_update:
        update_config = {
            "position": (640, 670),
            "size": (40, 50),
            "symbol": "",
            "fontsize": 40,
            "commands": {"<Button-1>": "update"}
        }
        create_ui_element(canvas_index, {
            "type": "icon_button",
            **update_config
        })
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 动态壁纸
# 功能: 动态壁纸播放器
# !目前仅适用于Windows10/11系统
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

if platform.system() == "Windows":
    if platform.win32_ver()[1].split('.')[2] >= "26100":


        def get_monitors_info():
            monitors = []
            for monitor in win32api.EnumDisplayMonitors():
                monitor_info = win32api.GetMonitorInfo(monitor[0])
                rect = monitor_info["Monitor"]
                work_area = monitor_info["Work"]
                monitors.append({
                    "left": rect[0],
                    "top": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1],
                    "work_area": work_area
                    })


            for i, m in enumerate(monitors):
                logging.info(f"检查到显示器: 显示器{i}: {m['width']}x{m['height']} @ ({m['left']},{m['top']})")

            return monitors



        def set_mpv_as_wallpaper(mpv_hwnd, workerw_hwnd, defview_hwnd):
            # 设置 MPV 窗口的父窗口为 WorkerW 窗口
            win32gui.SetParent(mpv_hwnd, workerw_hwnd)
            # 让桌面图标层透明，先隐藏再显示SHELLDLL_DefView窗口使其重绘
            win32gui.ShowWindow(defview_hwnd, win32con.SW_HIDE)
            time.sleep(0.1)
            win32gui.ShowWindow(defview_hwnd, win32con.SW_SHOWNORMAL)

        def play_video_as_wallpaper(video_path):
            monitors = get_monitors_info()
            processes = []

            for idx, monitor in enumerate(monitors):
                # 为每个显示器创建独立进程
                cmd = [
                    'mpv', '--title=MPV-{}'.format(idx),
                    '--no-border',
                    '--loop=inf',
                    '--fs',
                    '--geometry={}x{}+{}+{}'.format(
                        monitor['width'],
                        monitor['height'],
                        monitor['left'],
                        monitor['top']
                    ),
                    video_path
                ]
                processes.append(subprocess.Popen(cmd))

            time.sleep(len(monitors) * 0.5)  # 增加等待时间

            # 窗口处理逻辑（需要循环处理每个显示器）
            for idx in range(len(monitors)):
                # 在窗口重定位处添加：
                print(f"显示器{idx}，目标坐标: ({monitor['left']}, {monitor['top']})")
                mpv_hwnd = win32gui.FindWindow(None, f"MPV-{idx}")

                # 查找 Progman 窗口
                progman_hwnd = win32gui.FindWindow("Progman", None)

                if not progman_hwnd:
                    print("未能找到Progman窗口。")
                    return

                # 向 Progman 窗口发送特定消息
                win32gui.SendMessageTimeout(progman_hwnd, 0x052c, 0, 0, win32con.SMTO_NORMAL, 0x3e8)

                # 查找 WorkerW 窗口
                workerw_hwnd = win32gui.FindWindowEx(progman_hwnd, 0, "WorkerW", None)

                # 查找 SHELLDLL_DefView 窗口
                defview_hwnd = win32gui.FindWindowEx(progman_hwnd, 0, "SHELLDLL_DefView", None)

                if mpv_hwnd and workerw_hwnd and defview_hwnd:
                    # 设置 MPV 窗口的父窗口为 WorkerW 窗口，并处理图标层透明
                    set_mpv_as_wallpaper(mpv_hwnd, workerw_hwnd, defview_hwnd)
                else:
                    print("未能找到 MPV 窗口、WorkerW 窗口或SHELLDLL_DefView窗口。")
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 模块: 调试面板
# 功能: 开关调试模式/测试部分功能
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def show_debug_panel():
    debug_root = maliang.Toplevel(root,title=f"小树壁纸 调试面板 | {VER}+{BUILD_VER} ({INSIDE_VER})")


    debug_root.mainloop()

### ✨ 设置面板
canvas_setting = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
#创建一个覆盖canvas_setting_pages的形状，方便观察
maliang.Text(canvas_setting_pages, (500, 100), text="从左侧选择一个项目以开始", fontsize=25, anchor="n")

# maliang.Text(canvas_setting_pages, (10, 10), text="主题", fontsize=25, anchor="nw")
# canvas_setting.place(width=1280, height=720, x=640, y=360, anchor="center")
# maliang.Switch(canvas_setting, (20, 25), command=lambda b: style.set_color_mode(
# "dark" if b else "light"), default=style.get_color_mode())
back_canvas1 = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
# back_canvas1.place(x=50, y=670,width=40,height=40,anchor="center")
back_canvas1.place(x=50, y=670,width=40,height=40,anchor="center")
maliang.Text(back_canvas1, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_canvas1.bind("<Button-1>", lambda event: main())
maliang.Text(canvas_setting, (100, 50), text="设置", fontsize=50)
# maliang.Text(canvas_setting,[1280//2, 720//2-100],text="施工中，请等待后续测试版本〜",fontsize=50, anchor="center")
changed_light_theme=False
changed_dark_theme=False
changed_font=False
dark_theme_map=0
now_font="霞鹜文楷"
window_opacity=1
def change_setting_page(page):
    global canvas_setting_pages
    global del_log,del_temp
    global data_size
    global is_checked_update
    match page:
        case 0:
            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="主题", fontsize=30, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 70), text="深/浅色模式切换", fontsize=20, anchor="nw")
            def change_color_mode(b):
                global changed_dark_theme
                changed_dark_theme=False
                theme.set_color_mode("dark" if b else "light")
            color_mode_switch = maliang.Switch(canvas_setting_pages, (20, 105), command=change_color_mode, default=theme.get_color_mode()=="dark")
            if theme.get_color_mode() == "dark":
                color_mode_switch.set(True)
            else:
                color_mode_switch.set(False)
            maliang.Text(canvas_setting_pages, (10, 140), text="自定义浅色主题", fontsize=20, anchor="nw")
            # def change_light_theme(index):
            #     global changed_light_theme,changed_dark_theme
            #     changed_light_theme=True
            #     changed_dark_theme=False
            #     match index:
            #         case 6:
            #             style.set_theme_map(light_theme=粉雕玉琢)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 5:
            #             style.set_theme_map(light_theme=原木秋色)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 0:
            #             style.set_theme_map(light_theme=国行公祭)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 4:
            #             style.set_theme_map(light_theme=粉花春色)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 3:
            #             style.set_theme_map(light_theme=中秋月下)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 1:
            #             style.set_theme_map(light_theme=欢庆春节)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 2:
            #             style.set_theme_map(light_theme=清明祭扫)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)
            #         case 7:
            #             style.set_theme_map(light_theme=黄昏蓝调)
            #             style.set_color_mode("light")
            #             color_mode_switch.set(False)

            # light_mode_choose=maliang.SegmentedButton(canvas_setting_pages, [20, 170], text=["国行公祭","欢庆春节","清明祭扫","中秋月下","粉花春色","原木秋色","粉雕玉琢","黄昏蓝调"], layout="horizontal", command=change_light_theme)
            # if changed_light_theme:

            #     light_mode_choose.set(["国行公祭","欢庆春节","清明祭扫","中秋月下","粉花春色","原木秋色","粉雕玉琢","黄昏蓝调"].index(style.get_theme_map()["light"].__name__))
            # def reset_theme_map():
            #     global changed_dark_theme,changed_light_theme
            #     nonlocal light_mode_choose,dark_theme_choose
            #     configs.Theme.reset()
            #     changed_dark_theme=False
            #     changed_light_theme=False
            #     style.set_color_mode("dark" if style.get_color_mode() else "light")
            #     style.set_color_mode("dark" if style.get_color_mode() else "light")
            #     style.set_color_mode("dark" if style.get_color_mode() else "light")
            #     style.set_color_mode("system")
            #     color_mode_switch.set(style.get_color_mode()=="dark")
            #     light_mode_choose.destroy()
            #     dark_theme_choose.destroy()
            #     light_mode_choose=maliang.SegmentedButton(canvas_setting_pages, [20, 170], text=["国行公祭","欢庆春节","清明祭扫","中秋月下","粉花春色","原木秋色","粉雕玉琢","黄昏蓝调"], layout="horizontal", command=change_light_theme)
            #     dark_theme_choose=maliang.SegmentedButton(canvas_setting_pages, (20, 290), text=("normal", "acrylic", "aero", "transparent",
            #       "optimised", "win7", "inverse", "native", "popup"), layout="horizontal",command=change_dark_theme)
            #     root.update_idletasks()
            #     canvas_setting_pages.update_idletasks()

            # maliang.Button(canvas_setting_pages, (20, 230), text="重置主题", command=lambda: reset_theme_map(),size=(1000,30))

            # TODO : 重构主题功能
            maliang.Text(canvas_setting_pages, (30, 190), text="⚠️ 当前功能暂时无法使用", fontsize=25, anchor="nw")

            maliang.Text(canvas_setting_pages, (10, 260), text="自定义特殊效果模式(部分仅限深色模式)  - 实验性功能", fontsize=20, anchor="nw")

            def change_dark_theme(index):
                global changed_dark_theme,dark_theme_map
                maliang.dialogs.TkMessage(icon="warning", title="小树壁纸-警告", message="此功能为实验性功能，可能存在一些问题，请谨慎使用！")
                changed_dark_theme=True
                match index:


                    case 1:
                        color_mode_switch.set(True)
                        theme.set_color_mode("dark")
                        theme.set_color_mode("light")
                        theme.set_color_mode("dark")
                        theme.apply_theme(window=root,theme=("normal", "acrylic", "aero", "transparent","optimised", "win7", "inverse", "native", "popup", "mica")[index])

                        theme.set_color_mode("dark")
                    case 2:
                        color_mode_switch.set(True)
                        theme.set_color_mode("dark")
                        theme.set_color_mode("light")
                        theme.set_color_mode("dark")
                        theme.apply_theme(window=root,theme=("normal", "acrylic", "aero", "transparent","optimised", "win7", "inverse", "native", "popup", "mica")[index])

                        theme.set_color_mode("dark")
                    case 3:
                        color_mode_switch.set(True)
                        theme.set_color_mode("dark")
                        theme.set_color_mode("light")
                        theme.set_color_mode("dark")
                        theme.apply_theme(window=root,theme=("normal", "acrylic", "aero", "transparent","optimised", "win7", "inverse", "native", "popup", "mica")[index])

                        theme.set_color_mode("dark")
                    case 7:
                        color_mode_switch.set(True)
                        theme.set_color_mode("dark")
                        theme.set_color_mode("light")
                        theme.set_color_mode("dark")
                        theme.apply_theme(window=root,theme=("normal", "acrylic", "aero", "transparent","optimised", "win7", "inverse", "native", "popup", "mica")[index])

                        theme.set_color_mode("dark")


                    case _:
                        color_mode_switch.set(True)
                        theme.set_color_mode("dark")
                        theme.set_color_mode("light")
                        theme.set_color_mode("dark")
                        theme.apply_theme(window=root,theme=("normal", "acrylic", "aero", "transparent","optimised", "win7", "inverse", "native", "popup", "mica")[index])

                dark_theme_map=index

            dark_theme_choose=maliang.SegmentedButton(canvas_setting_pages, (20, 290), text=("normal", "acrylic", "aero", "transparent",
                  "optimised", "win7", "inverse", "native", "popup", "mica"), layout="horizontal",command=change_dark_theme)
            dark_theme_choose.set(dark_theme_map)
            maliang.Text(canvas_setting_pages, (10, 350), text="自定义字体 - 实验性功能", fontsize=20, anchor="nw")
            def change_font(index):
                global changed_font,now_font
                nonlocal choose_font
                changed_font=True
                match index:
                    case 0:
                        maliang.configs.Font.family = "霞鹜文楷"
                        root.update()
                        root.update_idletasks()
                        canvas_setting_pages.update()
                        canvas_setting_pages.update_idletasks()
                        changed_font=False
                    case 1:
                        maliang.dialogs.TkMessage(icon="warning", title="小树壁纸-警告", message="此功能为实验性功能，可能存在一些问题，请谨慎使用！")
                        def extract_content(text):
                            # 尝试匹配中括号内的内容
                            pattern_brackets = r'\{(.*?)\}'
                            match_brackets = re.search(pattern_brackets, text)
                            if match_brackets:
                                return match_brackets.group(1)  # 返回匹配到的内容

                            # 如果没有中括号，按空格分割
                            parts = text.split()
                            if parts:
                                return parts[0]  # 返回第一个部分

                            return None  # 如果没有任何内容，返回 None

                        def change_font_dialog(font_input):
                            # print("--------------\n"+font_input+"\n--------------")
                            logging.info(f"用户选择的字体: {font_input}")
                            maliang.configs.Font.family = extract_content(font_input)
                        maliang.dialogs.TkFontChooser(master=root,command=change_font_dialog)
                        root.update_idletasks()
                        root.update_idletasks()
                        canvas_setting_pages.update()
                        canvas_setting_pages.update_idletasks()
                        choose_font.destroy()
                        choose_font = maliang.SegmentedButton(canvas_setting_pages, (20, 380), text=["霞鹜文楷",f"自定义-[{maliang.configs.Font.family}]"], layout="horizontal",command=change_font,default=1)

            if changed_font:
                choose_font = maliang.SegmentedButton(canvas_setting_pages, (20, 380), text=["霞鹜文楷",f"自定义-[{maliang.configs.Font.family}]"], layout="horizontal",command=change_font,default=1)
            else:
                choose_font = maliang.SegmentedButton(canvas_setting_pages, (20, 380), text=["霞鹜文楷","自定义-[未选择]"], layout="horizontal",command=change_font,default=0)





        case 3:

            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="数据", fontsize=30, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 50), text="清理数据", fontsize=20, anchor="nw")
            data_size = maliang.Text(canvas_setting_pages, (10, 80), text=f"缓存文件：{get_folder_size("temp"):.2f}MB | 已保存的日志数量：{get_file_count('logs')}", fontsize=20, anchor="nw")
            del_temp = maliang.Button(canvas_setting_pages, (0, 110), text="清理缓存", command=lambda: del_temp_folder(),size=(500,50))
            del_log = maliang.Button(canvas_setting_pages, (500, 110), text="清理日志", command=lambda: del_log_folder(),size=(500,50))
            maliang.Text(canvas_setting_pages, (10, 165), text="壁纸默认下载位置", fontsize=20, anchor="nw")
            path_show = maliang.Text(canvas_setting_pages, (10, 195), text=f"当前壁纸下载位置：{cog.get_value("data.download_path")}", fontsize=20, anchor="nw")
            def change_download_path():
                new_path = filedialog.askdirectory(initialdir=cog.get_value("data.download_path"),title="选择壁纸下载位置",parent=root,mustexist=True)
                if new_path:
                    logging.info(f"用户选择的新下载位置: {new_path}")
                    cog.set_value("data.download_path", new_path.replace("/","\\"))

                    # save_cog()
                    path_show.set(f"当前壁纸下载位置：{cog.get_value("data.download_path")}")
            def change_download_path_default():
                # TODO : 修改默认下载路径
                Download_Path = get_my_pictures_path()
                cog.set_value("data.download_path" , Download_Path)
                logging.info(f"恢复默认下载位置: {Download_Path}")
                path_show.set(f"当前壁纸下载位置：{Download_Path}")
                # save_cog()
            maliang.Button(canvas_setting_pages, (0, 230), text="更改下载位置", command=change_download_path, size=(1000,50))
            maliang.Button(canvas_setting_pages, (0, 280), text="恢复默认位置", command=change_download_path_default, size=(1000,50))
        case 1:
            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="窗口", fontsize=30, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 50), text="窗口大小", fontsize=20, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 80), text=f"当前窗口大小：{root.winfo_width()}x{root.winfo_height()}", fontsize=20, anchor="nw")
            # maliang.Text(canvas_setting_pages, (10, 110), text="窗口模式", fontsize=20, anchor="nw")
            # def change_window_mode(mode):
            #     global window_mode
            #     window_mode = not mode

            #     if window_mode:
            #         root.attributes("-fullscreen", True)
            #         logging.info("切换到全屏模式")
            #     else:
            #         root.attributes("-fullscreen", False)
            #         logging.info("切换到窗口模式")

            # window_mode_choose=maliang.SegmentedButton(canvas_setting_pages, (20, 140), text=["全屏", "窗口"], layout="horizontal",command=change_window_mode,default=1)
            # window_mode_choose.set(window_mode)



            t = maliang.Text(canvas_setting_pages, (10, 145), text="窗口透明度 (%d%%)" % (root.alpha()*100), fontsize=20, anchor="nw")
            def update_window_alpha(p):
                nonlocal alpha_slider
                t.texts[0].set("窗口透明度 (%d%%)" % (p * 100))
                root.alpha(p)
                if p <= 0.1:
                    root.alpha(0)
                    alpha_slider.destroy()
                    ach = maliang.Toplevel(root,[700,300],title="成就")
                    ach.iconbitmap(r"./assets/icons/ach.ico")
                    ach.center()
                    def on_closing():
                        maliang.dialogs.TkMessage(master=ach,icon="warning", title="小树壁纸-警告", message="先做出选择再离开吧！",detail="否则主窗口将无法恢复！")
                    ach.protocol("WM_DELETE_WINDOW", on_closing)
                    canvas_ach = maliang.Canvas(ach, auto_zoom=True, keep_ratio="min", free_anchor=True)
                    canvas_ach.place(x=0, y=0, width=700, height=300, anchor="nw")
                    maliang.Text(canvas_ach, (10, 10), text="达成奇怪的成就：消失的窗口", fontsize=30, anchor="nw")
                    maliang.Text(canvas_ach, (10, 60), text="呃……或许你把主窗口弄不见了", fontsize=20, anchor="nw")
                    maliang.Text(canvas_ach, (10, 90), text="这可不行哦，你还想继续玩？", fontsize=20, anchor="nw")
                    maliang.Button(canvas_ach, (10, 250), text="好吧，那就再见了", command=lambda: os._exit(0), size=(200,40))
                    def help_window():
                        nonlocal alpha_slider
                        alpha_slider=maliang.Slider(canvas_setting_pages, (10, 180), (350, 30), command=update_window_alpha, default=root.alpha())
                        alpha_slider.set(1)
                        root.alpha(1)
                        t.texts[0].set("窗口透明度 (100%) 你已经被仁慈地拯救了 (*°▽°*)")
                        ach.destroy()


                    maliang.Button(canvas_ach, (250, 250), text="救救窗口", command=help_window, size=(200,40))





            alpha_slider=maliang.Slider(canvas_setting_pages, (10, 180), (350, 30), command=update_window_alpha, default=root.alpha())
            maliang.Text(canvas_setting_pages, (10, 220), text="置顶", fontsize=20, anchor="nw")
            maliang.Switch(canvas_setting_pages, (10, 250), command=lambda s: (root.attributes("-topmost", s), logging.info(f"置顶状态: {s}")), default=root.attributes("-topmost"))
            maliang.Text(canvas_setting_pages, (100, 220), text="隐藏标题栏", fontsize=20, anchor="nw")
            maliang.Switch(canvas_setting_pages, (100, 250), command=lambda s: (root.overrideredirect(s), logging.info(f"隐藏标题栏状态: {s}")), default=root.overrideredirect())
        case 2:
            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="主页", fontsize=30, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 50), text="主页背景(实验性功能)", fontsize=20, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 80), text="当前背景：", fontsize=20, anchor="nw")
            if cog.get_value("display.window_background_image_path") == "":
                current_bg=maliang.Text(canvas_setting_pages, (100, 80), text="无", fontsize=20, anchor="nw")

            else:
                current_bg=maliang.Text(canvas_setting_pages, (100, 80), text=f"{cog.get_value("display.window_background_image_path")}", fontsize=20, anchor="nw")
            def change_bg():
                new_bg = filedialog.askopenfilename(initialdir=cog.get_value("display.window_background_image_path"),title="选择壁纸",parent=root,filetypes=[("图片文件","*.jpg;*.png;*.jpeg")])
                if new_bg:
                    logging.info(f"用户选择的壁纸: {new_bg}")

                    cog.set_value("display.window_background_image_path",new_bg)

                    current_bg.set(f"{cog.get_value("display.window_background_image_path")}")

                    # canvas_setting.create_image(0, 0, image=maliang.PhotoImage(file=cog['window_wallpaper_path']), anchor="nw")
            def change_bg_default():
                cog.set_value("display.window_background_image_path" , "")

                current_bg.set("无")
            maliang.Button(canvas_setting_pages, (0, 110), text="更改背景", command=change_bg, size=(1000,50))
            maliang.Button(canvas_setting_pages, (0, 160), text="移除背景", command=change_bg_default, size=(1000,50))
            maliang.Text(canvas_setting_pages, (10, 210), text="主页布局", fontsize=20, anchor="nw")
            def change_home_style(style):
                global cog
                match style:
                    case 0:
                        cog.set_value("home_page.style", "default")
                        # cog["home_page_style"] = "default"
                        logging.info("用户选择的主页布局: 默认")
                    case 1:
                        cog.set_value("home_page.style", "next")
                        # cog["home_page_style"] = "next"
                        logging.info("用户选择的主页布局: Next")
                    case 2:
                        cog.set_value("home_page.style", "test")
                        # cog["home_page_style"] = "new"
                        logging.info("用户选择的主页布局: 新-测试")

                # save_cog()
            df=maliang.SegmentedButton(canvas_setting_pages, (20, 240), text=["默认", "Next", "新-测试"], layout="horizontal",command=change_home_style)

            if cog.get_value("home_page.style") == "default":
                df.set(0)
            elif cog.get_value("home_page.style") == "next":
                df.set(1)


        case 4:

            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="更新", fontsize=30, anchor="nw", weight="bold")
            maliang.Text(canvas_setting_pages, (10, 300), text="启动时自动检查更新：", fontsize=20, anchor="nw")
            maliang.Switch(canvas_setting_pages, (210, 300), command=lambda s: (cog.set_value("update.enabled", s), logging.info(f"启动时自动检查更新: {s}")), default=cog.get_value("update.enabled"))
            debug_mode_button = maliang.Button(canvas_setting_pages, (430, 340), text="调试面板",command=lambda: show_debug_panel())
            maliang.Text(canvas_setting_pages, (10, 350), text="更新通道", fontsize=20, anchor="nw")
            def change_update_channel(channel):
                if channel == 0:
                    dev_warning.forget()
                    cog.set_value("update.channel", "Stable")
                    logging.info("用户选择的更新通道: Stable")
                    debug_mode_button.forget()
                else:
                    dev_warning.forget(False)
                    # maliang.dialogs.TkMessage(icon="warning", title="警告", message="开发版功能可能不稳定或存在问题，请谨慎使用！", detail="请不要在生产环境中使用开发版功能！")
                    cog.set_value("update.channel", "Dev")
                    logging.info("用户选择的更新通道: Dev")
                    debug_mode_button.forget(False)
            dev_warning=maliang.Text(canvas_setting_pages, (10, 550), text="开发版功能可能不稳定或存在问题，请谨慎使用！", fontsize=17, anchor="nw")
            choose_update_channel=maliang.ComboBox(canvas_setting_pages, (110, 340),(300,40) ,text=["Stable(稳定版，推荐)", "Dev(开发版)"], command=lambda s: change_update_channel(s))
            if cog.get_value("update.channel") == "Stable":
                choose_update_channel.set(0)
                dev_warning.forget()
                debug_mode_button.forget()
            elif cog.get_value("update.channel") == "Dev":
                choose_update_channel.set(1)
            if is_checked_update:
                maliang.Text(canvas_setting_pages, (50, 150), text=f"最新版本：{update_check_result['version']}")

            else:
                update_check_spinner = maliang.Spinner(canvas_setting_pages, (50, 150), mode="indeterminate")
                try:
                    def handle_update_result(result):
                        """更新回调函数"""
                        global is_have_update, update_check_result
                        update_check_result = result
                        update_check_spinner.forget()
                        if result["status"] == "update_available":
                            logging.info(f"发现新版本: {result['version']}")
                            is_have_update=True

                        elif result["status"] == "test_update":
                            logging.info("测试更新被触发")
                            is_have_update=True
                        elif result["status"] == "error":
                            logging.error(f"更新检查失败：{result['error_message']}")
                            maliang.TkMessage(icon="error",title="更新",message="更新检查失败",detail="详细错误信息请查看日志")
                        elif result["status"] == "no_update":
                            is_have_update=True
                            maliang.Text(canvas_setting_pages, (50, 150), text="当前已是最新版本")
                        else:
                            logging.error(f"未知的更新状态：{result}")



                    checker = UpdateChecker()
                    checker.async_check(callback=handle_update_result)

                except Exception as e:
                    logging.error(f"更新检查失败：{e}")

                    maliang.dialogs.TkMessage(icon="error",title="更新",message="更新检查失败",detail="未知错误\n详细错误信息请查看日志")


        case 5:
            canvas_setting_pages.delete("all")
            canvas_setting_pages.destroy()
            canvas_setting_pages = maliang.Canvas(canvas_setting, auto_zoom=True, keep_ratio="min", free_anchor=True)
            canvas_setting_pages.place(x=170, y=140, width=1200, height=500, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 10), text="脚本", fontsize=30, anchor="nw")
            maliang.Text(canvas_setting_pages, (10, 50), text="运行脚本", fontsize=20, anchor="nw")
            def run_script():
                script_path = filedialog.askopenfilename(title="选择脚本",parent=root,filetypes=[("小树壁纸脚本","*.lts")])
                if script_path:
                    with open(script_path, "r", encoding="utf-8") as f:
                        threading.Thread(target=script_thread, args=(f.read(),)).start()
            maliang.Button(canvas_setting_pages, (0, 80), text="选择脚本", command=run_script, size=(1000,50))
        case 6:
            about()
        case 7:
            os._exit(0)
maliang.SegmentedButton(canvas_setting, [80, 200], text=["主题", "窗口", "主页", "数据", "更新", "脚本", "关于", "退出"], layout="vertical",command=change_setting_page)
# # 设置目标宽度或高度
# base_width1 = 150
# # 计算比例并调整图片大小
# img1 = Image.open(r"./assets/images/未完成.jpg")
# w_percent1 = base_width1 / float(img1.size[0])
# h_size1 = int(float(img1.size[1]) * float(w_percent1))
# img1 = img1.resize((base_width1, h_size1), Image.Resampling.LANCZOS)
# maliang.Image(canvas_setting,[1280//2, 720//2+50],image=maliang.PhotoImage(img1))

true_del = False
def clean_folder(folder_path, exclude_list=[]):
    """
    清空指定文件夹中的所有文件和子文件夹，但排除指定的文件或文件夹

    参数:
    folder_path (str): 要清空的文件夹路径
    exclude_list (list): 要排除的文件或文件夹名称列表
    """
    logging.info(f"准备清空文件夹: {folder_path}".replace("\\","/"))
    logging.info(f"排除列表: {exclude_list}".replace("\\","/"))

    try:
        for filename in os.listdir(folder_path):
            if filename in exclude_list:
                logging.info(f"跳过排除的文件或文件夹: {filename}".replace("\\","/"))
                continue  # 跳过排除的文件或文件夹
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    logging.info(f"删除文件或链接: {file_path}".replace("\\","/"))
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    logging.info(f"删除子文件夹: {file_path}".replace("\\","/"))
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.warning(f"无法删除 {file_path}。原因: {e}".replace("\\","/"))
        logging.info(f"文件夹 {folder_path} 清理完成")
    except Exception as e:
        logging.warning(f"无法清理文件夹 {folder_path}。原因: {e}".replace("\\","/"))

def return_choice(result):
    global true_del
    logging.info(f"用户选择: {result}")
    if result == "yes":
        true_del = True
        logging.info("用户确认清理文件夹")
    else:
        true_del = False
        logging.info("用户取消清理文件夹")

def del_temp_folder():
    logging.info("请求用户确认清理缓存文件夹")
    maliang.dialogs.TkMessage(
        icon="question", title="警告",
        message="你确定要清理 缓存 文件夹吗？",
        detail="此操作不可恢复！", option="yesno",
        default="no", command=lambda result: return_choice(result)
    )
    if true_del:
        logging.info("开始清理缓存文件夹")
        del_temp.disable()
        clean_folder("temp", exclude_list=[os.path.basename(home_page_assets_path)]+occupied_file_list)
        maliang.dialogs.TkMessage(icon="info", title="完成", message="缓存清理完成！")
        del_temp.disable(False)

    else:
        logging.info("清理缓存文件夹操作已取消")

    data_size.set(f"缓存文件：{get_folder_size("temp"):.2f}MB | 已保存的日志数量：{get_file_count('logs')}")

def del_log_folder():
    logging.info("请求用户确认清理日志文件夹")
    maliang.dialogs.TkMessage(
        icon="warning", title="警告",
        message="你确定要清理 日志 文件夹吗？\n你需要知道你正在做什么! \n日志文件对于查找错误非常重要",
        detail="这是一个危险行为，请谨慎操作！", option="yesno",
        default="no", command=lambda result: return_choice(result)
    )
    if true_del:
        logging.info("开始清理日志文件夹")
        del_log.disable()
        clean_folder("logs", exclude_list=[os.path.basename(LOG_FILE)])
        maliang.dialogs.TkMessage(icon="info", title="完成", message="日志清理完成！")

        del_log.disable(False)
    else:
        logging.info("清理日志文件夹操作已取消")

    data_size.set(f"缓存文件：{get_folder_size("temp"):.2f}MB | 已保存的日志数量：{get_file_count('logs')}")


### ✨ 彩蛋
def set_eggwallpaper():
    shutil.copyfile("./assets/images/egg.jpg", "/xiaoshu_wallpaper/bk.jpg")
    set_wallpaper("/xiaoshu_wallpaper/bk.jpg")
    maliang.dialogs.TkMessage(icon="info",title="完成",message="设置成功！",detail="已将彩蛋壁纸设置为桌面背景。")
    notification.notify(
        title='壁纸设置完成',
        message='壁纸文件位于：/xiaoshu_wallpaper\n文件名：bk.jpg\n请勿删除！',
        app_icon=cog.get_value("display.window_icon_path"),
        timeout=3,
    )
canvas_egg = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
maliang.Text(canvas_egg, (100, 100), text="彩蛋", fontsize=50,anchor="center")
maliang.Text(canvas_egg, (100, 150), text="恭喜你发现了一个彩蛋！", fontsize=25, anchor="w")
canvas_artistic = maliang.Canvas(canvas_egg, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_artistic.place(x=50, y=650,width=200,height=40,anchor="nw")
maliang.Text(canvas_artistic, (60, 10), text="画师：灵楼", fontsize=20, anchor="n", underline=True)
canvas_artistic.bind("<Button-1>", lambda event: webbrowser.open("https://space.bilibili.com/3546659155871883"))
back_egg = maliang.Canvas(canvas_egg, auto_zoom=True, keep_ratio="min", free_anchor=True)
back_egg.place(x=1200, y=50,width=40,height=50,anchor="center")
maliang.Text(back_egg, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_egg.bind("<Button-1>", lambda event: main())
set_wallpaper_egg_icon = maliang.Canvas(canvas_egg, auto_zoom=True, keep_ratio="min", free_anchor=True)
set_wallpaper_egg_icon.place(x=1200, y=150,width=40,height=50,anchor="center")
maliang.Text(set_wallpaper_egg_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
set_wallpaper_egg_icon.bind("<Button-1>", lambda event: set_eggwallpaper())
maliang.Text(canvas_egg, (1170, 190), text="设为壁纸", fontsize=15, anchor="w")
# 打开图片
img = Image.open(r"./assets/images/egg.jpg")
# 设置目标宽度或高度
base_width = 300
# 计算比例并调整图片大小
w_percent = base_width / float(img.size[0])
h_size = int(float(img.size[1]) * float(w_percent))
img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
maliang.Image(canvas_egg, (200, 400), image=maliang.PhotoImage(img), anchor="center")

### ✨ 关于面板
canvas_about = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
# canvas_about.place(width=1280, height=720, x=640, y=360, anchor="center")
back_canvas=maliang.Canvas(canvas_about)
back_canvas.place(x=50, y=670,width=40,height=40,anchor="center")
maliang.Text(back_canvas, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_canvas.bind("<Button-1>", lambda event: main())
maliang.Text(canvas_about, (100, 100), text="关于", fontsize=50, anchor="center")
maliang.Text(canvas_about, (100, 150), text="小树壁纸", fontsize=35, anchor="w")
maliang.Text(canvas_about, (100, 185), text=f"{VER}(内部版本号：{INSIDE_VER})", fontsize=20, anchor="w")
maliang.Text(canvas_about, (100, 250), text="制作：小树\n出品：小树工作室\n感谢所有参与测试的人！\n\n本程序基于AGPL-3.0 license开源", fontsize=20, anchor="nw")
open_source=maliang.Text(canvas_about, (100, 385), text="感谢开源项目maliang:https://github.com/Xiaokang2022/maliang\n本程序仅供个人学习交流使用，请勿用于商业用途！", fontsize=20, anchor="nw")
canvas_about.tag_bind(open_source, "<Button-1>", lambda event: webbrowser.open("https://github.com/Xiaokang2022/maliang"))
back_about = maliang.Canvas(canvas_about, auto_zoom=True, keep_ratio="min", free_anchor=True)
back_about.place(x=50, y=670,width=40,height=40,anchor="center")
maliang.Text(back_about, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_about.bind("<Button-1>", lambda event: main())

### ✨ 壁纸面板
wallpaper_path = "./assets/images/no_images.jpg"
canvas_wallpaper = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
# canvas_wallpaper_more = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
# canvas_wallpaper_more.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_unsplash = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_wallpaper_more_unsplash.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_wallhaven = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_wallpaper_more_wallhaven.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_erciyuan = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_wallpaper_more_erciyuan.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_fengjing = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_wallpaper_more_fengjing.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_360 = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_wallpaper_more_360.place(x=640, y=205,width=1280,height=395,anchor="n")
canvas_wallpaper_more_360_download = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
# 1280x720
# canvas_wallpaper.place(width=1280, height=720, x=640, y=360, anchor="center")
maliang.Text(canvas_wallpaper, (50, 50), text="壁纸源", fontsize=50,anchor="nw")
back_wallpaper = maliang.Canvas(canvas_wallpaper, auto_zoom=True, keep_ratio="min", free_anchor=True)
back_wallpaper.place(x=50, y=670,width=40,height=40,anchor="center")
maliang.Text(back_wallpaper, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_wallpaper.bind("<Button-1>", lambda event: main())
canvas_wallpaper_detail=maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
#### 壁纸面板-壁纸详情
def wallpaper_detail(*args):
    canvas_wallpaper.place_forget()
    def save_as():
        file_path = filedialog.asksaveasfilename(title="保存壁纸", filetypes=[("图片文件", os.path.splitext(wallpaper_path)[1])])
        if file_path:
            shutil.copyfile(wallpaper_path, file_path)
            os.system(f"explorer.exe /select,\"{file_path.replace("/","\\")}\"")

            notification.notify(
                title='壁纸保存成功',
                message=f'壁纸文件已保存至{file_path}\n文件名：{os.path.basename(file_path)}'.replace("\\","/"),
                app_icon=cog.get_value("display.window_icon_path"),
                timeout=3,
            )
    def download():
        shutil.copyfile(wallpaper_path, f"{cog.get_value("data.download_path")}\\{os.path.basename(wallpaper_path)}")
        os.system(f"explorer.exe /select,\"{cog.get_value("data.download_path")}\\{os.path.basename(wallpaper_path)}\"")
        notification.notify(
            title='壁纸下载完成',
            message=f'壁纸文件已保存至{cog.get_value("data.download_path")}\n文件名：{os.path.basename(wallpaper_path)}'.replace("\\","/"),
            app_icon=cog.get_value("display.window_icon_path"),
            timeout=3,
        )
    def copy_wallpaper():

        copy_image_to_clipboard(wallpaper_path)
        notification.notify(
            title='壁纸复制成功',
            message='壁纸文件已复制到剪贴板啦~',
            app_icon=cog.get_value("display.window_icon_path"),
            timeout=3,
        )
    def _set_wallpaper():
        copy_and_set_wallpaper(wallpaper_path)

        notification.notify(
            title='壁纸设置完成',
            message=f'壁纸文件位于：{WALLPAPER_PATH}\n文件名：{os.path.basename(wallpaper_path)}\n请勿删除！'.replace("\\","/"),
            app_icon=cog.get_value("display.window_icon_path"),
            timeout=3,
        )
    def set_background():
        shutil.copyfile(wallpaper_path, f"./assets/images/background.{os.path.basename(wallpaper_path).split('.')[-1]}")
        cog.set_value("display.window_background_image_path" , f"./assets/images/background.{os.path.basename(wallpaper_path).split('.')[-1]}")
        # save_cog()
        # notify=maliang.Toplevel(root,size=(300,100),title="提示",position=(10,10))
        notification.notify(
            title='壁纸设置成功',
            message='壁纸文件已设置为主页背景！',
            app_icon=cog.get_value("display.window_icon_path"),
            timeout=3,
        )
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # canvas_wallpaper.delete("all")
    canvas_wallpaper_detail.place_forget()
    canvas_wallpaper_detail.delete("all")
    canvas_wallpaper_detail.place(x=640, y=720//2,width=1280,height=720,anchor="center")
    maliang.Text(canvas_wallpaper_detail, (80, 50), text="壁纸详情", fontsize=50,anchor="nw")
    back_wallpaper_detail = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    back_wallpaper_detail.place(x=50, y=670,width=40,height=40,anchor="center")
    maliang.Text(back_wallpaper_detail, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    back_wallpaper_detail.bind("<Button-1>", lambda event: wallpaper())
    # maliang.Text(canvas_wallpaper_detail, (100, 150), text="壁纸来源：", fontsize=30,anchor="nw")
    # maliang.Text(canvas_wallpaper_detail, (100, 200), text="Unsplash", fontsize=30,anchor="nw")
    # maliang.Text(canvas_wallpaper_detail, (100, 250), text="Wallhaven", fontsize=30,anchor="nw")
    maliang.Image(canvas_wallpaper_detail,[80,120],image=resize_image(wallpaper_path,300),anchor="nw")

    # maliang.Button(canvas_wallpaper_detail, (100, 600), text="设为壁纸", command=lambda: copy_and_set_wallpaper(wallpaper_path))

    set_w_bing_icon = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    set_w_bing_icon.place(x=1230, y=670,width=40,height=50,anchor="center")
    maliang.Text(set_w_bing_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    set_w_bing_icon.bind("<Button-1>", lambda event: _set_wallpaper())
    maliang.Text(canvas_wallpaper_detail,(1230, 705),text="设为壁纸",fontsize=15,anchor="center")
    ll_icon = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    ll_icon.place(x=1150, y=670,width=40,height=50,anchor="center")
    maliang.Text(ll_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    ll_icon.bind("<Button-1>", lambda event: save_as())
    maliang.Text(canvas_wallpaper_detail,(1150, 705),text="另存为",fontsize=15,anchor="center")
    dd_icon = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    dd_icon.place(x=1070, y=670,width=40,height=50,anchor="center")
    maliang.Text(dd_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    dd_icon.bind("<Button-1>", lambda event: download())
    maliang.Text(canvas_wallpaper_detail,(1070, 705),text="下载",fontsize=15,anchor="center")
    copy_w_bing_icon = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    copy_w_bing_icon.place(x=990, y=670,width=40,height=50,anchor="center")
    maliang.Text(copy_w_bing_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    copy_w_bing_icon.bind("<Button-1>", lambda event: copy_wallpaper())
    maliang.Text(canvas_wallpaper_detail,(990, 705),text="复制",fontsize=15,anchor="center")
    set_background_icon = maliang.Canvas(canvas_wallpaper_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
    set_background_icon.place(x=910, y=670,width=40,height=50,anchor="center")
    maliang.Text(set_background_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
    set_background_icon.bind("<Button-1>", lambda event: set_background())
    maliang.Text(canvas_wallpaper_detail,(910, 705),text="设为主页背景",fontsize=15,anchor="center")
    canvas_wallpaper_detail.create_text(80, 450,text="",font=("Segoe Fluent lcons",25),anchor="nw",fill="red")
    maliang.Text(canvas_wallpaper_detail,(110, 440),text="版权警告：图片仅供作为壁纸使用，禁止用于其他用途\n小树壁纸不提供任何图片在线存储服务，图片源自网络，如出现任何违法违规行为请及时联系我们",fontsize=23,anchor="nw")

    # maliang.Text(canvas_wallpaper_detail, (100, 650), text="壁纸来源：", fontsize=30,anchor="nw")

#### 壁纸面板-Unsplash源
# def wallpaper_unsplash():
#     # global wallpaper_source_name
#     # wallpaper_source_name=value
#     # canvas_wallpaper_more.delete("all")
#     canvas_wallpaper_more_erciyuan.place_forget()
#     canvas_wallpaper_more_wallhaven.place_forget()
#     canvas_wallpaper_more_fengjing.place_forget()
#     canvas_wallpaper_more_unsplash.place(x=640, y=205,width=1280,height=395,anchor="n")
#     wallpaper_choose_button.set(0)
#     def random_size():
#         global unsplash_size
#         unsplash_size=0
#     def unsplash_1080P():
#         global unsplash_size
#         unsplash_size=1
#     def download_wallpaper():
#         if unsplash_size:
#             url = f"https://source.unsplash.com/random/1920x1080/"
#         else:
#             url = f"https://source.unsplash.com/random"
#     maliang.SegmentedButton(canvas_wallpaper_more_unsplash, (100, 25),text= ["随机大小","1920x1080"], commands=(random_size, unsplash_1080P), default=0)
#     maliang.Button(canvas_wallpaper_more_unsplash, (450, 30), text="获取数据", command=lambda: download_wallpaper())

#### 壁纸面板-聚合源通用下载

def download_wallpaper(type_name):
    global wallpaper_path
    global api_url
    canvas_download.delete("all")
    canvas_download.place_forget()
    canvas_download.place(x=640, y=205, width=1280, height=395, anchor="n")

    def long_running_task1(type_name=type_name):
        global wallpaper_path
        try:
            url = api_url
            root.update_idletasks()

            headers = {
                'User-Agent': UA
            }

            s = requests.Session()
            s.headers.update(headers)

            for attempt in range(3):
                resp = s.get(url, stream=True, allow_redirects=True)
                if resp.status_code == 200:
                    break
                elif resp.status_code == 521:
                    logging.warning(f"第 {attempt + 1} 次尝试下载失败，状态码：{resp.status_code}")
                    time.sleep(1)  # 等待一段时间后重试
                else:
                    raise Exception(f"下载失败，状态码：{resp.status_code}")

            if resp.status_code != 200:
                raise Exception(f"下载失败，状态码：{resp.status_code}")

            content_type = resp.headers.get('Content-Type')
            guessed_type = mimetypes.guess_extension(content_type)
            if not guessed_type:
                guessed_type = ".webp"  # 默认文件扩展名

            filename = f"./temp/{type_name}_{time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())}{guessed_type.lower()}"

            # print(filename)
            # wallpaper_path = filename

            # 确保临时目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            logging.info(f"开始下载 {filename}")
            if int(resp.headers.get('content-length', 0)) == 0:  # 未知文件大小
                total_size = None
                animation.Animation(2000, animation.smooth, callback=pb1.set,
                    fps=60, repeat=math.inf).start(delay=1500)
            else:
                # pb1.set(0)  # 进度条置零
                total_size = int(resp.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 512

            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size:
                            progress = downloaded_size / total_size * 100
                            pb1.set(progress)  # 更新进度条

                        root.update_idletasks()  # 刷新界面

            logging.info("下载完成！")
            wallpaper_path=change_file_extension(filename,determine_image_format(filename))

            canvas_download.place_forget()
            wallpaper_detail()

        except Exception as e:
            logging.error(f"下载失败: {e}")

            maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
            canvas_download.place_forget()
            wallpaper()  # 返回壁纸页面

    def start_task1(*args):
        root.after(1000, long_running_task1)

    canvas_detail.place_forget()
    canvas_download.place(width=1280, height=720, x=640, y=360, anchor="center")
    maliang.Text(canvas_download, (100, 100), text="正在下载...", fontsize=50, anchor="nw")
    # global pb1
    pb1 = maliang.ProgressBar(canvas_download, (420, 260), (380, 8))

    start_task1()
#### 壁纸面板-Wallhaven源
def wallpaper_wallhaven():
    # global wallpaper_source_name
    # wallpaper_source_name=value
    # canvas_wallpaper_more.delete("all")
    global api_url
    canvas_wallpaper_more_unsplash.place_forget()
    canvas_wallpaper_more_erciyuan.place_forget()
    canvas_wallpaper_more_fengjing.place_forget()
    canvas_wallpaper_more_360.place_forget()
    canvas_wallpaper_more_wallhaven.place(x=640, y=205,width=1280,height=395,anchor="n")
    wallpaper_choose_button.set(0)
    api_url="https://api.nguaduot.cn/wallhaven/random"
    def random_wallhaven():
        global api_url
        api_url="https://api.nguaduot.cn/wallhaven/random"
    def today_wallhaven():
        global api_url
        api_url="https://api.nguaduot.cn/wallhaven/today"
    def ch_return(ch1):
        (random_wallhaven, today_wallhaven)[ch1]()
    maliang.SegmentedButton(canvas_wallpaper_more_wallhaven, (100, 25),text= ["随机","每日"], command=ch_return, default=0)
    maliang.Button(canvas_wallpaper_more_wallhaven, (450, 30), text="获取数据", command=lambda: download_wallpaper("wallhaven"))

#### 壁纸面板-风景源
def wallpaper_风景():
    global api_url
    # global wallpaper_source_name
    # wallpaper_source_name=value
    # canvas_wallpaper_more.delete("all")
    canvas_wallpaper_more_unsplash.place_forget()
    canvas_wallpaper_more_wallhaven.place_forget()
    canvas_wallpaper_more_erciyuan.place_forget()
    canvas_wallpaper_more_360.place_forget()
    canvas_wallpaper_more_fengjing.place(x=640, y=205,width=1280,height=395,anchor="n")
    api_url="https://api.mmp.cc/api/pcwallpaper?category=landspace&type=jpg"
    def 风景_ch(ch1):
        global api_url
        match ch1:
            case 0:
                api_url="https://api.mmp.cc/api/pcwallpaper?category=landspace&type=jpg"
            case 1:
                api_url="https://tu.ltyuanfang.cn/api/fengjing.php"
            # case 2:
            #     api_url="https://api.dujin.org/pic/fengjing"
    maliang.SegmentedButton(canvas_wallpaper_more_fengjing, (100, 25),text= ["远梦接口","远方接口"], command=风景_ch, default=0)
    maliang.Button(canvas_wallpaper_more_fengjing, (450, 30), text="获取数据", command=lambda: download_wallpaper("landscape"))

#### 壁纸面板-二次元源
def wallpaper_二次元():
    global wallpaper_path
    global api_url
    # global wallpaper_source_name
    # wallpaper_source_name=value
    global is_choose
    if is_choose is not None:
        is_choose.destroy()
    # canvas_wallpaper_more.delete("all")
    canvas_wallpaper_more_unsplash.place_forget()
    canvas_wallpaper_more_wallhaven.place_forget()
    canvas_wallpaper_more_fengjing.place_forget()
    canvas_wallpaper_more_360.place_forget()
    canvas_wallpaper_more_erciyuan.place(x=640, y=205,width=1280,height=395,anchor="n")
    api_url="https://api.paugram.com/wallpaper/?source=sm"
    def paul_wallpaper():
        global is_choose,canvas_wallpaper_more_erciyuan,api_url
        api_url="https://api.paugram.com/wallpaper/?source=sm"
        if is_choose is not None:
            is_choose.destroy()

        def paul_ch(ch1):
            global api_url
            match ch1:
                case 0:
                    api_url="https://api.paugram.com/wallpaper/?source=sm"
                case 1:
                    api_url="https://api.paugram.com/wallpaper/?source=github"

        is_choose=maliang.SegmentedButton(canvas_wallpaper_more_erciyuan, (100, 75),text= ["sm.ms-白底动漫","github.io-白底动漫"], command=paul_ch, default=0)
    def ciyuan_wallpaper():
        global is_choose,canvas_wallpaper_more_erciyuan,api_url
        api_url="https://t.mwm.moe/pc"
        if is_choose is not None:
            is_choose.destroy()
        def ciyuan_ch(ch1):
            global api_url
            match ch1:
                case 0:
                    api_url="https://t.mwm.moe/pc"
                case 1:
                    api_url="https://t.mwm.moe/ysz"
                case 2:
                    api_url="https://t.mwm.moe/ai"
                case 3:
                    api_url="https://t.mwm.moe/fj"
                case 4:
                    api_url="https://t.mwm.moe/xhl"
                case 5:
                    api_url="https://t.mwm.moe/moe"

        is_choose=maliang.SegmentedButton(canvas_wallpaper_more_erciyuan, (100, 75),text= ["随机","原神","AI生成","风景","小狐狸","萌图"], command=ciyuan_ch, default=0)
    def other_wallpaper():
        global is_choose,canvas_wallpaper_more_erciyuan,api_url
        api_url="https://api.imlcd.cn/bg/acg.php"
        if is_choose is not None:
            is_choose.destroy()
        def other_wallpaper_ch(ch1):
            global api_url
            match ch1:
                case 0:
                    api_url="https://api.imlcd.cn/bg/acg.php"
                case 1:
                    api_url="https://img.paulzzh.com/touhou/random"
                case 2:
                    api_url="https://www.dmoe.cc/random.php"
                case 3:
                    api_url="https://image.anosu.top/pixiv/direct"
                case 4:
                    api_url=random.choice(["https://i.postimg.cc/zf2yRGXj/image.jpg","https://i.postimg.cc/ZRjVN3vQ/image.jpg","https://i.postimg.cc/FRVG56y8/4b290f6e-b886-effb-b9b1-4a97bbeea0fe.jpg","https://i.postimg.cc/3RZMSndJ/a3cde8b4-0197-1ad3-3760-9cb95dbc6517.jpg","https://i.postimg.cc/02RWMpQV/ea0ff1ca-0358-4fca-b2bb-5b3a51706bdc.jpg","https://i.postimg.cc/qRttT6HK/f5fd0dc2722faf65c455943574b087863546706878663505.jpg","https://i.postimg.cc/0NZ9J3vB/ss-f1ba762ccb2918909b05051891316f27ecbbb245-1920x1080.jpg"])
        is_choose=maliang.SegmentedButton(canvas_wallpaper_more_erciyuan, (100, 75),text= ["[忆云]随机","[PAULZZH]东方","[樱花]随机","[Anosu]Pixiv精选","[个人收集]饿殍：明末千里行"], command=other_wallpaper_ch, default=0)


    def 二次元_ch(ch1):
        global api_url
        match ch1:
            case 0:
                paul_wallpaper()
            case 1:
                ciyuan_wallpaper()
            case 2:
                other_wallpaper()
        # print(bing_data)
    maliang.SegmentedButton(canvas_wallpaper_more_erciyuan, (100, 25),text=["保罗源", "次元源","其他源"], command=二次元_ch, default=0)
    # maliang.SegmentedButton(canvas_wallpaper_more, (100, 25),layout="vertical",text=["[保罗]sm.ms-动漫", "[保罗]github.io-动漫", "[次元]原神","[次元]随机","[次元]AI生成","[次元]风景","[次元]小狐狸","[次元]萌图","[樱花]随机","[PAULZZH]东方"], commands=(), default=0)
    is_choose=None
    paul_wallpaper()
    maliang.Button(canvas_wallpaper_more_erciyuan, (600, 30), text="获取数据", command=lambda: download_wallpaper("anime"))

def wallpaper_360():
    global api_url,tid
    canvas_wallpaper_more_unsplash.place_forget()
    canvas_wallpaper_more_wallhaven.place_forget()
    canvas_wallpaper_more_fengjing.place_forget()
    canvas_wallpaper_more_erciyuan.place_forget()
    canvas_wallpaper_more_360.place(x=640, y=205,width=1280,height=395,anchor="n")
    tid=67
    # print(123456)
    # 精选 tid=67
    # 风景 tid=1
    # 宠物 tid=2
    # 动漫 tid=92
    # 插画 tid=62
    # 游戏 tid=109
    # 风格 tid=6
    # 科幻 tid=4
    # 美女 tid=70
    # 色系 tid=9
    # 汽车 tid=5
    # 影视 tid=86
    def wallpaper_360_get(ch):
        global tid

        match ch:
            case 0:
                tid=67
            case 1:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=1&page={pages.get()}&uid=0"
                tid=1
            case 2:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=2&page={pages.get()}&uid=0"
                tid=2
            case 3:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=92&page={pages.get()}&uid=0"
                tid=92
            case 4:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=62&page={pages.get()}&uid=0"
                tid=62
            case 5:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=109&page={pages.get()}&uid=0"
                tid=109
            case 6:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=6&page={pages.get()}&uid=0"
                tid=6
            case 7:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=4&page={pages.get()}&uid=0"
                tid=4
            case 8:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=70&page={pages.get()}&uid=0"
                tid=70
            case 9:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=9&page={pages.get()}&uid=0"
                tid=9
            case 10:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=5&page={pages.get()}&uid=0"
                tid=5
            case 11:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=86&page={pages.get()}&uid=0"
                tid=86
            case _:
                # data_url=f"https://mini.browser.360.cn/newtab/imgsx?tid=67&page={pages.get()}&uid=0"
                tid=67
        # print(ch,tid)
    def download_306_wallpaper():
        global wallpaper_360_path_list,tid
        canvas_wallpaper.place_forget()
        canvas_wallpaper_more_360.place_forget()
        canvas_wallpaper_more_360_download.place(x=0, y=0,width=1280,height=720,anchor="nw")
        canvas_wallpaper_more_360_download.delete("all")
        def back_to_360():
            canvas_wallpaper.place(width=1280, height=720, x=640, y=360, anchor="center")
            canvas_wallpaper_more_360.place(x=640, y=205,width=1280,height=395,anchor="n")
            canvas_wallpaper_more_360_download.place_forget()
            canvas_wallpaper_more_360_download.delete("all")
        maliang.Text(canvas_wallpaper_more_360_download, (100, 100), text="正在初步获取数据...", fontsize=50, anchor="nw")
        if pages.get().isdigit() is not True or int(pages.get()) < 1:
            canvas_wallpaper_more_360_download.delete("all")
            maliang.Text(canvas_wallpaper_more_360_download, (100, 100), text="错误", fontsize=50, anchor="nw")
            maliang.Text(canvas_wallpaper_more_360_download, (100, 180), text="页码必须为正整数数字！", fontsize=30, anchor="nw")
            # maliang.dialogs.TkMessage("页码必须为整数数字！", title="错误", icon="error")
            maliang.Button(canvas_wallpaper_more_360_download, (1150, 620), text="返回", command=back_to_360)
            # ch_360.set(0)
            return

        # if int(pages.get()) < 1:
        #     canvas_wallpaper_more_360_download.delete("all")
        #     maliang.Text(canvas_wallpaper_more_360_download, (100, 100), text="错误", fontsize=50, anchor="nw")
        #     maliang.Text(canvas_wallpaper_more_360_download, (100, 180), text="页码必须为大于等于1的整数数字！", fontsize=30, anchor="nw")
        #     # maliang.dialogs.TkMessage("页码必须为大于等于1的整数数字！", title="错误", icon="error")
        #     maliang.Button(canvas_wallpaper_more_360_download, (1150, 620), text="返回", command=back_to_360)
        #     # ch_360.set(0)
        #     return
        # global api_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
        }
        reponse = requests.get(f"https://mini.browser.360.cn/newtab/imgsx?tid={tid}&page={pages.get()}&uid=0", headers=headers)
        # print(tid)
        # print(reponse.text)

        if reponse.status_code == 200:
            json_data = reponse.json()

            if json_data["data"]["total_page"] < int(pages.get()):
                canvas_wallpaper_more_360_download.delete("all")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 100), text="错误", fontsize=50, anchor="nw")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 180), text="页码超出范围", fontsize=30, anchor="nw")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 220), text=f"请求页码:{pages.get()} | 最大页码:{json_data['data']['total_page']}", fontsize=25, anchor="nw")
                # maliang.dialogs.TkMessage("页码超出范围！", title="错误", icon="error")
                maliang.Button(canvas_wallpaper_more_360_download, (1150, 620), text="返回", command=back_to_360)
                # ch_360.set(0)
                return
            else:
                canvas_wallpaper_more_360_download.delete("all")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 100), text="详细数据获取成功", fontsize=50, anchor="nw")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 180), text=f"请求页码:{pages.get()} | 最大页码:{json_data['data']['total_page']}", fontsize=25, anchor="nw")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 220), text=f"本页共{len(json_data['data']['list'])}张图片", fontsize=25, anchor="nw")
                maliang.Text(canvas_wallpaper_more_360_download, (100, 260), text="正在下载图片...", fontsize=25, anchor="nw")

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
                }
                file_name_prefix = f"360_{time.strftime('%Y%m%d %H%M%S')}"
                completed_files = 0
                total_files = len(json_data['data']['list'])
                wallpaper_360_path_list=[]
                # print(list(range(total_files + 1)))
                logging.info(f"开始下载 {total_files} 个文件")
                def update_progress():
                    nonlocal completed_files
                    # 增加已完成文件数量
                    completed_files += 1

                    # 计算总进度
                    progress = completed_files / total_files
                    logging.info(f"已完成 {completed_files} / {total_files}，进度 {progress:.2%}")
                    # print(progress)
                    # 更新进度条
                    pb1.set(progress)
                    def change_img(img_index):
                        nonlocal now_show_img

                        img_show_360.set(resize_image(wallpaper_360_path_list[img_index],270))
                        now_show_img=wallpaper_360_path_list[img_index]
                    if progress >= 1:
                        canvas_wallpaper_more_360_download.delete("all")
                        maliang.Text(canvas_wallpaper_more_360_download, (100, 50), text="下载完成", fontsize=50, anchor="nw")
                        maliang.Text(canvas_wallpaper_more_360_download, (100, 130), text=f"请求页码:{pages.get()} | 最大页码:{json_data['data']['total_page']}", fontsize=25, anchor="nw")
                        maliang.Text(canvas_wallpaper_more_360_download, (100, 170), text=f"本页共{total_files}张图片", fontsize=25, anchor="nw")
                        maliang.SegmentedButton(canvas_wallpaper_more_360_download,[100, 210],text=list(range(1,total_files + 1)),command=lambda x: change_img(x),default=0)
                        img_show_360=maliang.Image(canvas_wallpaper_more_360_download, (100, 300), image=resize_image(wallpaper_360_path_list[0], 270), anchor="nw")
                        now_show_img=wallpaper_360_path_list[0]
                        def save_as():
                            file_path = filedialog.asksaveasfilename(title="保存壁纸", filetypes=[("图片文件", os.path.splitext(now_show_img)[1])])
                            if file_path:
                                shutil.copyfile(now_show_img, file_path)
                                os.system(f"explorer.exe /select,\"{file_path.replace("/","\\")}\"")

                                notification.notify(
                                    title='壁纸保存成功',
                                    message=f'壁纸文件已保存至{file_path}\n文件名：{os.path.basename(file_path)}'.replace("\\","/"),
                                    app_icon=cog.get_value("display.window_icon_path"),
                                    timeout=3,
                                )
                        def download():
                            shutil.copyfile(now_show_img, f"{cog.get_value("data.download_path")}\\{os.path.basename(now_show_img)}")
                            os.system(f"explorer.exe /select,\"{cog.get_value("data.download_path")}\\{os.path.basename(now_show_img)}\"")
                            notification.notify(
                                title='壁纸下载完成',
                                message=f'壁纸文件已保存至{cog.get_value("data.download_path")}\n文件名：{os.path.basename(now_show_img)}'.replace("\\","/"),
                                app_icon=cog.get_value("display.window_icon_path"),
                                timeout=3,
                            )
                        def copy_wallpaper():

                            copy_image_to_clipboard(now_show_img)
                            notification.notify(
                                title='壁纸复制成功',
                                message='壁纸文件已复制到剪贴板啦~',
                                app_icon=cog.get_value("display.window_icon_path"),
                                timeout=3,
                            )
                        def _set_wallpaper():
                            copy_and_set_wallpaper(now_show_img)

                            notification.notify(
                                title='壁纸设置完成',
                                message=f'壁纸文件位于：{WALLPAPER_PATH}\n文件名：{os.path.basename(now_show_img)}\n请勿删除！'.replace("\\","/"),
                                app_icon=cog.get_value("display.window_icon_path"),
                                timeout=3,
                            )
                        def go_back_wallpaper():
                            logging.info("从360壁纸返回壁纸选择页面")

                            if cog.get_value("data.clear_cache_when_360_back"):
                                logging.info("需要强制清理缓存")
                                clean_folder("./temp", [os.path.basename(home_page_assets_path)]+occupied_file_list)
                            back_wallpaper_detail.destroy()
                            set_w_bing_icon.destroy()
                            ll_icon.destroy()
                            dd_icon.destroy()
                            copy_w_bing_icon.destroy()
                            canvas_wallpaper_more_360_download.place_forget()
                            canvas_wallpaper_more_360_download.delete("all")
                            wallpaper()
                        ImageFile.LOAD_TRUNCATED_IMAGES = True

                        # maliang.Text(canvas_wallpaper_more_360_download, (80, 50), text="壁纸详情", fontsize=50,anchor="nw")
                        back_wallpaper_detail = maliang.Canvas(canvas_wallpaper_more_360_download, auto_zoom=True, keep_ratio="min", free_anchor=True)
                        back_wallpaper_detail.place(x=50, y=670,width=40,height=40,anchor="center")
                        maliang.Text(back_wallpaper_detail, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
                        back_wallpaper_detail.bind("<Button-1>", lambda event: go_back_wallpaper())

                        set_w_bing_icon = maliang.Canvas(canvas_wallpaper_more_360_download, auto_zoom=True, keep_ratio="min", free_anchor=True)
                        set_w_bing_icon.place(x=1230, y=670,width=40,height=50,anchor="center")
                        maliang.Text(set_w_bing_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
                        set_w_bing_icon.bind("<Button-1>", lambda event: _set_wallpaper())
                        maliang.Text(canvas_wallpaper_more_360_download,(1230, 705),text="设为壁纸",fontsize=15,anchor="center")
                        ll_icon = maliang.Canvas(canvas_wallpaper_more_360_download, auto_zoom=True, keep_ratio="min", free_anchor=True)
                        ll_icon.place(x=1150, y=670,width=40,height=50,anchor="center")
                        maliang.Text(ll_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
                        ll_icon.bind("<Button-1>", lambda event: save_as())
                        maliang.Text(canvas_wallpaper_more_360_download,(1150, 705),text="另存为",fontsize=15,anchor="center")
                        dd_icon = maliang.Canvas(canvas_wallpaper_more_360_download, auto_zoom=True, keep_ratio="min", free_anchor=True)
                        dd_icon.place(x=1070, y=670,width=40,height=50,anchor="center")
                        maliang.Text(dd_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
                        dd_icon.bind("<Button-1>", lambda event: download())
                        maliang.Text(canvas_wallpaper_more_360_download,(1070, 705),text="下载",fontsize=15,anchor="center")
                        copy_w_bing_icon = maliang.Canvas(canvas_wallpaper_more_360_download, auto_zoom=True, keep_ratio="min", free_anchor=True)
                        copy_w_bing_icon.place(x=990, y=670,width=40,height=50,anchor="center")
                        maliang.Text(copy_w_bing_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
                        copy_w_bing_icon.bind("<Button-1>", lambda event: copy_wallpaper())
                        maliang.Text(canvas_wallpaper_more_360_download,(990, 705),text="复制",fontsize=15,anchor="center")

                        canvas_wallpaper_more_360_download.create_text(80, 575,text="",font=("Segoe Fluent lcons",25),anchor="nw",fill="red")
                        maliang.Text(canvas_wallpaper_more_360_download,(110, 570),text="版权警告：图片仅供作为壁纸使用，禁止用于其他用途",fontsize=23,anchor="nw")

                def long_running_task1():
                    global wallpaper_360_path_list
                    try:
                        for i in range(len(json_data['data']['list'])):
                            url = json_data['data']['list'][i]["img"]


                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
                            }

                            s = requests.Session()
                            s.headers.update(headers)

                            for attempt in range(3):
                                resp = s.get(url, stream=True)
                                if resp.status_code == 200:
                                    break
                                elif resp.status_code == 521:
                                    logging.warning(f"第 {attempt + 1} 次尝试下载失败，状态码：{resp.status_code}")
                                    time.sleep(1)  # 等待一段时间后重试
                                else:
                                    raise Exception(f"下载失败，状态码：{resp.status_code}")

                            if resp.status_code != 200:
                                raise Exception(f"下载失败，状态码：{resp.status_code}")

                            content_type = resp.headers.get('Content-Type')
                            guessed_type = mimetypes.guess_extension(content_type)
                            if not guessed_type:
                                guessed_type = ".webp"  # 默认文件扩展名

                            filename = f"./temp/{file_name_prefix}_{i}{guessed_type}"
                            wallpaper_360_path_list.append(filename)

                            # 确保临时目录存在
                            os.makedirs(os.path.dirname(filename), exist_ok=True)

                            logging.info(f"开始下载 {filename}")

                            # total_size = int(resp.headers.get('content-length', 0))
                            downloaded_size = 0
                            chunk_size = 512

                            with open(filename, "wb") as f:
                                for chunk in resp.iter_content(chunk_size=chunk_size):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded_size += len(chunk)

                                        root.update_idletasks()

                            logging.info("下载完成！")
                            update_progress()
                            root.update_idletasks()  # 刷新界面
                            # canvas_download.place_forget()
                            # wallpaper_detail()

                    except Exception as e:
                        logging.error(f"下载失败: {e}")

                        maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
                        # canvas_download.place_forget()
                        canvas_wallpaper_more_360_download.place_forget()
                        canvas_wallpaper_more_360_download.delete("all")
                        wallpaper()  # 返回壁纸页面


                root.after(1000, long_running_task1)


                # global pb1
                pb1 = maliang.ProgressBar(canvas_wallpaper_more_360_download, (100, 330), (600, 8))

                # pb1.set(1)
    maliang.SegmentedButton(canvas_wallpaper_more_360, (100, 25),text= ["精选","风景","动物","动漫","插画","游戏","风格","科幻","美女","色系","汽车","影视"], command=wallpaper_360_get, default=0)
    maliang.Text(canvas_wallpaper_more_360, (100, 100), text="输入页码：", fontsize=20, anchor="nw")
    pages=maliang.InputBox(canvas_wallpaper_more_360, (100, 130))
    pages.set("1")
    # maliang.Text(canvas_wallpaper_more_360, (100, 160), text="输入项数：", fontsize=20, anchor="nw")
    maliang.Button(canvas_wallpaper_more_360, (1150, 350), text="获取数据", command=lambda: download_306_wallpaper())

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    # }
    # response = requests.get(data_url, headers=headers)

    # if response.status_code == 200:
    #     json_data = response.json()

    # else:
    #     logging.error(f"请求失败，状态码: {response.status_code}")
    #     maliang.dialogs.TkMessage(f"请求失败，状态码: {response.status_code}", title="错误", icon="error")

def wallpaper_choose(ch):
    (wallpaper_wallhaven,wallpaper_风景,wallpaper_二次元,wallpaper_360)[ch]()


wallpaper_choose_button=maliang.SegmentedButton(canvas_wallpaper, (100, 150),text= ["Wallhaven精选", "风景", "二次元", "360壁纸"], command=wallpaper_choose, default=0)


### ✨ Bing壁纸详细信息
canvas_detail = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
canvas_download = maliang.Canvas(root, auto_zoom=True, keep_ratio="min", free_anchor=True)
# canvas_detail.place(width=1280, height=720, x=640, y=360, anchor="center")


def huazhi_re1():
    global detail_image_url
    home_page_assets_data["url"]
    # print(1080)
def huazhi_re2(*args):
    global detail_image_url
    home_page_assets_data["url"].replace('1920x1080', 'UHD')
    # print("UHD")
def dd(*args):
    def long_running_task1():
        try:
            # global bing_data_name
            url=detail_image_url
            # print(get_bing_image())
            root.update_idletasks()
            # 自定义用户代理
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
            }

            # 发送HEAD请求以获取文件大小
            response = requests.head(url, headers=headers)
            root.update_idletasks()
            file_size = int(response.headers.get('Content-Length', 0))
            root.update_idletasks()
            # 自动识别文件名和扩展名
            # filename = url.split('/')[-1] or 'downloaded_file'
            filename = f"{time.strftime('Bing_%Y-%m-%d.jpg', time.localtime())}"
            root.update_idletasks()
            if not filename:
                filename = 'downloaded_file'
            root.update_idletasks()
            # 设定分段大小（例如：1MB）
            chunk_size = 1024 * 1024  # 1MB
            num_chunks = (file_size // chunk_size) + 1
            logging.info("开始下载")
            logging.info(f"开始下载 {filename}，总大小: {file_size} bytes，分为 {num_chunks} 段。")

            with open(f"{cog.get_value("data.download_path")}\\{filename}", 'wb') as file:
                for i in range(num_chunks):
                    root.update_idletasks()
                    start = i * chunk_size
                    end = min(start + chunk_size - 1, file_size - 1)

                    # 设置Range请求头
                    range_header = {'Range': f'bytes={start}-{end}'}
                    chunk_response = requests.get(url, headers={**headers, **range_header}, stream=True)
                    root.update_idletasks()
                    if chunk_response.status_code in (200, 206):  # 206表示部分内容
                        file.write(chunk_response.content)
                        root.update_idletasks()
                        logging.info(f"下载段 {i + 1}/{num_chunks} 完成，大小: {len(chunk_response.content)} bytes")
                    else:
                        logging.info(f"下载失败，状态码: {chunk_response.status_code}")
                        root.update_idletasks()
                        maliang.dialogs.TkMessage(f"下载失败，状态码: {chunk_response.status_code}", title="错误", icon="error")
                        os._exit(0)
            # print(bing_data_name)

            logging.info("下载完成！")
            os.system(f"explorer.exe /select,\"{cog.get_value("data.download_path")}\\{filename}\"")
            # maliang.dialogs.TkMessage(f"下载完成，文件位于：{cog.get_value("data.download_path")}\n文件名：{filename}", title="提示", icon="info")
            notification.notify(
                title='下载完成',
                message=f'文件位于：{cog.get_value("data.download_path")}\n文件名：{filename}',
                app_icon=cog.get_value("display.window_icon_path"),
                timeout=3,
            )
            more_bing()
        except Exception as e:
            maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
            logging.error(f"下载失败{e}")

            more_bing()

        # 任务完成后更新窗口
        # label.config(text="任务已完成!")

    def start_task1(*args):

        # label.config(text="任务正在进行中...")
        # 利用after方法调用长时间运行的任务
        root.after(100, long_running_task1)
    canvas_detail.place_forget()
    canvas_download.place(width=1280, height=720, x=640, y=360, anchor="center")
    maliang.Text(canvas_download, (100, 100), text="正在下载...", fontsize=50, anchor="nw")
    pb1 = maliang.ProgressBar(canvas_download, (420, 260), (380, 8))
    animation.Animation(2000, pb1.set, controller=animation.smooth,
                fps=60, repeat=-1).start(delay=1500)
    start_task1()

def ll(*args):
    def long_running_task1():
        try:
            # global bing_data_name
            url=detail_image_url
            # print(get_bing_image())
            root.update_idletasks()
            # 自定义用户代理
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
            }

            # 发送HEAD请求以获取文件大小
            response = requests.head(url, headers=headers)
            root.update_idletasks()
            file_size = int(response.headers.get('Content-Length', 0))
            root.update_idletasks()
            # 自动识别文件名和扩展名
            # filename = url.split('/')[-1] or 'downloaded_file'
            filename = filedialog.asksaveasfilename(title='Bing-另存为', filetypes=[('JPEG文件', '.jpg')], defaultextension=".jpg")
            root.update_idletasks()
            if not filename:

                while(filename is not True):
                    filename = filedialog.asksaveasfilename(title='Bing-另存为', filetypes=[('JPEG文件', '.jpg')], defaultextension=".jpg")
            root.update_idletasks()
            # 设定分段大小（例如：1MB）
            chunk_size = 1024 * 1024  # 1MB
            num_chunks = (file_size // chunk_size) + 1
            logging.info("开始下载")
            logging.info(f"开始下载 {filename}，总大小: {file_size} bytes，分为 {num_chunks} 段。")
            # home_page_assets_pathn=filedialog.askdirectory()
            with open(f"{filename}", 'wb') as file:
                for i in range(num_chunks):
                    root.update_idletasks()
                    start = i * chunk_size
                    end = min(start + chunk_size - 1, file_size - 1)

                    # 设置Range请求头
                    range_header = {'Range': f'bytes={start}-{end}'}
                    chunk_response = requests.get(url, headers={**headers, **range_header}, stream=True)
                    root.update_idletasks()
                    if chunk_response.status_code in (200, 206):  # 206表示部分内容
                        file.write(chunk_response.content)
                        root.update_idletasks()
                        logging.info(f"下载段 {i + 1}/{num_chunks} 完成，大小: {len(chunk_response.content)} bytes")
                    else:
                        logging.info(f"下载失败，状态码: {chunk_response.status_code}")
                        root.update_idletasks()
                        maliang.dialogs.TkMessage(f"下载失败，状态码: {chunk_response.status_code}", title="错误", icon="error")
                        os._exit(0)
            # print(bing_data_name)

            logging.info("下载完成！")
            os.system(f"explorer.exe /select,\"{filename.replace("/","\\")}\"")
            # maliang.dialogs.TkMessage(f"下载完成，文件位于：{cog.get_value("data.download_path")}\n文件名：{filename}", title="提示", icon="info")
            notification.notify(
                title='下载完成',
                message=f'文件位于：{os.path.dirname(os.path.abspath(filename))}\n文件名：{os.path.split(filename)[1]}',
                app_icon=cog.get_value("display.window_icon_path"),
                timeout=3,
            )
            more_bing()
        except Exception as e:
            maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
            logging.error(f"下载失败{e}")

            more_bing()

        # 任务完成后更新窗口
        # label.config(text="任务已完成!")

    def start_task1(*args):

        # label.config(text="任务正在进行中...")
        # 利用after方法调用长时间运行的任务
        root.after(100, long_running_task1)
    canvas_detail.place_forget()
    canvas_download.place(width=1280, height=720, x=640, y=360, anchor="center")
    maliang.Text(canvas_download, (100, 100), text="正在下载...", fontsize=50, anchor="nw")
    pb1 = maliang.ProgressBar(canvas_download, (420, 260), (380, 8))
    animation.Animation(2000, pb1.set, controller=animation.smooth,
                fps=60, repeat=-1).start(delay=1500)
    start_task1()
def set_w_bing(*args):
    def long_running_task1():
        try:
            # global bing_data_name
            url=detail_image_url
            # print(get_bing_image())
            root.update_idletasks()
            # 自定义用户代理
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
            }

            # 发送HEAD请求以获取文件大小
            response = requests.head(url, headers=headers)
            root.update_idletasks()
            file_size = int(response.headers.get('Content-Length', 0))
            root.update_idletasks()
            # 自动识别文件名和扩展名
            # filename = url.split('/')[-1] or 'downloaded_file'
            # filename = f"{time.strftime('Bing_%Y-%m-%d.jpg', time.localtime())}"
            root.update_idletasks()
            # if not filename:
                # filename = 'downloaded_file'
            root.update_idletasks()
            # 设定分段大小（例如：1MB）
            chunk_size = 1024 * 1024  # 1MB
            num_chunks = (file_size // chunk_size) + 1
            logging.info("开始下载")
            logging.info(f"开始下载 bk.jpg，总大小: {file_size} bytes，分为 {num_chunks} 段。")

            with open("{WALLPAPER_PATH}bk.jpg", 'wb') as file:
                for i in range(num_chunks):
                    root.update_idletasks()
                    start = i * chunk_size
                    end = min(start + chunk_size - 1, file_size - 1)

                    # 设置Range请求头
                    range_header = {'Range': f'bytes={start}-{end}'}
                    chunk_response = requests.get(url, headers={**headers, **range_header}, stream=True)
                    root.update_idletasks()
                    if chunk_response.status_code in (200, 206):  # 206表示部分内容
                        file.write(chunk_response.content)
                        root.update_idletasks()
                        logging.info(f"下载段 {i + 1}/{num_chunks} 完成，大小: {len(chunk_response.content)} bytes")
                    else:
                        logging.info(f"下载失败，状态码: {chunk_response.status_code}")
                        root.update_idletasks()
                        maliang.dialogs.TkMessage(f"下载失败，状态码: {chunk_response.status_code}", title="错误", icon="error")
                        os._exit(0)
            # print(bing_data_name)

            logging.info("下载完成！")
            # os.system(f"explorer.exe /select,\"{cog.get_value("data.download_path")}\\{filename}\"")
            # maliang.dialogs.TkMessage(f"下载完成，文件位于：{cog.get_value("data.download_path")}\n文件名：{filename}", title="提示", icon="info")
            set_wallpaper("{WALLPAPER_PATH}bk.jpg")
            notification.notify(
                title='壁纸设置完成',
                message=f'壁纸文件位于：{WALLPAPER_PATH}\n文件名：bk.jpg\n请勿删除！',
                app_icon=cog.get_value("display.window_icon_path"),
                timeout=3,
            )
            more_bing()
        except Exception as e:
            maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
            logging.error(f"下载失败{e}")

            more_bing()

        # 任务完成后更新窗口
        # label.config(text="任务已完成!")

    def start_task1(*args):

        # label.config(text="任务正在进行中...")
        # 利用after方法调用长时间运行的任务
        root.after(100, long_running_task1)
    canvas_detail.place_forget()
    canvas_download.place(width=1280, height=720, x=640, y=360, anchor="center")
    maliang.Text(canvas_download, (100, 100), text="正在下载...", fontsize=50, anchor="nw")
    pb1 = maliang.ProgressBar(canvas_download, (420, 260), (380, 8))
    animation.Animation(2000, pb1.set, controller=animation.smooth,
                fps=60, repeat=-1).start(delay=1500)
    start_task1()
def copy_w_bing(*args):
    def long_running_task1():
        try:
            # global bing_data_name
            url=detail_image_url
            # print(get_bing_image())
            root.update_idletasks()
            # 自定义用户代理
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
            }

            # 发送HEAD请求以获取文件大小
            response = requests.head(url, headers=headers)
            root.update_idletasks()
            file_size = int(response.headers.get('Content-Length', 0))
            root.update_idletasks()
            # 自动识别文件名和扩展名
            # filename = url.split('/')[-1] or 'downloaded_file'
            root.update_idletasks()

            root.update_idletasks()
            # 设定分段大小（例如：1MB）
            chunk_size = 1024 * 1024  # 1MB
            num_chunks = (file_size // chunk_size) + 1
            logging.info("开始下载")
            logging.info(f"开始下载 {TEMP}\\copy.jpg，总大小: {file_size} bytes，分为 {num_chunks} 段。")

            with open(f"{TEMP}\\copy.jpg", 'wb') as file:
                for i in range(num_chunks):
                    root.update_idletasks()
                    start = i * chunk_size
                    end = min(start + chunk_size - 1, file_size - 1)

                    # 设置Range请求头
                    range_header = {'Range': f'bytes={start}-{end}'}
                    chunk_response = requests.get(url, headers={**headers, **range_header}, stream=True)
                    root.update_idletasks()
                    if chunk_response.status_code in (200, 206):  # 206表示部分内容
                        file.write(chunk_response.content)
                        root.update_idletasks()
                        logging.info(f"下载段 {i + 1}/{num_chunks} 完成，大小: {len(chunk_response.content)} bytes")
                    else:
                        logging.info(f"下载失败，状态码: {chunk_response.status_code}")
                        root.update_idletasks()
                        maliang.dialogs.TkMessage(f"下载失败，状态码: {chunk_response.status_code}", title="错误", icon="error")
                        os._exit(0)
            # print(bing_data_name)

            logging.info("下载完成！")
            # os.system(f"explorer.exe /select,\"{cog.get_value("data.download_path")}\\{filename}\"")
            # maliang.dialogs.TkMessage(f"下载完成，文件位于：{cog.get_value("data.download_path")}\n文件名：{filename}", title="提示", icon="info")
            copy_image_to_clipboard(f"{TEMP}\\copy.jpg")
            notification.notify(
                title='已复制',
                message='已经复制成功啦 ~ ',
                app_icon=cog.get_value("display.window_icon_path"),
                timeout=3,
            )
            more_bing()
        except Exception as e:
            maliang.dialogs.TkMessage("下载失败，详细错误信息请查看日志", title="错误", icon="error")
            logging.error(f"下载失败{e}")
            more_bing()

        # 任务完成后更新窗口
        # label.config(text="任务已完成!")

    def start_task1(*args):

        # label.config(text="任务正在进行中...")
        # 利用after方法调用长时间运行的任务
        root.after(100, long_running_task1)
    canvas_detail.place_forget()
    canvas_download.place(width=1280, height=720, x=640, y=360, anchor="center")
    maliang.Text(canvas_download, (100, 100), text="正在获取图片数据...", fontsize=50, anchor="nw")
    pb1 = maliang.ProgressBar(canvas_download, (420, 260), (380, 8))
    # maliang.animation.Animation(2000, maliang.animation.smooth, callback=pb1.set,
    #                     fps=60, repeat=math.inf).start(delay=1500)
    animation.Animation(2000, pb1.set, controller=animation.smooth,
                fps=60, repeat=-1).start(delay=1500)
    start_task1()

canvas_detail.place(width=1280, height=720, x=0, y=-720)
maliang.Text(canvas_detail,(50, 70),text="详细信息",fontsize=40,anchor="w")
maliang.Text(canvas_detail,(50, 110),text="今日Bing",fontsize=25,anchor="w")
bing_detail_date = maliang.Text(canvas_detail,(50, 140),text="",fontsize=18,anchor="w")
bing_detail_title = maliang.Text(canvas_detail,(50, 170),text="",fontsize=25,anchor="w")
canvas_copyright=maliang.Canvas(canvas_detail,auto_zoom=True,keep_ratio=False)
canvas_copyright.place(x=40,y=190,width=1200,height=25,anchor="nw")
bing_detail_copyright = maliang.Text(canvas_copyright,(10,10),text="",fontsize=25,anchor="w",underline=True)
canvas_copyright.bind("<Button-1>", lambda event: webbrowser.open(home_page_assets_data['detail']['copyrightlink']))
maliang.Text(canvas_detail,(50, 230),text="预览：",fontsize=25,anchor="w")
bing_detail_image = maliang.Image(canvas_detail, (120, 230))
maliang.Text(canvas_detail,(50, 390),text="",fontsize=40,anchor="w")
canvas_detail.create_text(80, 450,text="",font=("Segoe Fluent lcons",25),anchor="nw",fill="red")
maliang.Text(canvas_detail,(110, 440),text="版权警告：图片仅供作为壁纸使用，禁止用于其他用途",fontsize=23,anchor="nw")
maliang.Button(canvas_detail, (1230, 670), size=(45,45),text="", fontsize=40, family="Segoe Fluent lcons",anchor="center",command=lambda: set_w_bing()).style.set(ol=("", "", ""),bg=("","",""))
maliang.Text(canvas_detail,(1230, 705),text="设为壁纸",fontsize=15,anchor="center")
ll_icon = maliang.Canvas(canvas_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
ll_icon.place(x=1150, y=670,width=40,height=50,anchor="center")
maliang.Text(ll_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
ll_icon.bind("<Button-1>", lambda event: ll())
maliang.Text(canvas_detail,(1150, 705),text="另存为",fontsize=15,anchor="center")
dd_icon = maliang.Canvas(canvas_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
dd_icon.place(x=1070, y=670,width=40,height=50,anchor="center")
maliang.Text(dd_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
dd_icon.bind("<Button-1>", lambda event: dd())
# b3=canvas_detail.create_image(1070, 670, image=maliang.PhotoImage(file=r"D:\Users\张秫\onedrive\OneDrive - 小树科技\图片\icon\dp.png"))
maliang.Text(canvas_detail,(1070, 705),text="下载",fontsize=15,anchor="center")
# canvas_detail.create_text(1070, 705, text="下载", font=15)
# canvas_detail.tag_bind(b3, "<Button-1>", lambda event: dd())
copy_w_bing_icon = maliang.Canvas(canvas_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
copy_w_bing_icon.place(x=990, y=670,width=40,height=50,anchor="center")
maliang.Text(copy_w_bing_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
copy_w_bing_icon.bind("<Button-1>", lambda event: copy_w_bing())
# b4=canvas_detail.create_image(990, 670, image=maliang.PhotoImage(file=r"D:\Users\张秫\onedrive\OneDrive - 小树科技\图片\icon\copy.png"))
maliang.Text(canvas_detail,(990, 705),text="复制",fontsize=15,anchor="center")
# canvas_detail.create_text(990, 705, text="复制", font=15)
# canvas_detail.tag_bind(b4, "<Button-1>", lambda event: copy_w_bing())
test_icon = maliang.Canvas(canvas_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
test_icon.place(x=1280//2, y=670,width=40,height=50,anchor="center")
maliang.Text(test_icon, (0, 10), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
test_icon.bind("<Button-1>", lambda event: webbrowser.open("https://www.bing.com/hp/api/v1/trivia"))
# b5=canvas_detail.create_image(1280//2, 670, image=maliang.PhotoImage(file=r"D:\Users\张秫\onedrive\OneDrive - 小树科技\图片\icon\test.png"))
maliang.Text(canvas_detail,(1280//2, 705),text="参与测验",fontsize=15,anchor="center")
# canvas_detail.create_text(1280//2, 705, text="参与测验", font=15)
# canvas_detail.tag_bind(b5, "<Button-1>", lambda event: webbrowser.open("https://www.bing.com/hp/api/v1/trivia"))
back_detail = maliang.Canvas(canvas_detail, auto_zoom=True, keep_ratio="min", free_anchor=True)
back_detail.place(x=50, y=670,width=40,height=40,anchor="center")
maliang.Text(back_detail, (0, 0), text="", fontsize=40, family="Segoe Fluent lcons",anchor="nw")
back_detail.bind("<Button-1>", lambda event: main())
is_load_index_wallpaper_detail = True



def update_window() -> None:
    """
    更新提示窗口
    """
    global update_check_result
    update_main_window = maliang.Toplevel(title="更新",size=[720,1280])
    update_main_canvas = maliang.Canvas(update_main_window, width=720, height=1280, auto_zoom=True, keep_ratio="min", free_anchor=True)
    update_main_canvas.place(x=0, y=0, anchor="nw")

    maliang.Text(update_main_canvas, (15, 15), text="检测到新版本", fontsize=40,family="MiSans")
    maliang.Text(update_main_canvas, (15, 70), text=f"当前版本：{VER}", fontsize=30,family="MiSans")
    maliang.Text(update_main_canvas, (15, 110), text=f"最新版本：{update_check_result['version']}", fontsize=30,family="MiSans")
    maliang.Text(update_main_canvas, (15, 170), text=f"更新内容：\n{update_check_result['update_note']}", fontsize=25,family="MiSans")

    update_main_window.mainloop()


class UpdateChecker:
    """
    异步更新检查器（带重试机制）
    """
    def __init__(self):
        self.result_queue = queue.Queue()
        self.timeout = 15  # 线程超时时间(秒)

    def _thread_worker(self, *args, **kwargs):
        """带重试机制的线程任务包装器"""
        max_retries = kwargs.pop('max_retries', 3)
        for attempt in range(max_retries):
            try:
                result = fetch_latest_release(*args, **kwargs)
                if result.get('status') != 'error' or attempt == max_retries -1:
                    self.result_queue.put(result)
                    break
                time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                self.result_queue.put({
                    "status": "error",
                    "error_message": f"线程执行异常: {str(e)}"
                })
                break

    def async_check(self, callback=None, retries=3, **kwargs):
        """启动带重试的异步检查"""
        def result_wrapper():
            result = {"status": "error", "error_message": "未知错误"}
            try:
                result = self.result_queue.get(timeout=self.timeout)
            except queue.Empty:
                logging.error("更新检查超时")

                result["error_message"] = "请求超时"
            except Exception as e:
                logging.error(f"更新检查异常: {str(e)}")

                result["error_message"] = str(e)
            finally:
                if callback:
                    if result.get('status') == 'error' and retries > 0:
                        logging.info(f"剩余重试次数：{retries-1}")
                        self.async_check(callback=callback, retries=retries-1, **kwargs)
                    else:
                        callback(result)

        threading.Thread(
            target=self._thread_worker,
            kwargs={**kwargs, 'max_retries': 3},
            daemon=True
        ).start()

        threading.Thread(target=result_wrapper, daemon=True).start()

    def parallel_checks(self, tasks, max_retries=3):
        """带重试的并发多任务检查"""
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._retry_fetch, task, max_retries): task_id
                for task_id, task in enumerate(tasks)
            }
            results = {}
            for future in concurrent.futures.as_completed(futures):
                task_id = futures[future]
                try:
                    results[task_id] = future.result()
                except Exception as e:
                    results[task_id] = {
                        "status": "error",
                        "error_message": str(e)
                    }
            return results

    def _retry_fetch(self, params, max_retries):
        for attempt in range(max_retries):
            try:
                result = fetch_latest_release(**params)
                if result.get('status') == 'error':
                    raise Exception(result.get('error_message', 'Unknown error'))
                return result
            except Exception as e:
                if attempt < max_retries -1:
                    time.sleep(2 ** attempt)
                else:
                    raise Exception(f"所有{max_retries}次重试均失败") from e


def load_home_page_data():
    global home_page_assets_data,loading_ring,home_page_assets_path,detail_image_url

    loading_ring.destroy()
    loading_ring = maliang.Spinner(canvas_loading, (50,50), (60,60), widths=(12, 12))
    loading_notice.set("正在加载数据...")
    if cog.get_value("home_page.source") == "bing":
        bing_data = get_bing_image()
        home_page_assets_data = {
            "source": "Bing",
            "url": bing_data[0]['url'],
            "title": bing_data[0]['title'],
            "copyright": bing_data[0]['copyright'],
            "detail": bing_data[0]
        }
    else:
        spotlight_data = random.choice(get_spotlight_image())
        home_page_assets_data = {
            "source": "Spotlight",
            "url": spotlight_data['url'],
            "title": spotlight_data['title'],
            "copyright": spotlight_data['copyright'],
            "detail": spotlight_data
        }

    temp_dir = "./temp"
    temp_filename = os.path.join(temp_dir, "home_page_image.temp")
    final_filename = os.path.join(temp_dir, "home_page_image")  # 暂时不带扩展名

    # 确保临时目录存在
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 检查并删除已存在的临时文件
        if os.path.exists(temp_filename):
            logging.info(f"发现已存在的临时文件 {temp_filename}，正在删除...".replace("\\","/"))
            os.remove(temp_filename)

        # 创建一个会话
        session = requests.Session()
        # 设置自定义User-Agent
        session.headers.update({'User-Agent': UA})

        # 发送HTTP请求，启用流式下载
        response = session.get(home_page_assets_data["url"], stream=True)
        response.raise_for_status()  # 如果响应状态码不是200，会抛出HTTPError异常

        # 获取文件总大小
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        if total_size <= 0:

            loading_ring.destroy()
            loading_ring = maliang.Spinner(canvas_loading, (50,50), (60,60), widths=(12, 12),mode="indeterminate")
        # 打开临时文件以二进制写入
        with open(temp_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤保持活动的块
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        # 计算下载进度百分比
                        progress = (downloaded_size / total_size)
                        # 更新进度条
                        if progress <= 1.0:

                            loading_ring.set(progress)

                        else:
                            loading_ring.set(1.0)
        loading_ring.set(1.0)
        logging.info(f"图片已成功下载并保存为临时文件 {temp_filename}".replace("\\","/"))

        # 使用内存中的BytesIO来识别图片格式
        with open(temp_filename, 'rb') as f:
            image_data = f.read()

        image_stream = io.BytesIO(image_data)
        image = Image.open(image_stream)
        image_format = image.format.lower()
        image_stream.close()

        # 确保最终文件不存在，然后重命名
        final_filepath = f"{final_filename}.{image_format}"
        if os.path.exists(final_filepath):
            logging.info(f"发现已存在的最终文件 {final_filepath}，正在删除...".replace("\\","/"))
            os.remove(final_filepath)

        os.rename(temp_filename, final_filepath)

        logging.info(f"图片格式识别为 {image_format}，已保存为 {final_filepath}".replace("\\","/"))

        home_page_assets_path = final_filepath
    except Exception as e:
        error_msg = f"下载图片时出错: {str(e)}"
        logging.error(error_msg)

        # 如果下载失败，删除临时文件
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        maliang.TkMessage(icon="error",title="加载失败",message="加载失败",detail="详细错误信息请查看日志")
        home_page_assets_path = "./assets/images/no_images.jpg"
    bing_detail_date.set(home_page_assets_data['detail']["date"])
    bing_detail_title.set(f"标题：{home_page_assets_data['detail']["title"]}")
    bing_detail_copyright.set(f"版权：{home_page_assets_data["detail"]["copyright"]}")
    detail_image_url = home_page_assets_data["detail"]["url"]
    if home_page_assets_data['source'] == "Bing":
        maliang.Text(canvas_detail,(980, 615),text="画质：",fontsize=18,anchor="center")
        def update_image_url(choose):
            global detail_image_url
            match choose:
                case 0:
                    detail_image_url=home_page_assets_data["detail"]["url"]
                case 1:
                    detail_image_url=home_page_assets_data["detail"]["url"].replace("1920x1080", "HUD")
        maliang.SegmentedButton(canvas_detail, (1000, 585), text=(
            "1080P", "HUD(原图)"), default=0, command=update_image_url)
    else:
        maliang.Text(canvas_detail,(980, 615),text="方向：",fontsize=18,anchor="center")
        def update_image_url(choose):
            global detail_image_url
            match choose:
                case 0:
                    detail_image_url=home_page_assets_data["detail"]["url"]
                case 1:
                    detail_image_url=home_page_assets_data["detail"]["portrait_image"]
        maliang.SegmentedButton(canvas_detail, (1000, 585), text=(
            "横向", "纵向"), default=0, command=update_image_url)
    bing_detail_image.set(resize_image(home_page_assets_path, 200))
    animation.MoveTkWidget(canvas_loading, (0, 720), 500, fps=60, controller=animation.smooth).start(delay=500)
    time.sleep(1)
    main()
canvas_loading.place(width=1280, height=720, x=0, y=0, anchor="nw")
maliang.Image(canvas_loading, (350, 300), image=resize_image(cog.get_value("display.window_icon_path"),100))
maliang.Text(canvas_loading , (500, 300),fontsize=80,text="小树壁纸")
loading_ring = maliang.Spinner(canvas_loading, (50 , 50), (60 , 60), mode="indeterminate", widths=(12,12))
loading_notice = maliang.Text(canvas_loading, (150 , 55),text="",fontsize=35)
if cog.get_value("update.enabled"):
    loading_notice.set("正在检查更新...")
    try:
        def handle_update_result(result):
            """更新回调函数"""
            global is_have_update, update_check_result
            update_check_result = result
            if result["status"] == "update_available":
                logging.info(f"发现新版本: {result['version']}")
                is_have_update=True

            elif result["status"] == "test_update":
                logging.info("测试更新被触发")
                is_have_update=True
            elif result["status"] == "error":
                logging.error(f"更新检查失败：{result['error_message']}")
                maliang.TkMessage(icon="error",title="更新",message="更新检查失败",detail="详细错误信息请查看日志")
            logging.info("开始加载资源")
            threading.Thread(target=load_home_page_data, daemon=True).start()


        checker = UpdateChecker()
        checker.async_check(callback=handle_update_result)

    except Exception as e:
        logging.error(f"更新检查失败：{e}")

        maliang.dialogs.TkMessage(icon="error",title="更新",message="更新检查失败",detail="未知错误\n详细错误信息请查看日志")

else:
    threading.Thread(target=load_home_page_data, daemon=True).start()






COMMAND_MAP = {
    "setting": setting,
    "about": about,
    "egg": egg,
    "wallpaper": wallpaper,
    "detail": more_bing,
    "update": update_window
}


start_panel()
root.mainloop()