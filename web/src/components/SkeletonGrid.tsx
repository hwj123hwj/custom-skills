/**
 * Skeleton loading components for first-screen shimmer effect.
 */

function SkeletonLine({ width = '100%', height = '14px' }: { width?: string; height?: string }) {
  return (
    <div
      className="skeleton"
      style={{ width, height }}
    />
  );
}

export function SkillCardSkeleton() {
  return (
    <div
      className="w-full rounded-xl p-5"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <div className="skeleton w-8 h-8 rounded-lg shrink-0" />
        <div className="flex-1 min-w-0">
          <SkeletonLine width="60%" height="16px" />
          <div className="flex gap-1.5 mt-2">
            <SkeletonLine width="48px" height="18px" />
            <SkeletonLine width="56px" height="18px" />
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2 mb-4">
        <SkeletonLine width="100%" height="14px" />
        <SkeletonLine width="80%" height="14px" />
      </div>

      {/* Footer */}
      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
        <SkeletonLine width="80px" height="12px" />
      </div>
    </div>
  );
}

export function AgentCardSkeleton() {
  return (
    <div
      className="w-full rounded-xl p-6"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="flex flex-col gap-1.5 shrink-0">
          <SkeletonLine width="40px" height="18px" />
          <SkeletonLine width="52px" height="18px" />
        </div>
        <div className="flex-1 min-w-0">
          <SkeletonLine width="50%" height="20px" />
          <div className="flex gap-1.5 mt-2">
            <SkeletonLine width="40px" height="18px" />
            <SkeletonLine width="52px" height="18px" />
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2 mb-4" style={{ minHeight: '40px' }}>
        <SkeletonLine width="100%" height="14px" />
        <SkeletonLine width="70%" height="14px" />
      </div>

      {/* Footer */}
      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
        <SkeletonLine width="80px" height="12px" />
      </div>
    </div>
  );
}

export function StoryCardSkeleton() {
  return (
    <div
      className="w-full rounded-xl p-6"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      <div className="flex gap-1.5 mb-3">
        <SkeletonLine width="48px" height="18px" />
        <SkeletonLine width="56px" height="18px" />
      </div>
      <SkeletonLine width="70%" height="20px" />
      <SkeletonLine width="100px" height="12px" />

      <div className="space-y-2 my-4" style={{ minHeight: '60px' }}>
        <SkeletonLine width="100%" height="14px" />
        <SkeletonLine width="90%" height="14px" />
        <SkeletonLine width="75%" height="14px" />
      </div>

      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
        <SkeletonLine width="100px" height="12px" />
      </div>
    </div>
  );
}

export function DeckCardSkeleton() {
  return (
    <div
      className="w-full rounded-xl p-5"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
      }}
    >
      {/* Preview area */}
      <div className="skeleton w-full rounded-xl mb-4" style={{ height: '176px' }} />

      <SkeletonLine width="60%" height="20px" />
      <SkeletonLine width="100px" height="12px" />

      <div className="space-y-2 my-3" style={{ minHeight: '40px' }}>
        <SkeletonLine width="100%" height="14px" />
        <SkeletonLine width="70%" height="14px" />
      </div>

      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
        <SkeletonLine width="120px" height="12px" />
      </div>
    </div>
  );
}

export function SkeletonGrid({ type }: { type: 'skills' | 'agents' | 'stories' | 'decks' }) {
  const SkeletonCard = {
    skills: SkillCardSkeleton,
    agents: AgentCardSkeleton,
    stories: StoryCardSkeleton,
    decks: DeckCardSkeleton,
  }[type];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 justify-items-center">
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
