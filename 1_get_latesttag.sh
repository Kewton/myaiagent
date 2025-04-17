#!/bin/bash

# エラー時に即終了
set -e

# GitHubの最新タグ名を取得
LATEST_TAG=$(git describe --tags $(git rev-list --tags --max-count=1))

# タグが取得できたかチェック
if [ -z "$LATEST_TAG" ]; then
  echo "タグが見つかりませんでした。まずはタグを作成してください。"
  exit 1
fi

echo "最新のタグ名: $LATEST_TAG"