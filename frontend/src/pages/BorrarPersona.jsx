import PageHeader from '../components/ui/PageHeader'
import SearchBar from '../components/ui/SearchBar'
import EmptyState from '../components/ui/EmptyState'

export default function BorrarPersona() {
  const found = false
  const showConfirm = false

  return (
    <div>
      <PageHeader
        title="Borrar Persona"
        description="Elimina un registro existente a partir del número de documento."
      />

      <div className="card max-w-2xl mx-auto mb-6">
        <SearchBar placeholder="Ingresa el documento a eliminar..." />
      </div>

      {!found && (
        <div className="card max-w-2xl mx-auto">
          <EmptyState
            iconBg="bg-red-50"
            icon={
              <svg className="w-8 h-8 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
            }
            title="Busca el registro a eliminar"
            description="Ingresa el número de documento de la persona que deseas borrar."
          />
        </div>
      )}

      {found && (
        <div className="card max-w-2xl mx-auto border-red-200">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-red-50 text-red-500 flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-display font-semibold text-surface-900">Juan Carlos Pérez García</h3>
              <p className="text-sm text-surface-500 mt-0.5">Cédula — 1020304050</p>
              <p className="text-sm text-red-600 mt-3">
                Esta acción no se puede deshacer. El registro será eliminado permanentemente.
              </p>
              <div className="flex gap-3 mt-4">
                <button className="btn-secondary py-2 px-4 text-sm">Cancelar</button>
                <button className="btn-danger py-2 px-6 text-sm">Confirmar Eliminación</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl">
            <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
              </svg>
            </div>
            <h3 className="text-center font-display font-semibold text-surface-900 mt-4">¿Eliminar registro?</h3>
            <p className="text-center text-sm text-surface-500 mt-2">
              Se borrará permanentemente a <strong>Juan Carlos Pérez García</strong> del sistema.
            </p>
            <div className="flex gap-3 mt-6">
              <button className="btn-secondary flex-1 py-2.5 text-sm">Cancelar</button>
              <button className="btn-danger flex-1 py-2.5 text-sm">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
