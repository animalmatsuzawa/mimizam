# mimizam音声指紋マッチングのスコア計算について

mimizamで採用している音声指紋比較時のスコア計算方法（histogram/hybrid/detailed）について、計算方法とパラメータについて記します。

---

## 1. スコアリング方式の概要

mimizamでは3つのスコアリング方式を実装しており、用途に応じて選択可能です：

### 1.1 方式の選択
- **hybrid方式**（デフォルト）: 2段階判定（高速候補選別 + 詳細評価）
- **histogram方式**: ヒストグラム分析のみ
- **detailed方式**: 多面的スコアリングのみ

### 1.2 共通パラメータ
```python
# 基本設定
min_confidence = 0.1        # 最小信頼度閾値
max_results = 10           # 最大結果数
time_tolerance = 0.3       # 時間許容度（秒）
freq_tolerance = 100       # 周波数許容度（Hz）

# 速度・ピッチ変化の許容範囲
freq_scale_factors = [0.9, 0.95, 1.0, 1.05, 1.1]  # ±10%のピッチ変化
```

---

## 2. Hybrid方式（推奨デフォルト）

### 2.1 概要
2段階の判定プロセスにより、速度と精度のバランスを実現：
1. **第1段階**: 高速ヒストグラム分析で候補絞り込み
2. **第2段階**: 多面的スコアリングで詳細評価

### 2.2 第1段階: 高速候補選別

#### 使用スケール
```python
hybrid_fast_scales = [0.8, 0.9, 1.0, 1.1, 1.2, 1.5]  # 高速候補抽出用
```

#### 計算方法
- 各スケールでクエリフィンガープリントをスケーリング
- データベース検索による一致ペア抽出
- ヒストグラム信頼度計算（軽量版）
- 上位K件（デフォルト10件）を候補として選出

#### ヒストグラム信頼度計算
```python
def _calculate_hybrid_histogram_confidence(match_pairs, time_scale):
    # 1. 時間差計算（スケール調整済み）
    offsets = [(db_time - query_time)/time_scale for query_time, db_time in match_pairs]
    
    # 2. 適応的ビン幅計算
    std_dev = np.std(offsets)
    bin_width = max(0.1, min(std_dev / 2, 0.5))  # 0.1-0.5秒の範囲
    
    # 3. ヒストグラム生成
    hist, _ = np.histogram(offsets, bins=bins, range=適応的レンジ)
    max_count = np.max(hist)
    
    # 4. 信頼度計算
    base_score = max_count / len(offsets)
    prominence_boost = 1.0 + (peak_prominence * 1.5)
    match_weight = min(1.0, log(max_count + 1) / log(15))
    scale_penalty = exp(-scale_deviation * 0.3)
    
    confidence = base_score * prominence_boost * match_weight * scale_penalty
```

#### パラメータについて
- **hybrid_fast_scales = [0.8, 0.9, 1.0, 1.1, 1.2, 1.5]**
  - 根拠: 候補絞り込みに必要最小限の範囲
  - 計算量: 6回検索で高速処理を実現
- **bin_width**: `max(0.1, min(std_dev / 2, 0.5))` - データ分散に応じた適応的調整
- **match_weight**: `log(max_count + 1) / log(15)` - 15一致で最大重みに到達
- **scale_penalty**: `exp(-scale_deviation * 0.3)` - 指数的減衰でスケール偏差をペナルティ化

### 2.3 第2段階: 詳細評価

#### 使用スケール
```python
detailed_scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0]  # 包括的
```

#### 計算方法
- 候補楽曲ごとに全スケール・全周波数スケールで再検索
- 多面的信頼度スコア計算
- 最適スケールの決定
- 最終信頼度として詳細評価結果を採用

#### パラメータについて
- **detailed_scales = [0.5〜2.0]**
  - 根拠: 実用的な再生速度変化の全範囲をカバー（0.5倍-2倍）
  - 用途: 高精度が要求される用途
  - 計算量: 11スケール × 5周波数スケール = 55回検索

---

## 3. Histogram方式（ヒストグラム分析）

### 3.1 概要
ヒストグラム分析による高速マッチング

### 3.2 使用スケール
```python
histogram_scales = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.5]  # 細かい刻み
```

### 3.3 計算方法

#### ヒストグラム信頼度計算
```python
def _calculate_histogram_confidence(max_count, total_matches, prominence, time_scale):
    # 1. 基本スコア：最大ビンの相対頻度
    base_score = max_count / total_matches
    
    # 2. ピークの突出度による強化
    prominence_boost = 1.0 + (prominence * 2.0)
    
    # 3. 一致数による重み付け（対数スケール）
    match_weight = min(1.0, log(max_count + 1) / log(20))  # 20一致で最大重み
    
    # 4. 時間スケールペナルティ
    scale_penalty = exp(-scale_deviation * 0.5)  # 指数的減衰
    
    # 5. 最終信頼度
    confidence = base_score * prominence_boost * match_weight * scale_penalty
    
    # 6. 高品質マッチのブースト
    if max_count >= 5 and prominence > 0.3:
        confidence = min(1.0, confidence * 1.5)
```

#### パラメータ根拠
- **bin_width**: `max(0.1, min(std_dev / 2, 1.0))` - データ分散に応じた適応的調整
- **offset_range**: `max(10, std_dev * 4)` - 統計的外れ値を考慮
- **prominence閾値**: `0.3` - 経験的に決定された有意性閾値
- **histogram_scales = [0.8〜1.5]**
  - 根拠: 一般的な音声指紋システム(Dejavu)の推奨範囲
  - 用途: 速度重視の用途
  - 計算量: 11スケールで高速処理
- **match_weight**: `log(max_count + 1) / log(20)` - 20一致で最大重みに到達
- **高品質マッチブースト**: max_count ≥ 5 かつ prominence > 0.3 で1.5倍

---

## 4. Detailed方式（多面的スコアリング）

### 4.1 概要
包括的な多面的評価による高精度マッチング

### 4.2 使用スケール
```python
detailed_scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0]  # 包括的（0.5倍-2倍）
freq_scale_factors = [0.9, 0.95, 1.0, 1.05, 1.1]  # ±10%のピッチ変化
```

### 4.3 基本信頼度計算

#### 時間アライメント分析
```python
def _calculate_confidence_score(match_pairs):
    # 1. 時間アライメントグループ化（tolerance=0.3秒）
    aligned_groups = _find_time_aligned_matches(match_pairs, 0.3)
    
    # 2. 最大グループサイズによる基本信頼度
    max_aligned_matches = max(len(group) for group in aligned_groups)
    base_confidence = max_aligned_matches / len(match_pairs)
    
    # 3. 一致数ボーナス
    if max_aligned_matches >= 20:
        base_confidence *= 1.3
    elif max_aligned_matches >= 10:
        base_confidence *= 1.2
    elif max_aligned_matches >= 5:
        base_confidence *= 1.1
    
    # 4. 分散ペナルティ
    if len(aligned_groups) > 3:
        base_confidence *= 0.9
    
    # 5. 冗長性ボーナス
    secondary_groups = [g for g in aligned_groups if len(g) >= 3]
    if secondary_groups:
        secondary_bonus = min(0.1 * len(secondary_groups), 0.3)
        base_confidence += secondary_bonus
    
    return min(base_confidence, 1.0)
```

#### パラメータについて
- **time_tolerance = 0.3秒**
  - 根拠: 音声のジッターやエンコーディング誤差を考慮
  - 影響: アライメントグループ化の精度に直接影響
  - 調整: ノイジーな環境では0.5秒まで拡大可能
- **一致数ボーナス（経験的閾値）**:
  - ≥20一致: ×1.3（強い証拠）
  - ≥10一致: ×1.2（中程度の証拠）
  - ≥5一致: ×1.1（弱い証拠）
- **分散ペナルティ**: アライメントグループ数 > 3で×0.9
- **冗長性ボーナス**: セカンダリグループ（≥3一致）ごとに+0.1（最大+0.3）

### 4.4 スケーリング補正

#### スケーリング付き信頼度計算
```python
def _calculate_confidence_score_with_scaling(match_pairs, time_scale, freq_scale):
    # 1. ベース信頼度計算
    base_confidence = _calculate_confidence_score(match_pairs)
    
    # 2. 時間スケールペナルティ
    scale_penalty = 1.0
    time_deviation = abs(time_scale - 1.0)
    
    if time_scale <= 0.7:          # 非常に遅い（0.5倍-0.7倍）
        scale_penalty *= 0.8
    elif time_scale >= 1.5:        # 非常に速い（1.5倍-2倍）
        scale_penalty *= 0.85
    elif time_deviation > 0.1:     # 中程度の速度変化
        scale_penalty *= (1.0 - time_deviation * 0.2)
    
    # 3. 周波数スケールペナルティ
    freq_deviation = abs(freq_scale - 1.0)
    if freq_deviation > 0.03:
        scale_penalty *= (1.0 - freq_deviation * 0.3)
    
    # 4. 極端スケーリング時のボーナス
    if len(match_pairs) >= 20 and (time_scale <= 0.7 or time_scale >= 1.5):
        base_confidence *= 1.15
    elif len(match_pairs) >= 10 and (time_deviation > 0.01 or freq_deviation > 0.01):
        base_confidence *= 1.1
    
    return min(base_confidence * scale_penalty, 1.0)
```

#### パラメータについて
- **時間スケールペナルティ（段階的調整）**:
  - time_scale ≤ 0.7: ×0.8（非常に遅い）
  - time_scale ≥ 1.5: ×0.85（非常に速い）
  - 中程度の変化: ×(1.0 - deviation × 0.2)
- **周波数スケールペナルティ**: freq_deviation > 0.03で×(1.0 - deviation × 0.3)
- **極端スケーリング時のボーナス**:
  - ≥20一致 + 極端スケール: ×1.15
  - ≥10一致 + スケール変化: ×1.1
- **freq_scale_factors = [0.9〜1.1]**: ±10%のピッチ変化に対応

---

## 5. 性能特性

### 5.1 計算量比較
| 方式      | スケール探索回数     | 相対計算量 | 精度 |
| --------- | -------------------- | ---------- | ---- |
| Histogram | 11回                 | 1.0x       | 標準 |
| Hybrid    | 6回+55回（候補のみ） | 1.5x       | 高   |
| Detailed  | 55回（全候補）       | 5.0x       | 最高 |

### 5.2 用途別推奨設定
- **リアルタイム処理**: Histogram方式
- **バランス型**: Hybrid方式（デフォルト）
- **高精度要求**: Detailed方式

---

## 6. 参考文献

- Avery Li-Chun Wang, "An Industrial-Strength Audio Search Algorithm", 2003
- 音声指紋システムの既存実装を参考
  - https://github.com/worldveil/dejavu
  - https://github.com/dpwe/audfprint
- 各係数は実験データと経験則に基づく
