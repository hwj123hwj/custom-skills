import type { Skill } from '../types/skill';
import { Calendar, ChevronRight } from 'lucide-react';

interface SkillCardProps {
  skill: Skill;
  onClick: (skill: Skill) => void;
}

export function SkillCard({ skill, onClick }: SkillCardProps) {
  return (
    <div 
      onClick={() => onClick(skill)}
      className="group relative w-full overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 hover:border-purple-500/50 hover:bg-white/10 transition-all duration-300 cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl filter grayscale group-hover:grayscale-0 transition-all duration-300">
            {skill.emoji}
          </span>
          <div>
            <h3 className="font-semibold text-lg text-white group-hover:text-purple-400 transition-colors">
              {skill.name}
            </h3>
            <div className="flex gap-2 mt-1">
              {skill.tags.map(tag => (
                <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/5">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <p className="text-gray-400 text-sm line-clamp-2 mb-4 min-h-[40px]">
        {skill.description || "No description provided."}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Calendar className="w-3 h-3" />
          <span>{skill.lastUpdated ? new Date(skill.lastUpdated).toLocaleDateString() : 'Unknown'}</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>View Details</span>
          <ChevronRight className="w-3 h-3" />
        </div>
      </div>
    </div>
  );
}
