import { useState } from 'react'
import PageHeader from '../components/ui/PageHeader'

export default function CrearPersona() {
  const [preview, setPreview] = useState(null)

  const handlePhotoPreview = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        alert('La foto no debe superar los 2 MB')
        e.target.value = ''
        return
      }
      setPreview(URL.createObjectURL(file))
    }
  }

  return (
    <div>
      <PageHeader
        title="Crear Persona"
        description="Registra una nueva persona con todos sus datos personales."
      />

      <div className="card max-w-3xl mx-auto">
        <form className="space-y-6">
          {/* Documento Section */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="sm:w-1/3">
              <label className="label">Tipo de documento</label>
              <select className="input-field" defaultValue="">
                <option value="" disabled>Seleccionar...</option>
                <option value="Tarjeta de identidad">Tarjeta de identidad</option>
                <option value="Cédula">Cédula</option>
              </select>
            </div>
            <div className="sm:w-2/3">
              <label className="label">Nro. Documento</label>
              <input
                type="text"
                className="input-field"
                placeholder="Máx. 10 dígitos"
                maxLength={10}
              />
              <p className="mt-1 text-xs text-surface-500">Solo números, máximo 10 caracteres.</p>
            </div>
          </div>

          <div className="h-px bg-surface-100" />

          {/* Nombres + Foto */}
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="flex-1 space-y-4">
              <div>
                <label className="label">Primer nombre</label>
                <input type="text" className="input-field" placeholder="Ej. Juan" maxLength={30} />
                <p className="mt-1 text-xs text-surface-500">Sin números, máx. 30 caracteres.</p>
              </div>
              <div>
                <label className="label">Segundo nombre</label>
                <input type="text" className="input-field" placeholder="Opcional" maxLength={30} />
              </div>
              <div>
                <label className="label">Apellidos</label>
                <input type="text" className="input-field" placeholder="Ej. Pérez García" maxLength={60} />
                <p className="mt-1 text-xs text-surface-500">Sin números, máx. 60 caracteres.</p>
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
                <input type="file" accept="image/*" className="hidden" onChange={handlePhotoPreview} />
              </label>
            </div>
          </div>

          <div className="h-px bg-surface-100" />

          {/* Datos Adicionales */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Fecha de nacimiento</label>
              <input type="date" className="input-field" />
              <p className="mt-1 text-xs text-surface-500">Formato dd-mmm-yyyy.</p>
            </div>
            <div>
              <label className="label">Género</label>
              <select className="input-field" defaultValue="">
                <option value="" disabled>Seleccionar...</option>
                <option value="Masculino">Masculino</option>
                <option value="Femenino">Femenino</option>
                <option value="No binario">No binario</option>
                <option value="Prefiero no reportar">Prefiero no reportar</option>
              </select>
            </div>
            <div>
              <label className="label">Correo electrónico</label>
              <input type="email" className="input-field" placeholder="correo@ejemplo.com" />
            </div>
            <div>
              <label className="label">Celular</label>
              <input type="text" className="input-field" placeholder="10 dígitos" maxLength={10} />
              <p className="mt-1 text-xs text-surface-500">Exactamente 10 dígitos numéricos.</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-surface-100">
            <button type="button" className="btn-secondary py-2.5 px-5 text-sm">Limpiar</button>
            <button type="submit" className="btn-primary py-2.5 px-8 text-sm">Crear Persona</button>
          </div>
        </form>
      </div>
    </div>
  )
}
