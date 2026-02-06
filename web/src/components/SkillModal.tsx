import { useState } from 'react';
import type { Skill } from '../types/skill';
import { X, Copy, Check, ExternalLink } from 'lucide-react';

interface SkillModalProps {
  skill: Skill | null;
  isOpen: boolean;
  onClose: () => void;
}

export function SkillModal({ skill, isOpen, onClose }: SkillModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !skill) return null;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const skillsCliCommand = `npx skills add https://github.com/hwj123hwj/custom-skills --skill ${skill.id}`;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-white/5 bg-white/5">
          <div className="flex items-center gap-4">
            <span className="text-4xl">{skill.emoji}</span>
            <div>
              <h2 className="text-2xl font-bold text-white">{skill.name}</h2>
              <div className="flex gap-2 mt-2">
                {skill.tags.map(tag => (
                  <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Description</h3>
            <p className="text-gray-200 leading-relaxed">
              {skill.description || "No description provided for this skill."}
            </p>
          </div>

          {/* Installation */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Installation</h3>
            <div className="bg-black/50 rounded-lg border border-white/10 overflow-hidden">
              <div className="p-4">
                <div className="group relative">
                  <div className="font-mono text-sm text-green-400 bg-black/50 p-4 rounded-lg border border-white/5 overflow-x-auto">
                    {skillsCliCommand}
                  </div>
                  <button
                    onClick={() => handleCopy(skillsCliCommand)}
                    className="absolute right-2 top-2 p-2 rounded-md bg-white/10 text-gray-400 hover:text-white hover:bg-white/20 transition-all opacity-0 group-hover:opacity-100"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scenarios */}
          {skill.scenarios.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Usage Scenarios</h3>
              <ul className="space-y-2">
                {skill.scenarios.map((scenario, index) => (
                  <li key={index} className="flex items-start gap-3 text-gray-300 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
                    {scenario}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-4 border-t border-white/5 bg-white/5 flex justify-end">
          <a 
            href={`https://github.com/hwj123hwj/custom-skills/tree/main/${skill.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
          >
            View Source
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
