interface LiquidacionKpiCardsProps {
  totalSinFactura: number
  totalConFactura: number
}

export function LiquidacionKpiCards({
  totalSinFactura,
  totalConFactura,
}: LiquidacionKpiCardsProps) {
  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value)

  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <p className="text-sm text-gray-500">Total sin factura</p>
        <p className="text-2xl font-bold text-gray-900">
          {formatCurrency(totalSinFactura)}
        </p>
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <p className="text-sm text-gray-500">Total con factura</p>
        <p className="text-2xl font-bold text-gray-900">
          {formatCurrency(totalConFactura)}
        </p>
      </div>
    </div>
  )
}
