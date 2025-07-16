"""
テスト用ユーティリティ関数
"""

import os
import tempfile
import numpy as np
from typing import Optional


def create_test_audio_file(output_dir: Optional[str] = None, filename: str = "test_audio.wav", duration: float = 2.0) -> str:
    """
    テスト用の音声ファイルを作成
    
    Args:
        output_dir: 出力ディレクトリ（Noneの場合は一時ディレクトリを作成）
        filename: ファイル名
        duration: 音声の長さ（秒）
    
    Returns:
        作成された音声ファイルのパス
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    sr = 22050
    t = np.linspace(0, duration, int(duration * sr))
    
    # 複数の周波数成分を持つ信号（A4, A5, E6音）
    audio = (
        0.5 * np.sin(2 * np.pi * 440 * t) +    # A4
        0.3 * np.sin(2 * np.pi * 880 * t) +    # A5
        0.2 * np.sin(2 * np.pi * 1320 * t)     # E6
    )
    
    audio_file = os.path.join(output_dir, filename)
    
    try:
        # soundfileを優先的に使用
        import soundfile as sf
        sf.write(audio_file, audio, sr)
    except ImportError:
        # soundfileが利用できない場合はwaveモジュールを使用
        import wave
        with wave.open(audio_file, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sr)
            audio_int16 = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
    
    return audio_file


class TestAudioMixin:
    """
    テスト用音声ファイル作成機能を提供するミックスイン
    """
    
    def setup_audio(self):
        """音声ファイル関連のセットアップ"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_file = create_test_audio_file(self.temp_dir)
    
    def teardown_audio(self):
        """音声ファイル関連のクリーンアップ"""
        if hasattr(self, 'test_audio_file') and os.path.exists(self.test_audio_file):
            os.unlink(self.test_audio_file)
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def _create_test_audio_file(self, filename: str = "test_audio.wav") -> str:
        """
        後方互換性のためのメソッド
        新しいコードではcreate_test_audio_file関数を直接使用することを推奨
        """
        return create_test_audio_file(self.temp_dir, filename)
