import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30">
      <div className="fixed inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
      
      <header className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white font-bold">
              CS
            </div>
            <h1 className="font-semibold text-lg tracking-tight">Custom Skills Hub</h1>
          </div>
          <a 
            href="https://github.com/hwj123hwj/custom-skills" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            GitHub
          </a>
        </div>
      </header>

      <main className="relative pt-24 pb-12 max-w-6xl mx-auto px-6">
        {children}
      </main>

      <footer className="border-t border-white/10 py-8 text-center text-sm text-gray-500">
        <p>© {new Date().getFullYear()} Custom Skills Hub. Open source on GitHub.</p>
      </footer>
    </div>
  );
}
