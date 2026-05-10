import { forwardRef } from 'react'

const techStack = [
  { name: 'React', color: 'from-cyan-400 to-blue-500' },
  { name: 'FastAPI', color: 'from-emerald-400 to-green-600' },
  { name: 'PostgreSQL', color: 'from-blue-400 to-indigo-600' },
  { name: 'n8n', color: 'from-orange-400 to-red-500' },
  { name: 'Auth0', color: 'from-rose-400 to-pink-600' },
  { name: 'Docker', color: 'from-sky-400 to-blue-600' },
]

const services = ['Frontend', 'ms-crear', 'ms-consultar', 'ms-modificar', 'ms-borrar', 'ms-log', 'n8n RAG', 'PostgreSQL', 'Auth0']

const getServiceStyle = (i) => {
  if (i === 0) return 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300 col-span-3 sm:col-span-5'
  if (i === 7) return 'bg-blue-500/10 border-blue-500/20 text-blue-300 col-span-2 sm:col-span-3'
  if (i === 8) return 'bg-rose-500/10 border-rose-500/20 text-rose-300 col-span-1 sm:col-span-2'
  return 'bg-white/[0.04] border-white/[0.06] text-surface-300'
}

const ArchitectureSection = forwardRef(function ArchitectureSection(_, ref) {
  return (
    <section ref={ref} className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="arch-card relative overflow-hidden rounded-3xl sm:rounded-[2rem] bg-surface-900 p-8 sm:p-12 lg:p-16">
          {/* Decorative grid */}
          <div className="absolute inset-0 opacity-[0.04]" style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }} />

          {/* Glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-to-b from-brand-500/20 to-transparent blur-3xl rounded-full" />

          <div className="relative">
            <div className="max-w-2xl mx-auto text-center">
              <span className="text-sm font-semibold text-brand-400 font-display tracking-wide uppercase">
                Stack Tecnológico
              </span>
              <h2 className="mt-4 text-2xl sm:text-3xl lg:text-4xl font-display font-bold text-white tracking-tight leading-tight">
                Arquitectura moderna,{' '}
                <br className="hidden sm:block" />
                escalable por diseño.
              </h2>
              <p className="mt-4 text-surface-400 text-sm sm:text-base max-w-lg mx-auto leading-relaxed">
                Cada componente corre en su propio contenedor Docker, orquestados
                en una red privada con volúmenes persistentes.
              </p>
            </div>

            {/* Tech Pills */}
            <div className="mt-10 sm:mt-14 flex flex-wrap justify-center gap-3 sm:gap-4">
              {techStack.map((tech) => (
                <div
                  key={tech.name}
                  className="tech-pill group relative px-5 sm:px-6 py-3 sm:py-3.5 rounded-xl sm:rounded-2xl bg-white/[0.07] border border-white/[0.08] hover:bg-white/[0.12] hover:border-white/[0.15] transition-all duration-300 cursor-default"
                >
                  <div className={`absolute inset-0 rounded-xl sm:rounded-2xl bg-gradient-to-r ${tech.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  <span className="relative text-sm sm:text-base font-display font-semibold text-white/80 group-hover:text-white transition-colors">
                    {tech.name}
                  </span>
                </div>
              ))}
            </div>

            {/* Architecture visual */}
            <div className="mt-12 sm:mt-16 grid grid-cols-3 sm:grid-cols-5 gap-2 sm:gap-3 max-w-2xl mx-auto">
              {services.map((service, i) => (
                <div
                  key={service}
                  className={`px-3 py-2.5 rounded-xl text-center text-[10px] sm:text-xs font-mono border transition-all duration-300 hover:scale-105 ${getServiceStyle(i)}`}
                >
                  {service}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
})

export default ArchitectureSection
