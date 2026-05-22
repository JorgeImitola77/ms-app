import { useState } from 'react'

export default function SearchBar({
  placeholder = 'Ingresa el número de documento...',
  buttonLabel = 'Buscar',
  value,
  onChange,
  onSearch,
  loading = false,
  maxLength = 10,
}) {
  const isControlled = value !== undefined
  const [internal, setInternal] = useState('')
  const current = isControlled ? value : internal

  const handleChange = (e) => {
    // Solo dígitos para nro_documento.
    const next = e.target.value.replace(/\D/g, '').slice(0, maxLength)
    if (onChange) onChange(next)
    if (!isControlled) setInternal(next)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (onSearch) onSearch(current)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <div className="flex-1 relative">
        <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        <input
          type="text"
          inputMode="numeric"
          className="input-field pl-11"
          placeholder={placeholder}
          maxLength={maxLength}
          value={current}
          onChange={handleChange}
        />
      </div>
      <button type="submit" disabled={loading} className="btn-primary py-2.5 px-6 text-sm disabled:opacity-60 disabled:cursor-not-allowed">
        {loading ? 'Buscando...' : buttonLabel}
      </button>
    </form>
  )
}
