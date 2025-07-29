# プロジェクト構造

mimizamプロジェクトの詳細な構造と各コンポーネントの役割について説明します。効率的な開発とメンテナンスのための構成を理解できます。

## 📁 ディレクトリ構造

```
mimizam/
├── src/                          # メインソースコード
│   ├── __init__.py              # パッケージ初期化
│   ├── mimizam.py               # 統合APIクラス
│   ├── audio_fingerprinter.py   # 音声指紋生成
│   ├── fingerprint_database.py  # データベース管理
│   ├── database_base.py         # データベース基底クラス
│   ├── database_backends.py     # バックエンドファクトリ
│   ├── adaptive_parameters.py   # 適応パラメータ調整
│   ├── exceptions.py            # カスタム例外
│   └── backends/                # データベースバックエンド
│       ├── __init__.py
│       ├── sqlite_backend.py    # SQLiteバックエンド
│       ├── mysql_backend.py     # MySQLバックエンド
│       ├── postgresql_backend.py # PostgreSQLバックエンド
│       └── elasticsearch_backend.py # Elasticsearchバックエンド
├── examples/                     # 使用例とデモ
│   ├── mimizam_demo.py          # 基本デモ
│   ├── video_fingerprinter.py   # 動画音声処理
│   ├── video_search.py          # 動画検索
│   └── compare_audio_fingerprinters.py # 性能比較
├── tests/                        # テストスイート
│   ├── __init__.py
│   ├── test_utils.py            # テストユーティリティ
│   ├── test_audio_fingerprinter.py # 音声指紋テスト
│   ├── test_fingerprint_database.py # データベーステスト
│   ├── test_database_backends.py # バックエンドテスト
│   ├── test_adaptive_parameters.py # 適応パラメータテスト
│   ├── test_performance.py      # パフォーマンステスト
│   └── test_*_containers.py     # コンテナテスト
├── scripts/                      # ユーティリティスクリプト
│   └── migrate_database.py      # データベース移行
├── docs/                         # ドキュメント
│   ├── wiki/                    # 日本語Wiki
│   ├── DATABASE_SETUP.md        # データベース設定
│   ├── fingerprint_*.md         # 技術詳細
│   └── *.md                     # その他ドキュメント
├── .github/                      # GitHub設定
│   └── workflows/               # CI/CDワークフロー
│       └── ci.yml               # 継続的インテグレーション
├── pyproject.toml               # プロジェクト設定
├── README.md                    # プロジェクト概要（英語）
├── README_JP.md                 # プロジェクト概要（日本語）
└── .gitignore                   # Git除外設定
```

## 🏗️ アーキテクチャ層

### 1. アプリケーション層 (`src/mimizam.py`)

```python
# 統合APIの提供
class Mimizam:
    """
    高レベル統合API
    - 簡単な楽曲追加・検索
    - 自動リソース管理
    - エラーハンドリング
    """
    
    def __init__(self, database_config: DatabaseConfig):
        self.fingerprinter = AudioFingerprinter()
        self.database = FingerprintDatabase(database_config)
        self.matcher = FingerprintMatcher()
    
    def add_song(self, file_path: str, title: str, artist: str) -> str:
        """楽曲をデータベースに追加"""
        pass
    
    def search_song(self, query_path: str, min_confidence: float = 0.3) -> List[Dict]:
        """楽曲を検索"""
        pass

# ファクトリ関数
def create_mimizam_sqlite(db_path: str) -> Mimizam:
    """SQLite版Mimizamを作成"""
    pass
```

### 2. 音声処理層 (`src/audio_fingerprinter.py`)

```python
class AudioFingerprinter:
    """
    音声指紋生成の中核
    - スペクトログラム解析
    - ピーク検出
    - ハッシュ生成
    """
    
    def __init__(self, **params):
        self.spectrogram_analyzer = SpectrogramAnalyzer(**params)
        self.hash_generator = HashGenerator(**params)
        self.adaptive_tuner = AdaptiveParameterTuner()
    
    def fingerprint_audio(self, audio: np.ndarray) -> List[Fingerprint]:
        """音声から指紋を生成"""
        pass

class SpectrogramAnalyzer:
    """スペクトログラム解析"""
    
    def compute_spectrogram(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """STFT計算"""
        pass
    
    def find_peaks(self, magnitude: np.ndarray) -> List[Peak]:
        """ピーク検出"""
        pass

class HashGenerator:
    """ハッシュ生成"""
    
    def generate_hashes(self, peaks: List[Peak]) -> List[Fingerprint]:
        """ピークからハッシュを生成"""
        pass
```

### 3. データベース層 (`src/fingerprint_database.py`)

```python
class FingerprintDatabase:
    """
    データベース操作の統合管理
    - バックエンド抽象化
    - トランザクション管理
    - エラーハンドリング
    """
    
    def __init__(self, config: DatabaseConfig):
        self.backend = create_backend(config)
        self.matcher = FingerprintMatcher()
    
    def add_song_with_fingerprints(self, song: Song, fingerprints: List[Fingerprint]) -> bool:
        """楽曲と指紋を追加"""
        pass
    
    def search_fingerprints(self, query_fingerprints: List[Fingerprint]) -> List[Dict]:
        """指紋検索"""
        pass
```

### 4. バックエンド層 (`src/backends/`)

```python
# 抽象基底クラス
class DatabaseBackend(ABC):
    """データベースバックエンドの基底クラス"""
    
    @abstractmethod
    def connect(self) -> bool:
        """データベース接続"""
        pass
    
    @abstractmethod
    def add_song(self, song: Song) -> bool:
        """楽曲追加"""
        pass
    
    @abstractmethod
    def search_fingerprints(self, fingerprints: List[Fingerprint]) -> Dict:
        """指紋検索"""
        pass

# 具体実装
class SQLiteBackend(DatabaseBackend):
    """SQLite実装"""
    pass

class MySQLBackend(DatabaseBackend):
    """MySQL実装"""
    pass
```

## 🧩 コンポーネント詳細

### メインモジュール (`src/`)

#### `__init__.py` - パッケージエントリポイント
```python
"""
mimizam音声指紋ライブラリ

主要なクラスと関数をエクスポート:
- Mimizam: 統合API
- AudioFingerprinter: 音声指紋生成
- FingerprintDatabase: データベース管理
- create_mimizam_*: ファクトリ関数
"""

from .mimizam import Mimizam
from .audio_fingerprinter import AudioFingerprinter
from .fingerprint_database import FingerprintDatabase
from .database_base import DatabaseConfig, Song, Fingerprint, Peak
from .mimizam import (
    create_mimizam_sqlite,
    create_mimizam_mysql,
    create_mimizam_postgresql,
    create_mimizam_elasticsearch
)

__version__ = "1.0.0"
__all__ = [
    'Mimizam',
    'AudioFingerprinter', 
    'FingerprintDatabase',
    'DatabaseConfig',
    'Song',
    'Fingerprint',
    'Peak',
    'create_mimizam_sqlite',
    'create_mimizam_mysql',
    'create_mimizam_postgresql',
    'create_mimizam_elasticsearch'
]
```

#### `database_base.py` - 基本データ構造
```python
"""
データベース関連の基本データ構造とインターフェース

主要クラス:
- DatabaseConfig: データベース設定
- Song: 楽曲情報
- Fingerprint: 音声指紋
- Peak: スペクトルピーク
- DatabaseBackend: バックエンド抽象クラス
"""

@dataclass
class DatabaseConfig:
    """データベース設定"""
    backend: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None  # SQLite用
```

#### `exceptions.py` - カスタム例外
```python
"""
mimizam固有の例外クラス

例外階層:
- MimizamError (基底)
  ├── AudioProcessingError
  ├── FingerprintGenerationError
  ├── DatabaseError
  │   ├── ConnectionError
  │   ├── QueryError
  │   └── MigrationError
  └── MatchingError
"""

class MimizamError(Exception):
    """mimizam基底例外"""
    pass

class AudioProcessingError(MimizamError):
    """音声処理エラー"""
    pass

class DatabaseError(MimizamError):
    """データベースエラー"""
    pass
```

### バックエンドモジュール (`src/backends/`)

#### バックエンド設計パターン
```python
# ファクトリパターンによるバックエンド生成
def create_backend(config: DatabaseConfig) -> DatabaseBackend:
    """設定に基づいてバックエンドを作成"""
    
    backend_map = {
        'sqlite': SQLiteBackend,
        'mysql': MySQLBackend,
        'postgresql': PostgreSQLBackend,
        'elasticsearch': ElasticsearchBackend
    }
    
    backend_class = backend_map.get(config.backend.lower())
    if not backend_class:
        raise ValueError(f"未対応のバックエンド: {config.backend}")
    
    return backend_class(config)
```

#### 各バックエンドの特徴
```python
# SQLite: ファイルベース、設定不要
class SQLiteBackend(DatabaseBackend):
    """
    特徴:
    - 単一ファイルDB
    - 設定不要
    - 小〜中規模向け
    """
    
    def connect(self) -> bool:
        self.connection = sqlite3.connect(self.db_path)
        # WALモード、キャッシュ最適化など

# MySQL: 高性能RDBMS
class MySQLBackend(DatabaseBackend):
    """
    特徴:
    - 高性能
    - レプリケーション対応
    - 中〜大規模向け
    """
    
    def connect(self) -> bool:
        self.connection = mysql.connector.connect(**config)
        # バッファプール、並列処理最適化など

# PostgreSQL: 高機能RDBMS
class PostgreSQLBackend(DatabaseBackend):
    """
    特徴:
    - 高度なSQL機能
    - JSON/JSONB対応
    - 分析・研究向け
    """

# Elasticsearch: 分散検索エンジン
class ElasticsearchBackend(DatabaseBackend):
    """
    特徴:
    - 分散処理
    - 全文検索
    - 超大規模向け
    """
```

## 📝 テスト構造 (`tests/`)

### テスト分類

#### 1. 単体テスト
```python
# test_audio_fingerprinter.py
class TestAudioFingerprinter(unittest.TestCase):
    """音声指紋生成の単体テスト"""
    
    def test_fingerprint_generation(self):
        """指紋生成テスト"""
        pass
    
    def test_peak_detection(self):
        """ピーク検出テスト"""
        pass

# test_fingerprint_database.py  
class TestFingerprintDatabase(unittest.TestCase):
    """データベース操作の単体テスト"""
    
    def test_song_addition(self):
        """楽曲追加テスト"""
        pass
    
    def test_fingerprint_search(self):
        """指紋検索テスト"""
        pass
```

#### 2. 統合テスト
```python
# test_database_backends.py
class TestDatabaseBackends(unittest.TestCase):
    """バックエンド統合テスト"""
    
    def test_sqlite_integration(self):
        """SQLite統合テスト"""
        pass
    
    def test_mysql_integration(self):
        """MySQL統合テスト"""
        pass
```

#### 3. コンテナテスト
```python
# test_mysql_containers.py
class TestMySQLContainers(unittest.TestCase):
    """MySQLコンテナテスト"""
    
    @classmethod
    def setUpClass(cls):
        """テストコンテナ起動"""
        cls.mysql_container = MySqlContainer("mysql:8.0")
        cls.mysql_container.start()
    
    def test_container_connection(self):
        """コンテナ接続テスト"""
        pass
```

## 🛠️ 開発ツール

### スクリプト (`scripts/`)

#### `migrate_database.py` - データベース移行
```python
"""
データベース移行ツール

機能:
- スキーマ分析
- データ移行
- マルチバックエンド対応
- 検証機能
"""

class DatabaseMigrator:
    """データベース移行器"""
    
    def analyze_schema(self, config: DatabaseConfig):
        """スキーマ分析"""
        pass
    
    def migrate_data(self, source_config: DatabaseConfig, 
                    target_config: DatabaseConfig):
        """データ移行"""
        pass
```

### 設定ファイル

#### `pyproject.toml` - プロジェクト設定
```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "mimizam"
version = "1.0.0"
description = "音声指紋による楽曲識別システム"
authors = ["mimizam contributors"]

[tool.poetry.dependencies]
python = "^3.8"
numpy = "^1.21.0"
librosa = "^0.9.0"
numba = "^0.56.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
black = "^22.0.0"
flake8 = "^5.0.0"
```

## 📚 ドキュメント構造 (`docs/`)

### Wiki構造
```
docs/wiki/
├── README.md                    # Wiki目次
├── 01_overview.md              # 概要
├── 02_installation.md          # インストール
├── 03_basic_usage.md           # 基本使用法
├── 04_architecture.md          # アーキテクチャ
├── 05_core_technology.md       # 核心技術
├── 06_project_structure.md     # プロジェクト構造
├── 07_unified_api.md           # 統合API
├── 08_lowlevel_api.md          # 低レベルAPI
├── 09_data_structures.md       # データ構造
├── 10_database_setup.md        # データベース設定
├── 11_backend_comparison.md    # バックエンド比較
├── 12_performance_optimization.md # パフォーマンス最適化
├── 13_fingerprint_generation.md # 指紋生成
├── 14_scoring_details.md       # スコアリング詳細
├── 15_adaptive_parameters.md   # 適応パラメータ
├── 16_basic_examples.md        # 基本例
├── 17_advanced_examples.md     # 高度な例
├── 18_video_processing.md      # 動画処理
├── 19_migration_tools.md       # 移行ツール
├── 20_performance_analysis.md  # パフォーマンス分析
├── 21_debugging.md             # デバッグ
├── 22_testing.md               # テスト
├── 23_performance_testing.md   # パフォーマンステスト
├── 24_quality_assurance.md     # 品質保証
├── 25_algorithm_comparison.md  # アルゴリズム比較
├── 26_references.md            # 参考文献
└── 27_faq.md                   # FAQ
```

### 技術ドキュメント
```
docs/
├── DATABASE_SETUP.md           # データベース設定詳細
├── fingerprint_generation_details.md # 指紋生成詳細
├── fingerprint_scoring_details.md    # スコアリング詳細
└── fingerprint_implementation_comparison.md # 実装比較
```

## 🔄 CI/CD構造 (`.github/`)

### ワークフロー
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    
    - name: Run tests
      run: |
        poetry run pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 🔗 関連ドキュメント

- [アーキテクチャ](./04_architecture.md) - システム設計詳細
- [インストール](./02_installation.md) - セットアップ手順
- [基本的な使用方法](./03_basic_usage.md) - 使用開始
- [テスト](./22_testing.md) - テスト実行方法
- [品質保証](./24_quality_assurance.md) - 品質管理

## 💡 開発のベストプラクティス

### 1. コード構成
- 単一責任の原則に従った設計
- 適切な抽象化レベルの維持
- 依存関係の明確化

### 2. テスト戦略
- 単体テスト、統合テスト、E2Eテストの組み合わせ
- テストカバレッジの維持
- コンテナを使用した環境分離

### 3. ドキュメント管理
- コードと同期したドキュメント更新
- 使用例の充実
- 技術的詳細の適切な記録

mimizamプロジェクトの構造を理解することで、効率的な開発と保守が可能になります。
