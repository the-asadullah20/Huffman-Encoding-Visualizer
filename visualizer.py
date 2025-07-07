"""
visualizer.py
Handles drawing and animating the Huffman tree on a Tkinter Canvas with classic binary tree layout (parent centered above children).
"""
import tkinter as tk
import time
from threading import Thread
from PIL import ImageGrab, Image, ImageDraw, ImageFont
from huffman import HuffmanNode
import math
import os

class TreeNodeVisual:
    """Visual representation of a Huffman tree node for animation and interaction."""
    def __init__(self, node, x, y, code='', color='lightgray'):
        self.node = node
        self.x = x
        self.y = y
        self.code = code
        self.color = color
        self.oval = None
        self.text = None
        self.line = None
        self.tooltip = None

class HuffmanTreeVisualizer:
    """Draws and animates the Huffman tree on a Tkinter Canvas with classic binary tree layout."""
    def __init__(self, canvas, tree, on_node_hover=None):
        self.canvas = canvas
        self.tree = tree
        self.node_visuals = []
        self.on_node_hover = on_node_hover
        self.node_radius = 25
        self.level_gap = 90
        self.h_gap = 30
        self.animation_delay = 0.7
        self.frames = []
        self._bind_events()
    def _bind_events(self):
        self.canvas.bind('<Motion>', self._on_mouse_move)
    def _on_mouse_move(self, event):
        for nv in self.node_visuals:
            if nv.oval:
                coords = self.canvas.coords(nv.oval)
                if coords and coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                    if self.on_node_hover:
                        self.on_node_hover(nv)
                    return
        if self.on_node_hover:
            self.on_node_hover(None)
    def clear(self):
        self.canvas.delete('all')
        self.node_visuals.clear()
    def _compute_subtree_width(self, node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        lw = self._compute_subtree_width(node.left)
        rw = self._compute_subtree_width(node.right)
        return lw + rw
    def _assign_positions(self, node, x, y, x_spacing, positions):
        if node is None:
            return x
        lw = self._compute_subtree_width(node.left)
        rw = self._compute_subtree_width(node.right)
        # Center parent above children
        if node.left:
            left_x = self._assign_positions(node.left, x, y + self.level_gap, x_spacing, positions)
        else:
            left_x = x
        if node.right:
            right_x = self._assign_positions(node.right, x + lw * x_spacing, y + self.level_gap, x_spacing, positions)
        else:
            right_x = x
        if node.left and node.right:
            my_x = (positions[node.left][0] + positions[node.right][0]) / 2
        elif node.left:
            my_x = positions[node.left][0] + x_spacing
        elif node.right:
            my_x = positions[node.right][0] - x_spacing
        else:
            my_x = x
        positions[node] = (my_x, y)
        return x + (lw + rw) * x_spacing if (lw + rw) > 0 else x + x_spacing
    def _layout_tree(self, root):
        positions = {}
        total_leaves = self._compute_subtree_width(root)
        x_spacing = max(self.node_radius * 2 + self.h_gap, 60)
        # Center the tree horizontally
        canvas_width = max(600, total_leaves * x_spacing + 2 * self.node_radius)
        start_x = canvas_width // 2
        self._assign_positions(root, start_x, self.node_radius + 40, x_spacing, positions)
        return positions, canvas_width
    def _center_positions(self, positions, canvas_width):
        if not positions:
            return positions
        min_x = min(x for x, y in positions.values())
        max_x = max(x for x, y in positions.values())
        tree_width = max_x - min_x
        # Center the tree in the canvas
        offset = (canvas_width - tree_width) // 2 - min_x
        return {node: (x + offset, y) for node, (x, y) in positions.items()}
    def draw_static(self, keep_centered=False):
        self.clear()
        self.node_visuals = []  # Rebuild node visuals for hover/click
        if not self.tree.root:
            return
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        zoom = getattr(self, 'zoom_level', 1.0)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        font_size = max(8, int(12 * zoom))
        line_width = max(1, int(2 * zoom))
        max_x = max(x for x, y in positions.values()) if positions else 600
        max_y = max(y for x, y in positions.values()) if positions else 600
        if keep_centered:
            canvas_w = int(self.canvas.winfo_width())
            offset = max(0, (canvas_w - (max_x + node_radius + 40)) // 2)
            positions = {node: (x + offset, y) for node, (x, y) in positions.items()}
        self.canvas.config(scrollregion=(0, 0, max_x + node_radius + 40, max_y + node_radius + 40))
        self._draw_tree(self.tree.root, positions, node_radius, font_size, line_width)
    def animate_construction(self, callback=None, keep_centered=False):
        self.clear()
        self.node_visuals = []  # Rebuild node visuals for hover/click
        steps = self.tree.get_steps()
        heap = [HuffmanNode(char, freq) for char, freq in self.tree.get_frequency_table().items()]
        for i, (left, right, merged) in enumerate(steps):
            heap = [n for n in heap if n != left and n != right]
            heap.append(merged)
            root = merged
            self.clear()
            self.node_visuals = []
            positions, canvas_width = self._layout_tree(root)
            positions = self._center_positions(positions, canvas_width)
            zoom = getattr(self, 'zoom_level', 1.0)
            positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
            node_radius = int(self.node_radius * zoom)
            font_size = max(8, int(12 * zoom))
            line_width = max(1, int(2 * zoom))
            max_x = max(x for x, y in positions.values()) if positions else 600
            max_y = max(y for x, y in positions.values()) if positions else 600
            if keep_centered:
                canvas_w = int(self.canvas.winfo_width())
                offset = max(0, (canvas_w - (max_x + node_radius + 40)) // 2)
                positions = {node: (x + offset, y) for node, (x, y) in positions.items()}
            self.canvas.config(scrollregion=(0, 0, max_x + node_radius + 40, max_y + node_radius + 40))
            self._draw_tree(root, positions, node_radius, font_size, line_width, highlight=(left, right))
            self.canvas.update()
            time.sleep(self.animation_delay)
        # Draw final tree
        self.clear()
        self.node_visuals = []
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        zoom = getattr(self, 'zoom_level', 1.0)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        font_size = max(8, int(12 * zoom))
        line_width = max(1, int(2 * zoom))
        max_x = max(x for x, y in positions.values()) if positions else 600
        max_y = max(y for x, y in positions.values()) if positions else 600
        if keep_centered:
            canvas_w = int(self.canvas.winfo_width())
            offset = max(0, (canvas_w - (max_x + node_radius + 40)) // 2)
            positions = {node: (x + offset, y) for node, (x, y) in positions.items()}
        self.canvas.config(scrollregion=(0, 0, max_x + node_radius + 40, max_y + node_radius + 40))
        self._draw_tree(self.tree.root, positions, node_radius, font_size, line_width)
        self.canvas.update()
        if callback:
            callback()
    def _draw_tree(self, node, positions, node_radius, font_size, line_width, highlight=None):
        if node is None:
            return None
        x, y = positions[node]
        if highlight and (node == highlight[0] or node == highlight[1]):
            color = 'lightgreen'
        elif node.char is not None:
            color = 'lightblue'
        else:
            color = 'lightgray'
        nv = TreeNodeVisual(node, x, y, '', color)
        self.node_visuals.append(nv)
        # Draw left child
        if node.left:
            child_nv = self._draw_tree(node.left, positions, node_radius, font_size, line_width, highlight)
            if child_nv:
                cx, cy = child_nv.x, child_nv.y
                dx, dy = cx - x, cy - y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                start_x = x + node_radius * dx / dist
                start_y = y + node_radius * dy / dist
                end_x = cx - node_radius * dx / dist
                end_y = cy - node_radius * dy / dist
                nv.line = self.canvas.create_line(start_x, start_y, end_x, end_y, fill='black', width=line_width)
        # Draw right child
        if node.right:
            child_nv = self._draw_tree(node.right, positions, node_radius, font_size, line_width, highlight)
            if child_nv:
                cx, cy = child_nv.x, child_nv.y
                dx, dy = cx - x, cy - y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                start_x = x + node_radius * dx / dist
                start_y = y + node_radius * dy / dist
                end_x = cx - node_radius * dx / dist
                end_y = cy - node_radius * dy / dist
                nv.line = self.canvas.create_line(start_x, start_y, end_x, end_y, fill='black', width=line_width)
        nv.oval = self.canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill=nv.color, outline='black', width=line_width
        )
        if node.char is not None:
            char_line = f"'{node.char}'"
            freq_line = f"{node.freq}"
            nv.text = self.canvas.create_text(
                x, y - font_size // 2, text=char_line,
                font=('Arial', font_size, 'bold'), fill='black')
            nv.text2 = self.canvas.create_text(
                x, y + font_size // 2 + 6, text=freq_line,
                font=('Arial', font_size, 'bold'), fill='black')
        else:
            label = f"{node.freq}"
            nv.text = self.canvas.create_text(
                x, y, text=label,
                font=('Arial', font_size, 'bold'), fill='black')
        return nv
    def _save_frame(self):
        # Save current canvas as a frame (for animation export)
        self.canvas.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        img = ImageGrab.grab((x, y, x + w, y + h))
        self.frames.append(img)
    def get_frames(self):
        return self.frames
    def draw_on_canvas(self, target_canvas, zoom=1.0):
        # Draw the full tree on the given canvas at the given zoom level
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        font_size = max(8, int(12 * zoom))
        line_width = max(1, int(2 * zoom))
        self._draw_tree_on_canvas(self.tree.root, positions, node_radius, font_size, line_width, target_canvas)
    def _draw_tree_on_canvas(self, node, positions, node_radius, font_size, line_width, canvas, highlight=None):
        if node is None:
            return None
        x, y = positions[node]
        if highlight and (node == highlight[0] or node == highlight[1]):
            color = 'lightgreen'
        elif node.char is not None:
            color = 'lightblue'
        else:
            color = 'lightgray'
        # Draw left child
        if node.left:
            child_nv = self._draw_tree_on_canvas(node.left, positions, node_radius, font_size, line_width, canvas, highlight)
            if child_nv:
                canvas.create_line(x, y, child_nv[0], child_nv[1], fill='black', width=line_width)
        # Draw right child
        if node.right:
            child_nv = self._draw_tree_on_canvas(node.right, positions, node_radius, font_size, line_width, canvas, highlight)
            if child_nv:
                canvas.create_line(x, y, child_nv[0], child_nv[1], fill='black', width=line_width)
        canvas.create_oval(
            x - node_radius, y - node_radius,
            x + node_radius, y + node_radius,
            fill=color, outline='black', width=line_width
        )
        if node.char is not None:
            char_line = f"'{node.char}'"
            freq_line = f"{node.freq}"
            bbox1 = draw.textbbox((0, 0), char_line, font=font)
            w1, h1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
            bbox2 = draw.textbbox((0, 0), freq_line, font=font)
            w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
            draw.text((x - w1 // 2, y - h1 // 2), char_line, fill='black', font=font)
            draw.text((x - w2 // 2, y + h1 // 2 + 6), freq_line, fill='black', font=font)
        else:
            label = f"{node.freq}"
            bbox = draw.textbbox((0, 0), label, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - w // 2, y - h // 2), label, fill='black', font=font)
        return (x, y)
    def render_to_image(self, zoom=1.0):
        # Render the full tree to a PIL image at the given zoom level
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        font_size = max(8, int(12 * zoom))
        line_width = max(1, int(2 * zoom))
        max_x = max(x for x, y in positions.values()) if positions else 600
        max_y = max(y for x, y in positions.values()) if positions else 600
        width = int(max_x + node_radius + 40)
        height = int(max_y + node_radius + 40)
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype('arial.ttf', font_size)
        except:
            font = ImageFont.load_default()
        self._draw_tree_on_image(self.tree.root, positions, node_radius, font, line_width, draw)
        return image
    def _draw_tree_on_image(self, node, positions, node_radius, font, line_width, draw, highlight=None):
        if node is None:
            return None
        x, y = positions[node]
        if highlight and (node == highlight[0] or node == highlight[1]):
            color = (144, 238, 144)  # lightgreen
        elif node.char is not None:
            color = (173, 216, 230)  # lightblue
        else:
            color = (211, 211, 211)  # lightgray
        # Draw left child
        if node.left:
            child_nv = self._draw_tree_on_image(node.left, positions, node_radius, font, line_width, draw, highlight)
            if child_nv:
                cx, cy = child_nv[0], child_nv[1]
                dx, dy = cx - x, cy - y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                start_x = x + node_radius * dx / dist
                start_y = y + node_radius * dy / dist
                end_x = cx - node_radius * dx / dist
                end_y = cy - node_radius * dy / dist
                draw.line([start_x, start_y, end_x, end_y], fill='black', width=line_width)
        # Draw right child
        if node.right:
            child_nv = self._draw_tree_on_image(node.right, positions, node_radius, font, line_width, draw, highlight)
            if child_nv:
                cx, cy = child_nv[0], child_nv[1]
                dx, dy = cx - x, cy - y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                start_x = x + node_radius * dx / dist
                start_y = y + node_radius * dy / dist
                end_x = cx - node_radius * dx / dist
                end_y = cy - node_radius * dy / dist
                draw.line([start_x, start_y, end_x, end_y], fill='black', width=line_width)
        draw.ellipse([x - node_radius, y - node_radius, x + node_radius, y + node_radius], fill=color, outline='black', width=line_width)
        if node.char is not None:
            char_line = f"'{node.char}'"
            freq_line = f"{node.freq}"
            bbox1 = draw.textbbox((0, 0), char_line, font=font)
            w1, h1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
            bbox2 = draw.textbbox((0, 0), freq_line, font=font)
            w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
            draw.text((x - w1 // 2, y - h1 // 2), char_line, fill='black', font=font)
            draw.text((x - w2 // 2, y + h1 // 2 + 6), freq_line, fill='black', font=font)
        else:
            label = f"{node.freq}"
            bbox = draw.textbbox((0, 0), label, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x - w // 2, y - h // 2), label, fill='black', font=font)
        return (x, y)
    def render_animation_frames_to_images(self, zoom=1.0, delay=0.7):
        # First, determine max width/height needed for any frame
        steps = self.tree.get_steps()
        heap = [HuffmanNode(char, freq) for char, freq in self.tree.get_frequency_table().items()]
        max_width, max_height = 0, 0
        frame_data = []
        for i, (left, right, merged) in enumerate(steps):
            heap = [n for n in heap if n != left and n != right]
            heap.append(merged)
            root = merged
            positions, canvas_width = self._layout_tree(root)
            positions = self._center_positions(positions, canvas_width)
            positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
            node_radius = int(self.node_radius * zoom)
            max_x = max(x for x, y in positions.values()) if positions else 600
            max_y = max(y for x, y in positions.values()) if positions else 600
            width = int(max_x + node_radius + 40)
            height = int(max_y + node_radius + 40)
            max_width = max(max_width, width)
            max_height = max(max_height, height)
            frame_data.append((root, positions, node_radius, left, right))
        # Also consider the final tree
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        max_x = max(x for x, y in positions.values()) if positions else 600
        max_y = max(y for x, y in positions.values()) if positions else 600
        width = int(max_x + node_radius + 40)
        height = int(max_y + node_radius + 40)
        max_width = max(max_width, width)
        max_height = max(max_height, height)
        # Now render each frame centered on a canvas of max_width, max_height
        frames = []
        for (root, positions, node_radius, left, right) in frame_data:
            image = Image.new('RGB', (max_width, max_height), 'white')
            draw = ImageDraw.Draw(image)
            try:
                font_size = max(8, int(12 * zoom))
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
            # Center positions in the max canvas
            min_x = min(x for x, y in positions.values())
            min_y = min(y for x, y in positions.values())
            offset_x = (max_width - (max(x for x, y in positions.values()) - min_x)) // 2 - min_x
            offset_y = (max_height - (max(y for x, y in positions.values()) - min_y)) // 2 - min_y
            centered_positions = {node: (x + offset_x, y + offset_y) for node, (x, y) in positions.items()}
            self._draw_tree_on_image(root, centered_positions, node_radius, font, max(1, int(2 * zoom)), draw, highlight=(left, right))
            frames.append(image)
        # Add several frames of the full tree at the end
        for _ in range(int(1.5 / delay)):
            image = Image.new('RGB', (max_width, max_height), 'white')
            draw = ImageDraw.Draw(image)
            try:
                font_size = max(8, int(12 * zoom))
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
            min_x = min(x for x, y in positions.values())
            min_y = min(y for x, y in positions.values())
            offset_x = (max_width - (max(x for x, y in positions.values()) - min_x)) // 2 - min_x
            offset_y = (max_height - (max(y for x, y in positions.values()) - min_y)) // 2 - min_y
            centered_positions = {node: (x + offset_x, y + offset_y) for node, (x, y) in positions.items()}
            self._draw_tree_on_image(self.tree.root, centered_positions, node_radius, font, max(1, int(2 * zoom)), draw)
            frames.append(image)
        return frames
    def stream_animation_frames_to_images(self, zoom=1.0, delay=0.7):
        # Like render_animation_frames_to_images, but yields each frame one at a time (memory efficient)
        steps = self.tree.get_steps()
        heap = [HuffmanNode(char, freq) for char, freq in self.tree.get_frequency_table().items()]
        max_width, max_height = 0, 0
        frame_data = []
        for i, (left, right, merged) in enumerate(steps):
            heap = [n for n in heap if n != left and n != right]
            heap.append(merged)
            root = merged
            positions, canvas_width = self._layout_tree(root)
            positions = self._center_positions(positions, canvas_width)
            positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
            node_radius = int(self.node_radius * zoom)
            max_x = max(x for x, y in positions.values()) if positions else 600
            max_y = max(y for x, y in positions.values()) if positions else 600
            width = int(max_x + node_radius + 40)
            height = int(max_y + node_radius + 40)
            max_width = max(max_width, width)
            max_height = max(max_height, height)
            frame_data.append((root, positions, node_radius, left, right))
        # Also consider the final tree
        positions, canvas_width = self._layout_tree(self.tree.root)
        positions = self._center_positions(positions, canvas_width)
        positions = {node: (x * zoom, y * zoom) for node, (x, y) in positions.items()}
        node_radius = int(self.node_radius * zoom)
        max_x = max(x for x, y in positions.values()) if positions else 600
        max_y = max(y for x, y in positions.values()) if positions else 600
        width = int(max_x + node_radius + 40)
        height = int(max_y + node_radius + 40)
        max_width = max(max_width, width)
        max_height = max(max_height, height)
        # Now yield each frame centered on a canvas of max_width, max_height
        for (root, positions, node_radius, left, right) in frame_data:
            image = Image.new('RGB', (max_width, max_height), 'white')
            draw = ImageDraw.Draw(image)
            try:
                font_size = max(8, int(12 * zoom))
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
            min_x = min(x for x, y in positions.values())
            min_y = min(y for x, y in positions.values())
            offset_x = (max_width - (max(x for x, y in positions.values()) - min_x)) // 2 - min_x
            offset_y = (max_height - (max(y for x, y in positions.values()) - min_y)) // 2 - min_y
            centered_positions = {node: (x + offset_x, y + offset_y) for node, (x, y) in positions.items()}
            self._draw_tree_on_image(root, centered_positions, node_radius, font, max(1, int(2 * zoom)), draw, highlight=(left, right))
            yield image
        # Add several frames of the full tree at the end
        for _ in range(int(1.5 / delay)):
            image = Image.new('RGB', (max_width, max_height), 'white')
            draw = ImageDraw.Draw(image)
            try:
                font_size = max(8, int(12 * zoom))
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()
            min_x = min(x for x, y in positions.values())
            min_y = min(y for x, y in positions.values())
            offset_x = (max_width - (max(x for x, y in positions.values()) - min_x)) // 2 - min_x
            offset_y = (max_height - (max(y for x, y in positions.values()) - min_y)) // 2 - min_y
            centered_positions = {node: (x + offset_x, y + offset_y) for node, (x, y) in positions.items()}
            self._draw_tree_on_image(self.tree.root, centered_positions, node_radius, font, max(1, int(2 * zoom)), draw)
            yield image 