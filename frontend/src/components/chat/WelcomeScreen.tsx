import React from 'react';
import { Lightbulb, Code2, FileSearch, Globe, Rocket, Palette } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Logo } from '../common/Logo';
import { extractPreferredName } from '../../utils/name';

interface WelcomeScreenProps {
  onSelectSuggestion: (prompt: string, enableWebSearch?: boolean, enableImageGeneration?: boolean) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectSuggestion }) => {
  const { user } = useAuth();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const preferredName = user?.preferred_name || extractPreferredName(user?.name);

  const suggestionCards = [
    {
      title: 'Generate an image',
      desc: 'Create photorealistic art and concept designs',
      prompt: 'Create an image of a majestic cybernetic lion in a glowing futuristic city',
      icon: <Palette className="w-4 h-4" />,
      webSearch: false,
      imageGen: true,
    },
    {
      title: 'Explain a concept',
      desc: 'Understand complex ideas in simple terms',
      prompt: 'Explain the core principles of quantum computing and why qubits are revolutionary.',
      icon: <Lightbulb className="w-4 h-4" />,
      webSearch: false,
      imageGen: false,
    },
    {
      title: 'Write code',
      desc: 'Build clean, production-ready algorithms',
      prompt: 'Write a Python FastAPI service with rate limiting and database connection pooling.',
      icon: <Code2 className="w-4 h-4" />,
      webSearch: false,
      imageGen: false,
    },
    {
      title: 'Analyze a document',
      desc: 'Extract key takeaways and action items',
      prompt: 'What are best practices for summarizing technical whitepapers and executive resumes?',
      icon: <FileSearch className="w-4 h-4" />,
      webSearch: false,
      imageGen: false,
    },
    {
      title: 'Search the web',
      desc: 'Get up-to-the-minute real-time data',
      prompt: 'What are the latest breakthrough updates in artificial intelligence this week?',
      icon: <Globe className="w-4 h-4" />,
      webSearch: true,
      imageGen: false,
    },
    {
      title: 'Help with a project',
      desc: 'Architect a roadmap from idea to launch',
      prompt: 'Create a comprehensive 4-week execution roadmap to launch an AI SaaS product.',
      icon: <Rocket className="w-4 h-4" />,
      webSearch: false,
      imageGen: false,
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center max-w-3xl lg:max-w-4xl mx-auto px-4 py-8 text-center animate-in fade-in duration-200">
      {/* Brand Header */}
      <div className="mb-8 flex flex-col items-center">
        <Logo size="lg" showText={false} className="mb-4" />
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-neutral-900 dark:text-white">
          {preferredName ? `${getGreeting()}, ${preferredName} 👋` : `${getGreeting()}! 👋`}
        </h1>
        <p className="mt-2 text-sm sm:text-base text-neutral-500 dark:text-neutral-400">
          How can I help you today?
        </p>
      </div>

      {/* Suggestion Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 w-full text-left">
        {suggestionCards.map((card, idx) => (
          <button
            key={idx}
            onClick={() => onSelectSuggestion(card.prompt, card.webSearch, card.imageGen)}
            type="button"
            className="group flex flex-col p-4 rounded-2xl border border-neutral-200/90 dark:border-neutral-800 bg-white dark:bg-[#181818] hover:bg-neutral-50 dark:hover:bg-[#202020] transition-colors shadow-sm text-left cursor-pointer"
          >
            <div className="flex items-center gap-2.5 mb-2">
              <div className="p-2 rounded-xl bg-neutral-100 dark:bg-[#262626] text-neutral-700 dark:text-neutral-300">
                {card.icon}
              </div>
              <span className="font-semibold text-xs sm:text-sm text-neutral-900 dark:text-white">
                {card.title}
              </span>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 line-clamp-2 leading-relaxed">
              {card.desc}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};
