import { forwardRef } from 'react'
import { Link } from 'react-router-dom'

const stats = [
  { value: '5', label: 'Microservicios', sublabel: 'FastAPI independientes' },
  { value: 'SSO', label: 'Auth0 JWT', sublabel: 'Autenticación segura' },
  { value: 'RAG', label: 'IA Integrada', sublabel: 'n8n + LLM' },
  { value: '100%', label: 'Containerizado', sublabel: 'Docker Compose' },
]

const HeroSection = forwardRef(function HeroSection(_, ref) {
  return (
    <section ref={ref} className="relative pt-28 sm:pt-36 lg:pt-44 pb-16 sm:pb-24 px-4 sm:px-6 lg:px-8">
      {/* Background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="orb-1 absolute top-20 right-[10%] w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] rounded-full bg-gradient-to-br from-brand-200/40 to-violet-200/30 blur-3xl" />
        <div className="orb-2 absolute top-[60%] left-[5%] w-[250px] h-[250px] sm:w-[400px] sm:h-[400px] rounded-full bg-gradient-to-br from-emerald-200/30 to-cyan-200/20 blur-3xl" />
        <div className="orb-3 absolute bottom-0 right-[30%] w-[200px] h-[200px] sm:w-[350px] sm:h-[350px] rounded-full bg-gradient-to-br from-amber-200/20 to-rose-200/20 blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto">
        <div className="max-w-4xl">
          {/* Badge */}
          <div className="hero-badge inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-black/[0.06] shadow-sm mb-6 sm:mb-8">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
            </span>
            <span className="text-xs sm:text-sm font-medium text-surface-700">
              5 microservicios en contenedores
            </span>
          </div>

          {/* Title */}
          <h1 className="font-display font-bold tracking-tight">
            <span className="hero-title-line block text-4xl sm:text-5xl md:text-6xl lg:text-[5.5rem] text-surface-900 leading-[1.05]">
              Gestión de datos
            </span>
            <span className="hero-title-line block text-4xl sm:text-5xl md:text-6xl lg:text-[5.5rem] leading-[1.05] mt-1 sm:mt-2">
              <span className="bg-gradient-to-r from-brand-600 via-violet-600 to-brand-600 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
                personales.
              </span>
            </span>
          </h1>

          {/* Subtitle */}
          <p className="hero-subtitle mt-6 sm:mt-8 text-base sm:text-lg lg:text-xl text-surface-600 leading-relaxed max-w-2xl">
            Plataforma integral con autenticación SSO, operaciones CRUD,
            consultas inteligentes con IA y trazabilidad completa.
            <span className="hidden sm:inline"> Todo desplegado en Docker.</span>
          </p>

          {/* Buttons */}
          <div className="hero-buttons mt-8 sm:mt-10 flex flex-col sm:flex-row gap-3 sm:gap-4">
            <Link
              to="/login"
              className="group relative inline-flex items-center justify-center gap-2 px-7 py-3.5 sm:py-4 bg-surface-900 text-white font-display font-semibold text-sm sm:text-base rounded-2xl hover:bg-surface-800 transition-all duration-300 shadow-xl shadow-surface-900/20 hover:shadow-2xl hover:shadow-surface-900/25 hover:-translate-y-0.5 active:translate-y-0"
            >
              Comenzar ahora
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>
            <a
              href="#features"
              className="inline-flex items-center justify-center gap-2 px-7 py-3.5 sm:py-4 bg-white text-surface-700 font-display font-semibold text-sm sm:text-base rounded-2xl border border-black/[0.08] hover:border-black/[0.15] hover:bg-surface-50 transition-all duration-200"
            >
              Explorar módulos
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </a>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-16 sm:mt-20 lg:mt-28 grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="hero-stat group relative bg-white rounded-2xl border border-black/[0.06] p-5 sm:p-6 hover:border-brand-200 hover:shadow-lg hover:shadow-brand-500/5 transition-all duration-300 cursor-default"
            >
              <div className="text-2xl sm:text-3xl font-display font-bold text-surface-900 group-hover:text-brand-700 transition-colors">
                {stat.value}
              </div>
              <div className="mt-1 text-sm font-medium text-surface-700">
                {stat.label}
              </div>
              <div className="text-xs text-surface-500 mt-0.5">
                {stat.sublabel}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
})

export default HeroSection
