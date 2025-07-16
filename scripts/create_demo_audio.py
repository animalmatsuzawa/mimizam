#!/usr/bin/env python3
"""Mimizam デモ用音声ファイル生成スクリプト"""

import os
from pathlib import Path

# デモファイル定数
DEMO_SONG1 = "test_media/demo_song1.wav"
DEMO_SONG2 = "test_media/demo_song2.wav"
DEMO_QUERY = "test_media/demo_query.wav"

def create_synthetic_demo_files():
    """合成音声でデモファイルを作成"""
    print("🔧 合成音声でデモファイルを生成中...")
    
    try:
        import numpy as np
        import soundfile as sf
        
        # サンプルレートと長さ
        sr = 22050
        duration = 5  # 5秒
        t = np.linspace(0, duration, int(sr * duration))
        
        # デモソング1: シンプルなメロディー
        freqs1 = [440, 523, 659, 784, 880]  # A, C, E, G, A
        melody1 = np.zeros_like(t)
        
        for i, freq in enumerate(freqs1):
            start_idx = int(i * len(t) / len(freqs1))
            end_idx = int((i + 1) * len(t) / len(freqs1))
            melody1[start_idx:end_idx] = np.sin(2 * np.pi * freq * t[start_idx:end_idx])
        
        # エンベロープを適用（フェードイン・アウト）
        envelope1 = np.ones_like(melody1)
        fade_len = int(0.1 * sr)  # 0.1秒のフェード
        envelope1[:fade_len] = np.linspace(0, 1, fade_len)
        envelope1[-fade_len:] = np.linspace(1, 0, fade_len)
        melody1 *= envelope1 * 0.3  # 音量調整
        
        # デモソング2: 違うメロディー
        freqs2 = [330, 392, 466, 554, 659]  # E, G, B♭, C#, E
        melody2 = np.zeros_like(t)
        
        for i, freq in enumerate(freqs2):
            start_idx = int(i * len(t) / len(freqs2))
            end_idx = int((i + 1) * len(t) / len(freqs2))
            melody2[start_idx:end_idx] = np.sin(2 * np.pi * freq * t[start_idx:end_idx])
        
        envelope2 = np.ones_like(melody2)
        envelope2[:fade_len] = np.linspace(0, 1, fade_len)
        envelope2[-fade_len:] = np.linspace(1, 0, fade_len)
        melody2 *= envelope2 * 0.3
        
        # WAVファイルとして保存
        sf.write(DEMO_SONG1, melody1, sr)
        sf.write(DEMO_SONG2, melody2, sr)
        
        print(f"✅ {DEMO_SONG1} を生成しました")
        print(f"✅ {DEMO_SONG2} を生成しました")
        
        # クエリファイル（demo_song1の一部）
        query_segment = melody1[int(sr*1):int(sr*3)]  # 1-3秒の部分
        sf.write(DEMO_QUERY, query_segment, sr)
        print(f"✅ {DEMO_QUERY} を生成しました")
        
        return True
        
    except ImportError:
        print("❌ soundfileライブラリが必要です")
        print("pip install soundfile でインストールしてください")
        return False
    except Exception as e:
        print(f"❌ 音声生成エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🎵 Mimizam デモ用音声ファイル作成")
    print("=" * 50)
    
    # プロジェクトルートに移動
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # test_mediaディレクトリを作成
    Path("test_media").mkdir(exist_ok=True)
    
    # 既存ファイルをチェック
    if Path(DEMO_SONG1).exists() and Path(DEMO_SONG2).exists():
        response = input("デモファイルは既に存在します。再作成しますか？ (y/N): ")
        if response.lower() != 'y':
            print("❌ 処理をキャンセルしました")
            return
    
    # 合成音声でデモファイルを作成
    if create_synthetic_demo_files():
        print("\n🎉 デモ用音声ファイルの準備が完了しました！")
        print("\n📁 作成されたファイル:")
        for filename in [DEMO_SONG1, DEMO_SONG2, DEMO_QUERY]:
            if Path(filename).exists():
                size = Path(filename).stat().st_size
                print(f"   {filename} ({size:,} bytes)")
        
        print("\n💡 これで examples/mimizam_demo.py を実行できます")
        print("   python examples/mimizam_demo.py")
    else:
        print("❌ デモファイルの作成に失敗しました")

if __name__ == "__main__":
    main()
