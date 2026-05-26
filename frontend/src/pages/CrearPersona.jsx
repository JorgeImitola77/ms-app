import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import PageHeader from '../components/ui/PageHeader'
import { useToast } from '../components/ui/Toast'
import { crearPersona } from '../api/personas'

const INITIAL = {
  tipo_documento: '',
  nro_documento: '',
  primer_nombre: '',
  segundo_nombre: '',
  apellidos: '',
  fecha_nacimiento: '',
  genero: '',
  correo: '',
  celular: '',
}

const HAS_NUMBER = /\d/
const ONLY_DIGITS = /^\d+$/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(form, foto) {
  const errors = {}

  if (!form.tipo_documento) errors.tipo_documento = 'Selecciona un tipo de documento.'

  if (!form.nro_documento) errors.nro_documento = 'El documento es obligatorio.'
  else if (!ONLY_DIGITS.test(form.nro_documento)) errors.nro_documento = 'Solo se permiten números.'
  else if (form.nro_documento.length > 10) errors.nro_documento = 'Máximo 10 dígitos.'

  if (!form.primer_nombre.trim()) errors.primer_nombre = 'El primer nombre es obligatorio.'
  else if (HAS_NUMBER.test(form.primer_nombre)) errors.primer_nombre = 'No puede contener números.'
  else if (form.primer_nombre.length > 30) errors.primer_nombre = 'Máximo 30 caracteres.'

  if (form.segundo_nombre && HAS_NUMBER.test(form.segundo_nombre)) {
    errors.segundo_nombre = 'No puede contener números.'
  }

  if (!form.apellidos.trim()) errors.apellidos = 'Los apellidos son obligatorios.'
  else if (HAS_NUMBER.test(form.apellidos)) errors.apellidos = 'No pueden contener números.'
  else if (form.apellidos.length > 60) errors.apellidos = 'Máximo 60 caracteres.'

  if (!form.fecha_nacimiento) errors.fecha_nacimiento = 'La fecha es obligatoria.'

  if (!form.genero) errors.genero = 'Selecciona un género.'

  if (!form.correo) errors.correo = 'El correo es obligatorio.'
  else if (!EMAIL_RE.test(form.correo)) errors.correo = 'Formato de correo inválido.'

  if (!form.celular) errors.celular = 'El celular es obligatorio.'
  else if (!/^\d{10}$/.test(form.celular)) errors.celular = 'Debe tener exactamente 10 dígitos.'

  if (!foto) errors.foto = 'La foto es obligatoria.'
  else if (foto.size > 2 * 1024 * 1024) errors.foto = 'La foto no debe superar 2 MB.'
  else if (!foto.type.startsWith('image/')) errors.foto = 'El archivo debe ser una imagen.'

  return errors
}

export default function CrearPersona() {
  const { getAccessTokenSilently } = useAuth0()
  const toast = useToast()

  const [form, setForm] = useState(INITIAL)
  const [foto, setFoto] = useState(null)
  const [preview, setPreview] = useState(null)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const setField = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const handlePhoto = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) {
      setErrors((prev) => ({ ...prev, foto: 'La foto no debe superar 2 MB.' }))
      e.target.value = ''
      return
    }
    if (!file.type.startsWith('image/')) {
      setErrors((prev) => ({ ...prev, foto: 'El archivo debe ser una imagen.' }))
      e.target.value = ''
      return
    }
    setFoto(file)
    setPreview(URL.createObjectURL(file))
    setErrors((prev) => ({ ...prev, foto: undefined }))
  }

  const handleReset = () => {
    setForm(INITIAL)
    setFoto(null)
    setPreview(null)
    setErrors({})
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const v = validate(form, foto)
    setErrors(v)
    if (Object.keys(v).length > 0) {
      toast.error('Revisa los campos marcados.')
      return
    }

    setSubmitting(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, val]) => fd.append(k, val))
      fd.append('foto', foto)
      await crearPersona(fd, getAccessTokenSilently)
      toast.success('Persona creada correctamente.')
      handleReset()
    } catch (err) {
      toast.error(err.message || 'No se pudo crear la persona.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Crear Persona"
        description="Registra una nueva persona con todos sus datos personales."
      />

      <div className="card max-w-3xl mx-auto">
        <form className="space-y-6" onSubmit={handleSubmit} noValidate>
          {/* Documento Section */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="sm:w-1/3">
              <label className="label">Tipo de documento</label>
              <select
                className="input-field"
                value={form.tipo_documento}
                onChange={(e) => setField('tipo_documento', e.target.value)}
              >
                <option value="" disabled>Seleccionar...</option>
                <option value="Tarjeta de identidad">Tarjeta de identidad</option>
                <option value="Cédula">Cédula</option>
              </select>
              {errors.tipo_documento && <p className="mt-1 text-xs text-red-600">{errors.tipo_documento}</p>}
            </div>
            <div className="sm:w-2/3">
              <label className="label">Nro. Documento</label>
              <input
                type="text"
                className="input-field"
                placeholder="Máx. 10 dígitos"
                maxLength={10}
                inputMode="numeric"
                value={form.nro_documento}
                onChange={(e) => setField('nro_documento', e.target.value.replace(/\D/g, ''))}
              />
              {errors.nro_documento
                ? <p className="mt-1 text-xs text-red-600">{errors.nro_documento}</p>
                : <p className="mt-1 text-xs text-surface-500">Solo números, máximo 10 caracteres.</p>}
            </div>
          </div>

          <div className="h-px bg-surface-100" />

          {/* Nombres + Foto */}
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="flex-1 space-y-4">
              <div>
                <label className="label">Primer nombre</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Ej. Juan"
                  maxLength={30}
                  value={form.primer_nombre}
                  onChange={(e) => setField('primer_nombre', e.target.value)}
                />
                {errors.primer_nombre
                  ? <p className="mt-1 text-xs text-red-600">{errors.primer_nombre}</p>
                  : <p className="mt-1 text-xs text-surface-500">Sin números, máx. 30 caracteres.</p>}
              </div>
              <div>
                <label className="label">Segundo nombre</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Opcional"
                  maxLength={30}
                  value={form.segundo_nombre}
                  onChange={(e) => setField('segundo_nombre', e.target.value)}
                />
                {errors.segundo_nombre && <p className="mt-1 text-xs text-red-600">{errors.segundo_nombre}</p>}
              </div>
              <div>
                <label className="label">Apellidos</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Ej. Pérez García"
                  maxLength={60}
                  value={form.apellidos}
                  onChange={(e) => setField('apellidos', e.target.value)}
                />
                {errors.apellidos
                  ? <p className="mt-1 text-xs text-red-600">{errors.apellidos}</p>
                  : <p className="mt-1 text-xs text-surface-500">Sin números, máx. 60 caracteres.</p>}
              </div>
            </div>

            {/* Photo Upload */}
            <div className="sm:w-44 flex flex-col items-center">
              <label className="label text-center w-full">Foto</label>
              <label className="cursor-pointer group">
                <div className="w-36 h-44 rounded-2xl border-2 border-dashed border-surface-200 bg-surface-50 flex flex-col items-center justify-center gap-2 group-hover:border-brand-400 group-hover:bg-brand-50/50 transition-colors overflow-hidden">
                  {preview ? (
                    <img src={preview} alt="Preview" className="w-full h-full object-cover rounded-xl" />
                  ) : (
                    <>
                      <div className="w-12 h-12 rounded-full bg-surface-100 flex items-center justify-center group-hover:bg-brand-100 transition-colors">
                        <svg className="w-6 h-6 text-surface-400 group-hover:text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z" />
                        </svg>
                      </div>
                      <span className="text-xs text-surface-500 group-hover:text-brand-500">Subir foto</span>
                      <span className="text-[10px] text-surface-500">Máx. 2 MB</span>
                    </>
                  )}
                </div>
                <input type="file" accept="image/*" className="hidden" onChange={handlePhoto} />
              </label>
              {errors.foto && <p className="mt-1 text-xs text-red-600 text-center">{errors.foto}</p>}
            </div>
          </div>

          <div className="h-px bg-surface-100" />

          {/* Datos Adicionales */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Fecha de nacimiento</label>
              <input
                type="date"
                className="input-field"
                value={form.fecha_nacimiento}
                onChange={(e) => setField('fecha_nacimiento', e.target.value)}
              />
              {errors.fecha_nacimiento
                ? <p className="mt-1 text-xs text-red-600">{errors.fecha_nacimiento}</p>
                : <p className="mt-1 text-xs text-surface-500">Formato dd-mmm-yyyy.</p>}
            </div>
            <div>
              <label className="label">Género</label>
              <select
                className="input-field"
                value={form.genero}
                onChange={(e) => setField('genero', e.target.value)}
              >
                <option value="" disabled>Seleccionar...</option>
                <option value="Masculino">Masculino</option>
                <option value="Femenino">Femenino</option>
                <option value="No binario">No binario</option>
                <option value="Prefiero no reportar">Prefiero no reportar</option>
              </select>
              {errors.genero && <p className="mt-1 text-xs text-red-600">{errors.genero}</p>}
            </div>
            <div>
              <label className="label">Correo electrónico</label>
              <input
                type="email"
                className="input-field"
                placeholder="correo@ejemplo.com"
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
                placeholder="10 dígitos"
                maxLength={10}
                inputMode="numeric"
                value={form.celular}
                onChange={(e) => setField('celular', e.target.value.replace(/\D/g, ''))}
              />
              {errors.celular
                ? <p className="mt-1 text-xs text-red-600">{errors.celular}</p>
                : <p className="mt-1 text-xs text-surface-500">Exactamente 10 dígitos numéricos.</p>}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-100">
            <button
              type="button"
              onClick={handleReset}
              disabled={submitting}
              className="btn-secondary py-2.5 px-5 text-sm disabled:opacity-60"
            >
              Limpiar
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary py-2.5 px-8 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {submitting ? 'Creando...' : 'Crear Persona'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
