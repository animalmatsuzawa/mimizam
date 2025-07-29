# 17. 高度な使用例

mimizamの高度な機能を活用した実践的な使用例を紹介します。

## 🎛️ 適応的パラメータ調整

### AdaptiveParameterTunerを使用した音声特性に応じた最適化

```python
from mimizam import AudioFingerprinter, AdaptiveParameterTuner
import numpy as np
import librosa

# 適応的パラメータ調整を有効にしたFingerprinter
fingerprinter = AudioFingerprinter(
    n_fft=2048,
    hop_length=512,
    sr=22050,
    enable_adaptive_params=True  # 適応的パラメータ調整を有効化
)

# 音声ファイルを読み込み
audio, sr = librosa.load("test_audio.wav", sr=22050)

# フィンガープリント生成（自動的にパラメータが調整される）
fingerprints = fingerprinter.fingerprint_audio(audio, debug=True)

print(f"生成されたフィンガープリント数: {len(fingerprints)}")

### 手動でのパラメータ調整

```python
from mimizam import AdaptiveParameterTuner

# パラメータチューナーを作成
tuner = AdaptiveParameterTuner()

# 音声特性を分析
characteristics = tuner.analyze_audio_characteristics(audio, sr=22050)

# パラメータを調整
adjusted_params = tuner.adjust_parameters(characteristics)

# 調整結果を表示
summary = tuner.get_parameter_summary(characteristics, adjusted_params)
print("パラメータ調整結果:")
print(summary)

# 調整されたパラメータでFingerprinterを作成
fingerprinter = AudioFingerprinter(
    n_fft=2048,
    hop_length=512,
    sr=22050,
    min_amplitude=adjusted_params['min_amplitude'],
    peak_neighborhood_size=adjusted_params['peak_neighborhood_size'],
    enable_adaptive_params=False  # 手動設定を使用
)
    """カスタムパラメータ最適化器"""
    
    def __init__(self):
        self.parameter_sets = {
            'speech_optimized': {
                'n_fft': 1024,          # 音声に適した小さなFFTサイズ
                'hop_length': 256,      # 高い時間解像度
                'min_amplitude': -50,   # 音声レベルに合わせた閾値
                'peak_neighborhood_size': 10
            },
            'music_optimized': {
                'n_fft': 2048,          # 音楽に適した標準FFTサイズ
                'hop_length': 512,      # バランスの取れた解像度
                'min_amplitude': -60,   # 音楽の動的レンジに対応
                'peak_neighborhood_size': 20
            },
            'high_quality': {
                'n_fft': 4096,          # 高品質分析用
                'hop_length': 256,      # 高い時間解像度
                'min_amplitude': -70,   # 低レベル音声も検出
                'peak_neighborhood_size': 30
            },
            'fast_processing': {
                'n_fft': 1024,          # 高速処理用
                'hop_length': 1024,     # 大きなホップ長
                'min_amplitude': -40,   # 高い閾値
                'peak_neighborhood_size': 5
            }
        }
    
    def analyze_audio_characteristics(self, audio: np.ndarray) -> Dict[str, float]:
        """音声特性分析"""
        
        # 基本統計
        rms = np.sqrt(np.mean(audio**2))
        peak_amplitude = np.max(np.abs(audio))
        dynamic_range = 20 * np.log10(peak_amplitude / (rms + 1e-10))
        
        # スペクトル特性
        S = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(S)
        
        # スペクトル重心
        spectral_centroids = librosa.feature.spectral_centroid(S=magnitude)[0]
        avg_spectral_centroid = np.mean(spectral_centroids)
        
        # スペクトル帯域幅
        spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude)[0]
        avg_spectral_bandwidth = np.mean(spectral_bandwidth)
        
        # ゼロ交差率
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        avg_zcr = np.mean(zcr)
        
        return {
            'rms': rms,
            'peak_amplitude': peak_amplitude,
            'dynamic_range': dynamic_range,
            'spectral_centroid': avg_spectral_centroid,
            'spectral_bandwidth': avg_spectral_bandwidth,
            'zero_crossing_rate': avg_zcr
        }
    
    def recommend_parameters(self, audio: np.ndarray) -> Dict[str, Any]:
        """音声特性に基づくパラメータ推奨"""
        
        characteristics = self.analyze_audio_characteristics(audio)
        
        # 推奨ロジック
        if characteristics['zero_crossing_rate'] > 0.1:
            # 音声らしい特徴
            recommended_set = 'speech_optimized'
        elif characteristics['spectral_centroid'] > 3000:
            # 高周波成分が多い（楽器音楽など）
            recommended_set = 'music_optimized'
        elif characteristics['dynamic_range'] > 20:
            # 動的レンジが広い
            recommended_set = 'high_quality'
        else:
            # 一般的な音声
            recommended_set = 'music_optimized'
        
        recommended_params = self.parameter_sets[recommended_set].copy()
        
        # 動的調整
        if characteristics['rms'] < 0.01:  # 低レベル音声
            recommended_params['min_amplitude'] -= 10
        
        if characteristics['peak_amplitude'] > 0.9:  # 高レベル音声
            recommended_params['min_amplitude'] += 5
        
        return {
            'recommended_set': recommended_set,
            'parameters': recommended_params,
            'characteristics': characteristics,
            'reasoning': self._generate_reasoning(characteristics, recommended_set)
        }
    
    def _generate_reasoning(self, characteristics: Dict[str, float], recommended_set: str) -> str:
        """推奨理由の生成"""
        
        reasons = []
        
        if characteristics['zero_crossing_rate'] > 0.1:
            reasons.append("高いゼロ交差率により音声と判定")
        
        if characteristics['spectral_centroid'] > 3000:
            reasons.append("高い周波数重心により楽器音楽と判定")
        
        if characteristics['dynamic_range'] > 20:
            reasons.append("広い動的レンジにより高品質設定を推奨")
        
        if characteristics['rms'] < 0.01:
            reasons.append("低RMSレベルにより感度を上げる設定を適用")
        
        return f"{recommended_set}を推奨: " + ", ".join(reasons)

# 使用例
optimizer = CustomParameterOptimizer()

# テスト音声読み込み
audio, sr = librosa.load("test_audio.wav", sr=22050)

# パラメータ推奨
recommendation = optimizer.recommend_parameters(audio)

print(f"推奨設定: {recommendation['recommended_set']}")
print(f"理由: {recommendation['reasoning']}")
print(f"パラメータ: {recommendation['parameters']}")

# 推奨パラメータでAudioFingerprinter作成
fingerprinter = AudioFingerprinter(**recommendation['parameters'])
fingerprints = fingerprinter.fingerprint_audio(audio)

print(f"生成された指紋数: {len(fingerprints)}")
```

## 🔄 複数バックエンドの統合活用

### ハイブリッドデータベース戦略

```python
from mimizam import create_mimizam_sqlite, create_mimizam_mysql, create_mimizam_elasticsearch
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Any

class HybridMimizamSystem:
    """ハイブリッドmimizamシステム"""
    
    def __init__(self):
        self.backends = {}
        self.primary_backend = None
        self.cache_backend = None
        self.archive_backend = None
        
    def setup_backends(self, config: Dict[str, Any]):
        """バックエンド設定"""
        
        # 高速キャッシュ用SQLite
        if 'cache' in config:
            self.cache_backend = create_mimizam_sqlite(config['cache']['path'])
            self.backends['cache'] = self.cache_backend
        
        # メインデータベース用MySQL
        if 'primary' in config:
            self.primary_backend = create_mimizam_mysql(**config['primary'])
            self.backends['primary'] = self.primary_backend
        
        # アーカイブ用Elasticsearch
        if 'archive' in config:
            self.archive_backend = create_mimizam_elasticsearch(**config['archive'])
            self.backends['archive'] = self.archive_backend
    
    def add_song_distributed(self, file_path: str, title: str, artist: str) -> Dict[str, str]:
        """分散楽曲追加"""
        
        results = {}
        
        # プライマリに追加
        if self.primary_backend:
            primary_id = self.primary_backend.add_song(file_path, title, artist)
            results['primary'] = primary_id
        
        # キャッシュに追加（非同期）
        if self.cache_backend:
            cache_id = self.cache_backend.add_song(file_path, title, artist)
            results['cache'] = cache_id
        
        # アーカイブに追加（バックグラウンド）
        if self.archive_backend:
            # 非同期でアーカイブに追加
            def archive_task():
                return self.archive_backend.add_song(file_path, title, artist)
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(archive_task)
                # 結果は待たずに続行
                results['archive_future'] = future
        
        return results
    
    def search_song_intelligent(self, query_path: str, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """インテリジェント検索"""
        
        search_results = []
        
        # 1. キャッシュから高速検索
        if self.cache_backend:
            start_time = time.time()
            cache_results = self.cache_backend.search_song(query_path, min_confidence)
            cache_time = time.time() - start_time
            
            if cache_results:
                for result in cache_results:
                    result['source'] = 'cache'
                    result['response_time'] = cache_time
                search_results.extend(cache_results)
        
        # 2. 十分な結果が得られない場合、プライマリを検索
        if len(search_results) < 3 and self.primary_backend:
            start_time = time.time()
            primary_results = self.primary_backend.search_song(query_path, min_confidence)
            primary_time = time.time() - start_time
            
            for result in primary_results:
                result['source'] = 'primary'
                result['response_time'] = primary_time
                
                # 重複除去
                if not any(r['song']['id'] == result['song']['id'] for r in search_results):
                    search_results.append(result)
        
        # 3. さらに結果が必要な場合、アーカイブを検索
        if len(search_results) < 5 and self.archive_backend:
            start_time = time.time()
            archive_results = self.archive_backend.search_song(query_path, min_confidence * 0.8)  # 閾値を下げる
            archive_time = time.time() - start_time
            
            for result in archive_results:
                result['source'] = 'archive'
                result['response_time'] = archive_time
                
                # 重複除去
                if not any(r['song']['id'] == result['song']['id'] for r in search_results):
                    search_results.append(result)
        
        # 信頼度でソート
        search_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return search_results

# 使用例
hybrid_system = HybridMimizamSystem()

# バックエンド設定
config = {
    'cache': {
        'path': 'cache.db'
    },
    'primary': {
        'host': 'localhost',
        'database': 'music_main',
        'username': 'user',
        'password': 'password'
    },
    'archive': {
        'host': 'localhost',
        'port': 9200,
        'index': 'music_archive'
    }
}

hybrid_system.setup_backends(config)

# 分散楽曲追加
add_results = hybrid_system.add_song_distributed(
    "new_song.wav", 
    "New Song", 
    "Artist Name"
)
print(f"追加結果: {add_results}")

# インテリジェント検索
search_results = hybrid_system.search_song_intelligent("query.wav")
print(f"検索結果: {len(search_results)}件")

for result in search_results:
    print(f"  {result['song']['title']} (信頼度: {result['confidence']:.2f}, "
          f"ソース: {result['source']}, 応答時間: {result['response_time']:.3f}秒)")
```

## 🚀 高性能バッチ処理

### 大規模データセット処理

```python
import os
import glob
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
import time
import logging
from pathlib import Path

class HighPerformanceBatchProcessor:
    """高性能バッチ処理器"""
    
    def __init__(self, mimizam, max_workers=None):
        self.mimizam = mimizam
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.setup_logging()
        
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_directory_parallel(self, directory_path: str, 
                                 file_patterns: List[str] = None,
                                 batch_size: int = 100) -> Dict[str, Any]:
        """ディレクトリ並列処理"""
        
        if file_patterns is None:
            file_patterns = ['*.wav', '*.mp3', '*.flac', '*.m4a']
        
        # ファイル一覧取得
        all_files = []
        for pattern in file_patterns:
            all_files.extend(glob.glob(os.path.join(directory_path, '**', pattern), recursive=True))
        
        self.logger.info(f"処理対象ファイル数: {len(all_files)}")
        
        # バッチに分割
        batches = [all_files[i:i+batch_size] for i in range(0, len(all_files), batch_size)]
        
        results = {
            'total_files': len(all_files),
            'processed_files': 0,
            'failed_files': 0,
            'processing_time': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        # 並列バッチ処理
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batch = {
                executor.submit(self._process_batch, batch, batch_idx): batch_idx 
                for batch_idx, batch in enumerate(batches)
            }
            
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    batch_result = future.result()
                    results['processed_files'] += batch_result['processed']
                    results['failed_files'] += batch_result['failed']
                    results['errors'].extend(batch_result['errors'])
                    
                    self.logger.info(f"バッチ {batch_idx + 1}/{len(batches)} 完了: "
                                   f"成功 {batch_result['processed']}, "
                                   f"失敗 {batch_result['failed']}")
                    
                except Exception as e:
                    self.logger.error(f"バッチ {batch_idx} 処理エラー: {e}")
                    results['errors'].append(f"Batch {batch_idx}: {str(e)}")
        
        results['processing_time'] = time.time() - start_time
        
        self.logger.info(f"全体処理完了: {results['processed_files']}/{results['total_files']} "
                        f"({results['processing_time']:.2f}秒)")
        
        return results

# 使用例
batch_processor = HighPerformanceBatchProcessor(mimizam, max_workers=4)

# 大規模ディレクトリ処理
results = batch_processor.process_directory_parallel(
    "/path/to/music/library",
    file_patterns=['*.wav', '*.mp3', '*.flac'],
    batch_size=50
)

print(f"処理結果: {results['processed_files']}/{results['total_files']} "
      f"({results['processing_time']:.2f}秒)")
```

## 🔗 関連ドキュメント

- [基本的な使用例](./16_basic_examples.md) - 基本操作
- [パフォーマンス最適化](./12_performance_optimization.md) - 性能向上
- [バックエンド比較](./11_backend_comparison.md) - データベース選択
- [適応的パラメータ](./15_adaptive_parameters.md) - 自動調整
- [動画処理](./18_video_processing.md) - 動画音声処理

## 💡 高度な使用例のベストプラクティス

### 1. パラメータ最適化
- 音声特性の事前分析
- 用途に応じた設定選択
- 継続的な性能監視

### 2. システム統合
- 適切なアーキテクチャ設計
- 障害対応の実装
- スケーラビリティの考慮

### 3. パフォーマンス管理
- リソース使用量の監視
- ボトルネックの特定
- 最適化の継続的実施

mimizamの高度な機能を活用して、実用的で高性能な音声識別システムを構築してください。
