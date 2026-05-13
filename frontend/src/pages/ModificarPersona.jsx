import PageHeader from '../components/ui/PageHeader'
import SearchBar from '../components/ui/SearchBar'
import EmptyState from '../components/ui/EmptyState'

export default function ModificarPersona() {
  const found = false

  return (
    <div>
      <PageHeader
        title="Modificar Persona"
        description="Busca por documento y actualiza los datos de la persona."
      />

      <div className="card max-w-3xl mx-auto mb-6">
        <SearchBar placeholder="Ingresa el documento a modificar..." />
      </div>

      {!found && (
        <div className="card max-w-3xl mx-auto">
          <EmptyState
            iconBg="bg-amber-50"
            icon={
              <svg className="w-8 h-8 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
              </svg>
            }
            title="Busca un registro"
            description="Ingresa el número de documento para cargar y editar los datos."
          />
        </div>
      )}

      {found && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex items-center gap-2 mb-6">
            <span className="inline-flex px-2.5 py-0.5 rounded-md bg-amber-50 text-amber-700 text-xs font-medium">
              Editando
            </span>
            <span className="text-sm font-mono text-surface-500">
              Cédula — 1020304050
            </span>
          </div>

          <form className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label">Primer nombre</label>
                <input type="text" className="input-field" defaultValue="Juan" maxLength={30} />
              </div>
              <div>
                <label className="label">Segundo nombre</label>
                <input type="text" className="input-field" defaultValue="Carlos" maxLength={30} />
              </div>
              <div className="sm:col-span-2">
                <label className="label">Apellidos</label>
                <input type="text" className="input-field" defaultValue="Pérez García" maxLength={60} />
              </div>
              <div>
                <label className="label">Fecha de nacimiento</label>
                <input type="date" className="input-field" defaultValue="1995-06-15" />
              </div>
              <div>
                <label className="label">Género</label>
                <select className="input-field" defaultValue="Masculino">
                  <option value="Masculino">Masculino</option>
                  <option value="Femenino">Femenino</option>
                  <option value="No binario">No binario</option>
                  <option value="Prefiero no reportar">Prefiero no reportar</option>
                </select>
              </div>
              <div>
                <label className="label">Correo electrónico</label>
                <input type="email" className="input-field" defaultValue="juan.perez@email.com" />
              </div>
              <div>
                <label className="label">Celular</label>
                <input type="text" className="input-field" defaultValue="3001234567" maxLength={10} />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-100">
              <button type="button" className="btn-secondary py-2.5 px-5 text-sm">Cancelar</button>
              <button type="submit" className="btn-primary py-2.5 px-8 text-sm">Guardar Cambios</button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
