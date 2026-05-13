import { forwardRef } from 'react'
import { Link } from 'react-router-dom'

const CTASection = forwardRef(function CTASection(_, ref) {
  return (
    <section ref={ref} className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="cta-content relative text-center">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-surface-900 tracking-tight leading-tight">
            ¿Listo para
            <span className="bg-gradient-to-r from-brand-600 to-violet-600 bg-clip-text text-transparent"> empezar</span>?
          </h2>
          <p className="mt-4 text-base sm:text-lg text-surface-600 max-w-md mx-auto">
            Autentícate con tu cuenta SSO y accede a todos los módulos del sistema.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/login"
              className="group w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-surface-900 text-white font-display font-semibold text-base rounded-2xl hover:bg-surface-800 transition-all duration-300 shadow-xl shadow-surface-900/20 hover:shadow-2xl hover:-translate-y-0.5 active:translate-y-0"
            >
              Iniciar Sesión con Auth0
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
})

export default CTASection
