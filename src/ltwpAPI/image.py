from PIL import Image, ImageDraw


class RoundedImage:
    def __init__(self, radius):
        """初始化圆角处理类
        :param radius: 圆角的半径
        """
        self.radius = radius

    def round_corners(self, img):
        """给图片添加圆角
        :param img: 输入的PIL Image对象
        :return: 处理后的PIL Image对象
        """
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        width, height = img.size
        draw.rounded_rectangle((0, 0, width, height), self.radius, fill=255)

        result = img.copy()
        result.putalpha(mask)

        return result
class ImageScaler:
    def __init__(self, img):
        """初始化图像缩放类
        :param img: 输入的PIL Image对象
        """
        if not isinstance(img, Image.Image):
            raise ValueError("必须传入一个PIL.Image对象")
        self.image = img
        self.original_width, self.original_height = self.image.size

    def scale_by_size(self, new_width=None, new_height=None, crop=False, crop_direction="top_left"):
        """根据指定宽度或高度按比例缩放图像，可以选择是否切除多余部分。
        :param new_width: 新的宽度，可以为None
        :param new_height: 新的高度，可以为None
        :param crop: 是否切除多余部分，默认False
        :param crop_direction: 切除多余部分的方向，可选'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :return: 缩放后的图像
        """
        if new_width is None and new_height is None:
            raise ValueError("至少需要指定宽度或高度中的一个")
        if new_width is not None and new_height is None:
            ratio = new_width / self.original_width
            new_height = int(self.original_height * ratio)
        elif new_width is None and new_height is not None:
            ratio = new_height / self.original_height
            new_width = int(self.original_width * ratio)

        scaled_image = self.image.resize((new_width, new_height), Image.LANCZOS)

        if crop:
            width_diff = new_width - scaled_image.width
            height_diff = new_height - scaled_image.height
            if crop_direction == "top_left":
                box = (0, 0, new_width, new_height)
            elif crop_direction == "top_right":
                box = (width_diff, 0, new_width + width_diff, new_height)
            elif crop_direction == "bottom_left":
                box = (0, height_diff, new_width, new_height + height_diff)
            elif crop_direction == "bottom_right":
                box = (width_diff, height_diff, new_width + width_diff, new_height + height_diff)
            else:
                raise ValueError("crop_direction参数错误，选择'top_left', 'top_right', 'bottom_left', 'bottom_right'")
            return scaled_image.crop(box)

        return scaled_image

    def scale_by_ratio(self, ratio, crop=False, crop_direction="top_left"):
        """根据指定的缩放比例缩放图像，可以选择是否切除多余部分。
        :param ratio: 缩放比例，大于0的浮点数
        :param crop: 是否切除多余部分，默认False
        :param crop_direction: 切除多余部分的方向，可选'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :return: 缩放后的图像
        """
        if ratio <= 0:
            raise ValueError("缩放比例必须大于0")
        new_width = int(self.original_width * ratio)
        new_height = int(self.original_height * ratio)

        scaled_image = self.image.resize((new_width, new_height), Image.LANCZOS)

        if crop:
            width_diff = self.original_width - new_width
            height_diff = self.original_height - new_height
            if crop_direction == "top_left":
                box = (0, 0, new_width, new_height)
            elif crop_direction == "top_right":
                box = (width_diff, 0, self.original_width, new_height)
            elif crop_direction == "bottom_left":
                box = (0, height_diff, new_width, self.original_height)
            elif crop_direction == "bottom_right":
                box = (width_diff, height_diff, self.original_width, self.original_height)
            else:
                raise ValueError("crop_direction参数错误，选择'top_left', 'top_right', 'bottom_left', 'bottom_right'")
            return scaled_image.crop(box)

        return scaled_image

    def scale_by_aspect_ratio(self, new_aspect_ratio, crop=False, crop_direction="top_left"):
        """根据指定的新宽高比缩放图像，可以选择是否切除多余部分。
        :param new_aspect_ratio: 新的宽高比，大于0的浮点数（宽度/高度）
        :param crop: 是否切除多余部分，默认False
        :param crop_direction: 切除多余部分的方向，可选'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :return: 缩放后的图像
        """
        if new_aspect_ratio <= 0:
            raise ValueError("宽高比必须大于0")

        if new_aspect_ratio > self.original_width / self.original_height:
            # 新的宽高比大于原始图的宽高比，以高度为基准缩放
            new_height = self.original_height
            new_width = int(new_height * new_aspect_ratio)
        else:
            # 新的宽高比小于或等于原始图的宽高比，以宽度为基准缩放
            new_width = self.original_width
            new_height = int(new_width / new_aspect_ratio)

        scaled_image = self.image.resize((new_width, new_height), Image.LANCZOS)

        if crop:
            width_diff = new_width - self.original_width
            height_diff = new_height - self.original_height
            if crop_direction == "top_left":
                box = (0, 0, self.original_width, self.original_height)
            elif crop_direction == "top_right":
                box = (width_diff, 0, new_width, self.original_height)
            elif crop_direction == "bottom_left":
                box = (0, height_diff, self.original_width, new_height)
            elif crop_direction == "bottom_right":
                box = (width_diff, height_diff, new_width, new_height)
            else:
                raise ValueError("crop_direction参数错误，选择'top_left', 'top_right', 'bottom_left', 'bottom_right'")
            return scaled_image.crop(box)

        return scaled_image

    def force_resize(self, new_width, new_height):
        """强制缩放到指定的高度和宽度。
        :param new_width: 新的宽度
        :param new_height: 新的高度
        :return: 强制缩放后的图像
        """
        return self.image.resize((new_width, new_height), Image.LANCZOS)
if __name__ == "__main__":
    raise "This file is not meant to be run directly."
