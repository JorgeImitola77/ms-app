import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import gsap from 'gsap'

export default function Login() {
  const formRef = useRef(null)
  const panelRef = useRef(null)

  useEffect(() => {
    const targets = ['.login-panel-content', '.login-check', '.login-ring', '.login-back', '.login-form-content', '.login-btn', '.terms']
    gsap.killTweensOf(targets)
    gsap.set(targets, { clearProps: 'all' })

    const ctx = gsap.context(() => {
      gsap.fromTo(targets,
        { opacity: 0 },
        { opacity: 1, duration: 1, ease: 'power1.out' }
      )
    })

    return () => ctx.revert()
  }, [])

  return (
    <div className="min-h-screen bg-[#fafafa] flex font-body">
      {/* Left Panel */}
      <div ref={panelRef} className="hidden lg:flex lg:w-[45%] xl:w-1/2 bg-surface-900 relative overflow-hidden items-center justify-center p-8 xl:p-16">
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-brand-900/40 via-transparent to-violet-900/30" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-gradient-to-b from-brand-500/15 to-transparent blur-3xl rounded-full" />

        <div className="login-panel-content relative z-10 max-w-md">
          <div className="flex items-center gap-3 mb-12">
            <span className="font-display font-bold text-2xl text-white tracking-tight">
              Explor<span className="text-brand-300">App</span>
            </span>
          </div>

          <h2 className="text-3xl xl:text-4xl font-display font-bold text-white tracking-tight leading-tight">
            Gestiona tus datos
            <span className="block text-white/70 mt-1">con total confianza.</span>
          </h2>

          <p className="mt-5 text-white/60 leading-relaxed text-sm xl:text-base">
            Plataforma segura con autenticación SSO, trazabilidad completa
            y consultas inteligentes en lenguaje natural.
          </p>

          <div className="mt-10 space-y-3.5">
            {[
              { text: 'Autenticación segura con Auth0', icon: 'shield' },
              { text: 'CRUD completo de registros personales', icon: 'data' },
              { text: 'Historial de auditoría en tiempo real', icon: 'clock' },
              { text: 'Consultas IA con RAG y n8n', icon: 'ai' },
            ].map((item) => (
              <div key={item.text} className="login-check flex items-center gap-3.5 group">
                <div className="w-8 h-8 rounded-lg bg-white/[0.06] border border-white/[0.08] flex items-center justify-center flex-shrink-0 group-hover:bg-brand-500/20 group-hover:border-brand-500/30 transition-colors duration-300">
                  <svg className="w-4 h-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                  </svg>
                </div>
                <span className="text-sm text-white/70 group-hover:text-white/90 transition-colors">{item.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Decorative rings */}
        <div className="login-ring absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full border border-white/[0.04]" />
        <div className="login-ring absolute -bottom-20 -left-20 w-[400px] h-[400px] rounded-full border border-white/[0.03]" />
        <div className="login-ring absolute -top-32 -right-32 w-[400px] h-[400px] rounded-full border border-white/[0.04]" />
      </div>

      {/* Right Panel - Login Form */}
      <div ref={formRef} className="flex-1 flex items-center justify-center p-6 sm:p-8">
        <div className="w-full max-w-[380px]">
          <Link to="/" className="login-back inline-flex items-center gap-2 text-sm text-surface-500 hover:text-surface-700 transition-colors mb-12 group">
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
            </svg>
            Volver al inicio
          </Link>

          <div className="login-form-content">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center gap-2.5 mb-10">
              <span className="font-display font-bold text-2xl text-surface-900">
                Explor<span className="text-brand-600">App</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-display font-bold text-surface-900 tracking-tight">
              Bienvenido de vuelta
            </h1>
            <p className="mt-2 text-surface-600 text-sm">
              Inicia sesión con tu cuenta para acceder al sistema.
            </p>
          </div>

          <div className="mt-8 space-y-3 login-form-content">
            {/* Auth0 Login Button */}
            <Link
              to='/app'
              className="login-btn w-full group flex items-center justify-center gap-3 py-4 px-6 bg-surface-900 text-white font-display font-semibold rounded-2xl hover:bg-surface-800 transition-all duration-300 shadow-xl shadow-surface-900/15 hover:shadow-2xl hover:shadow-surface-900/20 hover:-translate-y-0.5 active:translate-y-0"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2Zm0 3a3 3 0 1 1 0 6 3 3 0 0 1 0-6Zm0 14.5a8.46 8.46 0 0 1-5.68-2.18A3.99 3.99 0 0 1 10 14.5h4a3.99 3.99 0 0 1 3.68 2.82A8.46 8.46 0 0 1 12 19.5Z" fill="currentColor" />
              </svg>
              Continuar con Auth0
              <svg className="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </Link>

            {/* Divider */}
            <div className="flex items-center gap-4 py-1">
              <div className="flex-1 h-px bg-surface-200" />
              <span className="text-xs text-surface-500 font-medium">o continúa con</span>
              <div className="flex-1 h-px bg-surface-200" />
            </div>

            {/* Google SSO Button */}
            <Link
              to='/app'
              className="login-btn w-full flex items-center justify-center gap-3 py-3.5 px-6 bg-white text-surface-700 font-display font-semibold rounded-2xl border border-black/[0.08] hover:bg-surface-50 hover:border-black/[0.15] transition-all duration-200"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1Z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23Z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A10.96 10.96 0 0 0 1 12c0 1.77.42 3.45 1.18 4.93l3.66-2.84Z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53Z" fill="#EA4335" />
              </svg>
              Google
            </Link>

            {/* Microsoft Button */}
            <Link
              to='/app'
              className="login-btn w-full flex items-center justify-center gap-3 py-3.5 px-6 bg-white text-surface-700 font-display font-semibold rounded-2xl border border-black/[0.08] hover:bg-surface-50 hover:border-black/[0.15] transition-all duration-200"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path d="M11.4 2H2v9.4h9.4V2Z" fill="#F25022" />
                <path d="M22 2h-9.4v9.4H22V2Z" fill="#7FBA00" />
                <path d="M11.4 12.6H2V22h9.4v-9.4Z" fill="#00A4EF" />
                <path d="M22 12.6h-9.4V22H22v-9.4Z" fill="#FFB900" />
              </svg>
              Microsoft
            </Link>
          </div>

          <p className="mt-10 text-xs text-center text-surface-600 leading-relaxed terms">
            Al continuar, aceptas los términos de uso del sistema.
            <br />
            Universidad del Norte — Diseño de Software 2 — 2026
          </p>
        </div>
      </div>
    </div>
  )
}
