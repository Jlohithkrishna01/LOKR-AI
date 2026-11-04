import React from 'react';
import { FileText, Image as ImageIcon, FileSpreadsheet, FileCode, X, Loader2 } from 'lucide-react';
import { UploadedFileInfo } from '../../types';

interface FilePreviewChipProps {
  fileInfo: UploadedFileInfo | null;
  isLoading?: boolean;
  onRemove?: () => void;
  className?: string;
}

export const FilePreviewChip: React.FC<FilePreviewChipProps> = ({
  fileInfo,
  isLoading = false,
  onRemove,
  className = '',
}) => {
  if (!fileInfo && !isLoading) return null;

  const getIcon = (type?: string) => {
    const t = (type || '').toLowerCase();
    if (t.includes('pdf')) return <FileText className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
    if (t.includes('doc')) return <FileText className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
    if (t.includes('csv') || t.includes('xls')) return <FileSpreadsheet className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
    if (['png', 'jpg', 'jpeg', 'webp', 'gif'].includes(t)) return <ImageIcon className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
    return <FileCode className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />;
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-neutral-100 dark:bg-[#262626] text-xs text-neutral-800 dark:text-neutral-200 shadow-sm animate-in fade-in duration-150 ${className}`}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-neutral-500" />
      ) : (
        getIcon(fileInfo?.file_type)
      )}

      <div className="flex flex-col max-w-[180px] sm:max-w-[240px]">
        <span className="font-medium truncate">{fileInfo?.file_name || 'Uploading file...'}</span>
        {fileInfo?.file_size ? (
          <span className="text-[10px] text-neutral-400 dark:text-neutral-500">{formatSize(fileInfo.file_size)}</span>
        ) : null}
      </div>

      {onRemove && !isLoading && (
        <button
          onClick={onRemove}
          type="button"
          className="ml-1 p-0.5 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-700 text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 transition-colors"
          title="Remove file"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
