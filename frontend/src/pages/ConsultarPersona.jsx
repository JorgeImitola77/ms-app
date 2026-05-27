import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import SearchBar from '../components/ui/SearchBar'
import EmptyState from '../components/ui/EmptyState'
import { useToast } from '../components/ui/Toast'
import { consultarPersona } from '../api/personas'

export default function ConsultarPersona() {
  const { getAccessTokenSilently } = useAuth0()
  const toast = useToast()

  const [documento, setDocumento] = useState('')
  const [persona, setPersona] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const SERVICE_DOWN_MSG =
    'El servicio de consulta no está disponible en este momento. Intenta de nuevo en unos segundos.'

  const handleSearch = async (doc) => {
    if (!doc || !/^\d{1,10}$/.test(doc)) {
      toast.error('Ingresa un documento válido (1-10 dígitos).')
      return
    }
    setLoading(true)
    setError(null)
    setPersona(null)
    setSearched(true)
    try {
      const data = await consultarPersona(doc, getAccessTokenSilently)
      setPersona(data)
    } catch (err) {
      if (err.status === 404) {
        setError('No se encontró ninguna persona con ese documento.')
      } else if (err.status === 503) {
        setError(SERVICE_DOWN_MSG)
        toast.error(SERVICE_DOWN_MSG)
      } else {
        setError(err.message || 'Error al consultar la persona.')
        toast.error(err.message || 'Error al consultar la persona.')
      }
    } finally {
      setLoading(false)
    }
  }

  // foto_ruta viene como "/app/uploads/1020304050.jpg" — extraemos solo el nombre
  const fotoUrl = persona?.foto_ruta
    ? `http://localhost:8003/uploads/${persona.foto_ruta.split('/').pop()}`
    : null

  return (
    <div>
      <PageHeader
        title="Consultar Persona"
        description="Busca datos personales por número de documento."
      />

      <div className="card max-w-2xl mx-auto mb-6">
        <SearchBar
          placeholder="Ingresa el número de documento..."
          value={documento}
          onChange={setDocumento}
          onSearch={handleSearch}
          loading={loading}
        />
      </div>

      {loading && (
        <div className="card max-w-2xl mx-auto">
          <div className="flex flex-col items-center py-12 gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-brand-600 border-t-transparent animate-spin" />
            <p className="text-sm text-surface-500">Buscando persona...</p>
          </div>
        </div>
      )}

      {!loading && !persona && (
        <div className="card max-w-2xl mx-auto">
          <EmptyState
            iconBg="bg-surface-100"
            icon={
              <svg className="w-8 h-8 text-surface-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            }
            title={searched ? 'Sin resultados' : 'Realiza una búsqueda'}
            description={
              error
                ? error
                : searched
                ? 'No se encontró ninguna persona con ese documento.'
                : 'Ingresa un número de documento para buscar una persona.'
            }
          />
        </div>
      )}

      {!loading && persona && (
        <div className="card max-w-2xl mx-auto">
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="sm:w-36 flex-shrink-0">
              <div className="w-36 h-44 rounded-2xl bg-surface-100 flex items-center justify-center overflow-hidden">
                {fotoUrl ? (
                  <img
                    src={fotoUrl}
                    alt={`Foto de ${persona.primer_nombre}`}
                    className="w-full h-full object-cover"
                    onError={(e) => { e.currentTarget.style.display = 'none' }}
                  />
                ) : (
                  <svg className="w-16 h-16 text-surface-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
                  </svg>
                )}
              </div>
            </div>

            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex px-2.5 py-0.5 rounded-md bg-brand-50 text-brand-700 text-xs font-medium">
                  {persona.tipo_documento}
                </span>
                <span className="text-sm font-mono text-surface-500">
                  {persona.nro_documento}
                </span>
              </div>

              <h2 className="text-xl font-display font-bold text-surface-900">
                {persona.primer_nombre} {persona.segundo_nombre} {persona.apellidos}
              </h2>

              <div className="grid grid-cols-2 gap-3 pt-2">
                {[
                  { label: 'Fecha de nacimiento', value: persona.fecha_nacimiento },
                  { label: 'Género', value: persona.genero },
                  { label: 'Correo', value: persona.correo },
                  { label: 'Celular', value: persona.celular },
                ].map((field) => (
                  <div key={field.label}>
                    <p className="text-xs text-surface-500">{field.label}</p>
                    <p className="text-sm font-medium text-surface-700">{field.value || '—'}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
