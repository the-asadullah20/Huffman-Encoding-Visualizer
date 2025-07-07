"""
main.py
Tkinter GUI for Huffman Encoding Visualizer.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from huffman import HuffmanTree
from visualizer import HuffmanTreeVisualizer
from utils import export_canvas_as_image, export_frames_as_gif, copy_to_clipboard
from PIL import ImageGrab
import threading
import numpy as np

class HuffmanApp:
    """Main application class for the Huffman Encoding Visualizer."""
    def __init__(self, root):
        self.root = root
        self.root.title('Huffman Encoding Visualizer')
        self.root.geometry('1200x800')
        self._setup_styles()
        self._build_layout()
        self.tree = None
        self.visualizer = None
        self.tooltip = None
        self.frames = []
        self.zoom_level = 1.0
        self.animation_speed = 0.7
    def _setup_styles(self):
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 11))
        style.configure('TLabel', font=('Arial', 11))
        style.configure('Treeview', font=('Arial', 10))
    def _build_layout(self):
        # Main layout frames
        self.input_frame = ttk.Frame(self.root, padding=10)
        self.input_frame.pack(side='top', fill='x')
        self.center_frame = ttk.Frame(self.root)
        self.center_frame.pack(side='left', fill='both', expand=True)
        self.output_frame = ttk.Frame(self.root, padding=10)
        self.output_frame.pack(side='right', fill='y')
        # Input section
        ttk.Label(self.input_frame, text='Enter Text:').pack(side='left')
        self.textbox = tk.Text(self.input_frame, height=3, width=60, font=('Arial', 12))
        self.textbox.pack(side='left', padx=10)
        self.textbox.bind('<KeyRelease>', self._on_text_change)
        ttk.Button(self.input_frame, text='Visualize', command=self.visualize_animated).pack(side='left', padx=5)
        ttk.Button(self.input_frame, text='Reset', command=self.reset).pack(side='left', padx=5)
        ttk.Button(self.input_frame, text='Load File', command=self.load_file).pack(side='left', padx=5)
        # Zoom controls
        zoom_frame = ttk.Frame(self.center_frame)
        zoom_frame.pack(side='top', fill='x')
        ttk.Button(zoom_frame, text='Zoom In', command=self.zoom_in).pack(side='left', padx=2)
        ttk.Button(zoom_frame, text='Zoom Out', command=self.zoom_out).pack(side='left', padx=2)
        # Animation speed slider
        ttk.Label(zoom_frame, text='Animation Speed:').pack(side='left', padx=10)
        self.speed_var = tk.DoubleVar(value=0.7)
        self.speed_slider = ttk.Scale(zoom_frame, from_=0.1, to=2.0, orient='horizontal', variable=self.speed_var, command=self.on_speed_change)
        self.speed_slider.pack(side='left', padx=2)
        ttk.Label(zoom_frame, text='Slow').pack(side='left')
        ttk.Label(zoom_frame, text='Fast').pack(side='left')
        # Scrollable canvas for tree visualization
        canvas_frame = ttk.Frame(self.center_frame)
        canvas_frame.pack(side='top', fill='both', expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=700, height=700, bg='white', highlightthickness=2, highlightbackground='#aaa')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.h_scroll = tk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.h_scroll.pack(side='bottom', fill='x')
        self.v_scroll = tk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        self.v_scroll.pack(side='right', fill='y')
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Control-MouseWheel>', self.on_mousewheel_zoom)  # Windows/Linux
        self.canvas.bind('<Command-MouseWheel>', self.on_mousewheel_zoom)  # Mac
        self.canvas.bind('<ButtonPress-2>', self.on_drag_start)  # Middle mouse button
        self.canvas.bind('<B2-Motion>', self.on_drag_motion)
        self.canvas.bind('<ButtonPress-1>', self.on_drag_start)  # Left mouse button (for drag)
        self.canvas.bind('<B1-Motion>', self.on_drag_motion)
        # Output info section
        ttk.Label(self.output_frame, text='Output Information', font=('Arial', 13, 'bold')).pack(pady=5)
        self.info_text = tk.Text(self.output_frame, height=8, width=40, font=('Arial', 11), state='disabled', bg='#f8f8f8')
        self.info_text.pack(pady=5)
        ttk.Button(self.output_frame, text='Copy Encoded String', command=self.copy_encoded).pack(pady=2)
        ttk.Button(self.output_frame, text='Export Tree as Image', command=self.export_image).pack(pady=2)
        ttk.Button(self.output_frame, text='Export Animation as MP4', command=self.export_animation).pack(pady=2)
        # Frequency table
        ttk.Label(self.output_frame, text='Frequency Table', font=('Arial', 12, 'bold')).pack(pady=5)
        self.freq_table = ttk.Treeview(self.output_frame, columns=('char', 'freq'), show='headings', height=6)
        self.freq_table.heading('char', text='Char')
        self.freq_table.heading('freq', text='Frequency')
        self.freq_table.column('char', width=60, anchor='center')
        self.freq_table.column('freq', width=80, anchor='center')
        self.freq_table.pack(pady=2)
        # Huffman codes table
        ttk.Label(self.output_frame, text='Huffman Codes', font=('Arial', 12, 'bold')).pack(pady=5)
        self.codes_table = ttk.Treeview(self.output_frame, columns=('char', 'code'), show='headings', height=6)
        self.codes_table.heading('char', text='Char')
        self.codes_table.heading('code', text='Code')
        self.codes_table.column('char', width=60, anchor='center')
        self.codes_table.column('code', width=120, anchor='center')
        self.codes_table.pack(pady=2)
        # Tooltip label
        self.tooltip_label = ttk.Label(self.center_frame, text='', background='yellow', font=('Arial', 10), relief='solid')
        self.tooltip_label.place_forget()
    def _on_text_change(self, event=None):
        # Real-time update (optional enhancement)
        pass
    def on_speed_change(self, event=None):
        self.animation_speed = self.speed_var.get()
        if self.visualizer:
            self.visualizer.animation_delay = self.animation_speed
    def zoom_in(self):
        self.zoom_level *= 1.2
        self.visualize(redraw_only=True, keep_centered=True)
    def zoom_out(self):
        self.zoom_level /= 1.2
        self.visualize(redraw_only=True, keep_centered=True)
    def visualize(self, redraw_only=False, keep_centered=False):
        text = self.textbox.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('Input Required', 'Please enter some text.')
            return
        if not redraw_only:
            self.tree = HuffmanTree(text)
            self.visualizer = HuffmanTreeVisualizer(self.canvas, self.tree, on_node_hover=self.show_tooltip)
        self.visualizer.zoom_level = self.zoom_level
        self.visualizer.animation_delay = self.animation_speed
        self.visualizer.draw_static(keep_centered=keep_centered)
        if not redraw_only:
            self.update_output()
    def visualize_animated(self):
        text = self.textbox.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('Input Required', 'Please enter some text.')
            return
        self.tree = HuffmanTree(text)
        self.visualizer = HuffmanTreeVisualizer(self.canvas, self.tree, on_node_hover=self.show_tooltip)
        self.visualizer.zoom_level = self.zoom_level
        self.visualizer.animation_delay = self.animation_speed
        self.visualizer.animate_construction(callback=self.update_output)
    def update_output(self):
        # Output info
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', 'end')
        if not self.tree:
            self.info_text.config(state='disabled')
            return
        orig, comp, percent = self.tree.get_compression_stats()
        self.info_text.insert('end', f'Original Size: {orig} bits\n')
        self.info_text.insert('end', f'Compressed Size: {comp} bits\n')
        self.info_text.insert('end', f'Compression Saved: {percent:.2f}%\n')
        self.info_text.insert('end', f'Encoded String:\n{self.tree.get_encoded()}\n')
        self.info_text.config(state='disabled')
        # Frequency table
        for i in self.freq_table.get_children():
            self.freq_table.delete(i)
        for char, freq in self.tree.get_frequency_table().items():
            self.freq_table.insert('', 'end', values=(repr(char), freq))
        # Codes table
        for i in self.codes_table.get_children():
            self.codes_table.delete(i)
        for char, code in self.tree.get_codes().items():
            self.codes_table.insert('', 'end', values=(repr(char), code))
    def reset(self):
        self.textbox.delete('1.0', 'end')
        self.canvas.delete('all')
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', 'end')
        self.info_text.config(state='disabled')
        for i in self.freq_table.get_children():
            self.freq_table.delete(i)
        for i in self.codes_table.get_children():
            self.codes_table.delete(i)
        self.tooltip_label.place_forget()
        self.zoom_level = 1.0
        self.animation_speed = 0.7
        self.speed_var.set(0.7)
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.textbox.delete('1.0', 'end')
            self.textbox.insert('1.0', content)
    def export_image(self):
        # Ask user for export scale
        scale_win = tk.Toplevel(self.root)
        scale_win.title('Export Scale')
        tk.Label(scale_win, text='Export Scale (1 = normal, 2 = double, etc):').pack(padx=10, pady=5)
        scale_var = tk.IntVar(value=2)
        scale_box = ttk.Combobox(scale_win, textvariable=scale_var, values=[1, 2, 3, 4], state='readonly', width=5)
        scale_box.pack(padx=10, pady=5)
        def do_export():
            scale = scale_var.get()
            file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG Image', '*.png'), ('JPEG Image', '*.jpg')])
            if file_path:
                if not self.visualizer or not self.tree:
                    messagebox.showwarning('No Tree', 'Please visualize a tree first.')
                    return
                img = self.visualizer.render_to_image(zoom=self.visualizer.zoom_level * scale)
                img.save(file_path)
                messagebox.showinfo('Exported', f'Image saved to {file_path}')
            scale_win.destroy()
        ttk.Button(scale_win, text='Export', command=do_export).pack(pady=10)
        scale_win.transient(self.root)
        scale_win.grab_set()
        self.root.wait_window(scale_win)
    def export_animation(self):
        # Ask user for export scale
        scale_win = tk.Toplevel(self.root)
        scale_win.title('Export Scale')
        tk.Label(scale_win, text='Export Scale (1 = normal, 2 = double, etc):').pack(padx=10, pady=5)
        scale_var = tk.IntVar(value=2)
        scale_box = ttk.Combobox(scale_win, textvariable=scale_var, values=[1, 2, 3, 4], state='readonly', width=5)
        scale_box.pack(padx=10, pady=5)
        def do_export():
            scale = scale_var.get()
            file_path = filedialog.asksaveasfilename(defaultextension='.mp4', filetypes=[('MP4 Video', '*.mp4')])
            if file_path:
                if not self.visualizer or not self.tree:
                    messagebox.showwarning('No Animation', 'Please visualize a tree first.')
                    return
                self.visualizer.animate_construction(callback=self.update_output)
                # Show 'please wait' message
                wait_win = tk.Toplevel(self.root)
                wait_win.title('Exporting...')
                tk.Label(wait_win, text='Please wait, your video is being prepared...').pack(padx=20, pady=20)
                wait_win.transient(self.root)
                wait_win.grab_set()
                wait_win.update()
                def export_mp4():
                    import imageio
                    import numpy as np
                    writer = imageio.get_writer(file_path, fps=int(1/self.animation_speed) if self.animation_speed > 0 else 2, format='ffmpeg')
                    try:
                        for frame in self.visualizer.stream_animation_frames_to_images(zoom=self.visualizer.zoom_level * scale, delay=self.animation_speed):
                            writer.append_data(np.array(frame))
                        self.root.after(0, lambda: (wait_win.destroy(), messagebox.showinfo('Exported', f'Animation saved to {file_path}')))
                    except Exception as e:
                        self.root.after(0, lambda: (wait_win.destroy(), messagebox.showerror('Error', f'Failed to export animation: {e}')))
                    finally:
                        writer.close()
                threading.Thread(target=export_mp4, daemon=True).start()
            scale_win.destroy()
        ttk.Button(scale_win, text='Export', command=do_export).pack(pady=10)
        scale_win.transient(self.root)
        scale_win.grab_set()
        self.root.wait_window(scale_win)
    def copy_encoded(self):
        if self.tree:
            copy_to_clipboard(self.tree.get_encoded())
            messagebox.showinfo('Copied', 'Encoded string copied to clipboard!')
    def show_tooltip(self, node_visual):
        if node_visual is None:
            self.tooltip_label.place_forget()
            return
        label = ''
        if node_visual.node.char is not None:
            label = f"Char: {repr(node_visual.node.char)}\nCode: {self.tree.get_codes().get(node_visual.node.char, '')}"
        else:
            label = f"Freq: {node_visual.node.freq}"
        self.tooltip_label.config(text=label)
        # Convert canvas (x, y) to screen coordinates, accounting for scroll and zoom
        canvas_x = self.canvas.canvasx(node_visual.x)
        canvas_y = self.canvas.canvasy(node_visual.y)
        abs_x = self.canvas.winfo_rootx() + canvas_x
        abs_y = self.canvas.winfo_rooty() + canvas_y
        # Place tooltip near the node, offset a bit so it doesn't cover the node
        self.tooltip_label.place(x=canvas_x + 30, y=canvas_y - 10)
    def on_canvas_click(self, event):
        if not self.visualizer:
            return
        for nv in self.visualizer.node_visuals:
            if nv.oval:
                coords = self.canvas.coords(nv.oval)
                if coords and coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                    self.show_tooltip(nv)
                    return
        self.tooltip_label.place_forget()
    def on_mousewheel_zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    def on_drag_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
    def on_drag_motion(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

def main():
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()

if __name__ == '__main__':
    main() 