#!/bin/bash
set -e

SENSOR_BRANCH="sensor_data"
WORKTREE_DIR="sensor_data"
SOURCE_DIR="$WORKTREE_DIR/data"
TARGET_DIR="dashboard/_posts"

echo "=== Refreshing sensor data ==="

# If worktree doesn't exist, create it
if [ ! -d "$WORKTREE_DIR" ]; then
    echo "Adding worktree for branch '$SENSOR_BRANCH'..."
    git worktree add "$WORKTREE_DIR" "$SENSOR_BRANCH"
fi

# Update sensor data
echo "Pulling latest sensor data..."
cd "$WORKTREE_DIR"
git pull
cd ..

# Sync into Jekyll data folder
echo "Syncing posts into $TARGET_DIR..."
mkdir -p "$TARGET_DIR"

# Clear old copied posts
rsync -a --delete "$SOURCE_DIR"/ "$TARGET_DIR"/

echo "Sensor posts refreshed."
