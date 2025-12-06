from utils.utils import get_png_file_paths


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
        "index": 1,
        "num_photos": 8,
        "display_text": "2 x 4",
    },
    templates_path[1]: {
        "index": 0,
        "num_photos": 6,
        "display_text": "2 x 3",
    },
    templates_path[2]: {
        "index": 3,
        "num_photos": 4,
        "display_text": "2 x 2",
    },
}

templates_config = {
    0: {  # templateup4.png - 2x3 grid layout (ROTATED 90° CCW)
        "slots": [
            (40, 1207, 547, 540),  # Top-left → rotated
            (40, 627, 547, 540),  # Top-middle → rotated
            (40, 40, 547, 540),  # Top-right → rotated
            (620, 1207, 547, 540),  # Bottom-left → rotated
            (620, 627, 547, 540),  # Bottom-middle → rotated
            (620, 40, 547, 540),  # Bottom-right → rotated
        ],
        "num_photos": 6,
        "toRotate": False,
    },
    1: {  # templateup1.png - 1x4 horizontal layout
        "slots": [
            (50, 85, 500, 333),  # Slot 4
            (50, 475, 500, 333),  # Slot 3
            (50, 865, 500, 333),  # Slot 2
            (50, 1255, 500, 333),  # Slot 1
            (650, 85, 500, 333),  # Slot 8
            (650, 475, 500, 333),  # Slot 7
            (650, 865, 500, 333),  # Slot 6
            (650, 1255, 500, 333),  # Slot 5
            # (85, 50, 333, 500),  # Slot 1
            # (475, 50, 333, 500),  # Slot 2
            # (865, 50, 333, 500),  # Slot 3
            # (1255, 50, 333, 500),  # Slot 4
            # (85, 650, 333, 500),  # Slot 5
            # (475, 650, 333, 500),  # Slot 6
            # (865, 650, 333, 500),  # Slot 7
            # (1255, 650, 333, 500),  # Slot 8
        ],
        "num_photos": 8,
        "toRotate": False,
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
            (40, 620, 840, 540),  # Bottom-left
            (920, 40, 840, 540),  # Top-right
            (920, 620, 840, 540),  # Bottom-right
        ],
        "num_photos": 4,
        "toRotate": False,
    },
}
