import os
from tomlkit import TOMLDocument, parse, dumps
from typing import Any

class ConfigManager:
    """
    配置管理器类，用于加载、保存和管理配置文件。
    """

    def __init__(self, config_path: str = "Config.toml"):
        """
        初始化配置管理器。

        :param config_path: 配置文件的路径，默认为 "Config.toml"
        """
        self.config_path = config_path
        self.config: TOMLDocument = self._load_config()

    def _load_config(self) -> TOMLDocument:
        """
        加载配置文件。

        如果配置文件不存在，则抛出 FileNotFoundError 异常。

        :return: 解析后的配置文件内容
        :raise FileNotFoundError: 如果配置文件不存在
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        
        with open(self.config_path, "r", encoding="utf-8") as file:
            return parse(file.read())

    def save_config(self):
        """
        保存配置文件到指定路径。
        """
        with open(self.config_path, "w", encoding="utf-8") as file:
            file.write(dumps(self.config))

    def get_value(self, key_path: str) -> Any:
        """
        根据键路径获取配置值。

        :param key_path: 配置项的键路径，使用点号分隔层级，例如 "display.language"
        :return: 配置项的值
        """
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            value = value[key]
        return value
    def reload_config(self):
        """
        重新加载配置文件。
        """
        self.config = self._load_config()

    def set_value(self, key_path: str, value: Any, save_config: bool = True , reload_config: bool = True):
        """
        根据键路径设置配置值并保存配置文件。

        :param key_path: 配置项的键路径，使用点号分隔层级，例如 "display.language"
        :param value: 要设置的配置项的值
        :param save_config: 是否保存配置文件
        :param reload_config: 是否重新加载配置文件

        """
        keys = key_path.split(".")
        current = self.config
        for key in keys[:-1]:
            current = current[key]
        current[keys[-1]] = value
        if save_config:
            self.save_config()
        if reload_config:
            self.reload_config()

    def reset_config(self):
        """
        将配置文件重置为默认值并保存。
        """
        default_config = """[info] # 配置文件信息
version = "2.0.0" # 配置文件版本

[display] # 显示设置
language = "zh-CN" # 语言设置
color_mode = "auto" # 深/浅模式
window_background_image_path = "" # 窗口壁纸路径
window_icon_path = "./assets/icon/icon.ico" # 窗口图标路径

[update] # 更新设置
enabled = 1 # 是否启用更新检查
channel = "Stable" # 更新通道
[update.proxy] # 镜像设置
enabled = 1 # 是否使用镜像
proxy_index = 0 # 使用的镜像序号
proxy_list=[ # 镜像列表
    "https://www.ghproxy.cn/", 
    "https://gh.llkk.cc/", 
    "https://gh-proxy.com/", 
    "https://github.moeyy.xyz/"
] 

[data] # 数据保存设置
cache_path = "./cache" # 缓存路径
log_path = "./log" # 日志路径
download_path = "" # 下载路径
favorites_path = "" # 收藏夹路径
clear_cache_when_360_back = 1 # 使用360壁纸源后是否自动清理缓存

[automatic_wallpaper_change] # 壁纸自动轮换设置
mode = "random" # 壁纸自动轮换模式
interval_time = 600 # 壁纸自动轮换时间间隔,单位为秒

[download] # 下载设置
segmented_download_size = 200 # 分段下载大小,单位为KB
[download.proxy] # 下载时是否使用代理
enabled = 0 # 是否启用代理下载
mode = "http" # 代理服务器类型
server = "" # 代理服务器

[auto_start] # 自启动设置
enabled = 0 # 是否启用自启动
script_enabled = 0 # 是否启用脚本
script_path = "" # 脚本路径
change_wallpaper_enabled = 0 # 是否自动更换壁纸
change_wallpaper_mode = "bing" # 自动更换壁纸模式
automatic_wallpaper_change = 0 # 是否自动开启壁纸自动轮换

[home_page]
source = "bing" # 首页壁纸来源
style = "default" # 首页布局"""
        self.config = parse(default_config)
        self.save_config()
        self.reload_config()

# 示例用法
if __name__ == "__main__":
    config_manager = ConfigManager()

    # 读取配置值
    version = config_manager.get_value("info.version")
    print(f"当前版本: {version}")

    # 修改配置值
    config_manager.set_value("display.language", "en-US")

    # 重置配置文件
    # config_manager.reset_config()