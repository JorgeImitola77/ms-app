import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import { consultarLogs } from '../api/logs'

const modules = [
  {
    to: '/app/crear',
    title: 'Crear Persona',
    description: 'Registrar una nueva persona con todos sus datos personales y foto.',
    lightColor: 'bg-emerald-50',
    textColor: 'text-emerald-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-7.5-3a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9Zm-2.25 6c-2.485 0-4.5 1.343-4.5 3v1.5h13.5V18c0-1.657-2.015-3-4.5-3h-4.5Z" />
      </svg>
    ),
  },
  {
    to: '/app/consultar',
    title: 'Consultar Persona',
    description: 'Buscar y visualizar datos personales por número de documento.',
    lightColor: 'bg-blue-50',
    textColor: 'text-blue-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
      </svg>
    ),
  },
  {
    to: '/app/modificar',
    title: 'Modificar Datos',
    description: 'Actualizar información existente buscando por documento.',
    lightColor: 'bg-amber-50',
    textColor: 'text-amber-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
      </svg>
    ),
  },
  {
    to: '/app/borrar',
    title: 'Borrar Persona',
    description: 'Eliminar un registro existente a partir del número de documento.',
    lightColor: 'bg-red-50',
    textColor: 'text-red-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
      </svg>
    ),
  },
  {
    to: '/app/chat',
    title: 'Chat IA (RAG)',
    description: 'Consultas en lenguaje natural usando inteligencia artificial.',
    lightColor: 'bg-violet-50',
    textColor: 'text-violet-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
      </svg>
    ),
  },
  {
    to: '/app/logs',
    title: 'Consultar Log',
    description: 'Historial completo de transacciones con filtros avanzados.',
    lightColor: 'bg-surface-50',
    textColor: 'text-surface-600',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
      </svg>
    ),
  },
]

export default function Dashboard() {
  const { getAccessTokenSilently } = useAuth0()
  const [totalTransacciones, setTotalTransacciones] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [statsFailed, setStatsFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const data = await consultarLogs({}, getAccessTokenSilently)
        const arr = Array.isArray(data) ? data : data?.logs ?? []
        if (!cancelled) setTotalTransacciones(arr.length)
      } catch {
        // No rompemos el dashboard si falla — sólo marcamos el stat como no disponible.
        if (!cancelled) setStatsFailed(true)
      } finally {
        if (!cancelled) setStatsLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [getAccessTokenSilently])

  return (
    <div>
      <PageHeader
        title="Panel Principal"
        description="Selecciona un módulo para comenzar."
      />

      {/* Stat card: total de transacciones */}
      <div className="card mb-6 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-xs text-surface-500 uppercase tracking-wider font-medium">Total de transacciones</p>
          {statsLoading ? (
            <div className="mt-1 flex items-center gap-2">
              <div className="w-4 h-4 rounded-full border-2 border-brand-600 border-t-transparent animate-spin" />
              <span className="text-sm text-surface-500">Cargando...</span>
            </div>
          ) : statsFailed ? (
            <p className="mt-0.5 text-sm text-surface-500">No disponible</p>
          ) : (
            <p className="mt-0.5 text-2xl font-display font-bold text-surface-900">{totalTransacciones}</p>
          )}
        </div>
        <Link
          to="/app/logs"
          className="text-xs font-medium text-brand-600 hover:text-brand-700 transition-colors hidden sm:inline-flex items-center gap-1"
        >
          Ver historial
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
          </svg>
        </Link>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules.map((mod) => (
          <Link
            key={mod.to}
            to={mod.to}
            className="card group hover:border-black/[0.12] hover:shadow-xl hover:shadow-black/[0.03] hover:-translate-y-1"
          >
            <div className={`w-11 h-11 rounded-xl ${mod.lightColor} ${mod.textColor} flex items-center justify-center`}>
              {mod.icon}
            </div>
            <h3 className="mt-4 font-display font-semibold text-surface-900 group-hover:text-brand-700 transition-colors">
              {mod.title}
            </h3>
            <p className="mt-1.5 text-sm text-surface-600 leading-relaxed">
              {mod.description}
            </p>
            <div className="mt-4 flex items-center gap-1 text-xs font-medium text-surface-500 group-hover:text-brand-600 transition-colors">
              Ir al módulo
              <svg className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
