from tkinter import *
import math
import struct
import win32api
import win32gui
from ReadWriteMemory import ReadWriteMemory
from utils import world_to_screen
from config import SHOW_TEAM, SET_MAX_HEAHTH, local_player_address, player_info, player_array, player_count, matrix_offset, dec_bullet_offset

process = ReadWriteMemory().get_process_by_name('ac_client.exe')
process.open()

speedhack_value = 3


class local_player():
    def health():
        return(process.read(process.get_pointer(local_player_address, offsets=[player_info.get("health")])))

    def position():
        x, z, y = player_info.get("position")
        x = process.read(process.get_pointer(
            local_player_address, offsets=[x]), True)
        z = process.read(process.get_pointer(
            local_player_address, offsets=[z]), True)
        y = process.read(process.get_pointer(
            local_player_address, offsets=[y]), True)
        return([x, y, z])

    def yaw():
        x = process.read(process.get_pointer(
            local_player_address, offsets=[0x34]), True)
        return(x)

    def team():
        team_value = process.read(process.get_pointer(
            local_player_address, offsets=[0x30C]))
        return(team_value)


def get_all_player_positions(float=True):
    # 指针
    players = [process.get_pointer(player_array, offsets=[hex(
        offset*4)]) for offset in range(1, process.read(player_count))]
    result = []
    x_offset, z_offset, y_offset = player_info.get("position")
    x_foot_offset, z_foot_offset, y_foot_offset = player_info.get(
        "foot_position")
    for player in players:
        x = process.read(process.get_pointer(
            player, offsets=[x_offset]), float)
        z = process.read(process.get_pointer(
            player, offsets=[z_offset]), float)
        y = process.read(process.get_pointer(
            player, offsets=[y_offset]), float)
        team = process.read(process.get_pointer(
            player, offsets=[player_info.get("team")]))
        health = process.read(process.get_pointer(
            player, offsets=[player_info.get("health")]))
        foot_x = process.read(process.get_pointer(
            player, offsets=[x_foot_offset]), float)
        foot_y = process.read(process.get_pointer(
            player, offsets=[y_foot_offset]), float)
        foot_z = process.read(process.get_pointer(
            player, offsets=[z_foot_offset]), float)
        result.append([x, y, z, team, health, foot_x, foot_y, foot_z])
    return result


def is_teammate(target):
    if target[3] == local_player.team():
        return True
    else:
        return False


def aim(yaw, pitch):
    yaw_pointer = process.get_pointer(
        local_player_address, offsets=[player_info.get("yaw")])
    pitch_pointer = process.get_pointer(
        local_player_address, offsets=[player_info.get("pitch")])
    converted_yaw = struct.unpack("<I", struct.pack("<f", yaw))
    converted_pitch = struct.unpack("<I", struct.pack("<f", pitch))
    process.write(yaw_pointer, converted_yaw[0])
    process.write(pitch_pointer, converted_pitch[0])


def get_vector_between_player(localpos=False, enemypos=False):
    if localpos == False:
        localpos = local_player.position()

    if enemypos == False:
        enemypos = get_all_player_positions()
        if enemypos != []:
            enemypos = enemypos[0]

    x_diff = enemypos[0] - localpos[0]
    y_diff = enemypos[1] - localpos[1]
    z_diff = enemypos[2] - localpos[2]

    dist = math.sqrt(z_diff * z_diff + x_diff * x_diff)
    pitch = math.atan2(y_diff, dist) * 180.0 / math.pi

    if dist > 0.0:
        yaw = math.atan2(x_diff / dist, z_diff / dist) * 180 / math.pi
        yaw = abs(yaw - 180)
    else:
        yaw = 0
    return (yaw, pitch)


def shot_closest_enemy():
    positions = get_all_player_positions()
    if positions == []:
        return

    player_yaw = process.read(process.get_pointer(
        local_player_address, offsets=[0x34]), True)
    player_pitch = process.read(process.get_pointer(
        local_player_address, offsets=[0x38]), True)
    lowest = [0, 360, 360]
    for i, x in enumerate(positions):
        difference = abs(player_yaw - get_vector_between_player(enemypos=x)[0])
        if difference < lowest[1] and not is_teammate(x) and x[4] > 0 and x[4] < 101:
            lowest[0] = i
            lowest[1] = abs(
                player_yaw - get_vector_between_player(enemypos=x)[0])
            lowest[2] = abs(
                player_pitch - get_vector_between_player(enemypos=x)[1])

    if not is_teammate(positions[lowest[0]]) and (positions[lowest[0]][4] > 0 and positions[lowest[0]][4] < 101):
        aim(*get_vector_between_player(enemypos=positions[lowest[0]]))


def speedhack():
    speed_pointer = process.get_pointer(local_player_address, offsets=[0x74])
    process.write(speed_pointer, speedhack_value)


def read_matrix():
    _matrix_offset = matrix_offset
    # 4x4
    matrix = []
    for i in range(4):
        matrix.append([])
        for _ in range(4):
            matrix[i].append(process.read(_matrix_offset, True))
            _matrix_offset += 4
    return matrix


def get_viewport():
    viewport_passport = [0x591ED8, 0x591EDC]
    viewport = []
    for i in viewport_passport:
        viewport.append(process.read(i))
    return viewport


# 获取窗口分辨率
viewport = get_viewport()


def esp(canvas):
    positions = get_all_player_positions()
    localpos = local_player.position()

    my_matrix = read_matrix()

    for pos in positions:
        if is_teammate(pos):
            if not SHOW_TEAM:
                continue
            color = "blue"
        else:
            color = "red"
        color = "blue" if is_teammate(pos) else "red"
        pos_health = pos[4]
        if pos_health > 0 and pos_health < 101:
            # 画框
            pos_x, pos_y, pos_z = pos[0], pos[2], pos[1]
            foot_pos_x, foot_pos_y, foot_pos_z = pos[5], pos[7], pos[6]
            screen_x, screen_y = world_to_screen(
                my_matrix, viewport, pos_x, pos_y, pos_z)
            _, screen_foot_y = world_to_screen(
                my_matrix, viewport, foot_pos_x, foot_pos_y, foot_pos_z)
            distance = math.sqrt(
                (pos[0] - localpos[0])**2 + (pos[1] - localpos[1])**2 + (pos[2] - localpos[2])**2)
            screen_width = viewport[0] / distance  # 宽度随便搞了个函数
            canvas.create_rectangle(
                screen_x-screen_width/2, screen_y, screen_x+screen_width/2, screen_foot_y, outline=color)
            # 在框下方写上血量
            canvas.create_text(
                screen_x, screen_foot_y-7, text=str(pos_health), fill=color, font=("Purisa", 15, "bold"))
            # 画线
            canvas.create_line(
                viewport[0]/2, 0, screen_x, screen_y, fill=color)


MainWindow = Tk()
MainWindow.overrideredirect(1)  # remove title bar
MainWindow.attributes('-topmost', True)
MainWindow.wm_attributes("-transparentcolor", "white")
# 获取窗口ac_client.exe的位置和大小，覆盖在其上方
left, top, right, bottom = win32gui.GetWindowRect(
    win32gui.FindWindow(None, "AssaultCube"))
MainWindow.geometry("+%d+%d" % (left, top))
canvas = Canvas(MainWindow, width=right - left,
                height=bottom - top, bg="white")

# 修改减少子弹代码为nop
# 设置text段可读写
# process.write(dec_bullet_offset, b'\x90\x90')

while True:
    # 鼠标左键开启自瞄(硬锁)
    if win32api.GetAsyncKeyState(0x01) != 0:
        shot_closest_enemy()
    process.write(process.get_pointer(local_player_address,
                                      offsets=[player_info["health"]]), 0x7fffffff)
    esp(canvas)
    canvas.pack()
    MainWindow.update()
    canvas.delete("all")
