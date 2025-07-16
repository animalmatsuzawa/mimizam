#!/usr/bin/env python3
"""
テスト実行スクリプト
全テストモジュールを実行し、カバレッジレポートを生成
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """コマンドを実行して結果を表示"""
    print(f"\n {description}")
    print("============================================================")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ エラー: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """メイン実行関数"""
    # プロジェクトルートに移動
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(" mimizamテストスイート実行")
    print(f" 作業ディレクトリ: {os.getcwd()}")
    
    # 1. カバレッジ付き全テスト実行（一回で完了）
    success = run_command(
        "uv run python -m coverage run -m unittest discover tests -v",
        "全ユニットテスト実行（カバレッジ測定付き）"
    )
    
    if not success:
        print("❌ テストが失敗しました")
        sys.exit(1)
    
    # 2. カバレッジレポート生成
    run_command(
        "uv run python -m coverage report --include='src/*'",
        "カバレッジレポート"
    )
    
    # 3. HTMLレポート生成
    try:
        run_command(
            "uv run python -m coverage html",
            "HTMLカバレッジレポート生成"
        )
        print(" HTMLレポートが htmlcov/ ディレクトリに生成されました")
    except Exception as e:
        print(f"❌ HTMLレポート生成をスキップしました: {e}")

if __name__ == "__main__":
    main()

"""
📋 個別テスト実行コマンド:
uv run python3 -m unittest tests.test_fingerprint_database -v
uv run python3 -m unittest tests.test_audio_fingerprinting -v
uv run python3 -m unittest tests.test_mimizam_integration -v
uv run python3 -m unittest tests.test_mysql_containers -v
uv run python3 -m unittest tests.test_postgresql_containers -v
uv run python3 -m unittest tests.test_elasticsearch_containers -v
"""