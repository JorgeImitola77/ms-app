import PageHeader from '../components/ui/PageHeader'
import SearchBar from '../components/ui/SearchBar'
import EmptyState from '../components/ui/EmptyState'

const mockPersona = {
  nro_documento: '1020304050',
  tipo_documento: 'Cédula',
  primer_nombre: 'Juan',
  segundo_nombre: 'Carlos',
  apellidos: 'Pérez García',
  fecha_nacimiento: '1995-06-15',
  genero: 'Masculino',
  correo: 'juan.perez@email.com',
  celular: '3001234567',
}

export default function ConsultarPersona() {
  const showResult = false

  return (
    <div>
      <PageHeader
        title="Consultar Persona"
        description="Busca datos personales por número de documento."
      />

      <div className="card max-w-2xl mx-auto mb-6">
        <SearchBar placeholder="Ingresa el número de documento..." />
      </div>

      {!showResult && (
        <div className="card max-w-2xl mx-auto">
          <EmptyState
            iconBg="bg-surface-100"
            icon={
              <svg className="w-8 h-8 text-surface-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            }
            title="Sin resultados"
            description="Ingresa un número de documento para buscar una persona."
          />
        </div>
      )}

      {showResult && (
        <div className="card max-w-2xl mx-auto">
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="sm:w-36 flex-shrink-0">
              <div className="w-36 h-44 rounded-2xl bg-surface-100 flex items-center justify-center overflow-hidden">
                <svg className="w-16 h-16 text-surface-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
                </svg>
              </div>
            </div>

            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex px-2.5 py-0.5 rounded-md bg-brand-50 text-brand-700 text-xs font-medium">
                  {mockPersona.tipo_documento}
                </span>
                <span className="text-sm font-mono text-surface-500">
                  {mockPersona.nro_documento}
                </span>
              </div>

              <h2 className="text-xl font-display font-bold text-surface-900">
                {mockPersona.primer_nombre} {mockPersona.segundo_nombre} {mockPersona.apellidos}
              </h2>

              <div className="grid grid-cols-2 gap-3 pt-2">
                {[
                  { label: 'Fecha de nacimiento', value: mockPersona.fecha_nacimiento },
                  { label: 'Género', value: mockPersona.genero },
                  { label: 'Correo', value: mockPersona.correo },
                  { label: 'Celular', value: mockPersona.celular },
                ].map((field) => (
                  <div key={field.label}>
                    <p className="text-xs text-surface-500">{field.label}</p>
                    <p className="text-sm font-medium text-surface-700">{field.value}</p>
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
