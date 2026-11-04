import React from 'react';
import { ExternalLink, Globe } from 'lucide-react';
import { Source } from '../../types';

interface SourceCardProps {
  source: Source;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex flex-col justify-between p-3 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/80 dark:bg-[#181818] hover:bg-white dark:hover:bg-[#202020] hover:border-neutral-300 dark:hover:border-neutral-700 transition-colors shadow-sm text-left"
    >
      <div>
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-1.5 text-xs font-medium text-neutral-600 dark:text-neutral-400 truncate">
            <Globe className="w-3.5 h-3.5 shrink-0 text-neutral-500" />
            <span className="truncate">{source.source_name || 'Web Source'}</span>
          </div>
          <ExternalLink className="w-3.5 h-3.5 text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-white shrink-0 transition-colors" />
        </div>
        <h4 className="text-xs font-semibold text-neutral-900 dark:text-neutral-100 line-clamp-2 leading-snug">
          {source.title}
        </h4>
      </div>

      {source.snippet && (
        <p className="mt-2 text-[11px] text-neutral-500 dark:text-neutral-400 line-clamp-2 leading-relaxed">
          {source.snippet}
        </p>
      )}
    </a>
  );
};
