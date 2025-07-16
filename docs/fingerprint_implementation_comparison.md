# 音響指紋実装比較 - mimizam vs 既存実装

本ドキュメントでは、mimizamと代表的な既存実装を比較します。

---

## 1. フィンガープリント生成の比較

| 項目             | mimizam（本実装）                                | dejavu                                                 | audfprint                                              |
| ---------------- | ------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| スペクトログラム | librosa(STFT) + 最適化パラメータ                 | scipy/numpy                                            | numpy/scipy（独自STFT）                                |
| ピーク検出       | scipy.signal.find_peaks + 局所最大値・動的閾値   | ndimage.maximum_filter                                 | 2D最大値・閾値・パラメトリック                         |
| ハッシュ生成     | アンカー・ターゲット周波数・時間差量子化ハッシュ | アンカー・ターゲットの周波数・時間差を整数化しハッシュ | 周波数ペア・時間差を整数化しハッシュ（"landmark"方式） |
| パラメータ調整   | **最適化パラメータ**（音声特性ベース）           | 固定パラメータ中心                                     | 多数のパラメータをコマンドラインで調整可               |
| 処理速度         | **高速化**（最適化実装）                         | 標準速度                                               | 標準速度                                               |

**mimizamの特長**
- **Shazam-styleアルゴリズム**: constellation map方式をベースとした確実な実装
- **最適化実装**: librosaベースの高速スペクトログラム生成とscipy最適化ピーク検出
- **統一API**: 複数データベースバックエンド（SQLite/MySQL/PostgreSQL/Elasticsearch）の透過的利用

**共通点**
- いずれもShazam論文の「constellation map」方式をベース
- ピークペアからハッシュを作成しDBに格納

---

## 2. スコアリング（マッチ判定）の比較

| 項目             | mimizam（3種類スコアリング）                                          | dejavu                                                            | audfprint                                                            |
| ---------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| マッチ方法       | 3種類実装：①histogram②hybrid（2段階）③detailed（多面的精査）          | クエリ指紋のハッシュをDBで検索し、(query_time, db_time)ペアを収集 | クエリ指紋のハッシュをDBで検索し、(query_time, db_time)ペアを収集    |
| スコア計算       | **選択可能**：histogram/hybrid/detailed各方式で精度・速度バランス調整 | 時間差のヒストグラム、最頻値の一致数                              | 時間差のヒストグラム、最大binの一致数/割合（"offset histogram"）     |
| 速度・ピッチ変化 | 各スコアリング方式で対応（特にdetailedが高精度）                      | デフォルトでは考慮しない                                          | デフォルトでは考慮しない（ただしパラメータ調整である程度対応可）     |
| ノイズ耐性       | **高い**：detailed方式でグループ分布・冗長性・信頼性を多面考慮        | 最頻時間差のみに依存                                              | 最頻時間差のみに依存（ただし閾値・パラメータ調整でノイズ耐性向上可） |

## 3. アーキテクチャとスケーラビリティ

| 項目               | mimizam                                              | dejavu           | audfprint                  |
| ------------------ | ---------------------------------------------------- | ---------------- | -------------------------- |
| DBバックエンド     | **統一API**：SQLite/MySQL/PostgreSQL/Elasticsearch   | MySQL/PostgreSQL | CSV/ファイルベース         |
| 並列処理           | **最適化**：並列フィンガープリント生成               | 基本並列処理     | シングルスレッド           |
| API設計            | **統合API**：FingerprintDatabase統一インターフェース | Python API       | CLI中心（APIも可）         |
| 拡張性             | **高い**：プラガブルバックエンド・スコアリング方式   | 中程度           | 非常に高い（研究用に最適） |
| パフォーマンス監視 | **内蔵**：詳細なベンチマーク・性能分析機能           | 基本的な統計     | 基本的な統計               |

## 4. まとめ

### mimizamの優位性
- **標準Shazam実装**: constellation mapアルゴリズムによる確実な実装
- **統一API**: マルチデータベースバックエンド（SQLite/MySQL/PostgreSQL/Elasticsearch）の透過的利用
- **3種類スコアリング**: histogram/hybrid/detailed方式で用途に応じた精度・速度調整
- **最適化実装**: librosa + scipyベースの高速処理
- **プラガブル設計**: バックエンド・スコアリング方式の選択可能性
- **適応的処理**: 音声特性に応じた動的パラメータ調整
- **クラウドネイティブ**: PostgreSQL/Elasticsearchによる分散環境対応
- **内蔵ベンチマーク**: 詳細な性能分析機能

### dejavuの特長
- **シンプル設計**: 分かりやすいアーキテクチャとコード構成
- **MySQL/PostgreSQL対応**: リレーショナルDB環境での安定動作
- **Python生態系**: 豊富なライブラリとの連携

### audfprintの特長
- **研究用設計**: 多数のパラメータ調整による実験・分析向け
- **軽量**: ファイルベースでシンプルな依存関係
- **学術用**: 音響指紋研究・アルゴリズム比較に最適

## 5. 参考文献

- Avery Li-Chun Wang, "An Industrial-Strength Audio Search Algorithm", 2003  
  [https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- [dejavu GitHub](https://github.com/worldveil/dejavu)
- [audfprint GitHub](https://github.com/dpwe/audfprint)
- Mark Plumbley et al., "Pattern Recognition and Machine Learning for Audio Fingerprinting", Springer, 2019
