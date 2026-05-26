import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import SearchBar from '../components/ui/SearchBar'
import EmptyState from '../components/ui/EmptyState'
import { useToast } from '../components/ui/Toast'
import { consultarPersona, modificarPersona } from '../api/personas'

const EDITABLE_FIELDS = [
  'tipo_documento',
  'primer_nombre',
  'segundo_nombre',
  'apellidos',
  'fecha_nacimiento',
  'genero',
  'correo',
  'celular',
]

const HAS_NUMBER = /\d/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validateChanges(changes) {
  const errors = {}
  if (changes.primer_nombre !== undefined) {
    if (!changes.primer_nombre.trim()) errors.primer_nombre = 'No puede estar vacío.'
    else if (HAS_NUMBER.test(changes.primer_nombre)) errors.primer_nombre = 'No puede contener números.'
    else if (changes.primer_nombre.length > 30) errors.primer_nombre = 'Máximo 30 caracteres.'
  }
  if (changes.segundo_nombre !== undefined && HAS_NUMBER.test(changes.segundo_nombre)) {
    errors.segundo_nombre = 'No puede contener números.'
  }
  if (changes.apellidos !== undefined) {
    if (!changes.apellidos.trim()) errors.apellidos = 'No puede estar vacío.'
    else if (HAS_NUMBER.test(changes.apellidos)) errors.apellidos = 'No pueden contener números.'
    else if (changes.apellidos.length > 60) errors.apellidos = 'Máximo 60 caracteres.'
  }
  if (changes.correo !== undefined && !EMAIL_RE.test(changes.correo)) {
    errors.correo = 'Formato de correo inválido.'
  }
  if (changes.celular !== undefined && !/^\d{10}$/.test(changes.celular)) {
    errors.celular = 'Debe tener exactamente 10 dígitos.'
  }
  return errors
}

export default function ModificarPersona() {
  const { getAccessTokenSilently } = useAuth0()
  const toast = useToast()

  const [documento, setDocumento] = useState('')
  const [original, setOriginal] = useState(null) // persona tal como la trajo el backend
  const [form, setForm] = useState(null) // valores actualmente en el form
  const [searching, setSearching] = useState(false)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  const handleSearch = async (doc) => {
    if (!doc || !/^\d{1,10}$/.test(doc)) {
      toast.error('Ingresa un documento válido (1-10 dígitos).')
      return
    }
    setSearching(true)
    setOriginal(null)
    setForm(null)
    setErrors({})
    try {
      const data = await consultarPersona(doc, getAccessTokenSilently)
      setOriginal(data)
      // Inicializamos form sólo con los campos editables (normalizando null → '')
      const initial = {}
      EDITABLE_FIELDS.forEach((k) => { initial[k] = data[k] ?? '' })
      setForm(initial)
    } catch (err) {
      if (err.status === 404) {
        toast.error('No se encontró ninguna persona con ese documento.')
      } else {
        toast.error(err.message || 'Error al buscar la persona.')
      }
    } finally {
      setSearching(false)
    }
  }

  const setField = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const handleCancel = () => {
    setOriginal(null)
    setForm(null)
    setErrors({})
    setDocumento('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!original || !form) return

    // Determinar campos modificados (diff)
    const changes = {}
    EDITABLE_FIELDS.forEach((k) => {
      const before = original[k] ?? ''
      const after = form[k] ?? ''
      if (before !== after) changes[k] = after
    })

    if (Object.keys(changes).length === 0) {
      toast.error('No hay cambios para guardar.')
      return
    }

    const v = validateChanges(changes)
    setErrors(v)
    if (Object.keys(v).length > 0) {
      toast.error('Revisa los campos marcados.')
      return
    }

    setSaving(true)
    try {
      const updated = await modificarPersona(
        original.nro_documento,
        changes,
        getAccessTokenSilently,
      )
      toast.success('Datos actualizados correctamente.')
      // Refrescamos original con la respuesta (o fusionando los cambios)
      const next = updated || { ...original, ...changes }
      setOriginal(next)
      const refreshed = {}
      EDITABLE_FIELDS.forEach((k) => { refreshed[k] = next[k] ?? '' })
      setForm(refreshed)
    } catch (err) {
      toast.error(err.message || 'No se pudo actualizar la persona.')
    } finally {
      setSaving(false)
    }
  }

  const found = original && form

  return (
    <div>
      <PageHeader
        title="Modificar Persona"
        description="Busca por documento y actualiza los datos de la persona."
      />

      <div className="card max-w-3xl mx-auto mb-6">
        <SearchBar
          placeholder="Ingresa el documento a modificar..."
          value={documento}
          onChange={setDocumento}
          onSearch={handleSearch}
          loading={searching}
        />
      </div>

      {searching && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex flex-col items-center py-12 gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-brand-600 border-t-transparent animate-spin" />
            <p className="text-sm text-surface-500">Cargando datos...</p>
          </div>
        </div>
      )}

      {!searching && !found && (
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

      {!searching && found && (
        <div className="card max-w-3xl mx-auto">
          <div className="flex items-center gap-2 mb-6">
            <span className="inline-flex px-2.5 py-0.5 rounded-md bg-amber-50 text-amber-700 text-xs font-medium">
              Editando
            </span>
            <span className="text-sm font-mono text-surface-500">
              {original.tipo_documento} — {original.nro_documento}
            </span>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label">Tipo de documento</label>
                <select
                  className="input-field"
                  value={form.tipo_documento}
                  onChange={(e) => setField('tipo_documento', e.target.value)}
                >
                  <option value="Tarjeta de identidad">Tarjeta de identidad</option>
                  <option value="Cédula">Cédula</option>
                </select>
              </div>
              <div>
                <label className="label">Primer nombre</label>
                <input
                  type="text"
                  className="input-field"
                  maxLength={30}
                  value={form.primer_nombre}
                  onChange={(e) => setField('primer_nombre', e.target.value)}
                />
                {errors.primer_nombre && <p className="mt-1 text-xs text-red-600">{errors.primer_nombre}</p>}
              </div>
              <div>
                <label className="label">Segundo nombre</label>
                <input
                  type="text"
                  className="input-field"
                  maxLength={30}
                  value={form.segundo_nombre}
                  onChange={(e) => setField('segundo_nombre', e.target.value)}
                />
                {errors.segundo_nombre && <p className="mt-1 text-xs text-red-600">{errors.segundo_nombre}</p>}
              </div>
              <div className="sm:col-span-2">
                <label className="label">Apellidos</label>
                <input
                  type="text"
                  className="input-field"
                  maxLength={60}
                  value={form.apellidos}
                  onChange={(e) => setField('apellidos', e.target.value)}
                />
                {errors.apellidos && <p className="mt-1 text-xs text-red-600">{errors.apellidos}</p>}
              </div>
              <div>
                <label className="label">Fecha de nacimiento</label>
                <input
                  type="date"
                  className="input-field"
                  value={form.fecha_nacimiento}
                  onChange={(e) => setField('fecha_nacimiento', e.target.value)}
                />
              </div>
              <div>
                <label className="label">Género</label>
                <select
                  className="input-field"
                  value={form.genero}
                  onChange={(e) => setField('genero', e.target.value)}
                >
                  <option value="Masculino">Masculino</option>
                  <option value="Femenino">Femenino</option>
                  <option value="No binario">No binario</option>
                  <option value="Prefiero no reportar">Prefiero no reportar</option>
                </select>
              </div>
              <div>
                <label className="label">Correo electrónico</label>
                <input
                  type="email"
                  className="input-field"
                  value={form.correo}
                  onChange={(e) => setField('correo', e.target.value)}
                />
                {errors.correo && <p className="mt-1 text-xs text-red-600">{errors.correo}</p>}
              </div>
              <div>
                <label className="label">Celular</label>
                <input
                  type="text"
                  className="input-field"
                  maxLength={10}
                  inputMode="numeric"
                  value={form.celular}
                  onChange={(e) => setField('celular', e.target.value.replace(/\D/g, ''))}
                />
                {errors.celular && <p className="mt-1 text-xs text-red-600">{errors.celular}</p>}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-100">
              <button
                type="button"
                onClick={handleCancel}
                disabled={saving}
                className="btn-secondary py-2.5 px-5 text-sm disabled:opacity-60"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={saving}
                className="btn-primary py-2.5 px-8 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {saving ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
