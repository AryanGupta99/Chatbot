#!/bin/bash
set -e

echo "=================================="
echo "Building AceBuddy for Render"
echo "=================================="

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build knowledge base chunks
echo "Building knowledge base chunks..."
python -c "
from build_focused_kb import build_focused_knowledge_base
print('Building focused KB...')
chunks = build_focused_knowledge_base()
print(f'Built {len(chunks)} chunks')
"

# Rebuild vector store
echo "Rebuilding vector store..."
python rebuild_with_focused_data.py

echo "=================================="
echo "Build complete!"
echo "=================================="
