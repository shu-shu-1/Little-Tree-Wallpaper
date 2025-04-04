import os
import platform
import subprocess

class WallpaperChanger:
    """壁纸更换器类，用于在不同操作系统上更改桌面壁纸。

    该类支持Windows、macOS和Linux平台下的壁纸设置。它会根据当前操作系统调用相应的方法来更改壁纸。
    """

    def __init__(self):
        """初始化WallpaperChanger实例，并检测当前操作系统。"""
        self.system = platform.system()

    def set_wallpaper(self, path):
        """设置桌面壁纸。

        参数:
            path (str): 图像文件的路径，必须是有效的文件。

        抛出:
            FileNotFoundError: 如果给定的文件路径无效。
            NotImplementedError: 如果当前操作系统不受支持。
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"The file {path} does not exist.")

        if self.system == "Windows":
            self._set_wallpaper_windows(path)
        elif self.system == "Darwin":  # macOS
            self._set_wallpaper_mac(path)
        elif self.system == "Linux":
            self._set_wallpaper_linux(path)
        else:
            raise NotImplementedError("Unsupported operating system.")

    def _set_wallpaper_windows(self, path):
        """在Windows上设置壁纸。

        参数:
            path (str): 图像文件的路径。

        使用Windows API更改壁纸，并更新注册表以确保更改持久。
        """
        import ctypes
        import winreg as reg

        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "Wallpaper", 0, reg.REG_SZ, path)
        reg.CloseKey(key)

    def _set_wallpaper_mac(self, path):
        """在macOS上设置壁纸。

        参数:
            path (str): 图像文件的路径。

        使用AppleScript通过系统事件更改桌面壁纸。
        """
        script = f"""
        tell application "System Events"
            set desktopCount to count of desktops
            repeat with i from 1 to desktopCount
                set desktopPicture to (POSIX file "{path}") as alias
                tell desktop i to set picture to desktopPicture
            end repeat
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    def _set_wallpaper_linux(self, path):
        """在Linux上设置壁纸。

        参数:
            path (str): 图像文件的路径。

        尝试使用gsettings更改GNOME桌面环境的壁纸，如果失败则回退到feh。
        """
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{path}"], check=True)
        except Exception as e:
            print("Failed to set wallpaper using gsettings:", e)

            try:
                subprocess.run(["feh", "--bg-scale", path], check=True)
            except Exception as e:
                print("Failed to set wallpaper using feh:", e)
if __name__ == "__main__":
    raise "This file is not meant to be run directly."