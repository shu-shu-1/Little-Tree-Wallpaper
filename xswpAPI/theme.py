import subprocess
class AppearanceModeDetector:
    """
    检测操作系统当前处于深色模式还是浅色模式的类。
    """

    @staticmethod
    def get_appearance_mode():
        """
        根据操作系统类型获取当前的外观模式。
        
        Returns:
            str: 'dark' 或 'light' 表示深色或浅色模式；如果无法确定，则返回 'unknown'。
        """
        import sys
        if sys.platform == "win32": 
            return AppearanceModeDetector._get_windows_mode()
        elif sys.platform == "darwin":  
            return AppearanceModeDetector._get_mac_mode()
        elif sys.platform.startswith("linux"):  
            return AppearanceModeDetector._get_linux_mode()
        else:
            raise NotImplementedError(f"不支持的操作系统: {sys.platform}")

    @staticmethod
    def _get_windows_mode():
        """
        获取Windows系统的当前外观模式。
        
        Returns:
            str: 'dark' 或 'light' 表示深色或浅色模式；如果失败，则返回 'unknown'。
        """
        import winreg
        try:
            # 打开注册表项
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            # 读取AppsUseLightTheme的值
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            # 关闭注册表项
            winreg.CloseKey(key)
            # 根据值返回对应的主题
            return 'light' if value == 1 else 'dark'
        except Exception as e:
            print(f"获取Windows外观模式时出错: {e}")
            return 'unknown'

    @staticmethod
    def _get_mac_mode():
        """
        获取macOS系统的当前外观模式。
        
        Returns:
            str: 'dark' 或 'light' 表示深色或浅色模式；如果失败，则返回 'unknown'。
        """
        try:
            result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return 'dark' if result.stdout.strip().lower() == b'dark' else 'light'
        except Exception as e:
            print(f"获取macOS外观模式时出错: {e}")
            return 'unknown'

    @staticmethod
    def _get_linux_mode():
        """
        获取Linux系统的当前外观模式。
        
        注意：此方法假设用户使用的是基于GNOME的桌面环境。
        
        Returns:
            str: 'dark' 或 'light' 表示深色或浅色模式；如果失败，则返回 'unknown'。
        """
        try:
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            theme_name = result.stdout.decode('utf-8').strip().replace("'", "")
            return 'dark' if 'dark' in theme_name.lower() else 'light'
        except Exception as e:
            print(f"获取Linux外观模式时出错: {e}")
            return 'unknown'


