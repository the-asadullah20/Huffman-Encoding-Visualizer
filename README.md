# Huffman Encoding Visualizer

A Python Tkinter application to visualize the Huffman Encoding Compression Algorithm with smooth animations and interactive features.

## Features
- **Text Input:** Enter or paste text to compress.
- **Animated Huffman Tree Construction:** Watch the tree build step-by-step with color highlights.
- **Tree Visualization:** Canvas-based, interactive Huffman tree display.
- **Output Information:**
  - Final encoded bit string
  - Original vs compressed bit sizes
  - Compression percentage saved
  - Huffman codes for each character
  - Frequency table
- **Export Options:**
  - Download tree visualization as PNG/JPG
  - Export animation as MP4 (or save frames)
  - Copy encoded string to clipboard
- **Reset Button:** Clear all input and visuals.
- **Optional Enhancements:**
  - Light/Dark mode toggle
  - Drag and drop text files for input
  - Real-time tree updates as you type
  - Tooltips on tree nodes (character/code)

## Project Structure
- `main.py` — GUI logic and application entry point
- `huffman.py` — Huffman algorithm logic
- `visualizer.py` — Tree drawing and animation
- `utils.py` — Helpers (exporting images, clipboard, etc.)
- `requirements.txt` — Python dependencies

## Setup
1. **Install Python 3** (if not already installed)
2. **Clone or Download this repository**
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage
1. Enter text in the input box.
2. Click "Visualize" to see the Huffman tree animate.
3. Explore the output information and interact with the tree.
4. Use export/copy/reset features as needed.

## Requirements
- Python 3.x
- Tkinter (usually included with Python)
- [Pillow](https://pypi.org/project/Pillow/) (for image export)
- [imageio](https://pypi.org/project/imageio/) (for animation export)

## License
MIT 