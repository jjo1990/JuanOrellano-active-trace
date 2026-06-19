import { http, HttpResponse } from 'msw'

const API_URL = 'http://localhost:8000'

export function createFinanzasAdminHandlers() {
  return [
    http.get(`${API_URL}/api/liquidaciones/periodo`, () => {
      return HttpResponse.json({
        cohorte_id: 'coh-1',
        cohorte_nombre: '2025-C1',
        mes: 6,
        anio: 2025,
        cerrada: false,
        total_sin_factura: 450000,
        total_con_factura: 520000,
        entradas: [
          {
            id: 'liq-1',
            docente_id: 'doc-1',
            docente_nombre: 'Carlos Pérez',
            rol: 'PROFESOR',
            materias: ['Matemática', 'Álgebra'],
            salario_base: 150000,
            plus: [
              { clave: 'ANTIGUEDAD', descripcion: 'Antigüedad 5 años', monto: 10000 },
              { clave: 'EXTRA', descripcion: 'Coordinación extra', monto: 5000 },
            ],
            total: 165000,
            factura: false,
            segmento: 'general',
          },
          {
            id: 'liq-2',
            docente_id: 'doc-2',
            docente_nombre: 'Laura Martínez',
            rol: 'TUTOR',
            materias: ['Matemática'],
            salario_base: 80000,
            plus: [],
            total: 80000,
            factura: false,
            segmento: 'general',
          },
          {
            id: 'liq-3',
            docente_id: 'nex-1',
            docente_nombre: 'Pedro NEXO',
            rol: 'NEXO',
            materias: ['Matemática'],
            salario_base: 60000,
            plus: [],
            total: 60000,
            factura: false,
            segmento: 'nexo',
          },
          {
            id: 'liq-4',
            docente_id: 'doc-3',
            docente_nombre: 'Ana Factura',
            rol: 'PROFESOR',
            materias: ['Física'],
            salario_base: 120000,
            plus: [{ clave: 'ANTIGUEDAD', descripcion: 'Antigüedad', monto: 8000 }],
            total: 128000,
            factura: true,
            segmento: 'factura',
          },
        ],
      })
    }),

    http.get(`${API_URL}/api/liquidaciones/historial`, () => {
      return HttpResponse.json([
        {
          id: 'hist-1',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          mes: 3,
          anio: 2025,
          fecha_cierre: '2025-04-01T00:00:00Z',
          total_liquidado: 380000,
          cantidad_docentes: 5,
        },
        {
          id: 'hist-2',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          mes: 4,
          anio: 2025,
          fecha_cierre: '2025-05-01T00:00:00Z',
          total_liquidado: 410000,
          cantidad_docentes: 6,
        },
      ])
    }),

    http.get(`${API_URL}/api/liquidaciones/:id`, () => {
      return HttpResponse.json({
        cohorte_id: 'coh-1',
        cohorte_nombre: '2025-C1',
        mes: 3,
        anio: 2025,
        cerrada: true,
        fecha_cierre: '2025-04-01T00:00:00Z',
        total_sin_factura: 380000,
        total_con_factura: 380000,
        entradas: [
          {
            id: 'liq-1',
            docente_id: 'doc-1',
            docente_nombre: 'Carlos Pérez',
            rol: 'PROFESOR',
            materias: ['Matemática'],
            salario_base: 150000,
            plus: [],
            total: 150000,
            factura: false,
            segmento: 'general',
          },
        ],
      })
    }),

    http.post(`${API_URL}/api/liquidaciones/cerrar`, () => {
      return new HttpResponse(null, { status: 200 })
    }),

    http.get(`${API_URL}/api/salarios/base`, () => {
      return HttpResponse.json([
        {
          id: 'sal-1',
          rol: 'PROFESOR',
          monto: 150000,
          vigencia_desde: '2025-03-01T00:00:00Z',
          vigencia_hasta: '2025-07-31T00:00:00Z',
          activo: true,
        },
        {
          id: 'sal-2',
          rol: 'TUTOR',
          monto: 80000,
          vigencia_desde: '2025-03-01T00:00:00Z',
          vigencia_hasta: null,
          activo: true,
        },
        {
          id: 'sal-3',
          rol: 'COORDINADOR',
          monto: 100000,
          vigencia_desde: '2025-01-01T00:00:00Z',
          vigencia_hasta: '2025-02-28T00:00:00Z',
          activo: false,
        },
      ])
    }),

    http.get(`${API_URL}/api/salarios/plus`, () => {
      return HttpResponse.json([
        {
          id: 'pl-1',
          clave: 'ANTIGUEDAD',
          rol: 'PROFESOR',
          descripcion: 'Antigüedad 5 años',
          monto: 10000,
          vigencia_desde: '2025-03-01T00:00:00Z',
          vigencia_hasta: null,
          activo: true,
        },
        {
          id: 'pl-2',
          clave: 'EXTRA',
          rol: 'TUTOR',
          descripcion: 'Coordinación extra',
          porcentaje: 15,
          vigencia_desde: '2025-03-01T00:00:00Z',
          vigencia_hasta: null,
          activo: true,
        },
      ])
    }),

    http.post(`${API_URL}/api/salarios/base`, async () => {
      const body = await request.json()
      return HttpResponse.json({
        id: 'sal-new',
        ...body,
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/salarios/base/:id`, async () => {
      return HttpResponse.json({
        id: 'sal-1',
        rol: 'PROFESOR',
        monto: 160000,
        vigencia_desde: '2025-03-01T00:00:00Z',
        vigencia_hasta: '2025-07-31T00:00:00Z',
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/salarios/base/:id/desactivar`, () => {
      return new HttpResponse(null, { status: 200 })
    }),

    http.post(`${API_URL}/api/salarios/plus`, async ({ request }) => {
      const body = await request.json()
      return HttpResponse.json({
        id: 'pl-new',
        ...(body as Record<string, unknown>),
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/salarios/plus/:id`, async () => {
      return HttpResponse.json({
        id: 'pl-1',
        clave: 'ANTIGUEDAD',
        rol: 'PROFESOR',
        descripcion: 'Antigüedad 10 años',
        monto: 20000,
        vigencia_desde: '2025-03-01T00:00:00Z',
        vigencia_hasta: null,
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/salarios/plus/:id/desactivar`, () => {
      return new HttpResponse(null, { status: 200 })
    }),

    http.get(`${API_URL}/api/facturas`, () => {
      return HttpResponse.json([
        {
          id: 'fac-1',
          docente_id: 'doc-3',
          docente_nombre: 'Ana Factura',
          periodo: '2025-06',
          fecha_carga: '2025-06-15T00:00:00Z',
          detalle: 'Factura por servicios de docencia',
          archivo_nombre: 'factura-junio-2025.pdf',
          archivo_tamano: 245760,
          estado: 'Pendiente',
          monto: 128000,
        },
        {
          id: 'fac-2',
          docente_id: 'doc-4',
          docente_nombre: 'Juan Factura',
          periodo: '2025-05',
          fecha_carga: '2025-05-10T00:00:00Z',
          detalle: 'Factura por servicios de docencia - Mayo',
          estado: 'Abonada',
          fecha_pago: '2025-05-20T00:00:00Z',
          monto: 95000,
        },
      ])
    }),

    http.put(`${API_URL}/api/facturas/:id/estado`, async ({ request }) => {
      const body = (await request.json()) as { estado: string }
      return HttpResponse.json({
        id: 'fac-1',
        docente_id: 'doc-3',
        docente_nombre: 'Ana Factura',
        periodo: '2025-06',
        fecha_carga: '2025-06-15T00:00:00Z',
        detalle: 'Factura por servicios de docencia',
        estado: body.estado,
        monto: 128000,
        ...(body.estado === 'Abonada' ? { fecha_pago: '2025-06-20T00:00:00Z' } : {}),
      })
    }),

    http.get(`${API_URL}/api/admin/carreras`, () => {
      return HttpResponse.json([
        {
          id: 'car-1',
          codigo: 'ING-INF',
          nombre: 'Ingeniería Informática',
          activa: true,
        },
        {
          id: 'car-2',
          codigo: 'ING-ELEC',
          nombre: 'Ingeniería Electrónica',
          activa: false,
        },
      ])
    }),

    http.get(`${API_URL}/api/admin/cohortes`, () => {
      return HttpResponse.json([
        {
          id: 'coh-1',
          nombre: 'MAR-2025',
          anio_inicio: 2025,
          vigencia_desde: '2025-03-01T00:00:00Z',
          vigencia_hasta: '2025-07-31T00:00:00Z',
          activa: true,
        },
        {
          id: 'coh-2',
          nombre: 'AGO-2025',
          anio_inicio: 2025,
          vigencia_desde: '2025-08-01T00:00:00Z',
          vigencia_hasta: '2025-12-31T00:00:00Z',
          activa: false,
        },
      ])
    }),

    http.post(`${API_URL}/api/admin/carreras`, async ({ request }) => {
      const body = await request.json()
      return HttpResponse.json({
        id: 'car-new',
        ...(body as Record<string, unknown>),
        activa: true,
      })
    }),

    http.put(`${API_URL}/api/admin/carreras/:id`, async () => {
      return HttpResponse.json({
        id: 'car-1',
        codigo: 'ING-INF',
        nombre: 'Ingeniería Informática (actualizado)',
        activa: true,
      })
    }),

    http.put(`${API_URL}/api/admin/carreras/:id/estado`, async () => {
      return HttpResponse.json({
        id: 'car-1',
        codigo: 'ING-INF',
        nombre: 'Ingeniería Informática',
        activa: false,
      })
    }),

    http.post(`${API_URL}/api/admin/cohortes`, async ({ request }) => {
      const body = await request.json()
      return HttpResponse.json({
        id: 'coh-new',
        ...(body as Record<string, unknown>),
        activa: true,
      })
    }),

    http.put(`${API_URL}/api/admin/cohortes/:id`, async () => {
      return HttpResponse.json({
        id: 'coh-1',
        nombre: 'MAR-2025 (actualizado)',
        anio_inicio: 2025,
        vigencia_desde: '2025-03-01T00:00:00Z',
        vigencia_hasta: '2025-07-31T00:00:00Z',
        activa: true,
      })
    }),

    http.put(`${API_URL}/api/admin/cohortes/:id/estado`, async () => {
      return HttpResponse.json({
        id: 'coh-1',
        nombre: 'MAR-2025',
        anio_inicio: 2025,
        vigencia_desde: '2025-03-01T00:00:00Z',
        vigencia_hasta: '2025-07-31T00:00:00Z',
        activa: false,
      })
    }),

    http.get(`${API_URL}/api/admin/usuarios`, () => {
      return HttpResponse.json([
        {
          id: 'usr-1',
          nombre: 'Carlos Pérez',
          email: 'carlos@test.com',
          identificacion_fiscal: '20-12345678-9',
          roles: ['PROFESOR'],
          banco: 'Santander',
          cbu: '0000000000000000000001',
          alias_cbu: 'carlos.perez.santander',
          regional: 'Capital',
          modalidad_facturacion: null,
          activo: true,
        },
        {
          id: 'usr-2',
          nombre: 'Laura Martínez',
          email: 'laura@test.com',
          roles: ['TUTOR'],
          regional: 'Norte',
          activo: true,
        },
        {
          id: 'usr-3',
          nombre: 'Pedro Inactivo',
          email: 'pedro@test.com',
          roles: ['PROFESOR'],
          activo: false,
        },
      ])
    }),

    http.post(`${API_URL}/api/admin/usuarios`, async ({ request }) => {
      const body = await request.json()
      return HttpResponse.json({
        id: 'usr-new',
        ...(body as Record<string, unknown>),
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/admin/usuarios/:id`, async () => {
      return HttpResponse.json({
        id: 'usr-1',
        nombre: 'Carlos Pérez',
        email: 'carlos@test.com',
        roles: ['PROFESOR', 'COORDINADOR'],
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/admin/usuarios/:id/estado`, async () => {
      return new HttpResponse(null, { status: 200 })
    }),

    http.get(`${API_URL}/api/auditoria/log`, () => {
      return HttpResponse.json({
        items: [
          {
            id: 'aud-1',
            fecha: '2025-06-18T12:00:00Z',
            usuario_id: 'usr-1',
            usuario_nombre: 'Carlos Pérez',
            materia_id: 'mat-1',
            materia_nombre: 'Matemática',
            tipo_accion: 'importacion',
            registros_afectados: 45,
            ip: '192.168.1.100',
            user_agent: 'Mozilla/5.0 (Chrome)',
          },
          {
            id: 'aud-2',
            fecha: '2025-06-18T11:30:00Z',
            usuario_id: 'usr-2',
            usuario_nombre: 'Laura Martínez',
            materia_id: 'mat-1',
            materia_nombre: 'Matemática',
            tipo_accion: 'envio',
            registros_afectados: 12,
            ip: '192.168.1.101',
            user_agent: 'Mozilla/5.0 (Firefox)',
          },
        ],
        total: 2,
      })
    }),

    http.get(`${API_URL}/api/auditoria/acciones-por-dia`, () => {
      return HttpResponse.json([
        { fecha: '2025-06-16', cantidad: 45 },
        { fecha: '2025-06-17', cantidad: 23 },
        { fecha: '2025-06-18', cantidad: 67 },
      ])
    }),

    http.get(`${API_URL}/api/auditoria/estado-comunicaciones`, () => {
      return HttpResponse.json([
        {
          docente_id: 'doc-1',
          docente_nombre: 'Carlos Pérez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          pendientes: 0,
          enviados: 45,
          fallidos: 3,
          cancelados: 0,
        },
        {
          docente_id: 'doc-2',
          docente_nombre: 'Laura Martínez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          pendientes: 5,
          enviados: 30,
          fallidos: 1,
          cancelados: 2,
        },
      ])
    }),

    http.get(`${API_URL}/api/auditoria/interacciones`, () => {
      return HttpResponse.json([
        {
          docente_id: 'doc-1',
          docente_nombre: 'Carlos Pérez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          analisis_desempeno: 15,
          vista_previa: 10,
          importaciones: 8,
          envios: 12,
          limpieza_datos: 3,
          config_umbral: 2,
          emails_generados: 45,
          lotes_procesados: 3,
        },
      ])
    }),

    http.get(`${API_URL}/api/auditoria/ultimas-acciones`, () => {
      return HttpResponse.json([
        {
          id: 'aud-1',
          fecha: '2025-06-18T12:00:00Z',
          usuario_id: 'usr-1',
          usuario_nombre: 'Carlos Pérez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          tipo_accion: 'importacion',
          registros_afectados: 45,
          ip: '192.168.1.100',
        },
        {
          id: 'aud-2',
          fecha: '2025-06-18T11:30:00Z',
          usuario_id: 'usr-2',
          usuario_nombre: 'Laura Martínez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          tipo_accion: 'envio',
          registros_afectados: 12,
          ip: '192.168.1.101',
        },
      ])
    }),
  ]
}
