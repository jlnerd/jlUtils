#!/usr/bin/env bash

echo "Executing git_add_commit_push helper script...."

BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo ""
echo "Executing on branch: "$BRANCH
echo ""

UNAME=$OD_USER
EMAIL=$OD_USER"@apple.com"

echo "Configuring user.name to: $UNAME and user.email to: $EMAIL"
git config --global user.name $UNAME
git config --global user.email $EMAIL

echo ""
echo "Cleaning notebooks..."
echo ""
bash scripts/clean_notebooks.sh

set -e

echo ""
echo "Applying black formatting..."
echo ""
bash scripts/black_format.sh

echo ""
echo "Build Sphinx Docs"
echo ""
python scripts/build_docs.py

git init

git status

echo "Add and commit changes? [ENTER]:"
read
git add -u

git status

cz commit

echo "push commit(s)? [ENTER]:"
read
git push origin $BRANCH

