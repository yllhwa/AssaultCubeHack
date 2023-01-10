SHOW_TEAM = False
SET_MAX_HEAHTH = True

local_player_address = 0x0058AC00  # 玩家信息偏移

player_info = {
    "health": 0xEC,
    "position": [0x04, 0x08, 0x0C],
    "foot_position": [0x28, 0x2C, 0x30],
    "yaw": 0x34,
    "pitch": 0x38,
    "team": 0x30C,
}

player_array = 0x0058AC04  # 玩家数组偏移
player_count = 0x0058AC0C  # 玩家数量便宜

matrix_offset = 0x0057DFD0  # 位置矩阵偏移（4x4）

dec_bullet_offset = 0x004C73EF # 减少子弹代码偏移