def world_to_screen(my_matrix, viewport, pos_x, pos_y, pos_z):
    clip_x = pos_x*my_matrix[0][0] + pos_y * my_matrix[1][0] + pos_z * my_matrix[2][0] + my_matrix[3][0]
    clip_y = pos_x*my_matrix[0][1] + pos_y * my_matrix[1][1] + pos_z * my_matrix[2][1] + my_matrix[3][1]
    clip_z = pos_x*my_matrix[0][2] + pos_y * my_matrix[1][2] + pos_z * my_matrix[2][2] + my_matrix[3][2]
    clip_w = pos_x*my_matrix[0][3] + pos_y * my_matrix[1][3] + pos_z * my_matrix[2][3] + my_matrix[3][3]
    if clip_w < 0:
        return 0, 0
    ndc_x = clip_x/clip_w
    ndc_y = clip_y/clip_w
    ndc_z = clip_z/clip_w
    screen_x = (viewport[0] / 2) * ndc_x + ndc_x+  viewport[0] / 2
    screen_y = -(viewport[1] / 2) * ndc_y + ndc_y + viewport[1] / 2
    return screen_x, screen_y