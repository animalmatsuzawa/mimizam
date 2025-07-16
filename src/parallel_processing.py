"""
並列処理最適化モジュール - マルチプロセシングによるフィンガープリンティングの並列化
現状、遅いためデフォルトで無効
"""

import numpy as np
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict, Any, Optional, Callable
import time
import logging
import sys
import os
from dataclasses import dataclass
import librosa
from .database_base import Fingerprint


@dataclass
class ProcessingChunk:
    """処理チャンクを表現するデータクラス"""
    audio_segment: np.ndarray
    start_time: float
    chunk_id: int
    sr: int


class ParallelAudioProcessor:
    """音声処理の並列化を管理するクラス"""
    
    def __init__(self, max_workers: Optional[int] = None, chunk_duration: float = 30.0):
        """
        並列音声プロセッサーを初期化
        
        Args:
            max_workers: 最大ワーカー数（Noneの場合は自動）
            chunk_duration: 各チャンクの継続時間（秒）
        """
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        self.chunk_duration = chunk_duration
        self.logger = logging.getLogger(__name__)
    
    def split_audio_into_chunks(self, audio: np.ndarray, sr: int, 
                               overlap_ratio: float = 0.1) -> List[ProcessingChunk]:
        """
        音声を並列処理用のチャンクに分割
        
        Args:
            audio: 音声信号
            sr: サンプルレート
            overlap_ratio: チャンク間の重複比率
            
        Returns:
            処理チャンクのリスト
        """
        chunk_samples = int(self.chunk_duration * sr)
        overlap_samples = int(chunk_samples * overlap_ratio)
        step_size = chunk_samples - overlap_samples
        
        chunks = []
        chunk_id = 0
        
        for start_idx in range(0, len(audio), step_size):
            end_idx = min(start_idx + chunk_samples, len(audio))
            
            if end_idx - start_idx < chunk_samples * 0.5:  # 短すぎるチャンクはスキップ
                break
            
            audio_segment = audio[start_idx:end_idx]
            start_time = start_idx / sr
            
            chunk = ProcessingChunk(
                audio_segment=audio_segment,
                start_time=start_time,
                chunk_id=chunk_id,
                sr=sr
            )
            chunks.append(chunk)
            chunk_id += 1
        
        self.logger.info(f"Split audio into {len(chunks)} chunks ({self.chunk_duration}s each, {overlap_ratio*100:.1f}% overlap)")
        return chunks
    
    def process_chunks_parallel(self, chunks: List[ProcessingChunk], 
                              processing_func: Callable, **kwargs) -> List[Any]:
        """
        チャンクを並列処理
        
        Args:
            chunks: 処理チャンクのリスト
            processing_func: 処理関数
            **kwargs: 処理関数に渡す追加引数
            
        Returns:
            処理結果のリスト
        """
        results = []
        
        if len(chunks) == 1:
            # 単一チャンクの場合は並列処理しない
            return [processing_func(chunks[0], **kwargs)]
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # タスクを投入
            future_to_chunk = {
                executor.submit(processing_func, chunk, **kwargs): chunk 
                for chunk in chunks
            }
            
            # 結果を収集
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append((chunk.chunk_id, chunk.start_time, result))
                    self.logger.debug(f"Chunk {chunk.chunk_id} processing completed")
                except Exception as exc:
                    self.logger.error(f"Error in chunk {chunk.chunk_id}: {exc}")
                    results.append((chunk.chunk_id, chunk.start_time, None))
        
        # チャンクIDでソート
        results.sort(key=lambda x: x[0])
        return results
    
    def merge_fingerprint_results(self, results: List[Tuple[int, float, Any]], 
                                 overlap_threshold: float = 0.1) -> List[Any]:
        """
        並列処理された指紋結果をマージし、重複を除去
        
        Args:
            results: (chunk_id, start_time, fingerprints) のタプルリスト
            overlap_threshold: 重複とみなす時間閾値（秒）
            
        Returns:
            マージされたフィンガープリントリスト
        """
        merged_fingerprints = []
        seen_hashes = set()
        
        for chunk_id, start_time, fingerprints in results:
            if fingerprints is None:
                continue
            
            chunk_fps = self._process_chunk_fingerprints(
                fingerprints, start_time, seen_hashes, overlap_threshold
            )
            merged_fingerprints.extend(chunk_fps)
        
        self.logger.info(f"Merged fingerprint count: {len(merged_fingerprints)}")
        return merged_fingerprints
    
    def _process_chunk_fingerprints(self, fingerprints: List[Any], start_time: float,
                                   seen_hashes: set, overlap_threshold: float) -> List[Any]:
        """チャンクのフィンガープリントを処理"""
        chunk_fingerprints = []
        
        for fp in fingerprints:
            adjusted_time = fp.time_offset + start_time
            hash_key = fp.hash_value
            
            if not self._is_duplicate_fingerprint(hash_key, adjusted_time, seen_hashes, overlap_threshold):
                adjusted_fp = self._create_adjusted_fingerprint(fp, adjusted_time)
                chunk_fingerprints.append(adjusted_fp)
                seen_hashes.add((hash_key, adjusted_time))
        
        return chunk_fingerprints
    
    def _is_duplicate_fingerprint(self, hash_key: str, adjusted_time: float,
                                 seen_hashes: set, overlap_threshold: float) -> bool:
        """フィンガープリントが重複かどうかチェック"""
        for seen_hash, seen_time in seen_hashes:
            if (hash_key == seen_hash and 
                abs(adjusted_time - seen_time) < overlap_threshold):
                return True
        return False
    
    def _create_adjusted_fingerprint(self, fp: Any, adjusted_time: float) -> Any:
        """調整された時間オフセットで新しいフィンガープリントを作成"""
        return Fingerprint(
            hash_value=fp.hash_value,
            time_offset=adjusted_time,
            song_id=fp.song_id
        )


class MemoryOptimizer:
    """メモリ使用量を最適化するクラス"""
    
    def __init__(self, max_memory_gb: float = 2.0):
        """
        メモリオプティマイザーを初期化
        
        Args:
            max_memory_gb: 最大メモリ使用量（GB）
        """
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.logger = logging.getLogger(__name__)
    
    def estimate_audio_memory_usage(self, audio_length_samples: int, 
                                   dtype: np.dtype = np.float32) -> int:
        """
        音声データのメモリ使用量を推定
        
        Args:
            audio_length_samples: 音声の長さ（サンプル数）
            dtype: データ型
            
        Returns:
            推定メモリ使用量（バイト）
        """
        return audio_length_samples * dtype().itemsize
    
    def should_use_streaming(self, audio: np.ndarray) -> bool:
        """
        ストリーミング処理を使用すべきかどうか判断
        
        Args:
            audio: 音声データ
            
        Returns:
            ストリーミング処理を使用すべきかどうか
        """
        estimated_memory = self.estimate_audio_memory_usage(len(audio))
        # スペクトログラムやピーク検出で約5倍のメモリが必要と想定
        total_estimated = estimated_memory * 5
        
        return total_estimated > self.max_memory_bytes
    
    def get_optimal_chunk_size(self, audio_length: int, sr: int) -> float:
        """
        メモリ制約に基づいて最適なチャンクサイズを計算
        
        Args:
            audio_length: 音声の長さ（サンプル数）
            sr: サンプルレート
            
        Returns:
            最適なチャンクサイズ（秒）
        """
        if not self.should_use_streaming(np.zeros(audio_length, dtype=np.float32)):
            return audio_length / sr  # 全体を一度に処理
        
        # メモリ制約内で処理できる最大チャンクサイズを計算
        max_samples_per_chunk = self.max_memory_bytes // (np.float32().itemsize * 5)
        max_duration = max_samples_per_chunk / sr
        
        # 最小5秒、最大60秒に制限
        return max(5.0, min(60.0, max_duration))


def parallel_fingerprint_worker(chunk: ProcessingChunk, **kwargs) -> List:
    """
    並列処理用のワーカー関数
    
    Args:
        chunk: 処理チャンク
        **kwargs: AudioFingerprineterに渡すパラメータ
        
    Returns:
        フィンガープリントのリスト
    """
    try:
        # 動的import: 循環importを避けるため
        from .audio_fingerprinter import AudioFingerprinter
        
        # 並列処理では適応的パラメータと並列処理を無効にする
        kwargs_copy = kwargs.copy()
        kwargs_copy['enable_adaptive_params'] = False
        kwargs_copy['enable_parallel_processing'] = False
        
        fingerprinter = AudioFingerprinter(**kwargs_copy)
        fingerprints = fingerprinter.fingerprint_audio(chunk.audio_segment, debug=False)
        
        return fingerprints
    except Exception as e:
        logging.getLogger(__name__).error(f"Chunk processing error: {e}")
        return []


class StreamingProcessor:
    """大容量音声ファイルのストリーミング処理を管理"""
    
    def __init__(self, chunk_duration: float = 30.0, buffer_size: int = 8192):
        """
        ストリーミングプロセッサーを初期化
        
        Args:
            chunk_duration: チャンクサイズ（秒）
            buffer_size: バッファサイズ
        """
        self.chunk_duration = chunk_duration
        self.buffer_size = buffer_size
        self.logger = logging.getLogger(__name__)
    
    def process_audio_stream(self, audio_file_path: str, 
                           processing_func: Callable, **kwargs) -> List[Any]:
        """
        音声ファイルをストリーミング処理
        
        Args:
            audio_file_path: 音声ファイルのパス
            processing_func: 処理関数
            **kwargs: 処理関数への追加パラメータ
            
        Returns:
            処理結果のリスト
        """
        results = []
        
        # 音声ファイルの情報を取得
        duration = librosa.get_duration(path=audio_file_path)
        sr = librosa.get_samplerate(audio_file_path)
        
        self.logger.info(f"Starting streaming processing: {duration:.2f}s, {sr}Hz")
        
        # チャンクごとに処理
        for start_time in np.arange(0, duration, self.chunk_duration):
            end_time = min(start_time + self.chunk_duration, duration)
            
            # チャンクを読み込み
            audio_chunk, _ = librosa.load(
                audio_file_path, 
                sr=sr,
                offset=start_time,
                duration=end_time - start_time
            )
            
            # 処理を実行
            result = processing_func(audio_chunk, **kwargs)
            results.append((start_time, result))
            
            self.logger.debug(f"Chunk processing completed: {start_time:.1f}-{end_time:.1f}s")
        
        return results
