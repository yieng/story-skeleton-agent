#!/bin/bash

# Determine commit message: use $1 if provided, otherwise fall back to default
COMMIT_MSG="${1:-Deploying Streamlit lead magnet MVP}"

echo "Using commit message: \"$COMMIT_MSG\""

# Initialize and push workflow
git init
git add .
git commit -m "$COMMIT_MSG"
git branch -M main

# Check if remote already exists to prevent duplicate error messages
if ! git remote get-url origin &>/dev/null; then
    git remote add origin https://github.com/yieng/story-skeleton-agent.git
fi

git push -u origin main
