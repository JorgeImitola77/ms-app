import { forwardRef } from 'react'

const features = [
  {
    title: 'Crear Registros',
    description: 'Alta de personas con validación completa, upload de foto y documento único como llave primaria.',
    gradient: 'from-emerald-500 to-teal-600',
    iconBg: 'bg-emerald-500/10',
    iconColor: 'text-emerald-500',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-7.5-3a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9Zm-2.25 6c-2.485 0-4.5 1.343-4.5 3v1.5h13.5V18c0-1.657-2.015-3-4.5-3h-4.5Z" />
      </svg>
    ),
  },
  {
    title: 'Consultar & Modificar',
    description: 'Búsqueda instantánea por documento. Edición parcial con validación en tiempo real.',
    gradient: 'from-blue-500 to-indigo-600',
    iconBg: 'bg-blue-500/10',
    iconColor: 'text-blue-500',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
      </svg>
    ),
  },
  {
    title: 'Chat IA con RAG',
    description: 'Haz preguntas en lenguaje natural. n8n + LLM consultan tu base de datos y responden.',
    gradient: 'from-violet-500 to-purple-600',
    iconBg: 'bg-violet-500/10',
    iconColor: 'text-violet-500',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z" />
      </svg>
    ),
  },
  {
    title: 'Log de Auditoría',
    description: 'Cada transacción queda registrada. Filtra por tipo, documento o fecha al instante.',
    gradient: 'from-amber-500 to-orange-600',
    iconBg: 'bg-amber-500/10',
    iconColor: 'text-amber-500',
    icon: (
      <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
      </svg>
    ),
  },
]

const FeaturesSection = forwardRef(function FeaturesSection(_, ref) {
  return (
    <section id="features" ref={ref} className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="features-header max-w-2xl mb-12 sm:mb-16">
          <span className="text-sm font-semibold text-brand-600 font-display tracking-wide uppercase">
            Módulos
          </span>
          <h2 className="mt-3 text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-surface-900 tracking-tight leading-[1.1]">
            Cada función,{' '}
            <span className="text-surface-500">su propio servicio.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-surface-600 leading-relaxed">
            Arquitectura desacoplada donde cada módulo escala de forma independiente.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 gap-4 sm:gap-5">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="feature-card group relative bg-white rounded-2xl sm:rounded-3xl border border-black/[0.06] p-6 sm:p-8 hover:border-black/[0.12] transition-all duration-300 hover:shadow-xl hover:shadow-black/[0.03] hover:-translate-y-1 cursor-default overflow-hidden"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-[0.03] transition-opacity duration-500`} />
              <div className="relative">
                <div className={`w-12 h-12 sm:w-14 sm:h-14 rounded-2xl ${feature.iconBg} ${feature.iconColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>
                <h3 className="mt-5 text-lg sm:text-xl font-display font-bold text-surface-900">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm sm:text-base text-surface-600 leading-relaxed">
                  {feature.description}
                </p>
                <div className="mt-5 flex items-center gap-1.5 text-sm font-medium text-surface-500 group-hover:text-brand-600 transition-colors duration-200">
                  <span>Ir al módulo</span>
                  <svg className="w-4 h-4 group-hover:translate-x-1.5 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
})

export default FeaturesSection
