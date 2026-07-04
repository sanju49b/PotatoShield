import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { question, context } = await request.json()

    // Validate input
    if (!question || !context) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Get API key from environment (server-side only)
    const apiKey = process.env.OPENAI_API_KEY

    if (!apiKey) {
      console.error('[AI Advisor] OPENAI_API_KEY not found in environment')
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      )
    }

    // Build context-rich prompt
    const contextPrompt = `You are an expert agricultural AI assistant specializing in potato crop health management.

**Current Field Context:**
- Location: ${context.location}
- Date of Sowing: ${context.sowingDate}
- Growth Stage: ${context.growthStage}
- Days After Planting: ${context.daysAfterPlanting}
- Late Blight Risk: ${context.currentRisks?.late_blight || 0}%
- Early Blight Risk: ${context.currentRisks?.early_blight || 0}%
- Overall Risk: ${context.currentRisks?.overall || 0}%

**Your role:**
- Provide specific, actionable advice based on the farmer's current situation
- Explain technical concepts in simple terms
- Give time-sensitive recommendations (what to do today/this week)
- Be encouraging and supportive
- Keep responses concise (2-3 paragraphs max)

**User Question:** ${question}`

    // Call OpenAI API
    console.log('[AI Advisor] Calling OpenAI API...')
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are an expert agricultural AI assistant specializing in potato crop health, disease management, and sustainable farming practices. Provide practical, actionable advice.'
          },
          {
            role: 'user',
            content: contextPrompt
          }
        ],
        temperature: 0.7,
        max_tokens: 500
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('[AI Advisor] OpenAI API error:', response.status, errorText)
      return NextResponse.json(
        { error: `OpenAI API error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    const aiResponse = data.choices[0]?.message?.content || 'I apologize, but I couldn\'t generate a response. Please try again.'

    console.log('[AI Advisor] Response generated successfully')
    return NextResponse.json({ response: aiResponse })

  } catch (error: any) {
    console.error('[AI Advisor] Error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}

