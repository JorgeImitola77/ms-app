export default function EmptyState({ icon, iconBg, title, description }) {
  return (
    <div className="text-center py-16">
      <div className={`w-16 h-16 rounded-2xl ${iconBg} flex items-center justify-center mx-auto`}>
        {icon}
      </div>
      <h3 className="mt-4 font-display font-semibold text-surface-700">
        {title}
      </h3>
      <p className="mt-1 text-sm text-surface-500">
        {description}
      </p>
    </div>
  )
}
