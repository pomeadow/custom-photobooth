from utils import get_png_file_paths


# templates_path = get_png_file_paths("./resources/templates/")
templates_path = get_png_file_paths("./resources/templates/v0.1/")
# layout_metadata_v0 = {
#     templates_path[0]: {
#         "index": 0,
#         "num_photos": 6,
#         "display_text": "2 x 3",
#     },
#     templates_path[1]: {
#         "index": 1,
#         "num_photos": 4,
#         "display_text": "1 x 4",
#     },
#     templates_path[2]: {
#         "index": 2,
#         "num_photos": 3,
#         "display_text": "1 x 3",
#     },
#     templates_path[3]: {
#         "index": 3,
#         "num_photos": 4,
#         "display_text": "2 x 2",
#     },
# }

layout_metadata_v0_1 = {
    templates_path[0]: {
        "index": 0,
        "num_photos": 6,
        "display_text": "2 x 3",
    },
    templates_path[1]: {
        "index": 3,
        "num_photos": 4,
        "display_text": "2 x 2",
    },
}

templates_config = {
    0: {  # templateup4.png - 2x3 grid layout
        "slots": [
            (40, 40, 540, 547),  # Top-left
            (627, 40, 540, 547),  # Top-middle
            (1207, 40, 540, 547),  # Top-right
            (40, 620, 540, 547),  # Bottom-left
            (627, 620, 540, 547),  # Bottom-middle
            (1207, 620, 540, 547),  # Bottom-right
        ],
        "num_photos": 6,
        "toRotate": False,
    },
    1: {  # templateup1.png - 1x4 horizontal layout
        "slots": [
            (52, 50, 400, 500),  # Slot 1
            (489, 50, 400, 500),  # Slot 2
            (924, 50, 400, 500),  # Slot 3
            (1360, 50, 400, 500),  # Slot 4
        ],
        "num_photos": 4,
        "toRotate": True,
    },
    2: {  # templateup2.png - 1x3 horizontal layout
        "slots": [
            (76, 50, 500, 500),  # Left slot
            (651, 50, 500, 500),  # Middle slot
            (1226, 50, 500, 500),  # Right slot
        ],
        "num_photos": 3,
        "toRotate": True,
    },
    3: {  # templateup3.png - 2x2 grid layout
        "slots": [
            (40, 40, 840, 540),  # Top-left
            (920, 40, 840, 540),  # Top-right
            (40, 620, 840, 540),  # Bottom-left
            (920, 620, 840, 540),  # Bottom-right
        ],
        "num_photos": 4,
        "toRotate": False,
    },
}
