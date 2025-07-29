# システムアーキテクチャ

mimizamは、音声指紋生成と識別のための包括的なシステムです。本ドキュメントでは、システム全体のアーキテクチャと各コンポーネントの役割について詳しく説明します。

## 🏗️ 全体アーキテクチャ

mimizamは4つの主要レイヤーで構成されています：

```
┌─────────────────────────────────────────────────────────────┐
│                    アプリケーション層                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   CLI ツール    │  │  デモアプリ     │  │  カスタムアプリ │ │
│  │ video_search.py │  │ mimizam_demo.py │  │   (ユーザー)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    統合API層                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Mimizam クラス                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │create_sqlite│  │create_mysql │  │create_postgresql│  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   コア処理層                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │AudioFingerprinter│  │FingerprintDatabase│ │FingerprintMatcher│ │
│  │                 │  │                 │  │                 │ │
│  │SpectrogramAnalyzer│ │                 │  │                 │ │
│  │HashGenerator    │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  データベース層                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │SQLiteBackend│  │MySQLBackend │  │PostgreSQLBE │  │ElasticBE│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 レイヤー別詳細

### 1. アプリケーション層

#### CLI ツール
```python
# video_search.py - 動画音声検索ツール
python examples/video_search.py --query video.mp4 --database music.db

# video_fingerprinter.py - バッチ処理ツール
python examples/video_fingerprinter.py --input-dir videos/ --output-db batch.db
```

#### デモアプリケーション
```python
# mimizam_demo.py - 基本機能デモ
python examples/mimizam_demo.py

# lowlevelapi_demo.py - 低レベルAPI デモ
python examples/lowlevelapi_demo.py
```

### 2. 統合API層

#### Mimizam クラス
統合APIの中核となるクラスで、全てのデータベースバックエンドに対して一貫したインターフェースを提供します。

```python
class Mimizam:
    """統合音声指紋システム"""
    
    def __init__(self, database: FingerprintDatabase, 
                 fingerprinter: AudioFingerprinter):
        self.database = database
        self.fingerprinter = fingerprinter
    
    def add_song(self, file_path: str, title: str, artist: str) -> int:
        """楽曲追加の統合処理"""
        # 1. 音声読み込み
        # 2. 指紋生成
        # 3. データベース保存
        pass
    
    def search_song(self, query_path: str, **kwargs) -> List[Dict]:
        """音声検索の統合処理"""
        # 1. クエリ音声処理
        # 2. 指紋マッチング
        # 3. 結果ランキング
        pass
```

#### ファクトリ関数
```python
def create_mimizam_sqlite(db_path: str, **kwargs) -> Mimizam:
    """SQLite バックエンドでMimizam インスタンスを作成"""
    config = create_sqlite_config(db_path)
    database = FingerprintDatabase(config)
    fingerprinter = AudioFingerprinter(**kwargs)
    return Mimizam(database, fingerprinter)
```

### 3. コア処理層

#### AudioFingerprinter
音声指紋生成の中核コンポーネント：

```python
class AudioFingerprinter:
    """音声指紋生成器"""
    
    def __init__(self, n_fft=2048, hop_length=512, **kwargs):
        self.spectrogram_analyzer = SpectrogramAnalyzer(n_fft, hop_length)
        self.hash_generator = HashGenerator(**kwargs)
    
    def fingerprint_audio(self, audio: np.ndarray) -> List[Fingerprint]:
        """音声から指紋を生成"""
        # 1. スペクトログラム生成
        spectrogram = self.spectrogram_analyzer.compute_spectrogram(audio)
        
        # 2. ピーク検出
        peaks = self.spectrogram_analyzer.detect_peaks(spectrogram)
        
        # 3. ハッシュ生成
        fingerprints = self.hash_generator.generate_fingerprints(peaks)
        
        return fingerprints
```

#### FingerprintDatabase
データベース操作の統合インターフェース：

```python
class FingerprintDatabase:
    """指紋データベース統合インターフェース"""
    
    def __init__(self, config: DatabaseConfig):
        self.backend = self._create_backend(config)
        self.matcher = FingerprintMatcher()
    
    def add_song(self, title: str, artist: str, file_path: str) -> int:
        """楽曲をデータベースに追加"""
        return self.backend.add_song(title, artist, file_path)
    
    def search_fingerprints(self, query_fingerprints: List[Fingerprint]) -> List[Dict]:
        """指紋検索とマッチング"""
        # 1. データベース検索
        raw_matches = self.backend.find_matches(query_fingerprints)
        
        # 2. スコアリング
        scored_results = self.matcher.score_matches(raw_matches)
        
        return scored_results
```

#### FingerprintMatcher
指紋マッチングとスコアリング：

```python
class FingerprintMatcher:
    """指紋マッチングエンジン"""
    
    def score_matches(self, raw_matches: Dict, scoring_method: str = 'hybrid') -> List[Dict]:
        """マッチ結果のスコアリング"""
        if scoring_method == 'histogram':
            return self._histogram_scoring(raw_matches)
        elif scoring_method == 'detailed':
            return self._detailed_scoring(raw_matches)
        else:  # hybrid
            return self._hybrid_scoring(raw_matches)
```

### 4. データベース層

#### バックエンド実装
各データベースシステムに特化した実装：

```python
class SQLiteBackend(DatabaseBackend):
    """SQLite バックエンド実装"""
    
    def create_tables(self):
        """テーブル作成"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                file_path TEXT NOT NULL,
                album TEXT,
                meta TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                hash_value TEXT NOT NULL,
                time_offset REAL NOT NULL,
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        """)
```

## 🔄 データフロー

### 楽曲追加フロー

```
音声ファイル
    │
    ▼
┌─────────────────┐
│ 音声読み込み     │ ← librosa
│ (load_audio)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│スペクトログラム  │ ← STFT
│生成             │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ピーク検出       │ ← 局所最大値検出
│                │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ハッシュ生成     │ ← アンカー・ターゲット方式
│                │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│データベース保存  │ ← SQLite/MySQL/PostgreSQL/Elasticsearch
│                │
└─────────────────┘
```

### 音声検索フロー

```
クエリ音声
    │
    ▼
┌─────────────────┐
│指紋生成         │ ← 楽曲追加と同じプロセス
│                │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│データベース検索  │ ← ハッシュマッチング
│                │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│マッチングと     │ ← 時間アライメント
│スコアリング     │   信頼度計算
└─────────────────┘
    │
    ▼
┌─────────────────┐
│結果ランキング   │ ← 信頼度順ソート
│                │
└─────────────────┘
    │
    ▼
検索結果
```

## 🧩 コンポーネント間の相互作用

### SpectrogramAnalyzer と HashGenerator

```python
class SpectrogramAnalyzer:
    """スペクトログラム解析"""
    
    def compute_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """STFT によるスペクトログラム生成"""
        return librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
    
    def detect_peaks(self, spectrogram: np.ndarray) -> List[Peak]:
        """局所最大値検出"""
        # 近傍での最大値検出
        # 閾値フィルタリング
        # Peak オブジェクト生成
        pass

class HashGenerator:
    """ハッシュ生成器"""
    
    def generate_fingerprints(self, peaks: List[Peak]) -> List[Fingerprint]:
        """アンカー・ターゲット方式でハッシュ生成"""
        fingerprints = []
        for anchor in peaks:
            targets = self._find_targets(anchor, peaks)
            for target in targets:
                hash_value = self._compute_hash(anchor, target)
                fingerprint = Fingerprint(hash_value, anchor.time)
                fingerprints.append(fingerprint)
        return fingerprints
```

### AdaptiveParameterTuner との連携

```python
class AdaptiveParameterTuner:
    """適応パラメータ調整"""
    
    def optimize_for_audio(self, audio: np.ndarray) -> dict:
        """音声特性に応じたパラメータ最適化"""
        # 音声特性分析
        characteristics = self._analyze_audio(audio)
        
        # パラメータ調整
        if characteristics['complexity'] > 0.8:
            return {'min_amplitude': -70, 'peak_neighborhood_size': 30}
        elif characteristics['noise_level'] > 0.5:
            return {'min_amplitude': -40, 'peak_neighborhood_size': 15}
        else:
            return {}  # デフォルト設定
```

## 🔧 設定管理アーキテクチャ

### 階層的設定システム

```python
# 1. デフォルト設定
DEFAULT_CONFIG = {
    'fingerprinter': {
        'n_fft': 2048,
        'hop_length': 512,
        'min_amplitude': -60
    },
    'matcher': {
        'time_tolerance': 0.1,
        'freq_tolerance': 50
    }
}

# 2. プロファイル設定
PROFILE_CONFIGS = {
    'high_precision': {
        'fingerprinter': {'n_fft': 4096, 'min_amplitude': -70},
        'matcher': {'time_tolerance': 0.05}
    },
    'high_speed': {
        'fingerprinter': {'n_fft': 1024, 'min_amplitude': -40},
        'matcher': {'time_tolerance': 0.2}
    }
}

# 3. ユーザー設定
USER_CONFIG = {
    'fingerprinter': {'debug': True},
    'matcher': {'scoring_method': 'hybrid'}
}

# 4. 設定マージ
final_config = merge_configs(DEFAULT_CONFIG, PROFILE_CONFIGS['balanced'], USER_CONFIG)
```

## 📊 パフォーマンス考慮事項

### メモリ管理

```python
class MemoryEfficientProcessor:
    """メモリ効率的な処理"""
    
    def process_large_audio(self, audio_path: str, chunk_size: int = 30):
        """大きな音声ファイルのチャンク処理"""
        for chunk in self._load_audio_chunks(audio_path, chunk_size):
            fingerprints = self.fingerprinter.fingerprint_audio(chunk)
            self.database.add_fingerprints_batch(fingerprints)
            # チャンクごとにメモリ解放
            del chunk, fingerprints
```

### 並列処理

```python
class ParallelProcessor:
    """並列処理対応"""
    
    def process_multiple_files(self, file_paths: List[str]):
        """複数ファイルの並列処理"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self._process_single_file, path)
                for path in file_paths
            ]
            
            for future in as_completed(futures):
                result = future.result()
                # 結果処理
```

## 🔒 セキュリティアーキテクチャ

### データ保護

```python
class SecureDatabase:
    """セキュアなデータベース操作"""
    
    def __init__(self, config: DatabaseConfig):
        # 接続時の暗号化
        if config.use_ssl:
            self.connection = self._create_ssl_connection(config)
        
        # パスワードハッシュ化
        self.password_hash = self._hash_password(config.password)
    
    def sanitize_input(self, user_input: str) -> str:
        """入力サニタイゼーション"""
        # SQLインジェクション対策
        return user_input.replace("'", "''").replace(";", "")
```

## 🔗 拡張性

### プラグインアーキテクチャ

```python
class PluginManager:
    """プラグイン管理"""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_class):
        """プラグイン登録"""
        self.plugins[name] = plugin_class
    
    def load_plugin(self, name: str, **kwargs):
        """プラグイン読み込み"""
        if name in self.plugins:
            return self.plugins[name](**kwargs)
        raise ValueError(f"Unknown plugin: {name}")

# カスタムバックエンドプラグイン
class CustomBackend(DatabaseBackend):
    """カスタムデータベースバックエンド"""
    pass

# プラグイン登録
plugin_manager = PluginManager()
plugin_manager.register_plugin('custom_db', CustomBackend)
```

## 🔗 関連ドキュメント

- [統合API](./07_unified_api.md) - 統合API層の詳細
- [低レベルAPI](./08_lowlevel_api.md) - コア処理層の詳細
- [データベース設定](./10_database_setup.md) - データベース層の詳細
- [音声指紋生成](./13_fingerprint_generation.md) - 指紋生成アルゴリズム
- [パフォーマンス最適化](./12_performance_optimization.md) - 性能向上テクニック

## 💡 設計原則

### 1. 関心の分離
- 各レイヤーは明確な責任を持つ
- コンポーネント間の依存関係を最小化
- インターフェースを通じた疎結合

### 2. 拡張性
- プラグインアーキテクチャによる機能拡張
- 設定システムによるカスタマイズ
- 新しいバックエンドの容易な追加

### 3. 性能
- 適応的パラメータ調整
- メモリ効率的な処理
- 並列処理対応

### 4. 保守性
- 明確なコード構造
- 包括的なテストスイート
- 詳細なドキュメント
