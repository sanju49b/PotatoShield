# Whisper Translation Quality Benchmark

A comprehensive benchmark tool for evaluating Whisper models on Telugu/Hindi to English translation with quality metrics.

## Features

- **Multi-Model Testing**: Tests 4 Whisper models (small, medium, large-v3, large-v3-turbo)
- **Quality Metrics**: BLEU, CHRF, ROUGE-1/2/L scores
- **Performance Metrics**: Translation time, RTF (Real-Time Factor), word count
- **Auto Language Detection**: Automatically detects Telugu/Hindi
- **Reference Translation Support**: Compare translations against ground truth

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Set Up Dataset

Run the setup script:
```bash
python setup_dataset.py
```

This will:
- Create directory structure (`audio/`, `references/`, `benchmark_results/`)
- Create sample reference file
- Show download information for open-source datasets

### 2. Add Your Data

**Option A: Using your own audio files**
1. Place audio files in `audio/` directory
2. Create reference translations in `references/` directory
   - Match filenames: `audio.mp3` → `references/audio.txt`
   - Or use JSON: `references/references.json`

**Option B: Download open-source datasets**
- See `DATASET_GUIDE.md` for detailed information
- Recommended: Common Voice, OpenSLR, FLORES-101

### 3. Configure and Run

Edit `testing.py`:
```python
AUDIO_FILE = "audio/your_file.mp3"
REFERENCE_DIR = "references"  # or REFERENCE_FILE = "references/your_file.txt"
```

Run the benchmark:
```bash
python testing.py
```

## Directory Structure

```
testing/
├── audio/              # Your audio files
├── references/         # Reference translations
│   ├── audio.txt       # Individual reference files
│   └── references.json # Or JSON mapping
├── benchmark_results/  # Output results
├── testing.py          # Main benchmark script
├── setup_dataset.py    # Dataset setup helper
└── requirements.txt    # Dependencies
```

## Output

The benchmark generates:
- **Console logs**: Real-time progress and results
- **Log file**: `translation_benchmark_YYYYMMDD_HHMMSS.log`
- **JSON results**: `benchmark_results/benchmark_YYYYMMDD_HHMMSS.json`
- **Individual translations**: `benchmark_results/{model}_YYYYMMDD_HHMMSS.txt`

## Quality Metrics Explained

- **BLEU**: Measures n-gram precision (0-100, higher is better)
- **CHRF**: Character-level F-score (0-100, higher is better)
- **ROUGE-1**: Unigram overlap (0-100, higher is better)
- **ROUGE-2**: Bigram overlap (0-100, higher is better)
- **ROUGE-L**: Longest common subsequence (0-100, higher is better)

## Supported Datasets

See `DATASET_GUIDE.md` for detailed information on:
- BhasaAnuvaad (AI4Bharat)
- TeluguST-46
- FLEURS
- FLORES-101
- Common Voice
- OpenSLR

## Requirements

- Python 3.7+
- faster-whisper
- sacrebleu (for BLEU/CHRF)
- rouge-score (for ROUGE)
- pandas

## Notes

- Quality metrics require reference translations
- Without references, benchmark runs but skips quality evaluation
- Models are loaded from `/opt/whisper_models` (update `MODEL_DIR` if different)

## Troubleshooting

**No quality metrics?**
```bash
pip install sacrebleu rouge-score
```

**Audio file not found?**
- Check the path in `testing.py`
- Ensure audio file exists

**No reference translation?**
- Benchmark will run but skip quality evaluation
- Add reference files to `references/` directory
