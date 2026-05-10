export default function SearchBar({ placeholder = 'Ingresa el número de documento...', buttonLabel = 'Buscar' }) {
  return (
    <div className="flex gap-3">
      <div className="flex-1 relative">
        <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        <input
          type="text"
          className="input-field pl-11"
          placeholder={placeholder}
          maxLength={10}
        />
      </div>
      <button className="btn-primary py-2.5 px-6 text-sm">
        {buttonLabel}
      </button>
    </div>
  )
}
