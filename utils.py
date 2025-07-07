"""
utils.py
Helper functions for export and clipboard.
"""
import tkinter as tk
from PIL import ImageGrab
import imageio
import os

def export_canvas_as_image(canvas, filename):
    """Export the entire Tkinter canvas as an image file (PNG/JPG), including off-screen parts."""
    canvas.update()
    # Use scrollregion if set, otherwise fallback to visible area
    scrollregion = canvas.cget('scrollregion')
    if scrollregion:
        x0, y0, x1, y1 = map(float, scrollregion.split())
        width = int(x1 - x0)
        height = int(y1 - y0)
    else:
        x0, y0 = 0, 0
        width = canvas.winfo_width()
        height = canvas.winfo_height()
    # Create a new top-level window to render the full canvas off-screen
    temp = tk.Toplevel()
    temp.withdraw()
    temp_canvas = tk.Canvas(temp, width=width, height=height, bg='white')
    temp_canvas.pack()
    # Copy all items from the original canvas
    for item in canvas.find_all():
        coords = canvas.coords(item)
        item_type = canvas.type(item)
        if item_type == "oval":
            temp_canvas.create_oval(*coords, fill=canvas.itemcget(item, "fill"), outline=canvas.itemcget(item, "outline"), width=canvas.itemcget(item, "width"))
        elif item_type == "line":
            temp_canvas.create_line(*coords, fill=canvas.itemcget(item, "fill"), width=canvas.itemcget(item, "width"))
        elif item_type == "text":
            temp_canvas.create_text(*coords, text=canvas.itemcget(item, "text"), font=canvas.itemcget(item, "font"), fill=canvas.itemcget(item, "fill"))
    temp_canvas.update()
    x = temp_canvas.winfo_rootx()
    y = temp_canvas.winfo_rooty()
    img = ImageGrab.grab((x, y, x + width, y + height))
    img.save(filename)
    temp.destroy()

def export_frames_as_gif(frames, filename, fps=2):
    """Export a list of PIL images as a GIF animation."""
    try:
        # Convert frames to RGB format for GIF export
        rgb_frames = []
        for frame in frames:
            if hasattr(frame, 'convert'):
                rgb_frames.append(frame.convert('RGB'))
            else:
                # If frame is already a PIL Image
                rgb_frames.append(frame)
        imageio.mimsave(filename, rgb_frames, fps=fps)
    except Exception as e:
        raise Exception(f"Failed to export as GIF: {str(e)}")

def copy_to_clipboard(text):
    """Copy text to the system clipboard."""
    r = tk.Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()
    r.destroy() 