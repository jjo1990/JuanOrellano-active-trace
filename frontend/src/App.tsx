import { Routes, Route, Navigate } from 'react-router-dom'
import { PublicGuard } from '@/shared/components/PublicGuard'
import { AuthGuard } from '@/shared/components/AuthGuard'
import { AppShell } from '@/shared/components/AppShell'
import { UnauthorizedPage } from '@/shared/components/UnauthorizedPage'
import { RequirePermission } from '@/shared/components/RequirePermission'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { TwoFactorPage } from '@/features/auth/pages/TwoFactorPage'
import { ForgotPasswordPage } from '@/features/auth/pages/ForgotPasswordPage'
import { ResetPasswordPage } from '@/features/auth/pages/ResetPasswordPage'
import { DashboardPage } from '@/features/auth/pages/DashboardPage'
import { ImportarCalificaciones } from '@/features/academico/pages/ImportarCalificaciones'
import { ConfigurarUmbral } from '@/features/academico/pages/ConfigurarUmbral'
import { DashboardMateria } from '@/features/academico/pages/DashboardMateria'
import { ComunicarAtrasados } from '@/features/academico/pages/ComunicarAtrasados'
import { MonitorSeguimiento } from '@/features/academico/pages/MonitorSeguimiento'
import { GestionEquipos } from '@/features/coordinacion/pages/GestionEquipos'
import { GestionAvisos } from '@/features/coordinacion/pages/GestionAvisos'
import { GestionTareas } from '@/features/coordinacion/pages/GestionTareas'
import { MonitoresTransversales } from '@/features/coordinacion/pages/MonitoresTransversales'
import { GestionEncuentros } from '@/features/coordinacion/pages/GestionEncuentros'
import { GestionColoquios } from '@/features/coordinacion/pages/GestionColoquios'
import { GestionProgramas } from '@/features/coordinacion/pages/GestionProgramas'
import { SetupCuatrimestre } from '@/features/coordinacion/pages/SetupCuatrimestre'
import { LiquidacionesPeriodo } from '@/features/finanzas/pages/LiquidacionesPeriodo'
import { HistorialLiquidaciones } from '@/features/finanzas/pages/HistorialLiquidaciones'
import { GestionSalarios } from '@/features/finanzas/pages/GestionSalarios'
import { GestionFacturas } from '@/features/finanzas/pages/GestionFacturas'
import { EstructuraAcademica } from '@/features/admin/pages/EstructuraAcademica'
import { GestionUsuarios } from '@/features/admin/pages/GestionUsuarios'
import { PanelAuditoria } from '@/features/admin/pages/PanelAuditoria'
import { LogAuditoria } from '@/features/admin/pages/LogAuditoria'

export function App() {
  return (
    <Routes>
      <Route element={<PublicGuard />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/2fa" element={<TwoFactorPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
      </Route>

      <Route element={<AuthGuard />}>
        <Route element={<AppShell />}>
          <Route path="/app" element={<DashboardPage />} />
          <Route path="/app/unauthorized" element={<UnauthorizedPage />} />

          <Route
            path="/materias/:id/importar"
            element={
              <RequirePermission permission="calificaciones:importar">
                <ImportarCalificaciones />
              </RequirePermission>
            }
          />
          <Route
            path="/materias/:id/umbral"
            element={
              <RequirePermission permission="calificaciones:importar">
                <ConfigurarUmbral />
              </RequirePermission>
            }
          />
          <Route
            path="/materias/:id/dashboard"
            element={
              <RequirePermission permission="atrasados:ver">
                <DashboardMateria />
              </RequirePermission>
            }
          />
          <Route
            path="/materias/:id/comunicar"
            element={
              <RequirePermission permission="comunicacion:enviar">
                <ComunicarAtrasados />
              </RequirePermission>
            }
          />
          <Route
            path="/monitor"
            element={
              <RequirePermission permission="atrasados:ver">
                <MonitorSeguimiento />
              </RequirePermission>
            }
          />

          {/* Coordinación routes */}
          <Route
            path="/equipos"
            element={
              <RequirePermission permission="equipos:asignar">
                <GestionEquipos />
              </RequirePermission>
            }
          />
          <Route
            path="/avisos"
            element={
              <RequirePermission permission="avisos:publicar">
                <GestionAvisos />
              </RequirePermission>
            }
          />
          <Route
            path="/tareas"
            element={
              <RequirePermission permission="tareas:gestionar">
                <GestionTareas />
              </RequirePermission>
            }
          />
          <Route
            path="/monitores"
            element={
              <RequirePermission permission="atrasados:ver">
                <MonitoresTransversales />
              </RequirePermission>
            }
          />
          <Route
            path="/encuentros"
            element={
              <RequirePermission permission="encuentros:gestionar">
                <GestionEncuentros />
              </RequirePermission>
            }
          />
          <Route
            path="/coloquios"
            element={
              <RequirePermission permission="coloquios:gestionar">
                <GestionColoquios />
              </RequirePermission>
            }
          />
          <Route
            path="/programas"
            element={
              <RequirePermission permission="estructura:gestionar">
                <GestionProgramas />
              </RequirePermission>
            }
          />
          <Route
            path="/setup"
            element={
              <RequirePermission permission="equipos:asignar">
                <SetupCuatrimestre />
              </RequirePermission>
            }
          />

          {/* Finanzas routes */}
          <Route
            path="/liquidaciones"
            element={
              <RequirePermission permission="liquidaciones:ver">
                <LiquidacionesPeriodo />
              </RequirePermission>
            }
          />
          <Route
            path="/liquidaciones/historial"
            element={
              <RequirePermission permission="liquidaciones:ver">
                <HistorialLiquidaciones />
              </RequirePermission>
            }
          />
          <Route
            path="/salarios"
            element={
              <RequirePermission permission="liquidaciones:configurar-salarios">
                <GestionSalarios />
              </RequirePermission>
            }
          />
          <Route
            path="/facturas"
            element={
              <RequirePermission permission="liquidaciones:ver">
                <GestionFacturas />
              </RequirePermission>
            }
          />

          {/* Admin routes */}
          <Route
            path="/estructura"
            element={
              <RequirePermission permission="estructura:gestionar">
                <EstructuraAcademica />
              </RequirePermission>
            }
          />
          <Route
            path="/usuarios"
            element={
              <RequirePermission permission="usuarios:gestionar">
                <GestionUsuarios />
              </RequirePermission>
            }
          />
          <Route
            path="/auditoria"
            element={
              <RequirePermission permission="auditoria:ver">
                <PanelAuditoria />
              </RequirePermission>
            }
          />
          <Route
            path="/auditoria/log"
            element={
              <RequirePermission permission="auditoria:ver">
                <LogAuditoria />
              </RequirePermission>
            }
          />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
