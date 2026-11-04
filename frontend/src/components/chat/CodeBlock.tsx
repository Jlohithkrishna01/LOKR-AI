import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTheme } from '../../context/ThemeContext';
import { copyToClipboard } from '../../utils/clipboard';

interface CodeBlockProps {
  language: string;
  value: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, value }) => {
  const [copied, setCopied] = useState(false);
  const { isDark } = useTheme();

  const handleCopy = async (e: React.MouseEvent | React.TouchEvent) => {
    e.stopPropagation();
    const success = await copyToClipboard(value);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const detectedLang = language || 'text';

  return (
    <div className={`relative my-4 rounded-xl overflow-hidden border shadow-sm ${
      isDark
        ? 'border-neutral-800 bg-[#141414]'
        : 'border-neutral-200 bg-[#f8f9fa]'
    }`}>
      {/* Code Header Bar */}
      <div className={`flex items-center justify-between px-4 py-2 border-b text-xs ${
        isDark
          ? 'bg-[#1b1b1b] border-neutral-800 text-neutral-400'
          : 'bg-[#f0f2f5] border-neutral-200 text-neutral-600'
      }`}>
        <span className="font-mono font-medium lowercase tracking-wide">
          {detectedLang}
        </span>
        <button
          onClick={handleCopy}
          type="button"
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer select-none ${
            isDark
              ? 'text-neutral-300 hover:text-white bg-neutral-800/80 hover:bg-neutral-700'
              : 'text-neutral-700 hover:text-neutral-900 bg-neutral-200/80 hover:bg-neutral-300/80'
          }`}
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-emerald-500 font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy code</span>
            </>
          )}
        </button>
      </div>

      {/* Code Syntax Display */}
      <div className="text-sm font-mono overflow-x-auto p-1">
        <SyntaxHighlighter
          language={detectedLang}
          style={isDark ? vscDarkPlus : prism}
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: 'transparent',
            fontSize: '0.875rem',
            lineHeight: 1.6,
          }}
          wrapLines={true}
          wrapLongLines={true}
        >
          {value}
        </SyntaxHighlighter>
      </div>
    </div>
  );
};
