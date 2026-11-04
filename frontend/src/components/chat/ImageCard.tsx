import React, { useState, useEffect, useRef } from 'react';
import { Download, Maximize2, Copy, Check, Sparkles, X, ExternalLink, RefreshCw } from 'lucide-react';
import { copyToClipboard } from '../../utils/clipboard';

interface ImageCardProps {
  src: string;
  alt?: string;
  prompt?: string;
  className?: string;
}

export const ImageCard: React.FC<ImageCardProps> = ({
  src,
  alt = 'AI Generated Image',
  prompt,
  className = '',
}) => {
  const getFullSrc = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    if (url.startsWith('/')) return `${window.location.origin}${url}`;
    return `${window.location.origin}/${url}`;
  };

  const [currentSrc, setCurrentSrc] = useState<string>(() => getFullSrc(src));
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    setCurrentSrc(getFullSrc(src));
    setIsLoaded(false);
    setHasError(false);
  }, [src]);

  useEffect(() => {
    if (imgRef.current && imgRef.current.complete && imgRef.current.naturalWidth > 0) {
      setIsLoaded(true);
      setHasError(false);
    }
  }, [currentSrc]);

  const cleanPrompt = prompt || alt || 'AI Image';

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await fetch(currentSrc);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `lokr-ai-${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      const link = document.createElement('a');
      link.href = currentSrc;
      link.target = '_blank';
      link.download = 'lokr-image.jpg';
      link.click();
    }
  };

  const handleCopyUrl = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const success = await copyToClipboard(currentSrc);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleImageError = () => {
    if (currentSrc.includes(':5173/uploads/')) {
      const directBackendUrl = currentSrc.replace(':5173/uploads/', ':8000/uploads/');
      setCurrentSrc(directBackendUrl);
      return;
    }
    setHasError(true);
  };

  return (
    <>
      <div
        className={`group relative my-3 max-w-lg rounded-2xl overflow-hidden border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#181818] shadow-md transition-all duration-300 hover:shadow-lg ${className}`}
      >
        {/* Error Fallback */}
        {hasError ? (
          <div className="w-full p-6 text-center text-xs bg-rose-50/20 dark:bg-rose-950/20 border border-rose-500/20 rounded-2xl">
            <p className="font-semibold text-rose-500 mb-1">Could not display generated image</p>
            <p className="text-neutral-400 text-[11px] mb-3">The image service may still be generating or unreachable.</p>
            <div className="flex items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => {
                  setHasError(false);
                  setIsLoaded(false);
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-black text-white dark:bg-white dark:text-black font-medium transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry</span>
              </button>
              <a
                href={currentSrc}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 font-medium transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Open Link</span>
              </a>
            </div>
          </div>
        ) : (
          <div
            className="relative cursor-pointer overflow-hidden min-h-[260px] flex items-center justify-center bg-neutral-100 dark:bg-[#141414]"
            onClick={() => isLoaded && setIsLightboxOpen(true)}
          >
            {/* Loading Skeleton */}
            {!isLoaded && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-neutral-100 dark:bg-[#141414] animate-pulse text-neutral-400 select-none pointer-events-none">
                <Sparkles className="w-7 h-7 mb-2 animate-spin text-neutral-500" />
                <span className="text-xs font-medium select-none">Loading image...</span>
              </div>
            )}

            <img
              ref={imgRef}
              src={currentSrc}
              alt={cleanPrompt}
              onLoad={() => {
                setIsLoaded(true);
                setHasError(false);
              }}
              onError={handleImageError}
              className={`w-full h-auto object-cover transition-opacity duration-300 ${
                isLoaded ? 'opacity-100' : 'opacity-0'
              }`}
            />

            {/* Hover Actions Toolbar Overlay */}
            {isLoaded && (
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex flex-col justify-between p-3">
                {/* Top buttons */}
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-black/70 text-white backdrop-blur-md">
                    <Sparkles className="w-3 h-3 text-neutral-300" />
                    <span>AI Generated</span>
                  </span>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={handleCopyUrl}
                      type="button"
                      className="p-1.5 rounded-lg bg-black/60 hover:bg-black/90 text-white backdrop-blur-md transition-colors"
                      title="Copy image link"
                    >
                      {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={handleDownload}
                      type="button"
                      className="p-1.5 rounded-lg bg-black/60 hover:bg-black/90 text-white backdrop-blur-md transition-colors"
                      title="Download image"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsLightboxOpen(true);
                      }}
                      type="button"
                      className="p-1.5 rounded-lg bg-black/60 hover:bg-black/90 text-white backdrop-blur-md transition-colors"
                      title="Fullscreen view"
                    >
                      <Maximize2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Bottom Prompt Pill */}
                {cleanPrompt && (
                  <div className="p-2.5 rounded-xl bg-black/70 backdrop-blur-md text-white text-xs line-clamp-2">
                    <span className="font-semibold text-neutral-300">Prompt: </span>
                    <span className="text-neutral-200">{cleanPrompt}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Lightbox Fullscreen Modal */}
      {isLightboxOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in duration-200"
          onClick={() => setIsLightboxOpen(false)}
        >
          <div
            className="relative max-w-4xl max-h-[90vh] flex flex-col items-center"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top Close / Download Header */}
            <div className="w-full flex items-center justify-between mb-2 text-white px-2">
              <span className="text-xs font-medium text-neutral-300 truncate max-w-md">
                {cleanPrompt}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/20 hover:bg-white/30 text-white text-xs font-semibold backdrop-blur-md transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </button>
                <a
                  href={currentSrc}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-xl bg-white/20 hover:bg-white/30 text-white transition-colors"
                  title="Open original in new tab"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
                <button
                  onClick={() => setIsLightboxOpen(false)}
                  className="p-1.5 rounded-xl bg-white/20 hover:bg-white/30 text-white transition-colors"
                  title="Close lightbox"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Fullscreen Image */}
            <img
              src={currentSrc}
              alt={cleanPrompt}
              className="max-h-[80vh] w-auto max-w-full rounded-2xl shadow-2xl object-contain border border-white/10"
            />
          </div>
        </div>
      )}
    </>
  );
};
