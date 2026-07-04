'use client'

import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownRendererProps {
  content: string
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Headings
        h1: ({ node, ...props }) => (
          <h1 className="text-2xl font-bold text-[#e8e8e8] mb-4 mt-6" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-xl font-semibold text-[#e8e8e8] mb-3 mt-5" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-lg font-semibold text-[#d8d8d8] mb-2 mt-4" {...props} />
        ),
        h4: ({ node, ...props }) => (
          <h4 className="text-base font-semibold text-[#d8d8d8] mb-2 mt-3" {...props} />
        ),
        
        // Paragraphs
        p: ({ node, ...props }) => (
          <p className="mb-3 leading-relaxed text-[#e8e8e8]" {...props} />
        ),
        
        // Bold text
        strong: ({ node, ...props }) => (
          <strong className="font-bold text-[#f8f8f8]" {...props} />
        ),
        
        // Italic text
        em: ({ node, ...props }) => (
          <em className="italic text-[#d8d8d8]" {...props} />
        ),
        
        // Lists
        ul: ({ node, ...props }) => (
          <ul className="list-disc list-inside mb-3 space-y-1 text-[#e8e8e8]" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal list-inside mb-3 space-y-1 text-[#e8e8e8]" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="ml-4 text-[#e8e8e8]" {...props} />
        ),
        
        // Code
        code: ({ node, inline, ...props }: any) =>
          inline ? (
            <code
              className="bg-[#3a3a3a] text-orange-400 px-1.5 py-0.5 rounded text-sm font-mono"
              {...props}
            />
          ) : (
            <code
              className="block bg-[#2a2a2a] text-[#e8e8e8] p-3 rounded-lg mb-3 overflow-x-auto font-mono text-sm"
              {...props}
            />
          ),
        
        // Blockquotes
        blockquote: ({ node, ...props }) => (
          <blockquote
            className="border-l-4 border-orange-500 pl-4 italic text-[#c8c8c8] mb-3"
            {...props}
          />
        ),
        
        // Links
        a: ({ node, ...props }) => (
          <a
            className="text-orange-400 hover:text-orange-300 underline"
            target="_blank"
            rel="noopener noreferrer"
            {...props}
          />
        ),
        
        // Horizontal rule
        hr: ({ node, ...props }) => (
          <hr className="border-t border-[#3a3a3a] my-4" {...props} />
        ),
        
        // Tables
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto mb-4">
            <table className="min-w-full border border-[#3a3a3a]" {...props} />
          </div>
        ),
        th: ({ node, ...props }) => (
          <th className="border border-[#3a3a3a] px-4 py-2 bg-[#2a2a2a] text-[#e8e8e8] font-semibold" {...props} />
        ),
        td: ({ node, ...props }) => (
          <td className="border border-[#3a3a3a] px-4 py-2 text-[#d8d8d8]" {...props} />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

