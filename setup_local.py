#!/usr/bin/env python3
"""
Local setup script for Discord Crypto Bot

This script helps set up the bot for local development and execution.
It installs dependencies, creates necessary directories, and validates configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"➤ {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"  ✓ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required!")
        print(f"  Current version: {sys.version}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    dependencies = [
        "discord.py==2.5.2",
        "aiohttp==3.12.14", 
        "matplotlib==3.10.3",
        "pandas==2.3.1",
        "groq==0.30.0",
        "flask==3.1.1",
        "python-dotenv==1.1.1"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["data", "logs", "charts"]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"  ✓ Created/verified directory: {directory}")
        except Exception as e:
            print(f"  ✗ Failed to create {directory}: {e}")
            return False
    
    return True

def check_env_file():
    """Check if environment file exists."""
    print("\n🔐 Checking environment configuration...")
    
    if os.path.exists('.env'):
        print("  ✓ .env file found")
        
        # Read and check for required variables
        with open('.env', 'r') as f:
            content = f.read()
        
        required_vars = ['DISCORD_TOKEN', 'GROQ_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if var not in content or f'{var}=' not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"  ⚠️  Missing environment variables: {', '.join(missing_vars)}")
            print("     Please add them to your .env file")
        else:
            print("  ✓ All required environment variables found")
        
        return True
    else:
        print("  ⚠️  .env file not found")
        print("     Please copy .env.example to .env and fill in your API keys:")
        print("     cp .env.example .env")
        return False

def validate_bot_files():
    """Check if all required bot files exist."""
    print("\n📋 Validating bot files...")
    
    required_files = [
        'main.py',
        'crypto_tracker.py',
        'chart_generator.py',
        'ai_advisor.py',
        'data_manager.py',
        'config.py',
        'keepalive.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n  ✗ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Discord Crypto Bot - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Validate bot files
    if not validate_bot_files():
        print("\n❌ Setup failed: Missing required bot files")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Could not create directories")
        sys.exit(1)
    
    # Check environment configuration
    env_ok = check_env_file()
    
    print("\n" + "=" * 50)
    
    if env_ok:
        print("✅ Setup completed successfully!")
        print("\nTo run the bot:")
        print("  python main.py")
        print("\nTo keep it running with UptimeRobot:")
        print(f"  Use this URL: http://your-domain.com:5000/ping")
    else:
        print("⚠️  Setup completed with warnings")
        print("   Please configure your .env file before running the bot")
    
    print("\n📚 Available commands:")
    print("   /price <crypto>   - Get price and chart")
    print("   /trending         - View trending cryptos") 
    print("   /advice <crypto>  - Get AI trading advice")
    print("   /track <crypto>   - Start tracking crypto")
    print("   /untrack <crypto> - Stop tracking crypto")
    print("   /help             - Show help")

if __name__ == "__main__":
    main()