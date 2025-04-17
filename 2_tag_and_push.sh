#!/bin/bash

# 使用方法:
# ./tag_and_push.sh v1.0.0

set -e

TAG_NAME=$1

if [ -z "$TAG_NAME" ]; then
  echo "エラー: タグ名を指定してください。"
  echo "例: ./tag_and_push.sh v1.0.0"
  exit 1
fi

echo "タグ名: $TAG_NAME で作成・プッシュします。よろしいですか？ (y/n)"
read -r answer

if [[ "$answer" != "y" ]]; then
  echo "キャンセルしました。"
  exit 0
fi

# タグ作成
git tag $TAG_NAME
echo "ローカルにタグ $TAG_NAME を作成しました。"

# GitHubにプッシュ
git push origin $TAG_NAME
echo "GitHub にタグ $TAG_NAME をプッシュしました。"