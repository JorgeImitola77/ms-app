export default function LandingFooter() {
  return (
    <footer className="border-t border-black/[0.06] py-8 sm:py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="font-display font-semibold text-sm text-surface-700">
            Explor<span className="text-brand-600">App</span>
          </span>
        </div>
        <p className="text-xs text-surface-500">
          Universidad del Norte — Diseño de Software 2 — 2026
        </p>
      </div>
    </footer>
  )
}
