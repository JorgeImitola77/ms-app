import { forwardRef } from 'react'
import { Link } from 'react-router-dom'

const Navbar = forwardRef(function Navbar(_, ref) {
  return (
    <nav ref={ref} className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-2xl border-b border-black/[0.04]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 sm:h-18 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <span className="font-display font-bold text-xl text-surface-900 tracking-tight">
            Explor<span className="text-brand-600">App</span>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <a href="#features" className="hidden sm:block text-sm text-surface-500 hover:text-surface-800 font-medium transition-colors px-3 py-2">
            Características
          </a>
          <Link
            to="/login"
            className="relative px-5 py-2.5 bg-surface-900 text-white font-display font-semibold text-sm rounded-xl hover:bg-surface-800 transition-all duration-200 shadow-lg shadow-surface-900/20 hover:shadow-surface-900/30 hover:-translate-y-0.5 active:translate-y-0"
          >
            Iniciar Sesión
          </Link>
        </div>
      </div>
    </nav>
  )
})

export default Navbar
