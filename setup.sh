#!/bin/bash

# MiraC2 Setup Script
# This script sets up both the Rust backend and Python GUI

set -e

echo "🔴 Setting up MiraC2 - Rust Core + Python GUI"
echo "================================================"

# Check if Rust is installed
if ! command -v rustc &> /dev/null; then
    echo "❌ Rust is not installed. Please install Rust first:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Rust version: $(rustc --version)"
echo "✅ Python version: $(python3 --version)"
echo ""

# Build Rust components
echo "🦀 Building Rust components..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "✅ Rust components built successfully"
else
    echo "❌ Failed to build Rust components"
    exit 1
fi

echo ""

# Set up Python environment
echo "🐍 Setting up Python environment..."
cd python-gui

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

cd ..

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 To run MiraC2:"
echo "   1. Start the Rust server:"
echo "      cargo run --bin mira-server"
echo ""
echo "   2. In another terminal, start the Python GUI:"
echo "      cd python-gui"
echo "      source venv/bin/activate"
echo "      python main.py"
echo ""
echo "🎨 Theme: Cyberpunk (RED+BLACK+GREEN)"
echo "🔐 Encryption: AES-256-GCM"
echo "🌐 Default server port: 8080"