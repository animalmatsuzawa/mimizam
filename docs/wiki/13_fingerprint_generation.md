# 音声指紋生成アルゴリズム詳細

mimizamの音声指紋生成は、Shazamアルゴリズムをベースとした高精度な音声識別システムです。本ドキュメントでは、詳細なアルゴリズムと実装について説明します。

## 🎵 音声指紋生成の概要

音声指紋システムでは、音声データから特徴的なパターンを抽出し、コンパクトなハッシュ値として格納します。このプロセスは以下の段階で構成されます：

### 基本処理フロー

1. **音声前処理**: サンプリングレート変換・正規化
2. **スペクトログラム生成**: STFT（短時間フーリエ変換）による周波数解析
3. **ピーク検出**: 局所最大値の抽出
4. **ハッシュ生成**: アンカー・ターゲットペアからのハッシュ値作成

mimizamでは音声特性に応じてパラメータを最適化し、高精度かつ高速な処理を実現しています。

## 🔬 詳細アルゴリズム

### 1. スペクトログラム生成

音声データを時間-周波数表現に変換します。

#### STFT（短時間フーリエ変換）
```python
from mimizam import AudioFingerprinter

# 基本設定
fingerprinter = AudioFingerprinter(
    n_fft=2048,        # FFTサイズ（周波数分解能）
    hop_length=512,    # ホップ長（時間分解能）
    window='hann'      # 窓関数
)

# 音声読み込みとスペクトログラム生成
audio = fingerprinter.load_audio("song.wav")
spectrogram = fingerprinter.generate_spectrogram(audio)
```

#### パラメータの意味
- **FFTサイズ**: 通常1024または2048サンプル（周波数分解能と時間分解能のトレードオフ）
- **ホップ長**: FFTサイズの1/4程度（時間分解能の調整）
- **窓関数**: ハニング窓またはハミング窓（スペクトル漏れの抑制）

#### 設計根拠
- Wang 2003の基本手法に基づく時間-周波数解析
- 音声特性に応じたパラメータ調整により精度向上

### 2. ピーク検出

スペクトログラムから局所最大値（ピーク）を検出します。

#### 局所最大値検出
```python
# ピーク検出設定
fingerprinter = AudioFingerprinter(
    min_amplitude=-60,           # 最小振幅閾値（dB）
    peak_neighborhood_size=20,   # 近傍サイズ
    enable_adaptive_params=True  # 適応パラメータ
)

# ピーク検出実行
peaks = fingerprinter.find_peaks(spectrogram)
print(f"検出されたピーク数: {len(peaks)}")
```

#### Peak データ構造
```python
from mimizam import Peak
import numpy as np

# Peak オブジェクト（numpy.float64型で最適化済み）
peak = Peak(
    time=np.float64(1.5),      # 時間（秒）
    frequency=np.float64(440), # 周波数（Hz）
    amplitude=np.float64(-20)  # 振幅（dB）
)
```

#### 最適化ポイント
- **動的閾値**: 音声のノイズレベルに応じた検出閾値の自動調整
- **密度制御**: 過密なピークの間引き処理
- **近傍サイズ**: 通常3×3または5×5の範囲（ノイズ除去と精度のバランス）

### 3. ハッシュ生成

検出されたピークからハッシュ値を生成します。

#### アンカー・ターゲット方式
```python
# ハッシュ生成設定
fingerprinter = AudioFingerprinter(
    target_zone_t=1.8,    # ターゲットゾーン時間範囲（秒）
    target_zone_f=1000,   # ターゲットゾーン周波数範囲（Hz）
    max_time_delta=200    # 最大時間差（フレーム）
)

# 指紋生成実行
fingerprints = fingerprinter.fingerprint_audio(audio)
print(f"生成された指紋数: {len(fingerprints)}")
```

#### Fingerprint データ構造
```python
from mimizam import Fingerprint

# Fingerprint オブジェクト
fingerprint = Fingerprint(
    hash_value="a1b2c3d4e5f6...",  # SHA-256ハッシュ値
    time_offset=1.5               # 時間オフセット（秒）
)
```

#### 技術的詳細
- **ターゲットゾーン**: アンカーから一定範囲内のピークを選択
- **特徴量**: 周波数差・時間差を組み合わせた特徴ベクトル
- **ハッシュ化**: SHA-256による固定長ハッシュ値の生成
- **量子化**: 特徴量の正規化による安定性向上

### 4. 実装における最適化

#### 音声特性に応じたパラメータ調整
```python
from mimizam import AdaptiveParameterTuner

# 適応パラメータ調整
tuner = AdaptiveParameterTuner()
optimized_params = tuner.optimize_for_audio(audio)

fingerprinter = AudioFingerprinter(**optimized_params)
```

#### 処理効率の向上
```python
# Numba JIT最適化の活用
fingerprinter = AudioFingerprinter(
    use_numba_optimization=True,  # Numba最適化有効
    parallel_processing=True      # 並列処理有効
)

# メモリ効率的な処理
fingerprinter = AudioFingerprinter(
    chunk_size=30,  # 30秒チャンクで処理
    memory_limit=1024  # メモリ制限（MB）
)
```

## 🔧 カスタマイズ例

### 高精度設定
```python
# 高精度音声指紋生成
high_precision_fingerprinter = AudioFingerprinter(
    n_fft=4096,              # 高い周波数分解能
    hop_length=256,          # 細かい時間分解能
    min_amplitude=-70,       # 敏感な検出
    peak_neighborhood_size=30, # 大きな近傍サイズ
    target_zone_t=2.0,       # 広いターゲットゾーン
    target_zone_f=1500
)
```

### 高速設定
```python
# 高速音声指紋生成
fast_fingerprinter = AudioFingerprinter(
    n_fft=1024,              # 小さなFFTサイズ
    hop_length=512,          # 粗い時間分解能
    min_amplitude=-40,       # 高い閾値
    peak_neighborhood_size=10, # 小さな近傍サイズ
    enable_adaptive_params=True, # 適応最適化
    use_numba_optimization=True  # JIT最適化
)
```

### ジャンル特化設定
```python
# クラシック音楽用設定
classical_fingerprinter = AudioFingerprinter(
    n_fft=4096,              # 高周波数分解能
    hop_length=256,          # 細かい時間分解能
    min_amplitude=-65,       # 低い閾値（微細な変化を捉える）
    target_zone_f=2000       # 広い周波数範囲
)

# ポップス音楽用設定
pop_fingerprinter = AudioFingerprinter(
    n_fft=2048,              # 標準分解能
    hop_length=512,          # 標準時間分解能
    min_amplitude=-50,       # 中程度の閾値
    target_zone_f=1000       # 標準周波数範囲
)
```

## 📊 可視化とデバッグ

### スペクトログラム可視化
```python
import matplotlib.pyplot as plt

# スペクトログラムとピークの可視化
fingerprinter.visualize_analysis(
    audio, 
    title="音声指紋生成プロセス",
    show_peaks=True,      # ピーク表示
    show_fingerprints=True # 指紋表示
)
plt.show()
```

### 処理統計の確認
```python
from mimizam import PerformanceMonitor

# パフォーマンス監視
monitor = PerformanceMonitor()
fingerprinter.set_performance_monitor(monitor)

# 指紋生成実行
fingerprints = fingerprinter.fingerprint_audio(audio)

# 統計情報表示
stats = monitor.get_statistics()
print(f"処理時間: {stats['total_time']:.2f}秒")
print(f"ピーク数: {stats['peak_count']}")
print(f"指紋数: {stats['fingerprint_count']}")
print(f"処理速度: {stats['processing_speed']:.1f}x リアルタイム")
```

## 🧪 品質評価

### 指紋品質の評価
```python
# 指紋品質評価
quality_metrics = fingerprinter.evaluate_fingerprint_quality(fingerprints)
print(f"指紋密度: {quality_metrics['density']:.2f} 指紋/秒")
print(f"ユニーク率: {quality_metrics['uniqueness']:.2%}")
print(f"安定性スコア: {quality_metrics['stability']:.2f}")
```

### A/Bテスト
```python
# 異なる設定での比較
config_a = AudioFingerprinter(n_fft=2048, hop_length=512)
config_b = AudioFingerprinter(n_fft=4096, hop_length=256)

fingerprints_a = config_a.fingerprint_audio(audio)
fingerprints_b = config_b.fingerprint_audio(audio)

print(f"設定A: {len(fingerprints_a)}個の指紋")
print(f"設定B: {len(fingerprints_b)}個の指紋")
```

## 🔬 アルゴリズム詳細

### 数学的基礎

#### STFT変換
```
X(m,k) = Σ[n=0 to N-1] x(n+mH) * w(n) * e^(-j2πkn/N)
```
- `m`: 時間フレームインデックス
- `k`: 周波数ビンインデックス
- `H`: ホップ長
- `w(n)`: 窓関数

#### ピーク検出条件
```
P(t,f) = 1 if |X(t,f)| > threshold AND |X(t,f)| = max(|X(t±δt, f±δf)|)
         0 otherwise
```

#### ハッシュ生成
```
hash = SHA256(f1 || f2 || Δt)
```
- `f1`: アンカー周波数
- `f2`: ターゲット周波数  
- `Δt`: 時間差

## 📚 参考文献・引用

- **Avery Li-Chun Wang**, "An Industrial-Strength Audio Search Algorithm", 2003  
  [https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- **村田昇**「音響指紋とその応用」, 映像情報メディア学会誌, 2012年
- **Mark Plumbley et al.**, "Pattern Recognition and Machine Learning for Audio Fingerprinting", Springer, 2019
- **Bishop, C. M.** "Pattern Recognition and Machine Learning", Springer, 2006

## 🔧 実装のベストプラクティス

### 1. メモリ効率
```python
# 大きな音声ファイルの処理
def process_large_audio(file_path, chunk_duration=30):
    fingerprinter = AudioFingerprinter()
    all_fingerprints = []
    
    for chunk in fingerprinter.load_audio_chunks(file_path, chunk_duration):
        chunk_fingerprints = fingerprinter.fingerprint_audio(chunk)
        all_fingerprints.extend(chunk_fingerprints)
    
    return all_fingerprints
```

### 2. エラーハンドリング
```python
from mimizam import AudioProcessingError, FingerprintGenerationError

try:
    fingerprints = fingerprinter.fingerprint_audio(audio)
except AudioProcessingError as e:
    print(f"音声処理エラー: {e}")
except FingerprintGenerationError as e:
    print(f"指紋生成エラー: {e}")
```

### 3. 設定の保存・読み込み
```python
import json

# 設定の保存
config = fingerprinter.get_config()
with open("fingerprinter_config.json", "w") as f:
    json.dump(config, f, indent=2)

# 設定の読み込み
with open("fingerprinter_config.json", "r") as f:
    config = json.load(f)
fingerprinter = AudioFingerprinter(**config)
```

## 🔗 関連ドキュメント

- [スコアリング詳細](./14_scoring_details.md) - マッチングアルゴリズム
- [適応パラメータ調整](./15_adaptive_parameters.md) - 自動最適化
- [パフォーマンス最適化](./12_performance_optimization.md) - 高速化テクニック
- [実装例](./16_basic_examples.md) - 実践的なサンプルコード
