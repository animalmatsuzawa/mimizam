# 適応パラメータ調整

mimizamの適応パラメータ調整システムは、音声の特性に基づいて動的にフィンガープリンティングパラメータを最適化します。音声の種類や品質に応じて自動的に最適な設定を選択し、識別精度を向上させます。

## 🎯 適応パラメータ調整の概要

### システム構成

```
適応パラメータ調整システム
├── AdaptiveParameterTuner
│   ├── 音声特性分析
│   ├── パラメータ調整ロジック
│   └── 最適化戦略
└── PerformanceMonitor
    ├── 処理時間監視
    ├── 指紋品質評価
    └── パフォーマンス統計
```

## 🔧 AdaptiveParameterTuner クラス

### 基本的な使用方法

```python
from mimizam import AudioFingerprinter
from mimizam.adaptive_parameters import AdaptiveParameterTuner
import librosa

# 適応パラメータチューナーの初期化
tuner = AdaptiveParameterTuner()

# 音声ファイルの読み込み
audio, sr = librosa.load("sample_music.wav", sr=22050)

# 音声特性の分析
characteristics = tuner.analyze_audio_characteristics(audio, sr)

# パラメータの調整
adjusted_params = tuner.adjust_parameters(characteristics)

# 調整されたパラメータで指紋生成器を作成
fingerprinter = AudioFingerprinter(
    enable_adaptive_params=True,
    **adjusted_params
)

# 音声指紋の生成
fingerprints = fingerprinter.fingerprint_audio(audio)

print(f"生成された指紋数: {len(fingerprints)}")
```

### 音声特性分析の詳細

```python
def analyze_audio_example():
    """音声特性分析の詳細例"""
    
    tuner = AdaptiveParameterTuner()
    
    # 様々な音声タイプでの分析
    audio_files = [
        ("classical_music.wav", "クラシック音楽"),
        ("rock_song.wav", "ロック音楽"),
        ("speech.wav", "音声"),
        ("ambient_sound.wav", "環境音")
    ]
    
    for file_path, description in audio_files:
        audio, sr = librosa.load(file_path, sr=22050)
        characteristics = tuner.analyze_audio_characteristics(audio, sr)
        
        print(f"\n=== {description} の分析結果 ===")
        print(f"継続時間: {characteristics['duration']:.2f}秒")
        print(f"RMS: {characteristics['rms']:.4f}")
        print(f"静寂比率: {characteristics['silence_ratio']:.2f}")
        print(f"スペクトルエントロピー: {characteristics['spectral_entropy']:.2f}")
        print(f"ゼロクロッシング率: {characteristics['zero_crossing_rate']:.4f}")
        print(f"テンポ: {characteristics['tempo']:.1f} BPM")
        print(f"スペクトル重心: {characteristics['spectral_centroid_mean']:.0f} Hz")
        print(f"動的レンジ: {characteristics['dynamic_range']:.4f}")
```

### 音声特性の詳細項目

```python
# 分析される音声特性
AUDIO_CHARACTERISTICS = {
    'duration': '音声の継続時間（秒）',
    'rms': 'RMS（Root Mean Square）振幅',
    'peak_amplitude': 'ピーク振幅',
    'silence_ratio': '静寂部分の比率',
    'spectral_entropy': 'スペクトルエントロピー（複雑さ指標）',
    'zero_crossing_rate': 'ゼロクロッシング率',
    'tempo': 'テンポ（BPM）',
    'dynamic_range': '動的レンジ',
    'spectral_centroid_mean': 'スペクトル重心の平均値'
}
```

## ⚙️ パラメータ調整ロジック

### デフォルトパラメータ

```python
# デフォルトパラメータ設定
DEFAULT_PARAMETERS = {
    'min_amplitude': -60,           # 最小振幅閾値（dB）
    'peak_neighborhood_size': 10,   # ピーク検出近傍サイズ
    'target_zone_size': 5,          # ターゲットゾーンサイズ
    'max_peaks_per_second': 15,     # 1秒あたりの最大ピーク数
    'min_peak_separation': 0.02,    # 最小ピーク間隔（秒）
    'time_delta_range': (0.1, 2.0)  # 時間差範囲（秒）
}
```

### 静寂レベルに基づく調整

```python
def adjust_for_silence_example():
    """静寂レベルに基づくパラメータ調整例"""
    
    # 静寂が多い音声（silence_ratio > 0.5）の場合
    if characteristics['silence_ratio'] > 0.5:
        adjusted_params = {
            'min_amplitude': -70,        # より低い振幅まで検出
            'max_peaks_per_second': 10   # ピーク数を減らして精度向上
        }
        print("静寂が多い音声: 感度を上げて検出")
    
    # 通常の音声の場合
    else:
        adjusted_params = {
            'min_amplitude': -60,        # 標準的な閾値
            'max_peaks_per_second': 15   # 標準的なピーク数
        }
        print("通常の音声: 標準パラメータを使用")
```

### 複雑さに基づく調整

```python
def adjust_for_complexity_example():
    """音声複雑さに基づくパラメータ調整例"""
    
    spectral_entropy = characteristics['spectral_entropy']
    
    if spectral_entropy > 7:
        # 複雑な音声（多楽器、ノイズ多）
        adjusted_params = {
            'min_amplitude': -50,           # 高い閾値でノイズ除去
            'peak_neighborhood_size': 15,   # 大きな近傍でピーク検出
            'target_zone_size': 3           # 小さなターゲットゾーン
        }
        print("複雑な音声: ノイズ耐性を向上")
        
    elif spectral_entropy < 4:
        # 単純な音声（単一楽器、音声など）
        adjusted_params = {
            'target_zone_size': 8,          # 大きなターゲットゾーン
            'max_peaks_per_second': 20      # 多くのピークを検出
        }
        print("単純な音声: 詳細な特徴を抽出")
        
    else:
        # 中程度の複雑さ
        adjusted_params = DEFAULT_PARAMETERS.copy()
        print("中程度の複雑さ: 標準パラメータを使用")
```

### テンポに基づく調整

```python
def adjust_for_tempo_example():
    """テンポに基づくパラメータ調整例"""
    
    tempo = characteristics['tempo']
    
    if tempo > 140:
        # 高速テンポ（ダンス、エレクトロニック）
        adjusted_params = {
            'max_peaks_per_second': 20,     # 多くのピークを検出
            'min_peak_separation': 0.01     # 短い間隔でピーク検出
        }
        print("高速テンポ: 高密度ピーク検出")
        
    elif tempo < 80:
        # 低速テンポ（バラード、クラシック）
        adjusted_params = {
            'max_peaks_per_second': 12,     # 少ないピーク数
            'min_peak_separation': 0.03     # 長い間隔でピーク検出
        }
        print("低速テンポ: 低密度ピーク検出")
        
    else:
        # 中程度のテンポ
        adjusted_params = {
            'max_peaks_per_second': 15,     # 標準的なピーク数
            'min_peak_separation': 0.02     # 標準的な間隔
        }
        print("中程度テンポ: 標準パラメータを使用")
```

### スペクトル特性に基づく調整

```python
def adjust_for_spectral_characteristics_example():
    """スペクトル特性に基づくパラメータ調整例"""
    
    spectral_centroid = characteristics['spectral_centroid_mean']
    
    if spectral_centroid > 3000:
        # 高周波成分が多い音声（シンバル、高音楽器）
        adjusted_params = {
            'peak_neighborhood_size': 8,    # 小さな近傍サイズ
            'max_peaks_per_second': 18      # 多くのピークを検出
        }
        print("高周波音声: 高周波特徴を重視")
        
    elif spectral_centroid < 1000:
        # 低周波成分が多い音声（ベース、人の声）
        adjusted_params = {
            'peak_neighborhood_size': 12,   # 大きな近傍サイズ
            'target_zone_size': 6           # 大きなターゲットゾーン
        }
        print("低周波音声: 低周波特徴を重視")
        
    else:
        # バランスの取れたスペクトル
        adjusted_params = DEFAULT_PARAMETERS.copy()
        print("バランス音声: 標準パラメータを使用")
```

## 📊 PerformanceMonitor クラス

### パフォーマンス監視の基本

```python
from mimizam.adaptive_parameters import PerformanceMonitor

# パフォーマンス監視器の初期化
monitor = PerformanceMonitor()

# 処理時間の記録
import time

start_time = time.time()
fingerprints = fingerprinter.fingerprint_audio(audio)
processing_time = time.time() - start_time

monitor.record_processing_time("fingerprint_generation", processing_time)
monitor.record_fingerprint_count(len(fingerprints))

# ピーク検出数の記録
peaks = fingerprinter.spectrogram_analyzer.find_peaks(magnitude)
monitor.record_peak_count(len(peaks))

# パフォーマンスサマリーの表示
print(monitor.get_performance_summary())
```

### 詳細なパフォーマンス分析

```python
def detailed_performance_analysis():
    """詳細なパフォーマンス分析例"""
    
    monitor = PerformanceMonitor()
    tuner = AdaptiveParameterTuner()
    
    # 複数の音声ファイルでテスト
    test_files = [
        "test1.wav", "test2.wav", "test3.wav", 
        "test4.wav", "test5.wav"
    ]
    
    for file_path in test_files:
        audio, sr = librosa.load(file_path, sr=22050)
        
        # 音声特性分析
        characteristics = tuner.analyze_audio_characteristics(audio, sr)
        adjusted_params = tuner.adjust_parameters(characteristics)
        
        # 指紋生成（時間測定）
        fingerprinter = AudioFingerprinter(**adjusted_params)
        
        start_time = time.time()
        fingerprints = fingerprinter.fingerprint_audio(audio)
        processing_time = time.time() - start_time
        
        # メトリクス記録
        monitor.record_processing_time("total_processing", processing_time)
        monitor.record_fingerprint_count(len(fingerprints))
        
        # 個別処理時間の記録
        monitor.record_processing_time("per_second", processing_time / (len(audio) / sr))
        
        print(f"ファイル: {file_path}")
        print(f"  処理時間: {processing_time:.3f}秒")
        print(f"  指紋数: {len(fingerprints)}")
        print(f"  指紋密度: {len(fingerprints) / (len(audio) / sr):.1f} 指紋/秒")
    
    # 総合パフォーマンスサマリー
    print("\n=== 総合パフォーマンス ===")
    print(monitor.get_performance_summary())
```

## 🎛️ 高度な適応調整

### カスタム調整戦略

```python
class CustomParameterTuner(AdaptiveParameterTuner):
    """カスタム適応パラメータチューナー"""
    
    def __init__(self):
        super().__init__()
        self.genre_specific_params = {
            'classical': {
                'min_amplitude': -65,
                'peak_neighborhood_size': 12,
                'target_zone_size': 6
            },
            'electronic': {
                'min_amplitude': -55,
                'peak_neighborhood_size': 8,
                'max_peaks_per_second': 20
            },
            'speech': {
                'min_amplitude': -70,
                'peak_neighborhood_size': 15,
                'target_zone_size': 4
            }
        }
    
    def detect_genre(self, characteristics: Dict[str, float]) -> str:
        """音声特性からジャンルを推定"""
        
        # 簡単なルールベース分類
        if characteristics['spectral_centroid_mean'] < 1500 and characteristics['tempo'] < 100:
            return 'classical'
        elif characteristics['spectral_entropy'] > 6 and characteristics['tempo'] > 120:
            return 'electronic'
        elif characteristics['zero_crossing_rate'] > 0.1:
            return 'speech'
        else:
            return 'general'
    
    def adjust_parameters(self, characteristics: Dict[str, float]) -> Dict[str, Any]:
        """ジャンル特化型パラメータ調整"""
        
        # 基本調整
        params = super().adjust_parameters(characteristics)
        
        # ジャンル特化調整
        genre = self.detect_genre(characteristics)
        if genre in self.genre_specific_params:
            params.update(self.genre_specific_params[genre])
            print(f"ジャンル特化調整適用: {genre}")
        
        return params

# カスタムチューナーの使用
custom_tuner = CustomParameterTuner()
characteristics = custom_tuner.analyze_audio_characteristics(audio, sr)
custom_params = custom_tuner.adjust_parameters(characteristics)
```

### 機械学習ベースの調整

```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class MLParameterTuner(AdaptiveParameterTuner):
    """機械学習ベース適応パラメータチューナー"""
    
    def __init__(self):
        super().__init__()
        self.models = {}
        self.is_trained = False
    
    def train_models(self, training_data):
        """機械学習モデルの訓練"""
        
        # 特徴量とターゲットの準備
        features = []
        targets = {
            'min_amplitude': [],
            'peak_neighborhood_size': [],
            'max_peaks_per_second': []
        }
        
        for data in training_data:
            characteristics = data['characteristics']
            optimal_params = data['optimal_params']
            
            # 特徴量ベクトル
            feature_vector = [
                characteristics['duration'],
                characteristics['rms'],
                characteristics['spectral_entropy'],
                characteristics['zero_crossing_rate'],
                characteristics['tempo'],
                characteristics['spectral_centroid_mean']
            ]
            features.append(feature_vector)
            
            # ターゲット値
            for param_name in targets.keys():
                targets[param_name].append(optimal_params[param_name])
        
        features = np.array(features)
        
        # 各パラメータに対してモデルを訓練
        for param_name, target_values in targets.items():
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(features, target_values)
            self.models[param_name] = model
        
        self.is_trained = True
        print("機械学習モデルの訓練完了")
    
    def predict_parameters(self, characteristics: Dict[str, float]) -> Dict[str, Any]:
        """機械学習による最適パラメータ予測"""
        
        if not self.is_trained:
            print("警告: モデルが訓練されていません。デフォルト調整を使用します。")
            return super().adjust_parameters(characteristics)
        
        # 特徴量ベクトルの作成
        feature_vector = np.array([[
            characteristics['duration'],
            characteristics['rms'],
            characteristics['spectral_entropy'],
            characteristics['zero_crossing_rate'],
            characteristics['tempo'],
            characteristics['spectral_centroid_mean']
        ]])
        
        # 各パラメータの予測
        predicted_params = self._get_default_parameters()
        
        for param_name, model in self.models.items():
            predicted_value = model.predict(feature_vector)[0]
            predicted_params[param_name] = predicted_value
        
        return predicted_params

# ML チューナーの使用例（訓練データが必要）
# ml_tuner = MLParameterTuner()
# ml_tuner.train_models(training_data)
# ml_params = ml_tuner.predict_parameters(characteristics)
```

## 📈 パラメータ調整の効果測定

### A/Bテスト実装

```python
def parameter_ab_test():
    """パラメータ調整のA/Bテスト"""
    
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    
    results = {
        'default': {'accuracy': [], 'processing_time': []},
        'adaptive': {'accuracy': [], 'processing_time': []}
    }
    
    for audio_file in test_audio_files:
        audio, sr = librosa.load(audio_file, sr=22050)
        
        # デフォルトパラメータでのテスト
        default_fingerprinter = AudioFingerprinter(enable_adaptive_params=False)
        
        start_time = time.time()
        default_fingerprints = default_fingerprinter.fingerprint_audio(audio)
        default_time = time.time() - start_time
        
        # 適応パラメータでのテスト
        adaptive_fingerprinter = AudioFingerprinter(enable_adaptive_params=True)
        
        start_time = time.time()
        adaptive_fingerprints = adaptive_fingerprinter.fingerprint_audio(audio)
        adaptive_time = time.time() - start_time
        
        # 結果記録
        results['default']['processing_time'].append(default_time)
        results['adaptive']['processing_time'].append(adaptive_time)
        
        print(f"ファイル: {audio_file}")
        print(f"  デフォルト: {len(default_fingerprints)}指紋, {default_time:.3f}秒")
        print(f"  適応調整: {len(adaptive_fingerprints)}指紋, {adaptive_time:.3f}秒")
    
    # 統計分析
    default_avg_time = np.mean(results['default']['processing_time'])
    adaptive_avg_time = np.mean(results['adaptive']['processing_time'])
    
    print(f"\n=== A/Bテスト結果 ===")
    print(f"デフォルト平均処理時間: {default_avg_time:.3f}秒")
    print(f"適応調整平均処理時間: {adaptive_avg_time:.3f}秒")
    print(f"処理時間改善率: {(default_avg_time - adaptive_avg_time) / default_avg_time * 100:.1f}%")
```

## 🔗 関連ドキュメント

- [音声指紋生成アルゴリズム](./13_fingerprint_generation.md) - 指紋生成詳細
- [パフォーマンス最適化](./12_performance_optimization.md) - 性能向上技術
- [パフォーマンス分析](./20_performance_analysis.md) - 詳細分析手法
- [基本的な使用方法](./03_basic_usage.md) - 基本操作
- [低レベルAPI](./08_lowlevel_api.md) - 詳細制御

## 💡 適応調整のベストプラクティス

### 1. 音声特性の理解
- 対象音声の種類を把握
- 品質レベルの確認
- ノイズレベルの評価

### 2. パラメータ調整の検証
- A/Bテストによる効果測定
- 複数の音声での検証
- 処理時間と精度のバランス

### 3. 継続的な改善
- パフォーマンス監視の実装
- フィードバックループの構築
- 新しい音声タイプへの対応

適応パラメータ調整により、mimizamシステムは様々な音声に対して最適な性能を発揮できます。
