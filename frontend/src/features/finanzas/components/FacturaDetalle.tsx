import type { Factura } from '@/features/finanzas/types'

interface FacturaDetalleProps {
  factura: Factura
}

export function FacturaDetalle({ factura }: FacturaDetalleProps) {
  return (
    <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <div>
          <dt className="text-xs font-medium text-gray-500">Fecha de carga</dt>
          <dd className="text-gray-700">
            {new Date(factura.fecha_carga).toLocaleDateString('es-AR')}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Período</dt>
          <dd className="text-gray-700">{factura.periodo}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Docente</dt>
          <dd className="text-gray-700">{factura.docente_nombre}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Estado</dt>
          <dd className="text-gray-700">{factura.estado}</dd>
        </div>
        {factura.detalle && (
          <div className="col-span-2">
            <dt className="text-xs font-medium text-gray-500">Detalle</dt>
            <dd className="text-gray-700">{factura.detalle}</dd>
          </div>
        )}
        {factura.archivo_nombre && (
          <div className="col-span-2">
            <dt className="text-xs font-medium text-gray-500">Archivo</dt>
            <dd className="text-gray-700">
              {factura.archivo_nombre}
              {factura.archivo_tamano && (
                <span className="text-xs text-gray-500 ml-2">
                  ({Math.round(factura.archivo_tamano / 1024)} KB)
                </span>
              )}
            </dd>
          </div>
        )}
        {factura.monto != null && (
          <div>
            <dt className="text-xs font-medium text-gray-500">Monto</dt>
            <dd className="text-gray-700">
              {new Intl.NumberFormat('es-AR', {
                style: 'currency',
                currency: 'ARS',
              }).format(factura.monto)}
            </dd>
          </div>
        )}
        {factura.fecha_pago && (
          <div>
            <dt className="text-xs font-medium text-gray-500">Fecha de pago</dt>
            <dd className="text-gray-700">
              {new Date(factura.fecha_pago).toLocaleDateString('es-AR')}
            </dd>
          </div>
        )}
      </dl>
    </div>
  )
}
