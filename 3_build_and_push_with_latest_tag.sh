#!/bin/bash

# 使用方法:
# ./build_and_push_with_latest_tag.sh

set -e

# 最新のタグ名を取得
LATEST_TAG=$(git describe --tags $(git rev-list --tags --max-count=1))

if [ -z "$LATEST_TAG" ]; then
  echo "タグが見つかりません。先にタグを作成してください。"
  exit 1
fi

echo "最新のタグ名: $LATEST_TAG を使って Docker ビルド＆プッシュを行います。よろしいですか？ (y/n)"
read -r answer

if [[ "$answer" != "y" ]]; then
  echo "キャンセルしました。"
  exit 0
fi

# 元のパスを記憶
ROOT_DIR=$(pwd)

# コンテナ情報の配列（各行：ディレクトリ名 イメージ名）
containers=(
  "aiagentapi mynoo/aiagentapi"
  "aiagentui mynoo/aiagentui"
  "my-mcp-server mynoo/aiagentmcp"
)

# 各コンテナをビルド＆プッシュ
for container in "${containers[@]}"; do
  DIR_NAME=$(echo "$container" | awk '{print $1}')
  IMAGE_NAME=$(echo "$container" | awk '{print $2}')

  echo "▶️ ビルド中: $IMAGE_NAME:$LATEST_TAG"

  cd "$ROOT_DIR/$DIR_NAME"
  docker build --platform linux/arm64 -t ${IMAGE_NAME}:${LATEST_TAG} . --no-cache

  echo "⬆️ プッシュ中: $IMAGE_NAME:$LATEST_TAG"
  docker push ${IMAGE_NAME}:${LATEST_TAG}

  echo "✅ 完了: $IMAGE_NAME:$LATEST_TAG"
done

# 最後にルートに戻る
cd "$ROOT_DIR"

echo "🎉 すべてのコンテナのビルド＆プッシュが完了しました。"