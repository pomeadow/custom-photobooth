from PIL import Image
from utils.utils import get_png_file_paths


def rgb_to_hex(r, g, b):
    """
    Converts RGB integer values (0-255) to a hexadecimal color code.
    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
    Returns:
        str: Hexadecimal color code in the format '#RRGGBB'.
    """
    if not all(0 <= c <= 255 for c in [r, g, b]):
        raise ValueError("RGB values must be between 0 and 255")
    return f"#{r:02X}{g:02X}{b:02X}"


"""This configuration has to be hardcoded here for precise control."""
templates_config = {
    8: {  # 4x1 Vertical layout
        "slots": [
            (50, 85, 500, 333),  # Slot 4
            (50, 475, 500, 333),  # Slot 3
            (50, 865, 500, 333),  # Slot 2
            (50, 1255, 500, 333),  # Slot 1
            (650, 85, 500, 333),  # Slot 8
            (650, 475, 500, 333),  # Slot 7
            (650, 865, 500, 333),  # Slot 6
            (650, 1255, 500, 333),  # Slot 5
        ],
        "num_photos": 8,
    },
    4: {  # 2x2 grid Horizontal layout
        "slots": [
            (40, 40, 840, 540),  # Top-left
            (40, 620, 840, 540),  # Bottom-left
            (920, 40, 840, 540),  # Top-right
            (920, 620, 840, 540),  # Bottom-right
        ],
        "num_photos": 4,
    },
}

templates_path = get_png_file_paths("./resources/templates/v0.1/")
# print(templates_path)

templates_config_dict = dict()


def initialize_templates_config_dict():
    templates_path.sort()
    for template in templates_path:
        pixel_10_rgb = Image.open(template).getpixel((10, 10))
        if pixel_10_rgb is None or type(pixel_10_rgb) != tuple or len(pixel_10_rgb) < 3:
            raise Exception(f"Could not get pixel at (10,10) for {template}")
        # print(f"Pixel at (10,10): {pixel_10_rgb}")
        if "horizontal" in template.lower():
            templates_config_dict[template] = {
                "num_photos": 4,
                "display_text": "2 x 2",
                "color": pixel_10_rgb,
                "slots": templates_config[4]["slots"],
            }
        else:
            templates_config_dict[template] = {
                "num_photos": 8,
                "display_text": "2 x 4",
                "color": pixel_10_rgb,
                "slots": templates_config[8]["slots"],
            }
    # print(f"Initialized templates_config_dict: {templates_config_dict.keys()}")
