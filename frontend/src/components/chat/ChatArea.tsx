import React, { useEffect, useRef } from 'react';
import { Loader2, Globe } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { WelcomeScreen } from './WelcomeScreen';
import { MessageItem } from './MessageItem';
import { SourceCard } from './SourceCard';
import { ImageCard } from './ImageCard';
import { ChatInput } from './ChatInput';

interface ChatAreaProps {
  enterToSend?: boolean;
  showTimestamps?: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  enterToSend = true,
  showTimestamps = true,
}) => {
  const {
    currentConversation,
    isLoadingChat,
    isStreaming,
    streamingStatus,
    streamingSources,
    streamingContent,
    streamingImage,
    sendMessage,
    stopGenerating,
    regenerateMessage,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom('smooth');
  }, [currentConversation?.messages, streamingContent, streamingStatus]);

  const handleSuggestionSelect = (prompt: string, enableWebSearch?: boolean, enableImageGeneration?: boolean) => {
    sendMessage({
      content: prompt,
      enableWebSearch: !!enableWebSearch,
      enableImageGeneration: !!enableImageGeneration,
    });
  };

  const messages = currentConversation?.messages || [];
  const hasMessages = messages.length > 0 || isStreaming;

  // Find last user message for regeneration
  const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-white dark:bg-[#0d0d0d] transition-colors">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6">
        {isLoadingChat ? (
          <div className="h-full flex flex-col items-center justify-center gap-3 text-neutral-400">
            <Loader2 className="w-6 h-6 animate-spin text-neutral-500" />
            <p className="text-sm font-medium">Loading conversation...</p>
          </div>
        ) : !hasMessages ? (
          <WelcomeScreen onSelectSuggestion={handleSuggestionSelect} />
        ) : (
          <div className="flex flex-col py-6 max-w-3xl lg:max-w-4xl mx-auto w-full">
            {messages.map((msg, index) => {
              const isLastAssistant =
                msg.role === 'assistant' &&
                index === messages.length - 1 &&
                !isStreaming;

              return (
                <MessageItem
                  key={msg.id || index}
                  message={msg}
                  isLastAssistant={isLastAssistant}
                  showTimestamp={showTimestamps}
                  onRegenerate={
                    lastUserMsg ? () => regenerateMessage(lastUserMsg) : undefined
                  }
                />
              );
            })}

            {/* Active Streaming Assistant Response */}
            {isStreaming && (
              <div className="w-full my-4">
                <div className="flex items-start gap-3 sm:gap-4 max-w-3xl lg:max-w-4xl mx-auto">
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
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-xs sm:text-sm text-neutral-900 dark:text-white">
                        LOKR AI
                      </span>
                    </div>

                    {/* Status Badge (Searching web or Thinking...) */}
                    {streamingStatus && (
                      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-neutral-100 dark:bg-[#212121] border border-neutral-200 dark:border-neutral-700 text-neutral-800 dark:text-neutral-200 text-xs font-medium mb-3">
                        {streamingStatus.includes('web') ? (
                          <Globe className="w-3.5 h-3.5 text-neutral-500 animate-spin" />
                        ) : (
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-neutral-500" />
                        )}
                        <span>{streamingStatus}</span>
                      </div>
                    )}

                    {/* Sources preview during stream */}
                    {streamingSources.length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-neutral-600 dark:text-neutral-300">
                          <Globe className="w-3.5 h-3.5 text-neutral-500" />
                          <span>Sources ({streamingSources.length})</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                          {streamingSources.map((src, idx) => (
                            <SourceCard key={idx} source={src} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Streaming Image Preview */}
                    {streamingImage && (
                      <div className="mb-3">
                        <ImageCard
                          src={streamingImage.image_url}
                          alt={streamingImage.prompt}
                          prompt={streamingImage.prompt}
                        />
                      </div>
                    )}

                    {/* Typing Animation when waiting for stream start */}
                    {!streamingContent && !streamingImage && (
                      <div className="flex items-center gap-1.5 py-2">
                        <span className="w-2 h-2 rounded-full bg-neutral-400 dark:bg-neutral-500 animate-typing-1" />
                        <span className="w-2 h-2 rounded-full bg-neutral-400 dark:bg-neutral-500 animate-typing-2" />
                        <span className="w-2 h-2 rounded-full bg-neutral-400 dark:bg-neutral-500 animate-typing-3" />
                      </div>
                    )}

                    {/* Streaming Text Content with Blinking Cursor */}
                    {streamingContent && (
                      <div className="markdown-body text-sm sm:text-base text-neutral-900 dark:text-neutral-100 leading-relaxed font-normal whitespace-pre-wrap">
                        {streamingContent}
                        <span className="inline-block w-1.5 h-4 ml-1 bg-neutral-800 dark:bg-neutral-200 animate-pulse align-middle" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Floating Bottom Chat Input */}
      <ChatInput
        onSend={sendMessage}
        onStop={stopGenerating}
        isStreaming={isStreaming}
        enterToSend={enterToSend}
      />
    </div>
  );
};
