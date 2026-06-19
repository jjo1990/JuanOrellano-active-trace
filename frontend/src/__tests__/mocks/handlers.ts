import { http, HttpResponse } from 'msw'
import { createTestToken } from './jwt'
import { createFinanzasAdminHandlers } from './handlers-finanzas-admin'

const API_URL = 'http://localhost:8000'

const validAccessToken = createTestToken({
  sub: 'user-1',
  tenant_id: 'tenant-1',
  roles: ['PROFESOR'],
})

const validRefreshToken = createTestToken({
  sub: 'user-1',
  tenant_id: 'tenant-1',
  roles: ['PROFESOR'],
})

interface LoginBody {
  email: string
  password: string
}

interface TwoFactorBody {
  challenge_token: string
  totp_code: string
}

interface ResetBody {
  token: string
  new_password: string
}

export function createHandlers() {
  return [
    ...createFinanzasAdminHandlers(),
    http.get(`${API_URL}/api/health`, () => {
      return HttpResponse.json({ status: 'ok' })
    }),

    http.post(`${API_URL}/api/auth/login`, async ({ request }) => {
      const body = (await request.json()) as LoginBody

      if (!body.email || !body.password) {
        return HttpResponse.json(
          { detail: 'Credenciales inválidas' },
          { status: 401 }
        )
      }

      if (body.email === '2fa@test.com') {
        return HttpResponse.json({
          requires_2fa: true,
          challenge_token: 'challenge-token-123',
        })
      }

      if (body.email === 'fail@test.com') {
        return HttpResponse.json(
          { detail: 'Credenciales inválidas' },
          { status: 401 }
        )
      }

      return HttpResponse.json({
        access_token: validAccessToken,
        refresh_token: validRefreshToken,
        token_type: 'bearer',
      })
    }),

    http.post(`${API_URL}/api/auth/login/2fa`, async ({ request }) => {
      const body = (await request.json()) as TwoFactorBody

      if (!body.challenge_token || !body.totp_code) {
        return HttpResponse.json(
          { detail: 'Challenge token y código requeridos' },
          { status: 400 }
        )
      }

      if (body.totp_code === '000000') {
        return HttpResponse.json(
          { detail: 'Código inválido' },
          { status: 401 }
        )
      }

      return HttpResponse.json({
        access_token: validAccessToken,
        refresh_token: validRefreshToken,
        token_type: 'bearer',
      })
    }),

    http.post(`${API_URL}/api/auth/refresh`, async ({ request }) => {
      const body = (await request.json()) as { refresh_token?: string }

      if (!body.refresh_token) {
        return HttpResponse.json(
          { detail: 'Refresh token requerido' },
          { status: 400 }
        )
      }

      if (body.refresh_token === 'invalid-refresh') {
        return HttpResponse.json(
          { detail: 'Token inválido' },
          { status: 401 }
        )
      }

      const newAccessToken = createTestToken({
        sub: 'user-1',
        tenant_id: 'tenant-1',
        roles: ['PROFESOR'],
      })
      return HttpResponse.json({
        access_token: newAccessToken,
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
      })
    }),

    http.post(`${API_URL}/api/auth/logout`, () => {
      return HttpResponse.json({ message: 'Sesión cerrada' })
    }),

    http.post(`${API_URL}/api/auth/forgot`, () => {
      return HttpResponse.json({
        message: 'Si el email existe, se envió un enlace',
      })
    }),

    http.post(`${API_URL}/api/auth/reset`, async ({ request }) => {
      const body = (await request.json()) as ResetBody

      if (!body.token || !body.new_password) {
        return HttpResponse.json(
          { detail: 'Token y nueva contraseña requeridos' },
          { status: 400 }
        )
      }

      if (body.token === 'expired-token') {
        return HttpResponse.json(
          { detail: 'Token inválido o expirado' },
          { status: 400 }
        )
      }

      return HttpResponse.json({
        message: 'Contraseña actualizada correctamente.',
      })
    }),

    http.post(`${API_URL}/api/calificaciones/importar`, async ({ request }) => {
      const url = new URL(request.url)
      const isPreview = url.searchParams.get('preview') === 'true'

      if (isPreview) {
        return HttpResponse.json({
          alumnos: [
            { id: 'a1', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', legajo: 'L001' },
            { id: 'a2', nombre: 'Ana', apellido: 'Lopez', email: 'ana@test.com', legajo: 'L002' },
          ],
          actividades: [
            { id: 'act1', nombre: 'TP1', tipo: 'TP', peso: 1 },
            { id: 'act2', nombre: 'Parcial 1', tipo: 'Parcial', peso: 2 },
            { id: 'act3', nombre: 'TP2', tipo: 'TP', peso: 1 },
          ],
          calificaciones_preview: [
            { id: 'c1', alumno_id: 'a1', actividad_id: 'act1', nota: 7.5, estado: 'Aprobado', alumno_nombre: 'Juan Perez', actividad_nombre: 'TP1' },
            { id: 'c2', alumno_id: 'a1', actividad_id: 'act2', nota: 4, estado: 'Desaprobado', alumno_nombre: 'Juan Perez', actividad_nombre: 'Parcial 1' },
            { id: 'c3', alumno_id: 'a2', actividad_id: 'act1', nota: 8, estado: 'Aprobado', alumno_nombre: 'Ana Lopez', actividad_nombre: 'TP1' },
          ],
        })
      }

      return HttpResponse.json(
        { detail: 'Parámetro preview requerido' },
        { status: 400 }
      )
    }),

    http.post(`${API_URL}/api/calificaciones/importar/confirmar`, async () => {
      return HttpResponse.json({
        importacion_id: 'imp-1',
        calificaciones_importadas: 3,
        actividades_detectadas: 3,
        alumnos_detectados: 2,
      })
    }),

    http.get(`${API_URL}/api/calificaciones`, () => {
      return HttpResponse.json([
        { id: 'c1', alumno_id: 'a1', actividad_id: 'act1', nota: 7.5, estado: 'Aprobado', alumno_nombre: 'Juan Perez', actividad_nombre: 'TP1' },
        { id: 'c2', alumno_id: 'a1', actividad_id: 'act2', nota: 4, estado: 'Desaprobado', alumno_nombre: 'Juan Perez', actividad_nombre: 'Parcial 1' },
      ])
    }),

    http.get(`${API_URL}/api/calificaciones/:id`, () => {
      return HttpResponse.json({
        id: 'c1', alumno_id: 'a1', actividad_id: 'act1', nota: 7.5, estado: 'Aprobado',
      })
    }),

    http.get(`${API_URL}/api/umbrales/:materiaId`, () => {
      return HttpResponse.json({
        materia_id: 'mat-1',
        porcentaje: 60,
      })
    }),

    http.put(`${API_URL}/api/umbrales/:materiaId`, async () => {
      return HttpResponse.json({
        materia_id: 'mat-1',
        porcentaje: 70,
      })
    }),

    http.get(`${API_URL}/api/analisis/atrasados`, () => {
      return HttpResponse.json([
        {
          alumno_id: 'a1',
          alumno_nombre: 'Juan Perez',
          actividades_pendientes: 2,
          nota_promedio: 5.5,
          estado: 'Atrasado',
        },
        {
          alumno_id: 'a2',
          alumno_nombre: 'Ana Lopez',
          actividades_pendientes: 0,
          nota_promedio: 8,
          estado: 'Al día',
        },
      ])
    }),

    http.get(`${API_URL}/api/analisis/ranking`, () => {
      return HttpResponse.json([
        { alumno_id: 'a2', alumno_nombre: 'Ana Lopez', aprobadas: 3, promedio: 8 },
        { alumno_id: 'a1', alumno_nombre: 'Juan Perez', aprobadas: 1, promedio: 5.5 },
      ])
    }),

    http.get(`${API_URL}/api/analisis/notas-finales`, () => {
      return HttpResponse.json([
        { alumno_id: 'a2', alumno_nombre: 'Ana Lopez', nota_final: 8, estado: 'Aprobado' },
        { alumno_id: 'a1', alumno_nombre: 'Juan Perez', nota_final: 5.5, estado: 'Desaprobado' },
      ])
    }),

    http.get(`${API_URL}/api/analisis/tps-sin-corregir`, () => {
      return HttpResponse.json([
        {
          alumno_id: 'a1',
          alumno_nombre: 'Juan Perez',
          actividad_id: 'act3',
          actividad_nombre: 'TP2',
          fecha_entrega: '2025-06-10',
          estado: 'Entregado',
        },
      ])
    }),

    http.get(`${API_URL}/api/analisis/monitor`, () => {
      return HttpResponse.json([
        {
          alumno_id: 'a1',
          alumno_nombre: 'Juan Perez',
          email: 'juan@test.com',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          actividades_completadas: 2,
          actividades_totales: 5,
          estado_general: 'Atrasado',
          materias: [
            { materia_id: 'mat-1', materia_nombre: 'Matemática', estado: 'Atrasado' },
          ],
        },
        {
          alumno_id: 'a2',
          alumno_nombre: 'Ana Lopez',
          email: 'ana@test.com',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          actividades_completadas: 5,
          actividades_totales: 5,
          estado_general: 'Al día',
          materias: [
            { materia_id: 'mat-1', materia_nombre: 'Matemática', estado: 'Al día' },
          ],
        },
      ])
    }),

    http.post(`${API_URL}/api/comunicaciones/preview`, async () => {
      return HttpResponse.json({
        asunto: 'Aviso de actividades pendientes',
        cuerpo: '<p>Hola Juan Perez, tenés 2 actividades pendientes en Matemática.</p>',
        destinatarios: [
          { id: 'a1', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', legajo: 'L001' },
        ],
        cantidad: 1,
      })
    }),

    http.post(`${API_URL}/api/comunicaciones/enviar`, async () => {
      return HttpResponse.json({
        lote_id: 'lote-1',
        total: 1,
        estado: 'Pendiente',
      })
    }),

    http.get(`${API_URL}/api/comunicaciones/estado/:loteId`, () => {
      return HttpResponse.json([
        {
          id: 'env-1',
          lote_id: 'lote-1',
          alumno_id: 'a1',
          alumno_nombre: 'Juan Perez',
          email: 'juan@test.com',
          estado: 'Enviado',
          enviado_en: '2025-06-18T12:00:00Z',
        },
      ])
    }),

    http.get(`${API_URL}/api/comunicaciones/historial`, () => {
      return HttpResponse.json([
        {
          id: 'lote-1',
          materia_id: 'mat-1',
          plantilla_id: 'default',
          estado: 'Enviado',
          total_destinatarios: 1,
          enviados: 1,
          errores: 0,
          creado_en: '2025-06-18T12:00:00Z',
        },
      ])
    }),

    http.get(`${API_URL}/api/equipos`, () => {
      return HttpResponse.json([
        {
          id: 'eq-1',
          docente_id: 'doc-1',
          docente_nombre: 'Carlos Pérez',
          rol: 'PROFESOR',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          fecha_inicio: '2025-03-01',
          fecha_fin: '2025-07-15',
          activo: true,
        },
        {
          id: 'eq-2',
          docente_id: 'doc-2',
          docente_nombre: 'Laura Martínez',
          rol: 'TUTOR',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          comision_id: 'com-2',
          comision_nombre: 'Comisión B',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          fecha_inicio: '2025-03-01',
          fecha_fin: '2025-07-15',
          activo: true,
        },
      ])
    }),

    http.post(`${API_URL}/api/equipos/masivo`, async () => {
      return HttpResponse.json({ asignaciones_creadas: 2 })
    }),

    http.post(`${API_URL}/api/equipos/clonar`, async () => {
      return HttpResponse.json({ asignaciones_clonadas: 5 })
    }),

    http.put(`${API_URL}/api/equipos/:id`, async () => {
      return HttpResponse.json({
        id: 'eq-1',
        docente_id: 'doc-1',
        docente_nombre: 'Carlos Pérez',
        rol: 'PROFESOR',
        materia_id: 'mat-1',
        materia_nombre: 'Matemática',
        comision_id: 'com-1',
        comision_nombre: 'Comisión A',
        cohorte_id: 'coh-1',
        cohorte_nombre: '2025-C1',
        fecha_inicio: '2025-03-01',
        fecha_fin: '2025-12-31',
        activo: true,
      })
    }),

    http.get(`${API_URL}/api/equipos/export`, () => {
      return new HttpResponse(new Blob(['test'], { type: 'application/vnd.ms-excel' }), {
        headers: { 'Content-Type': 'application/vnd.ms-excel' },
      })
    }),

    http.get(`${API_URL}/api/avisos`, () => {
      return HttpResponse.json([
        {
          id: 'av-1',
          titulo: 'Aviso general',
          cuerpo: 'Bienvenidos al cuatrimestre',
          scope: 'Global',
          severidad: 'Media',
          fecha_inicio: '2025-03-01T00:00:00Z',
          fecha_fin: '2025-07-15T00:00:00Z',
          requiere_ack: true,
          creado_por: 'user-1',
          creado_en: '2025-03-01T00:00:00Z',
          activo: true,
        },
      ])
    }),

    http.post(`${API_URL}/api/avisos`, async () => {
      return HttpResponse.json({
        id: 'av-new',
        titulo: 'Nuevo aviso',
        cuerpo: 'Test',
        scope: 'Global',
        severidad: 'Media',
        fecha_inicio: '2025-03-01T00:00:00Z',
        fecha_fin: '2025-07-15T00:00:00Z',
        requiere_ack: false,
        creado_por: 'user-1',
        creado_en: '2025-03-01T00:00:00Z',
        activo: true,
      })
    }),

    http.put(`${API_URL}/api/avisos/:id`, async () => {
      return HttpResponse.json({
        id: 'av-1',
        titulo: 'Aviso actualizado',
        cuerpo: 'Test',
        scope: 'Global',
        severidad: 'Alta',
        fecha_inicio: '2025-03-01T00:00:00Z',
        fecha_fin: '2025-07-15T00:00:00Z',
        requiere_ack: false,
        creado_por: 'user-1',
        creado_en: '2025-03-01T00:00:00Z',
        activo: true,
      })
    }),

    http.delete(`${API_URL}/api/avisos/:id`, () => {
      return new HttpResponse(null, { status: 204 })
    }),

    http.get(`${API_URL}/api/avisos/:id/acknowledgments`, () => {
      return HttpResponse.json([
        {
          id: 'ack-1',
          aviso_id: 'av-1',
          usuario_id: 'user-2',
          usuario_nombre: 'Juan Pérez',
          confirmado_en: '2025-03-02T00:00:00Z',
        },
      ])
    }),

    http.get(`${API_URL}/api/tareas`, () => {
      return HttpResponse.json([
        {
          id: 'tar-1',
          titulo: 'Corregir TPs',
          descripcion: 'Corregir todos los TPs de la materia',
          estado: 'Pendiente',
          asignado_por_id: 'user-1',
          asignado_por_nombre: 'Coordinador',
          asignado_a_id: 'doc-1',
          asignado_a_nombre: 'Carlos Pérez',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          fecha_limite: '2025-06-30T00:00:00Z',
          creado_en: '2025-03-01T00:00:00Z',
          actualizado_en: '2025-03-01T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/tareas`, async () => {
      return HttpResponse.json({
        id: 'tar-new',
        titulo: 'Nueva tarea',
        estado: 'Pendiente',
        asignado_por_id: 'user-1',
        asignado_por_nombre: 'Coordinador',
        asignado_a_id: 'doc-1',
        asignado_a_nombre: 'Carlos Pérez',
        creado_en: '2025-03-01T00:00:00Z',
        actualizado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.put(`${API_URL}/api/tareas/:id`, async () => {
      return HttpResponse.json({
        id: 'tar-1',
        titulo: 'Corregir TPs',
        estado: 'Pendiente',
        asignado_por_id: 'user-1',
        asignado_por_nombre: 'Coordinador',
        asignado_a_id: 'doc-1',
        asignado_a_nombre: 'Carlos Pérez',
        creado_en: '2025-03-01T00:00:00Z',
        actualizado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.put(`${API_URL}/api/tareas/:id/estado`, async () => {
      return HttpResponse.json({
        id: 'tar-1',
        titulo: 'Corregir TPs',
        estado: 'En progreso',
        asignado_por_id: 'user-1',
        asignado_por_nombre: 'Coordinador',
        asignado_a_id: 'doc-1',
        asignado_a_nombre: 'Carlos Pérez',
        creado_en: '2025-03-01T00:00:00Z',
        actualizado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.post(`${API_URL}/api/tareas/:id/delegar`, async () => {
      return HttpResponse.json({
        id: 'tar-1',
        titulo: 'Corregir TPs',
        estado: 'Pendiente',
        asignado_por_id: 'user-1',
        asignado_por_nombre: 'Coordinador',
        asignado_a_id: 'doc-2',
        asignado_a_nombre: 'Laura Martínez',
        creado_en: '2025-03-01T00:00:00Z',
        actualizado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/tareas/:id/comentarios`, () => {
      return HttpResponse.json([
        {
          id: 'com-1',
          tarea_id: 'tar-1',
          usuario_id: 'user-1',
          usuario_nombre: 'Coordinador',
          texto: 'Comentario de prueba',
          creado_en: '2025-03-01T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/tareas/:id/comentarios`, async () => {
      return HttpResponse.json({
        id: 'com-new',
        tarea_id: 'tar-1',
        usuario_id: 'user-1',
        usuario_nombre: 'Coordinador',
        texto: 'Nuevo comentario',
        creado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/analisis/monitor`, () => {
      return HttpResponse.json([
        {
          alumno_id: 'a1',
          alumno_nombre: 'Juan Pérez',
          email: 'juan@test.com',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          actividades_completadas: 2,
          actividades_totales: 5,
          estado_general: 'Atrasado',
          materias: [
            { materia_id: 'mat-1', materia_nombre: 'Matemática', estado: 'Atrasado' },
          ],
        },
        {
          alumno_id: 'a2',
          alumno_nombre: 'Ana López',
          email: 'ana@test.com',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          actividades_completadas: 5,
          actividades_totales: 5,
          estado_general: 'Al día',
          materias: [
            { materia_id: 'mat-1', materia_nombre: 'Matemática', estado: 'Al día' },
          ],
        },
      ])
    }),

    http.get(`${API_URL}/api/analisis/monitor/docente`, () => {
      return HttpResponse.json([
        {
          alumno_id: 'a1',
          alumno_nombre: 'Juan Pérez',
          email: 'juan@test.com',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          comision_id: 'com-1',
          comision_nombre: 'Comisión A',
          actividades_completadas: 2,
          actividades_totales: 5,
          estado: 'Atrasado',
        },
      ])
    }),

    http.get(`${API_URL}/api/usuarios/docentes`, () => {
      return HttpResponse.json([
        { id: 'doc-1', nombre: 'Carlos Pérez', email: 'carlos@test.com', roles: ['PROFESOR'] },
        { id: 'doc-2', nombre: 'Laura Martínez', email: 'laura@test.com', roles: ['TUTOR'] },
        { id: 'doc-3', nombre: 'Pedro Gómez', email: 'pedro@test.com', roles: ['AUXILIAR'] },
      ])
    }),

    http.get(`${API_URL}/api/encuentros`, () => {
      return HttpResponse.json([
        {
          id: 'enc-1',
          dia: 'Lunes',
          hora_inicio: '09:00',
          hora_fin: '11:00',
          meet_url: 'https://meet.google.com/abc',
          cantidad_semanas: 16,
          tipo: 'Recurrente',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          docente_id: 'doc-1',
          docente_nombre: 'Carlos Pérez',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          creado_en: '2025-03-01T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/encuentros`, async () => {
      return HttpResponse.json({
        id: 'enc-new',
        dia: 'Lunes',
        hora_inicio: '09:00',
        hora_fin: '11:00',
        tipo: 'Recurrente',
        materia_id: 'mat-1',
        docente_id: 'doc-1',
        cohorte_id: 'coh-1',
        creado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/encuentros/:id/instancias`, () => {
      return HttpResponse.json([
        {
          id: 'ins-1',
          encuentro_id: 'enc-1',
          fecha: '2025-03-10',
          estado: 'Programada',
          meet_url: 'https://meet.google.com/abc',
          creado_en: '2025-03-01T00:00:00Z',
        },
        {
          id: 'ins-2',
          encuentro_id: 'enc-1',
          fecha: '2025-03-17',
          estado: 'Realizada',
          video_url: 'https://video.example.com/1',
          creado_en: '2025-03-01T00:00:00Z',
          actualizado_en: '2025-03-17T00:00:00Z',
        },
      ])
    }),

    http.put(`${API_URL}/api/encuentros/instancias/:id`, async () => {
      return HttpResponse.json({
        id: 'ins-1',
        encuentro_id: 'enc-1',
        fecha: '2025-03-10',
        estado: 'Realizada',
        meet_url: 'https://meet.google.com/abc',
        video_url: 'https://video.example.com/1',
        comentario: 'Clase realizada',
        creado_en: '2025-03-01T00:00:00Z',
        actualizado_en: '2025-03-10T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/guardias`, () => {
      return HttpResponse.json([
        {
          id: 'gua-1',
          fecha: '2025-03-15T00:00:00Z',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          docente_cubierto_id: 'doc-1',
          docente_cubierto_nombre: 'Carlos Pérez',
          tutor_id: 'doc-2',
          tutor_nombre: 'Laura Martínez',
          comentario: 'Cubrió la clase del lunes',
          creado_en: '2025-03-15T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/guardias`, async () => {
      return HttpResponse.json({
        id: 'gua-new',
        fecha: '2025-03-15T00:00:00Z',
        materia_id: 'mat-1',
        materia_nombre: 'Matemática',
        docente_cubierto_id: 'doc-1',
        docente_cubierto_nombre: 'Carlos Pérez',
        tutor_id: 'doc-2',
        tutor_nombre: 'Laura Martínez',
        creado_en: '2025-03-15T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/coloquios`, () => {
      return HttpResponse.json([
        {
          id: 'col-1',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          dias: ['Lunes', 'Martes'],
          cupo_por_turno: 5,
          activo: true,
          creado_en: '2025-06-01T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/coloquios`, async () => {
      return HttpResponse.json({
        id: 'col-new',
        materia_id: 'mat-1',
        cohorte_id: 'coh-1',
        dias: ['Lunes', 'Martes'],
        cupo_por_turno: 5,
        activo: true,
        creado_en: '2025-06-01T00:00:00Z',
      })
    }),

    http.post(`${API_URL}/api/coloquios/:id/importar-alumnos`, async () => {
      return HttpResponse.json({ alumnos_importados: 15 })
    }),

    http.get(`${API_URL}/api/coloquios/:id/reservas`, () => {
      return HttpResponse.json([
        {
          id: 'tur-1',
          coloquio_id: 'col-1',
          fecha: '2025-07-01',
          hora: '09:00',
          cupo: 5,
          reservas: [
            {
              id: 'res-1',
              turno_id: 'tur-1',
              alumno_id: 'a1',
              alumno_nombre: 'Juan Pérez',
              alumno_email: 'juan@test.com',
              confirmada: true,
              creado_en: '2025-06-15T00:00:00Z',
            },
          ],
          libre: 3,
          ocupado: 2,
        },
      ])
    }),

    http.get(`${API_URL}/api/coloquios/metricas`, () => {
      return HttpResponse.json({
        total_convocados: 30,
        reservas_confirmadas: 20,
        turnos_libres: 10,
        porcentaje_ocupacion: 67,
      })
    }),

    http.get(`${API_URL}/api/programas`, () => {
      return HttpResponse.json([
        {
          id: 'prog-1',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          carrera_id: 'car-1',
          carrera_nombre: 'Ingeniería',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          archivo_nombre: 'programa-matematica-2025.pdf',
          creado_en: '2025-03-01T00:00:00Z',
        },
      ])
    }),

    http.post(`${API_URL}/api/programas`, () => {
      return HttpResponse.json({
        id: 'prog-new',
        materia_id: 'mat-1',
        carrera_id: 'car-1',
        cohorte_id: 'coh-1',
        archivo_nombre: 'nuevo-programa.pdf',
        creado_en: '2025-03-01T00:00:00Z',
      })
    }),

    http.get(`${API_URL}/api/fechas-academicas`, () => {
      return HttpResponse.json([
        {
          id: 'fe-1',
          tipo: 'Parcial',
          numero: 1,
          fecha: '2025-04-15T00:00:00Z',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
          comentario: 'Temas 1 a 5',
        },
        {
          id: 'fe-2',
          tipo: 'TP',
          numero: 1,
          fecha: '2025-05-10T00:00:00Z',
          materia_id: 'mat-1',
          materia_nombre: 'Matemática',
          cohorte_id: 'coh-1',
          cohorte_nombre: '2025-C1',
        },
      ])
    }),

    http.post(`${API_URL}/api/fechas-academicas`, async () => {
      return HttpResponse.json({
        id: 'fe-new',
        tipo: 'Parcial',
        numero: 2,
        fecha: '2025-06-01T00:00:00Z',
        materia_id: 'mat-1',
        cohorte_id: 'coh-1',
      })
    }),

    http.put(`${API_URL}/api/fechas-academicas/:id`, async () => {
      return HttpResponse.json({
        id: 'fe-1',
        tipo: 'Parcial',
        numero: 1,
        fecha: '2025-04-20T00:00:00Z',
        materia_id: 'mat-1',
        cohorte_id: 'coh-1',
      })
    }),

    http.delete(`${API_URL}/api/fechas-academicas/:id`, () => {
      return new HttpResponse(null, { status: 204 })
    }),

    http.get(`${API_URL}/api/perfil`, ({ request }) => {
      const authHeader = request.headers.get('Authorization')

      if (!authHeader) {
        return HttpResponse.json(
          { detail: 'No autorizado' },
          { status: 401 }
        )
      }

      if (authHeader.includes('expired')) {
        return HttpResponse.json(
          { detail: 'Token expirado' },
          { status: 401 }
        )
      }

      return HttpResponse.json({
        id: 'user-1',
        tenant_id: 'tenant-1',
        email: 'maria@test.com',
        nombre: 'María',
        apellidos: 'González',
        display_name: 'María González',
        dni: null,
        cuil: null,
        cbu: null,
        alias_cbu: null,
        banco: null,
        regional: null,
        legajo: null,
        legajo_profesional: null,
        facturador: false,
        activo: true,
        created_at: null,
        updated_at: null,
      })
    }),
  ]
}
