"""
mimizam.examples - mimizamの使用例

このモジュールには、mimizam音声指紋システムの様々な使用例とデモが含まれています。
"""

# 主要なデモ関数をエクスポート
try:
    from .mimizam_demo import main as demo_main
except ImportError:
    demo_main = None

try:
    from .video_fingerprinter import main as video_main
except ImportError:
    video_main = None

__all__ = ['demo_main', 'video_main']
