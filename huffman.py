"""
huffman.py
Huffman Encoding algorithm logic for visualization.
"""
import heapq
from collections import Counter

class HuffmanNode:
    """Node for Huffman Tree."""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanTree:
    """Huffman Tree construction and encoding logic."""
    def __init__(self, text):
        self.text = text
        self.frequency = Counter(text)
        self.root = None
        self.codes = {}
        self.encoded = ''
        self._build_tree()
        self._generate_codes()
        self._encode_text()
    def _build_tree(self):
        heap = [HuffmanNode(char, freq) for char, freq in self.frequency.items()]
        heapq.heapify(heap)
        self.steps = []  # For visualization: record each merge step
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
            self.steps.append((left, right, merged))
        self.root = heap[0] if heap else None
    def _generate_codes(self):
        def dfs(node, code):
            if node is None:
                return
            if node.char is not None:
                self.codes[node.char] = code
            dfs(node.left, code + '0')
            dfs(node.right, code + '1')
        if self.root:
            dfs(self.root, '')
    def _encode_text(self):
        self.encoded = ''.join(self.codes[c] for c in self.text)
    def get_frequency_table(self):
        return dict(self.frequency)
    def get_codes(self):
        return self.codes
    def get_encoded(self):
        return self.encoded
    def get_steps(self):
        """Return the list of merge steps for visualization."""
        return self.steps
    def get_compression_stats(self):
        original_bits = len(self.text) * 8
        compressed_bits = len(self.encoded)
        if original_bits == 0:
            percent = 0
        else:
            percent = 100 * (original_bits - compressed_bits) / original_bits
        return original_bits, compressed_bits, percent 