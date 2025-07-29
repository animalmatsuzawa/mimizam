#!/usr/bin/env python3
"""
Peak型最適化の性能分析スクリプト
matsu582のGitHubコメント対応: Peak型をnumpy.float64に変更する性能影響を調査
"""

import time
import numpy as np
import json
from dataclasses import dataclass, asdict
from typing import List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.audio_fingerprinter import Peak

@dataclass
class PeakFloat:
    """現在の実装: Python float型を使用"""
    time: float
    frequency: float
    amplitude: float

@dataclass
class PeakNumpy:
    """提案された実装: numpy.float64型を使用"""
    time: np.float64
    frequency: np.float64
    amplitude: np.float64

def generate_test_data(num_peaks: int = 5000):
    """テスト用のピークデータを生成（30秒音声の典型的なピーク数）"""
    np.random.seed(42)
    times = np.random.uniform(0, 30, num_peaks)
    frequencies = np.random.uniform(20, 8000, num_peaks)
    amplitudes = np.random.uniform(-80, -20, num_peaks)
    return times, frequencies, amplitudes

def benchmark_peak_creation_float(times, frequencies, amplitudes, iterations=10):
    """float型でのPeak作成性能測定"""
    total_time = 0
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        peaks = [
            PeakFloat(
                time=float(times[i]),
                frequency=float(frequencies[i]),
                amplitude=float(amplitudes[i])
            )
            for i in range(len(times))
        ]
        end_time = time.perf_counter()
        total_time += (end_time - start_time)
    
    return total_time / iterations, peaks

def benchmark_peak_creation_numpy(times, frequencies, amplitudes, iterations=10):
    """numpy.float64型でのPeak作成性能測定"""
    total_time = 0
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        peaks = [
            PeakNumpy(
                time=np.float64(times[i]),
                frequency=np.float64(frequencies[i]),
                amplitude=np.float64(amplitudes[i])
            )
            for i in range(len(times))
        ]
        end_time = time.perf_counter()
        total_time += (end_time - start_time)
    
    return total_time / iterations, peaks

def benchmark_json_serialization(peaks_float, peaks_numpy, iterations=5):
    """JSON シリアライゼーション性能測定"""
    
    float_times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        json_data = json.dumps([asdict(peak) for peak in peaks_float[:100]])
        end_time = time.perf_counter()
        float_times.append(end_time - start_time)
    
    numpy_times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        json_data = json.dumps([asdict(peak) for peak in peaks_numpy[:100]])
        end_time = time.perf_counter()
        numpy_times.append(end_time - start_time)
    
    return np.mean(float_times), np.mean(numpy_times)

def measure_memory_usage():
    """メモリ使用量の概算測定"""
    import sys
    
    peak_float = PeakFloat(time=1.234, frequency=440.0, amplitude=-20.5)
    float_size = sys.getsizeof(peak_float) + sys.getsizeof(peak_float.time) + \
                 sys.getsizeof(peak_float.frequency) + sys.getsizeof(peak_float.amplitude)
    
    peak_numpy = PeakNumpy(time=np.float64(1.234), frequency=np.float64(440.0), amplitude=np.float64(-20.5))
    numpy_size = sys.getsizeof(peak_numpy) + sys.getsizeof(peak_numpy.time) + \
                 sys.getsizeof(peak_numpy.frequency) + sys.getsizeof(peak_numpy.amplitude)
    
    return float_size, numpy_size

def main():
    print("=== Peak型最適化 性能分析レポート ===")
    print("matsu582のGitHubコメント対応: Peak型をnumpy.float64に変更する性能影響調査\n")
    
    print("1. テストデータ生成中...")
    times, frequencies, amplitudes = generate_test_data(5000)
    print(f"   生成されたピーク数: {len(times)} (30秒音声の典型的な数)")
    
    print("\n2. Peak作成性能測定中...")
    float_time, peaks_float = benchmark_peak_creation_float(times, frequencies, amplitudes)
    numpy_time, peaks_numpy = benchmark_peak_creation_numpy(times, frequencies, amplitudes)
    
    print(f"   float型での作成時間: {float_time:.6f}秒")
    print(f"   numpy.float64型での作成時間: {numpy_time:.6f}秒")
    
    if float_time > numpy_time:
        improvement = ((float_time - numpy_time) / float_time) * 100
        print(f"   → numpy.float64型が {improvement:.2f}% 高速")
    else:
        degradation = ((numpy_time - float_time) / float_time) * 100
        print(f"   → float型が {degradation:.2f}% 高速")
    
    print("\n3. JSON シリアライゼーション性能測定中...")
    float_json_time, numpy_json_time = benchmark_json_serialization(peaks_float, peaks_numpy)
    
    print(f"   float型でのJSON変換時間: {float_json_time:.6f}秒")
    print(f"   numpy.float64型でのJSON変換時間: {numpy_json_time:.6f}秒")
    
    if float_json_time > numpy_json_time:
        json_improvement = ((float_json_time - numpy_json_time) / float_json_time) * 100
        print(f"   → numpy.float64型が {json_improvement:.2f}% 高速")
    else:
        json_degradation = ((numpy_json_time - float_json_time) / float_json_time) * 100
        print(f"   → float型が {json_degradation:.2f}% 高速")
    
    print("\n4. メモリ使用量測定中...")
    float_memory, numpy_memory = measure_memory_usage()
    
    print(f"   float型でのメモリ使用量: {float_memory} bytes")
    print(f"   numpy.float64型でのメモリ使用量: {numpy_memory} bytes")
    
    if float_memory > numpy_memory:
        memory_improvement = ((float_memory - numpy_memory) / float_memory) * 100
        print(f"   → numpy.float64型が {memory_improvement:.2f}% メモリ効率的")
    else:
        memory_overhead = ((numpy_memory - float_memory) / float_memory) * 100
        print(f"   → float型が {memory_overhead:.2f}% メモリ効率的")
    
    print("\n=== 総合評価 ===")
    
    overall_creation_improvement = ((float_time - numpy_time) / float_time) * 100 if float_time > numpy_time else 0
    overall_json_improvement = ((float_json_time - numpy_json_time) / float_json_time) * 100 if float_json_time > numpy_json_time else 0
    
    print(f"Peak作成性能改善: {overall_creation_improvement:.2f}%")
    print(f"JSON変換性能改善: {overall_json_improvement:.2f}%")
    
    print("\n=== 推奨事項 ===")
    if overall_creation_improvement > 10:
        print("✅ numpy.float64型への変更を推奨")
        print("   理由: 10%以上の性能改善が期待できる")
    elif overall_creation_improvement > 5:
        print("⚠️  numpy.float64型への変更を検討")
        print("   理由: 5-10%の性能改善が期待できるが、実装複雑性とのトレードオフを考慮")
    else:
        print("❌ numpy.float64型への変更は推奨しない")
        print("   理由: 性能改善が限定的で、実装複雑性の増加に見合わない")
    
    print("\n=== 実装上の考慮事項 ===")
    print("1. JSON互換性: 両方の型でJSON変換が正常に動作することを確認済み")
    print("2. 型変換コスト: 現在のfloat()変換コストが削減される")
    print("3. コード変更範囲: Peak作成箇所3か所の修正が必要")
    print("4. 後方互換性: 既存のAPIには影響なし")

if __name__ == "__main__":
    main()
