"""
Dataset Setup Helper Script
Helps download and prepare datasets for translation quality evaluation
"""

import os
import json
import requests
from pathlib import Path
import zipfile
import tarfile

def create_sample_reference():
    """Create a sample reference translation file for testing"""
    os.makedirs("references", exist_ok=True)
    
    # Sample reference translations (you'll need to add your own audio files)
    sample_references = {
        "test_audio.mp3": "This is a sample reference translation. Replace this with actual reference translations from your dataset.",
        "sample1.mp3": "Another sample reference translation for testing purposes.",
        "sample2.mp3": "Yet another reference translation example."
    }
    
    # Save as JSON
    json_path = "references/references.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_references, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created sample reference file: {json_path}")
    print("  Edit this file to add your actual reference translations")
    return json_path

def download_common_voice_info():
    """Print information about downloading Common Voice dataset"""
    print("\n" + "="*80)
    print("COMMON VOICE DATASET")
    print("="*80)
    print("\n1. Visit: https://commonvoice.mozilla.org/")
    print("2. Download Telugu or Hindi dataset")
    print("3. Extract audio files")
    print("4. Note: You'll need to manually create English translations")
    print("   or use provided transcriptions as references")
    print("\nDownload links:")
    print("  - Telugu: https://commonvoice.mozilla.org/en/datasets")
    print("  - Hindi: https://commonvoice.mozilla.org/en/datasets")

def download_openslr_info():
    """Print information about OpenSLR datasets"""
    print("\n" + "="*80)
    print("OPENSLR DATASETS")
    print("="*80)
    print("\nTelugu Speech Dataset (SLR66):")
    print("  URL: https://www.openslr.org/66/")
    print("  Contains: Telugu audio with transcriptions")
    print("  Note: You'll need to translate transcriptions to English")
    print("\nHindi Speech Dataset (SLR54):")
    print("  URL: https://www.openslr.org/54/")
    print("  Contains: Hindi audio with transcriptions")

def download_flores_info():
    """Print information about FLORES-101 dataset"""
    print("\n" + "="*80)
    print("FLORES-101 DATASET")
    print("="*80)
    print("\nHigh-quality translation benchmark:")
    print("  GitHub: https://github.com/facebookresearch/flores")
    print("  Contains: 3,001 sentences in 101 languages")
    print("  Format: Text translations (can pair with audio)")
    print("\nTo use:")
    print("  1. Download FLORES-101")
    print("  2. Extract English translations for Telugu/Hindi pairs")
    print("  3. Create audio files or find matching audio")
    print("  4. Organize in references/ directory")

def create_directory_structure():
    """Create recommended directory structure"""
    directories = [
        "audio",
        "references",
        "benchmark_results"
    ]
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created directory: {dir_name}/")
    
    # Create .gitkeep files
    for dir_name in directories:
        gitkeep = os.path.join(dir_name, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, 'w') as f:
                f.write("")
    
    print("\nDirectory structure created:")
    print("  audio/          - Place your audio files here")
    print("  references/     - Place reference translations here")
    print("  benchmark_results/ - Results will be saved here")

def print_quick_start():
    """Print quick start guide"""
    print("\n" + "="*80)
    print("QUICK START GUIDE")
    print("="*80)
    print("\n1. Place your audio files in the 'audio/' directory")
    print("2. Create reference translations:")
    print("   Option A: Create individual .txt files in 'references/'")
    print("            matching audio filenames (e.g., audio.mp3 -> references/audio.txt)")
    print("   Option B: Create 'references/references.json' with mapping:")
    print("            {\"audio.mp3\": \"English translation here\"}")
    print("\n3. Update testing.py:")
    print("   AUDIO_FILE = \"audio/your_file.mp3\"")
    print("   REFERENCE_DIR = \"references\"")
    print("\n4. Run: python testing.py")

def main():
    print("="*80)
    print("DATASET SETUP HELPER")
    print("="*80)
    
    print("\nThis script will help you set up datasets for translation evaluation.")
    print("\nChoose an option:")
    print("1. Create directory structure")
    print("2. Create sample reference file")
    print("3. Show Common Voice download info")
    print("4. Show OpenSLR download info")
    print("5. Show FLORES-101 download info")
    print("6. Show quick start guide")
    print("7. Do all of the above")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    if choice == "1":
        create_directory_structure()
    elif choice == "2":
        create_sample_reference()
    elif choice == "3":
        download_common_voice_info()
    elif choice == "4":
        download_openslr_info()
    elif choice == "5":
        download_flores_info()
    elif choice == "6":
        print_quick_start()
    elif choice == "7":
        create_directory_structure()
        create_sample_reference()
        download_common_voice_info()
        download_openslr_info()
        download_flores_info()
        print_quick_start()
    else:
        print("Invalid choice. Running all setup...")
        create_directory_structure()
        create_sample_reference()
        print_quick_start()
    
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Add your audio files to the 'audio/' directory")
    print("2. Add reference translations to the 'references/' directory")
    print("3. Update testing.py with your audio file path")
    print("4. Run the benchmark!")

if __name__ == "__main__":
    main()
