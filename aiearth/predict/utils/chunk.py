from aiearth.predict.utils.box import Box


def get_chunk_windows(extent: Box, chunk_size):
    xmin, ymin, xmax, ymax = (
        extent.xmin,
        extent.ymin,
        extent.xmax,
        extent.ymax,
    )

    windows = []
    indexes = []
    for idx_y, y in enumerate(range(ymin, ymax, chunk_size)):
        for idx_x, x in enumerate(range(xmin, xmax, chunk_size)):
            right_x_bound = max(0, x + chunk_size - extent.xmax)
            bottom_y_bound = max(0, y + chunk_size - extent.ymax)

            chunk_width = chunk_size - right_x_bound
            chunk_height = chunk_size - bottom_y_bound

            box = Box.from_xywh(x, y, chunk_width, chunk_height)
            windows.append(box)
            indexes.append((idx_y, idx_x))

    return (windows, indexes)
