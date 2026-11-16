"""关系板的静止帧、分层条和证据并排。

证据图只缩小、不放大。并排图上写明原生尺寸，避免把小图叫成高清。
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from . import draw as D


def fit_down(image, slot_w, slot_h):
    scale = min(1.0, slot_w / image.width, slot_h / image.height)
    if scale < 1:
        size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        return image.resize(size, Image.Resampling.LANCZOS), scale
    return image, scale


def side_by_side(board_image, evidence_image, title):
    canvas = Image.new("RGB", (D.W, D.H), D.BG)
    pen = ImageDraw.Draw(canvas)
    evidence, evidence_scale = fit_down(evidence_image, 600, 620)
    board, board_scale = fit_down(board_image, 620, 620)
    pen.text((24, 12), title, fill=D.WHITE, font=D.font(16, 1))
    canvas.paste(evidence, (24, 48 + (620 - evidence.height) // 2))
    canvas.paste(board, (660, 48 + (620 - board.height) // 2))
    note = (
        f"证据原生 {evidence_image.width}×{evidence_image.height}，图上 {evidence.width}×{evidence.height}。"
        "只缩小，不放大，也不把它叫做高清成片。"
    )
    pen.text((24, 688), note, fill=D.MUT, font=D.font(15, 1))
    meta = {
        "evidence_native": [evidence_image.width, evidence_image.height],
        "evidence_drawn": [evidence.width, evidence.height],
        "board_drawn": [board.width, board.height],
        "upscaled": evidence_scale > 1 or board_scale > 1,
        "native_size": [D.W, D.H],
    }
    return canvas, meta


def progress_sheet(frames):
    """frames: list of (name, image)."""
    columns = min(4, max(1, len(frames)))
    rows = (len(frames) + columns - 1) // columns
    cell_w, cell_h = 320, 180
    caption = 28
    sheet = Image.new("RGB", (columns * cell_w, rows * (cell_h + caption)), D.BG)
    pen = ImageDraw.Draw(sheet)
    for index, (name, image) in enumerate(frames):
        thumb, _ = fit_down(image, cell_w, cell_h)
        x = (index % columns) * cell_w
        y = (index // columns) * (cell_h + caption)
        sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y))
        pen.text((x + 6, y + cell_h + 4), name, fill=D.WHITE, font=D.font(14, 1))
    return sheet


def before_after(before, after, before_name, after_name, stamp):
    canvas = Image.new("RGB", (D.W, D.H), D.BG)
    pen = ImageDraw.Draw(canvas)
    left, _ = fit_down(before, 620, 600)
    right, _ = fit_down(after, 620, 600)
    canvas.paste(left, (16, 48))
    canvas.paste(right, (644, 48))
    pen.text((16, 12), before_name, fill=D.MUT, font=D.font(18, 1))
    pen.text((644, 12), after_name, fill=D.ATT, font=D.font(18, 1))
    pen.text((16, 680), stamp, fill=D.MUT, font=D.font(16, 1))
    return canvas
