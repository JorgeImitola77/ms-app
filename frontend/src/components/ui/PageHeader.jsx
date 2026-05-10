export default function PageHeader({ title, description }) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-display font-bold text-surface-900 tracking-tight">
        {title}
      </h1>
      {description && (
        <p className="mt-1 text-surface-600">{description}</p>
      )}
    </div>
  )
}
