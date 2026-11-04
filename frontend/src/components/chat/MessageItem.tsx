import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Copy,
  Check,
  RotateCw,
  ThumbsUp,
  ThumbsDown,
  FileText,
  Globe,
} from 'lucide-react';
import { Message } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { Avatar } from '../common/Avatar';
import { CodeBlock } from './CodeBlock';
import { SourceCard } from './SourceCard';
import { ImageCard } from './ImageCard';
import { copyToClipboard } from '../../utils/clipboard';

interface MessageItemProps {
  message: Message;
  isLastAssistant?: boolean;
  onRegenerate?: () => void;
  showTimestamp?: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  isLastAssistant = false,
  onRegenerate,
  showTimestamp = true,
}) => {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'liked' | 'disliked' | null>(null);

  const isUser = message.role === 'user';

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatTime = (isoString?: string) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="w-full my-4">
      {isUser ? (
        /* User Message (ChatGPT right-aligned bubble style) */
        <div className="flex justify-end items-end gap-2.5 max-w-3xl lg:max-w-4xl mx-auto">
          <div className="flex flex-col items-end max-w-[85%] sm:max-w-[75%]">
            {showTimestamp && (
              <span className="text-[11px] text-neutral-400 dark:text-neutral-500 mb-1 px-1">
                {formatTime(message.created_at)}
              </span>
            )}

            <div className="rounded-2xl sm:rounded-3xl px-4 py-2.5 sm:px-5 sm:py-3.5 bg-light-card dark:bg-dark-card border border-neutral-200/80 dark:border-neutral-800 text-neutral-900 dark:text-neutral-100 shadow-sm">
              {/* Attached File Preview */}
              {message.file_name && (
                <div className="mb-2 inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white/80 dark:bg-black/30 text-xs text-neutral-800 dark:text-neutral-200">
                  <FileText className="w-3.5 h-3.5 text-neutral-600 dark:text-neutral-400" />
                  <span className="font-medium truncate max-w-[220px]">{message.file_name}</span>
                </div>
              )}

              <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words font-normal">
                {message.content}
              </p>
            </div>
          </div>

          <Avatar
            src={user?.profile_image}
            name={user?.name || 'User'}
            size="sm"
            className="mb-1 shrink-0 ring-1 ring-neutral-300 dark:ring-neutral-700"
          />
        </div>
      ) : (
        /* Assistant Message (ChatGPT clean transparent left-aligned area) */
        <div className="flex items-start gap-3 sm:gap-4 max-w-3xl lg:max-w-4xl mx-auto group">
          {/* LOKR AI Emblem Avatar */}
          <div className="shrink-0 mt-0.5">
            <div className="w-8 h-8 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center shadow-sm">
              <svg viewBox="180 115 660 660" fill="none" className="w-[62%] h-[62%]" stroke="none">
                <path
                  d="M 539 598 L 518 619 L 550 651 L 552 651 L 571 632 L 571 630 Z M 484 469 L 382 565 L 382 626 L 511 752 L 641 626 L 641 565 L 609 534 L 588 556 L 609 577 L 609 611 L 511 707 L 415 612 L 415 578 L 504 489 Z M 620 467 L 611 474 L 533 549 L 453 629 L 472 648 L 474 648 L 481 642 L 533 590 L 640 487 Z M 341 462 L 312 491 L 333 511 L 361 482 Z M 476 396 L 454 418 L 511 477 L 550 515 L 571 494 Z M 609 391 L 587 413 L 689 514 L 710 492 Z M 659 424 L 681 445 L 715 411 L 694 390 Z M 328 391 L 310 409 L 310 411 L 414 517 L 416 517 L 437 496 L 332 389 Z M 671 298 L 671 347 L 773 448 L 664 560 L 664 622 L 698 655 L 709 664 L 731 641 L 694 605 L 694 577 L 817 453 L 821 447 Z M 559 254 L 511 300 L 464 254 L 442 276 L 473 307 L 488 324 L 386 425 L 408 446 L 547 311 L 581 276 Z M 317 229 L 291 254 L 326 288 L 326 325 L 202 448 L 358 604 L 358 559 L 250 448 L 358 342 L 358 268 Z M 512 133 L 455 189 L 381 266 L 381 342 L 415 376 L 437 355 L 437 353 L 413 329 L 413 281 L 511 182 L 609 281 L 609 329 L 519 420 L 519 422 L 540 442 L 643 341 L 643 267 Z"
                  fill="currentColor"
                  fillRule="evenodd"
                />
              </svg>
            </div>
          </div>

          <div className="flex-1 min-w-0">
            {/* Header: Name & Timestamp */}
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold text-xs sm:text-sm text-neutral-900 dark:text-white">
                LOKR AI
              </span>
              {showTimestamp && (
                <span className="text-[11px] text-neutral-400 dark:text-neutral-500">
                  {formatTime(message.created_at)}
                </span>
              )}
            </div>

            {/* Sources Section (If AI answer has web search sources) */}
            {message.sources && message.sources.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-neutral-600 dark:text-neutral-300">
                  <Globe className="w-3.5 h-3.5 text-neutral-500" />
                  <span>Sources ({message.sources.length})</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                  {message.sources.map((src, idx) => (
                    <SourceCard key={src.id || idx} source={src} />
                  ))}
                </div>
              </div>
            )}

            {/* Markdown Body Content */}
            <div className="markdown-body text-sm sm:text-base text-neutral-900 dark:text-neutral-100 leading-relaxed font-normal">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || '');
                    const isInline = !match && !String(children).includes('\n');
                    if (isInline) {
                      return (
                        <code
                          className="px-1.5 py-0.5 rounded font-mono text-xs bg-neutral-100 dark:bg-[#212121] text-neutral-900 dark:text-neutral-200 border border-neutral-200 dark:border-neutral-800"
                          {...props}
                        >
                          {children}
                        </code>
                      );
                    }
                    return (
                      <CodeBlock
                        language={match ? match[1] : ''}
                        value={String(children).replace(/\n$/, '')}
                      />
                    );
                  },
                  a({ node, children, href, ...props }) {
                    return (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium underline hover:opacity-80"
                        {...props}
                      >
                        {children}
                      </a>
                    );
                  },
                  img({ node, src, alt, ...props }: any) {
                    return (
                      <ImageCard
                        src={src || ''}
                        alt={alt || ''}
                        prompt={alt}
                      />
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Standalone Image Card if message has image file_url not yet in markdown */}
            {message.file_url && message.file_type === 'image' && !message.content.includes(message.file_url) && (
              <div className="mt-3">
                <ImageCard
                  src={message.file_url}
                  alt={message.file_name || 'Generated Image'}
                  prompt={message.file_name || undefined}
                />
              </div>
            )}

            {/* Assistant Action Buttons Toolbar */}
            <div className="flex items-center gap-1 mt-3 pt-1 text-neutral-400 dark:text-neutral-500">
              <button
                onClick={handleCopy}
                type="button"
                className="p-1.5 rounded-lg hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors cursor-pointer"
                title="Copy response"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
              </button>

              {isLastAssistant && onRegenerate && (
                <button
                  onClick={onRegenerate}
                  type="button"
                  className="p-1.5 rounded-lg hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#212121] transition-colors"
                  title="Regenerate response"
                >
                  <RotateCw className="w-4 h-4" />
                </button>
              )}

              <button
                onClick={() => setFeedback(feedback === 'liked' ? null : 'liked')}
                type="button"
                className={`p-1.5 rounded-lg transition-colors ${
                  feedback === 'liked'
                    ? 'text-neutral-900 dark:text-white bg-neutral-200 dark:bg-neutral-800'
                    : 'hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#212121]'
                }`}
                title="Good response"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>

              <button
                onClick={() => setFeedback(feedback === 'disliked' ? null : 'disliked')}
                type="button"
                className={`p-1.5 rounded-lg transition-colors ${
                  feedback === 'disliked'
                    ? 'text-neutral-900 dark:text-white bg-neutral-200 dark:bg-neutral-800'
                    : 'hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-[#212121]'
                }`}
                title="Bad response"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
