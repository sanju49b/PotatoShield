# Potato Shield – Architecture Diagram Export

This folder contains the **full system architecture** (RAI, agents, models, algorithms, storage, external services) in two formats. Use either method below to get a **PNG** for slides or posters.

---

## Option 1: HTML → PNG (recommended)

1. Open **`potato-shield-architecture.html`** in Chrome or Edge.
2. Zoom so the whole diagram fits (e.g. 80% or 100%).
3. Capture the diagram:
   - **Windows:** `Win + Shift + S` (Snipping Tool) and select the diagram area, then save as PNG.
   - Or: **Ctrl + P** → “Save as PDF” → open PDF and export the page as PNG.

---

## Option 2: Mermaid → PNG

1. Go to **[mermaid.live](https://mermaid.live)**.
2. Open **`potato-shield-architecture.mmd`** in a text editor and copy all content.
3. Paste into the Mermaid Live Editor left panel.
4. Use **Actions → PNG** (or **SVG**) to download the diagram.
5. Optional: adjust the **theme** (e.g. dark) in the editor.

If you use Node.js and want CLI export:

```bash
npx @mermaid-js/mermaid-cli mmdc -i potato-shield-architecture.mmd -o potato-shield-architecture.png -b transparent -w 1600
```

---

## What the diagram includes

- **User & presentation:** User, Next.js frontend, Chat UI, Dashboard  
- **API & RAI:** FastAPI, RAI middleware, local guard, RAI client  
- **Infosys RAI Toolkit:** Moderation, Privacy, Hallucination, Safety, Fairness, Explainability  
- **Agents (LangGraph):** Load context, Router, Data collection, Predictive, Blight prediction, Diagnostic, General chat, Save conversation  
- **Models & algorithms:** Disease classifier (ML), Rule engine, Sliding window, Hutton criteria, Infection periods, Persistence/cumulative, LLMs  
- **Memory & storage:** Short-term, Long-term, DynamoDB, SQLite  
- **External services:** Open-Meteo, Tavily, OpenAI, AWS SES, Infosys RAI backend  

Use the PNG in your competition slide or poster as the main system-structure diagram.
