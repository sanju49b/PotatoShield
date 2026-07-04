'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

interface MLValidation {
  validated: boolean
  adjustment_made: boolean
  disagreement_score: number
  ml_prediction: {
    disease: string
    confidence: number
    late_blight: number
    early_blight: number
  }
  model_accuracy?: number
  model_metrics?: {
    accuracy: number
    precision: number
    recall: number
    f1_score: number
    training_samples: number
    test_samples: number
  }
  recommendation: string
}

interface DiseaseRiskSummaryProps {
  lateBlightRisk: number
  earlyBlightRisk: number
  mlValidation?: MLValidation
  onExplain?: (type: 'late' | 'early' | 'overall') => void
}

export default function DiseaseRiskSummary({ lateBlightRisk, earlyBlightRisk, mlValidation, onExplain }: DiseaseRiskSummaryProps) {
  // Determine which disease has the highest risk
  const highestRisk = Math.max(lateBlightRisk, earlyBlightRisk)
  const isLateBlightHighest = lateBlightRisk >= earlyBlightRisk
  const dominantDisease = isLateBlightHighest ? 'late' : 'early'
  const dominantRisk = isLateBlightHighest ? lateBlightRisk : earlyBlightRisk

  const getRiskColor = (risk: number) => {
    if (risk > 75) return 'from-red-600 to-red-800'
    if (risk > 50) return 'from-orange-500 to-orange-700'
    if (risk > 25) return 'from-yellow-500 to-yellow-700'
    return 'from-green-500 to-green-700'
  }

  const getRiskLabel = (risk: number) => {
    if (risk > 75) return 'Critical'
    if (risk > 50) return 'High'
    if (risk > 25) return 'Moderate'
    return 'Low'
  }

  const getRecommendation = (risk: number, type: 'late' | 'early') => {
    if (risk > 75) {
      return type === 'late' 
        ? 'Apply Mancozeb 2.5 kg/ha immediately. Monitor daily.'
        : 'Apply preventive fungicide. Check lower leaves.'
    }
    if (risk > 50) {
      return 'Monitor closely. Prepare fungicide application.'
    }
    if (risk > 25) {
      return 'Continue regular monitoring. Maintain field hygiene.'
    }
    return 'Low risk. Continue standard practices.'
  }

  return (
    <section className="w-full">
      {/* Contextual header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-[#e8e8e8] mb-2">Disease Risk Assessment</h2>
        <p className="text-[#b8b8b8] text-sm max-w-2xl mx-auto">
          Based on current weather conditions, soil moisture levels, and historical outbreak patterns, 
          our AI model has calculated the primary disease risk for your field. The assessment below 
          represents the most significant threat requiring immediate attention.
        </p>
      </div>

      {/* Main risk card */}
      <div className="flex justify-center mb-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className={`bg-gradient-to-br ${getRiskColor(dominantRisk)} rounded-2xl p-8 shadow-2xl border-2 max-w-md w-full ${
            dominantRisk > 75 ? 'border-red-400' : dominantRisk > 50 ? 'border-orange-400' : 'border-yellow-400'
          }`}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              {isLateBlightHighest ? '🔴' : '🟡'} {isLateBlightHighest ? 'Late Blight' : 'Early Blight'} Risk
            </h3>
            <button
              aria-label={`Explain ${isLateBlightHighest ? 'Late' : 'Early'} Blight prediction`}
              title="Get AI explanation"
              onClick={() => onExplain && onExplain(dominantDisease)}
              className="text-white/90 hover:text-white bg-white/10 hover:bg-white/20 border border-white/20 rounded-full px-3 py-1.5 text-xs font-medium transition-all hover:scale-105"
            >
              🤖 Explain
            </button>
          </div>
          <div className="text-7xl font-black text-white mb-3 text-center">{Math.round(dominantRisk)}%</div>
          <div className="text-white/90 text-lg mb-4 text-center font-semibold">{getRiskLabel(dominantRisk)} Risk</div>
          <p className="text-white/90 text-base mb-6 text-center leading-relaxed">{getRecommendation(dominantRisk, dominantDisease)}</p>
          <div className="text-center">
            <Link href="#recommendations" className="text-white underline text-sm hover:text-white/80 font-medium">
              View detailed recommendations →
            </Link>
          </div>
          {/* Show comparison info */}
          <div className="mt-6 pt-6 border-t border-white/20 text-center">
            <p className="text-white/70 text-xs mb-1">Secondary Risk Assessment</p>
            <p className="text-white/80 text-sm font-medium">
              {isLateBlightHighest 
                ? `Early Blight: ${Math.round(earlyBlightRisk)}%`
                : `Late Blight: ${Math.round(lateBlightRisk)}%`
              }
            </p>
          </div>
        </motion.div>
      </div>

      {/* Secondary ML Engine Validation */}
      {mlValidation && mlValidation.validated && (
        <div className="mt-8 bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-blue-300 flex items-center gap-2">
              🤖 Secondary ML Engine Validation
            </h3>
            {mlValidation.model_accuracy && (
              <div className="bg-blue-500/20 border border-blue-400/30 rounded-lg px-3 py-1.5">
                <span className="text-blue-200 text-xs font-semibold">
                  Model Accuracy: {(mlValidation.model_accuracy * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-black/20 rounded-lg p-4 border border-blue-400/20">
              <p className="text-blue-200 text-xs mb-2 font-medium">ML Prediction</p>
              <p className="text-white text-lg font-bold">
                {mlValidation.ml_prediction.disease}
              </p>
              <p className="text-blue-300 text-sm mt-1">
                Confidence: {(mlValidation.ml_prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
            
            <div className="bg-black/20 rounded-lg p-4 border border-blue-400/20">
              <p className="text-blue-200 text-xs mb-2 font-medium">ML Risk Percentages</p>
              <div className="flex justify-between text-sm">
                <span className="text-white">
                  Late Blight: <span className="font-bold">{mlValidation.ml_prediction.late_blight.toFixed(1)}%</span>
                </span>
                <span className="text-white">
                  Early Blight: <span className="font-bold">{mlValidation.ml_prediction.early_blight.toFixed(1)}%</span>
                </span>
              </div>
            </div>
          </div>
          
          {mlValidation.adjustment_made && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
              <p className="text-yellow-300 text-xs font-medium mb-1">⚠️ Prediction Adjusted</p>
              <p className="text-yellow-200 text-xs">
                Disagreement detected ({mlValidation.disagreement_score.toFixed(1)}%). 
                Predictions were adjusted using weighted average (60% primary, 40% ML).
              </p>
            </div>
          )}
          
          {mlValidation.model_metrics && (
            <div className="bg-black/20 rounded-lg p-3 border border-blue-400/20">
              <p className="text-blue-200 text-xs mb-2 font-medium">Model Performance Metrics</p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-blue-300">Precision:</span>
                  <span className="text-white ml-2">{(mlValidation.model_metrics.precision * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-blue-300">Recall:</span>
                  <span className="text-white ml-2">{(mlValidation.model_metrics.recall * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-blue-300">F1 Score:</span>
                  <span className="text-white ml-2">{(mlValidation.model_metrics.f1_score * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-blue-300">Training Samples:</span>
                  <span className="text-white ml-2">{mlValidation.model_metrics.training_samples}</span>
                </div>
              </div>
            </div>
          )}
          
          <p className="text-blue-200 text-xs mt-4 italic">
            {mlValidation.recommendation}
          </p>
        </div>
      )}

      {/* Additional context */}
      <div className="text-center mt-6 space-y-2">
        <p className="text-[#808080] text-xs max-w-xl mx-auto">
          This risk assessment uses a <strong className="text-purple-300">sliding window algorithm</strong> that considers weather trends across a 7-day period for each forecast day, 
          ensuring more stable and context-aware predictions. Updated in real-time based on weather forecasts and environmental conditions.
        </p>
        {mlValidation && mlValidation.validated && (
          <p className="text-[#808080] text-xs max-w-xl mx-auto">
            <strong className="text-blue-300">Secondary ML Engine:</strong> A RandomForest classifier trained on historical disease data validates predictions for consistency. 
            Model accuracy: <strong>{(mlValidation.model_accuracy! * 100).toFixed(1)}%</strong>.
          </p>
        )}
        <p className="text-[#808080] text-xs max-w-xl mx-auto">
          Monitor your field regularly and follow the recommendations above to protect your crop.
        </p>
      </div>
    </section>
  )
}

