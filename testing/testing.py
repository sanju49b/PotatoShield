"""
Whisper Multi-Model Translation Benchmark
Tests: small, medium, large-v3, large-v3-turbo
Direct translation pipeline (Telugu/Hindi -> English)
Performance and quality comparison with evaluation metrics
"""

import time
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from faster_whisper import WhisperModel
import pandas as pd

# Quality evaluation metrics
try:
    from sacrebleu.metrics import BLEU, CHRF
    from rouge_score import rouge_scorer
    QUALITY_METRICS_AVAILABLE = True
except ImportError:
    QUALITY_METRICS_AVAILABLE = False
    print("Warning: Quality metrics not available. Install with: pip install sacrebleu rouge-score")

# Model configurations
MODELS_TO_TEST = {
    'small': {
        'path': 'models--Systran--faster-whisper-small',
        'compute_type': 'int8'
    },
    'medium': {
        'path': 'models--Systran--faster-whisper-medium', 
        'compute_type': 'int8'
    },
    'large-v3': {
        'path': 'models--Systran--faster-whisper-large-v3',
        'compute_type': 'int8'
    },
    'large-v3-turbo': {
        'path': 'models--mobiuslabsgmbh--faster-whisper-large-v3-turbo',
        'compute_type': 'int8'
    }
}

MODEL_DIR = "/opt/whisper_models"

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'translation_benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def deduplicate_segments(text):
    """Remove repetitive sequences while preserving context"""
    lines = text.split('. ')
    seen = {}
    result = []
    
    for line in lines:
        if line not in seen or len(result) - seen.get(line, -999) > 2:
            result.append(line)
            seen[line] = len(result)
    
    return '. '.join(result)

def test_translation_model(model_name, model_config, audio_path, logger, reference_text=None):
    """
    Test a single model's translation performance
    
    Args:
        model_name: Name of the model
        model_config: Model configuration dict
        audio_path: Path to audio file
        logger: Logger instance
        reference_text: Optional reference translation for quality evaluation
    
    Returns:
        dict with results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing Model: {model_name.upper()}")
    logger.info(f"{'='*80}")
    
    results = {
        'model': model_name,
        'audio_file': os.path.basename(audio_path),
        'success': False
    }
    
    try:
        # Load model
        logger.info(f"Loading model from: {model_config['path']}")
        load_start = time.time()
        
        model_path = os.path.join(MODEL_DIR, model_config['path'])
        model = WhisperModel(
            model_path,
            device="cpu",
            compute_type=model_config['compute_type']
        )
        
        load_time = time.time() - load_start
        results['load_time'] = load_time
        logger.info(f"✓ Model loaded in {load_time:.2f}s")
        
        # Direct translation with AUTO language detection
        logger.info(f"\nAuto-detecting language and translating to English...")
        translate_start = time.time()
        
        segments, info = model.transcribe(
            audio_path,
            task="translate",  # Direct translation
            language=None,  
            beam_size=5,
            vad_filter=True,
            vad_parameters={
                'min_silence_duration_ms': 500
            }
        )
        
        # Process segments
        translated_parts = []
        segment_count = 0
        total_duration = 0
        
        for segment in segments:
            translated_parts.append(segment.text)
            segment_count += 1
            total_duration = max(total_duration, segment.end)
            
            if segment_count % 20 == 0:
                logger.info(f"  Processed {segment_count} segments...")
        
        translate_time = time.time() - translate_start
        
        # Combine and deduplicate
        translated_text = " ".join(translated_parts)
        original_length = len(translated_text)
        translated_text = deduplicate_segments(translated_text)
        deduplicated_length = len(translated_text)
        
        # Calculate metrics
        results.update({
            'success': True,
            'translate_time': translate_time,
            'total_time': load_time + translate_time,
            'segment_count': segment_count,
            'audio_duration': total_duration,
            'rtf': translate_time / total_duration if total_duration > 0 else 0,  # Real-time factor
            'translated_text': translated_text,
            'text_length': len(translated_text),
            'word_count': len(translated_text.split()),
            'deduplication_ratio': (original_length - deduplicated_length) / original_length * 100 if original_length > 0 else 0,
            'detected_language': info.language,
            'language_probability': info.language_probability
        })
        
        # Evaluate translation quality if reference is provided
        if reference_text:
            logger.info(f"\nEvaluating translation quality against reference...")
            quality_scores = evaluate_translation_quality(translated_text, reference_text)
            results['quality_scores'] = quality_scores
            
            if quality_scores.get('bleu') is not None:
                logger.info(f"  - BLEU: {quality_scores['bleu']:.2f}")
                logger.info(f"  - CHRF: {quality_scores['chrf']:.2f}")
                logger.info(f"  - ROUGE-1: {quality_scores['rouge1']:.2f}")
                logger.info(f"  - ROUGE-2: {quality_scores['rouge2']:.2f}")
                logger.info(f"  - ROUGE-L: {quality_scores['rougeL']:.2f}")
            else:
                logger.warning(f"  - Quality metrics unavailable: {quality_scores.get('error', 'Unknown error')}")
        
        logger.info(f"\n✓ Translation completed:")
        logger.info(f"  - Detected language: {info.language} (confidence: {info.language_probability:.2%})")
        logger.info(f"  - Segments: {segment_count}")
        logger.info(f"  - Audio duration: {total_duration:.1f}s")
        logger.info(f"  - Translation time: {translate_time:.2f}s")
        logger.info(f"  - Real-time factor: {results['rtf']:.2f}x")
        logger.info(f"  - Words generated: {results['word_count']}")
        logger.info(f"  - Deduplication saved: {results['deduplication_ratio']:.1f}%")
        
        # Preview
        preview = translated_text[:200] + "..." if len(translated_text) > 200 else translated_text
        logger.info(f"\nPreview:\n{preview}\n")
        
    except Exception as e:
        logger.error(f"✗ Model test failed: {str(e)}")
        results['error'] = str(e)
        import traceback
        traceback.print_exc()
    
    return results

def calculate_translation_similarity(text1, text2):
    """
    Calculate simple word-level similarity between two translations
    (as a proxy for consistency)
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) * 100 if union else 0.0

def evaluate_translation_quality(hypothesis, reference):
    """
    Evaluate translation quality using multiple metrics
    
    Args:
        hypothesis: Generated translation text
        reference: Reference translation text (ground truth)
    
    Returns:
        dict with BLEU, METEOR, ROUGE scores
    """
    if not QUALITY_METRICS_AVAILABLE:
        return {
            'bleu': None,
            'chrf': None,
            'rouge1': None,
            'rouge2': None,
            'rougeL': None,
            'error': 'Quality metrics not installed'
        }
    
    if not hypothesis or not reference:
        return {
            'bleu': 0.0,
            'chrf': 0.0,
            'rouge1': 0.0,
            'rouge2': 0.0,
            'rougeL': 0.0
        }
    
    scores = {}
    
    try:
        # BLEU Score (sacrebleu)
        bleu = BLEU()
        # BLEU expects lists of references and hypotheses
        bleu_score = bleu.corpus_score([hypothesis], [[reference]])
        scores['bleu'] = bleu_score.score
        
        # CHRF Score (character-level F-score)
        chrf = CHRF()
        chrf_score = chrf.corpus_score([hypothesis], [[reference]])
        scores['chrf'] = chrf_score.score
        
        # ROUGE Scores
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_scores = scorer.score(reference, hypothesis)
        scores['rouge1'] = rouge_scores['rouge1'].fmeasure * 100
        scores['rouge2'] = rouge_scores['rouge2'].fmeasure * 100
        scores['rougeL'] = rouge_scores['rougeL'].fmeasure * 100
        
    except Exception as e:
        logging.warning(f"Error calculating quality metrics: {str(e)}")
        scores['error'] = str(e)
    
    return scores

def load_reference_translation(audio_path, reference_dir=None, reference_file=None):
    """
    Load reference translation for an audio file
    
    Supports multiple formats:
    1. Direct reference file path
    2. Reference directory with matching filenames
    3. JSON mapping file (audio_file -> reference_text)
    
    Args:
        audio_path: Path to audio file
        reference_dir: Directory containing reference translations
        reference_file: Direct path to reference translation file
    
    Returns:
        Reference translation text or None
    """
    if reference_file and os.path.exists(reference_file):
        try:
            with open(reference_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logging.warning(f"Error loading reference file {reference_file}: {e}")
    
    if reference_dir and os.path.exists(reference_dir):
        audio_basename = os.path.splitext(os.path.basename(audio_path))[0]
        
        # Try different extensions
        for ext in ['.txt', '.ref', '.reference']:
            ref_path = os.path.join(reference_dir, f"{audio_basename}{ext}")
            if os.path.exists(ref_path):
                try:
                    with open(ref_path, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except Exception as e:
                    logging.warning(f"Error loading reference {ref_path}: {e}")
        
        # Try JSON mapping file
        json_map = os.path.join(reference_dir, 'references.json')
        if os.path.exists(json_map):
            try:
                with open(json_map, 'r', encoding='utf-8') as f:
                    refs = json.load(f)
                    audio_key = os.path.basename(audio_path)
                    if audio_key in refs:
                        return refs[audio_key]
            except Exception as e:
                logging.warning(f"Error loading JSON mapping {json_map}: {e}")
    
    return None

def benchmark_all_models(audio_path, reference_text=None, reference_dir=None, reference_file=None):
    """
    Run benchmark on all models with auto language detection
    
    Args:
        audio_path: Path to audio file
        reference_text: Optional reference translation text
        reference_dir: Optional directory containing reference translations
        reference_file: Optional direct path to reference translation file
    
    Returns:
        List of results
    """
    logger = setup_logging()
    
    logger.info("="*80)
    logger.info("WHISPER MULTI-MODEL TRANSLATION BENCHMARK")
    logger.info("="*80)
    logger.info(f"\nAudio file: {audio_path}")
    logger.info(f"Language detection: AUTOMATIC")
    logger.info(f"Models to test: {', '.join(MODELS_TO_TEST.keys())}")
    logger.info(f"Model directory: {MODEL_DIR}\n")
    
    # Check if audio file exists
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return []
    
    # Load reference translation if not provided directly
    if not reference_text:
        reference_text = load_reference_translation(audio_path, reference_dir, reference_file)
    
    if reference_text:
        logger.info(f"✓ Reference translation loaded ({len(reference_text)} chars)")
        logger.info(f"  Preview: {reference_text[:100]}...\n")
    else:
        logger.info("⚠ No reference translation provided - quality metrics will not be calculated\n")
    
    all_results = []
    
    # Test each model
    for model_name, model_config in MODELS_TO_TEST.items():
        result = test_translation_model(
            model_name, 
            model_config, 
            audio_path,
            logger,
            reference_text=reference_text
        )
        all_results.append(result)
        
        # Small delay between models
        time.sleep(2)
    
    # Print comparison summary
    print_comparison_summary(all_results, logger)
    
    # Print quality comparison if references available
    if reference_text:
        print_quality_comparison(all_results, logger)
    
    # Calculate inter-model similarities
    print_similarity_analysis(all_results, logger)
    
    # Print language detection summary
    print_language_detection_summary(all_results, logger)
    
    return all_results

def print_comparison_summary(results, logger):
    """Print performance comparison table"""
    logger.info("\n" + "="*80)
    logger.info("PERFORMANCE COMPARISON")
    logger.info("="*80)
    
    # Create comparison table
    header = f"{'Model':<20} {'Load(s)':<10} {'Trans(s)':<10} {'Total(s)':<10} {'RTF':<8} {'Words':<8} {'Segs':<8}"
    logger.info(header)
    logger.info("-" * 80)
    
    successful_results = [r for r in results if r.get('success')]
    
    for result in successful_results:
        model = result['model']
        load_time = result.get('load_time', 0)
        trans_time = result.get('translate_time', 0)
        total_time = result.get('total_time', 0)
        rtf = result.get('rtf', 0)
        words = result.get('word_count', 0)
        segments = result.get('segment_count', 0)
        
        row = f"{model:<20} {load_time:<10.2f} {trans_time:<10.2f} {total_time:<10.2f} {rtf:<8.2f} {words:<8} {segments:<8}"
        logger.info(row)
    
    logger.info("="*80)
    
    # Highlight fastest and most efficient
    if successful_results:
        fastest = min(successful_results, key=lambda x: x.get('translate_time', float('inf')))
        logger.info(f"\n🏆 Fastest translation: {fastest['model']} ({fastest.get('translate_time', 0):.2f}s)")
        
        most_efficient = min(successful_results, key=lambda x: x.get('rtf', float('inf')))
        logger.info(f"⚡ Most efficient (RTF): {most_efficient['model']} ({most_efficient.get('rtf', 0):.2f}x)")

def print_similarity_analysis(results, logger):
    """Analyze translation consistency across models"""
    logger.info("\n" + "="*80)
    logger.info("TRANSLATION CONSISTENCY ANALYSIS")
    logger.info("="*80)
    
    successful_results = [r for r in results if r.get('success') and r.get('translated_text')]
    
    if len(successful_results) < 2:
        logger.info("Not enough successful translations to compare")
        return
    
    logger.info("\nWord overlap between model translations (%):\n")
    
    # Compare each pair
    model_names = [r['model'] for r in successful_results]
    
    # Header
    header = f"{'':20}"
    for name in model_names:
        header += f"{name:<15}"
    logger.info(header)
    logger.info("-" * (20 + 15 * len(model_names)))
    
    # Similarity matrix
    for i, result1 in enumerate(successful_results):
        row = f"{result1['model']:<20}"
        for j, result2 in enumerate(successful_results):
            if i == j:
                row += f"{'100.0':<15}"
            elif i < j:
                similarity = calculate_translation_similarity(
                    result1['translated_text'],
                    result2['translated_text']
                )
                row += f"{similarity:<15.1f}"
            else:
                row += f"{'':<15}"
        logger.info(row)
    
    logger.info("\nNote: Higher values indicate more similar translations (word overlap)")
    logger.info("="*80)

def print_quality_comparison(results, logger):
    """Print translation quality metrics comparison"""
    logger.info("\n" + "="*80)
    logger.info("TRANSLATION QUALITY COMPARISON")
    logger.info("="*80)
    
    successful_results = [r for r in results if r.get('success') and r.get('quality_scores')]
    
    if not successful_results:
        logger.info("No quality metrics available (reference translation not provided)")
        return
    
    # Header
    header = f"{'Model':<20} {'BLEU':<10} {'CHRF':<10} {'ROUGE-1':<10} {'ROUGE-2':<10} {'ROUGE-L':<10}"
    logger.info(f"\n{header}")
    logger.info("-" * 80)
    
    for result in successful_results:
        model = result['model']
        scores = result.get('quality_scores', {})
        
        bleu = scores.get('bleu', 0) if scores.get('bleu') is not None else 'N/A'
        chrf = scores.get('chrf', 0) if scores.get('chrf') is not None else 'N/A'
        r1 = scores.get('rouge1', 0) if scores.get('rouge1') is not None else 'N/A'
        r2 = scores.get('rouge2', 0) if scores.get('rouge2') is not None else 'N/A'
        rl = scores.get('rougeL', 0) if scores.get('rougeL') is not None else 'N/A'
        
        if isinstance(bleu, (int, float)):
            row = f"{model:<20} {bleu:<10.2f} {chrf:<10.2f} {r1:<10.2f} {r2:<10.2f} {rl:<10.2f}"
        else:
            row = f"{model:<20} {str(bleu):<10} {str(chrf):<10} {str(r1):<10} {str(r2):<10} {str(rl):<10}"
        logger.info(row)
    
    logger.info("="*80)
    
    # Highlight best performing models
    if successful_results:
        # Find best BLEU
        best_bleu = max(
            [(r, r.get('quality_scores', {}).get('bleu', 0)) 
             for r in successful_results 
             if r.get('quality_scores', {}).get('bleu') is not None],
            key=lambda x: x[1],
            default=(None, None)
        )
        if best_bleu[0]:
            logger.info(f"\n🏆 Best BLEU score: {best_bleu[0]['model']} ({best_bleu[1]:.2f})")
        
        # Find best ROUGE-L
        best_rouge = max(
            [(r, r.get('quality_scores', {}).get('rougeL', 0)) 
             for r in successful_results 
             if r.get('quality_scores', {}).get('rougeL') is not None],
            key=lambda x: x[1],
            default=(None, None)
        )
        if best_rouge[0]:
            logger.info(f"⭐ Best ROUGE-L score: {best_rouge[0]['model']} ({best_rouge[1]:.2f})")
    
    logger.info("\nNote: Higher scores indicate better translation quality")
    logger.info("="*80)

def print_language_detection_summary(results, logger):
    """Print summary of detected languages across models"""
    logger.info("\n" + "="*80)
    logger.info("LANGUAGE DETECTION SUMMARY")
    logger.info("="*80)
    
    successful_results = [r for r in results if r.get('success')]
    
    if not successful_results:
        logger.info("No successful translations to analyze")
        return
    
    logger.info(f"\n{'Model':<20} {'Detected Lang':<15} {'Confidence':<12}")
    logger.info("-" * 80)
    
    for result in successful_results:
        model = result['model']
        lang = result.get('detected_language', 'N/A')
        prob = result.get('language_probability', 0)
        
        logger.info(f"{model:<20} {lang:<15} {prob:<12.2%}")
    
    # Check if all models detected the same language
    languages = [r.get('detected_language') for r in successful_results]
    unique_langs = set(languages)
    
    if len(unique_langs) == 1:
        logger.info(f"\n✓ All models consistently detected: {languages[0]}")
    else:
        logger.info(f"\n⚠ Models detected different languages: {', '.join(unique_langs)}")
    
    logger.info("="*80)

def save_results(results, output_dir='benchmark_results'):
    """Save results to JSON and text files"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_path = os.path.join(output_dir, f'benchmark_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save individual translations
    for result in results:
        if result.get('success') and result.get('translated_text'):
            txt_path = os.path.join(
                output_dir, 
                f"{result['model']}_{timestamp}.txt"
            )
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(result['translated_text'])
    
    print(f"\n✓ Results saved to: {output_dir}/")
    return json_path

if __name__ == "__main__":
    # Configuration
    AUDIO_FILE = "test_audio.mp3"  # Update this path
    REFERENCE_DIR = "references"  # Directory containing reference translations
    REFERENCE_FILE = None  # Or specify direct path: "references/test_audio.txt"
    
    print("\n" + "="*80)
    print("WHISPER TRANSLATION BENCHMARK (AUTO LANGUAGE DETECTION)")
    print("="*80)
    print(f"\nAudio file: {AUDIO_FILE}")
    print(f"Language detection: AUTOMATIC")
    print(f"\nModels to test:")
    for i, model in enumerate(MODELS_TO_TEST.keys(), 1):
        print(f"  {i}. {model}")
    
    if REFERENCE_DIR or REFERENCE_FILE:
        print(f"\nReference translation: {'Directory' if REFERENCE_DIR else 'File'}")
        if REFERENCE_DIR:
            print(f"  Directory: {REFERENCE_DIR}")
        if REFERENCE_FILE:
            print(f"  File: {REFERENCE_FILE}")
        print("  ✓ Quality metrics will be calculated")
    else:
        print("\n⚠ No reference translation provided - quality metrics will be skipped")
        print("  To enable quality evaluation, set REFERENCE_DIR or REFERENCE_FILE")
    
    if not QUALITY_METRICS_AVAILABLE:
        print("\n⚠ Quality metrics libraries not installed!")
        print("  Install with: pip install sacrebleu rouge-score")
        print("  Quality evaluation will be skipped.")
    
    input("\nPress Enter to start benchmark...")
    
    # Run benchmark
    results = benchmark_all_models(
        AUDIO_FILE,
        reference_dir=REFERENCE_DIR,
        reference_file=REFERENCE_FILE
    )
    
    # Save results
    if results:
        save_results(results)
        print("\n✓ Benchmark complete!")
    else:
        print("\n✗ Benchmark failed - check logs for details")