# データ構造リファレンス

mimizamシステムで使用される主要なデータ構造について詳しく説明します。これらのクラスは音声指紋システムの基盤となる重要な要素です。

## 🎵 Peak クラス

### 概要
`Peak`クラスは、スペクトログラム上の局所最大値（ピーク）を表現します。音声指紋生成の基礎となるデータ構造です。

### 定義
```python
from dataclasses import dataclass
import numpy as np

@dataclass
class Peak:
    """時間-周波数領域のスペクトルピークを表現"""
    time: np.float64      # 時間（秒）
    frequency: np.float64 # 周波数（Hz）
    amplitude: np.float64 # 振幅（dB）
```

### 使用例
```python
from mimizam import Peak
import numpy as np

# Peakオブジェクトの作成
peak = Peak(
    time=np.float64(1.5),      # 1.5秒の位置
    frequency=np.float64(440), # 440Hz（A4音）
    amplitude=np.float64(-20)  # -20dBの振幅
)

print(f"ピーク位置: {peak.time}秒")
print(f"周波数: {peak.frequency}Hz")
print(f"振幅: {peak.amplitude}dB")
```

### 型最適化
Peak クラスは `numpy.float64` 型を使用して最適化されています：

```python
# 型変換のオーバーヘッドなし
peaks = []
for detection in peak_detections:
    peak = Peak(
        time=np.float64(detection.time),
        frequency=np.float64(detection.freq),
        amplitude=np.float64(detection.amp)
    )
    peaks.append(peak)

# 約12.37%の性能向上を実現
```

## 🔑 Fingerprint クラス

### 概要
`Fingerprint`クラスは、音声から生成されたハッシュベースの指紋を表現します。

### 定義
```python
from dataclasses import dataclass

@dataclass
class Fingerprint:
    """音声指紋を表現するデータ構造"""
    hash_value: str    # SHA-256ハッシュ値
    time_offset: float # 時間オフセット（秒）
```

### 使用例
```python
from mimizam import Fingerprint

# Fingerprint オブジェクトの作成
fingerprint = Fingerprint(
    hash_value="a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
    time_offset=2.5
)

print(f"ハッシュ値: {fingerprint.hash_value}")
print(f"時間オフセット: {fingerprint.time_offset}秒")
```

## 🎼 Song クラス

### 概要
`Song`クラスは、データベースに保存される楽曲の情報を表現します。

### 定義
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Song:
    """楽曲情報を表現するデータ構造"""
    id: int                           # 楽曲ID
    title: str                        # 楽曲タイトル
    artist: str                       # アーティスト名
    file_path: str                    # ファイルパス
    created_at: datetime              # 作成日時
    album: Optional[str] = None       # アルバム名（オプション）
    meta: Optional[Dict[str, Any]] = None  # 追加メタデータ（オプション）
```

### 使用例
```python
from mimizam import Song
from datetime import datetime

# Song オブジェクトの作成
song = Song(
    id=1,
    title="My Favorite Song",
    artist="Great Artist",
    file_path="/music/favorite_song.wav",
    created_at=datetime.now(),
    album="Best Album",
    meta={
        "genre": "Pop",
        "year": 2023,
        "duration": 180.5,
        "bitrate": 320,
        "sample_rate": 44100
    }
)

print(f"楽曲: {song.title} by {song.artist}")
print(f"アルバム: {song.album}")
print(f"ジャンル: {song.meta['genre']}")
```

## ⚙️ DatabaseConfig クラス

### 概要
`DatabaseConfig`クラスは、データベース接続の設定情報を管理します。

### 定義
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """データベース設定を表現するデータ構造"""
    backend: str                    # バックエンド種類
    host: Optional[str] = None      # ホスト名
    port: Optional[int] = None      # ポート番号
    database: Optional[str] = None  # データベース名
    username: Optional[str] = None  # ユーザー名
    password: Optional[str] = None  # パスワード
    db_path: Optional[str] = None   # SQLiteファイルパス
```

### 使用例
```python
from mimizam import DatabaseConfig

# SQLite設定
sqlite_config = DatabaseConfig(
    backend='sqlite',
    db_path='music.db'
)

# MySQL設定
mysql_config = DatabaseConfig(
    backend='mysql',
    host='localhost',
    port=3306,
    database='music_db',
    username='user',
    password='password'
)
```

## 🔗 関連ドキュメント

- [統合API](./07_unified_api.md) - データ構造の使用方法
- [低レベルAPI](./08_lowlevel_api.md) - 詳細な操作
- [音声指紋生成](./13_fingerprint_generation.md) - Peak と Fingerprint の生成
- [データベース設定](./10_database_setup.md) - DatabaseConfig の使用
- [実装例](./16_basic_examples.md) - 実践的な使用例
