#!/bin/bash
set -e

SENSOR_BRANCH="sensor_data"
SENSOR_DIR="sensor_data"
TARGET_DIR="site/_posts"

echo "=== Refreshing sensor data ==="

# If worktree doesn't exist, create it
if [ ! -d "$SENSOR_DIR/.git" ]; then
    echo "Adding worktree for $SENSOR_BRANCH..."
    git worktree add "$SENSOR_DIR" "$SENSOR_BRANCH"
fi

# Update sensor data
echo "Pulling latest sensor data..."
cd "$SENSOR_DIR"
git pull
cd ..

# Sync into Jekyll data folder
echo "Syncing into $TARGET_DIR..."
mkdir -p "$TARGET_DIR"
# shellcheck disable=SC2115
rm -rf "$TARGET_DIR"/*
cp "$SENSOR_DIR"/* "$TARGET_DIR"/

echo "Done."
