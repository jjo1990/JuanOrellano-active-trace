from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_user,
    get_db,
    get_tenant_from_header,
    require_permission,
    resolve_impersonation,
)
from app.core.rate_limiter import InMemoryRateLimiter
from app.repositories.audit_log import AuditLogRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChallengeResponse,
    ForgotRequest,
    Login2faRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    ResetRequest,
    TwoFactorEnrollResponse,
    TwoFactorStatusResponse,
    TwoFactorVerifyRequest,
    UserInfo,
)
from app.services.audit import AuditService
from app.services.auth_service import AuthService
from app.services.impersonation import ImpersonationService

router = APIRouter(prefix="/api/auth", tags=["auth"])

_rate_limiter = InMemoryRateLimiter()


def _build_service(db: AsyncSession, tenant_id: UUID) -> AuthService:
    user_repo = UserRepository(db, tenant_id)
    rt_repo = RefreshTokenRepository(db, tenant_id)
    return AuthService(user_repo, rt_repo, _rate_limiter)


@router.post("/login")
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    ip = request.client.host if request.client else "unknown"
    result = await service.login(body.email, body.password, tenant_id, ip)
    if result.requires_2fa:
        return ChallengeResponse(requires_2fa=True, challenge_token=result.challenge_token)
    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/login/2fa")
async def login_2fa(
    body: Login2faRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    result = await service.complete_2fa_login(body.challenge_token, body.totp_code)
    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    result = await service.refresh(body.refresh_token, user.id)
    return RefreshResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    await service.logout(body.refresh_token, user.id)
    return {"message": "Sesión cerrada correctamente."}


@router.post("/forgot")
async def forgot(
    body: ForgotRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    await service.forgot(body.email, tenant_id)
    return {
        "message": (
            "Si el email está registrado, recibirás un enlace "
            "para recuperar tu contraseña."
        ),
    }


@router.post("/reset")
async def reset(
    body: ResetRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    await service.reset(body.token, body.new_password)
    return {"message": "Contraseña actualizada correctamente."}


@router.post("/2fa/enroll", response_model=TwoFactorEnrollResponse)
async def enroll_2fa(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    result = await service.enroll_2fa(user.id)
    return TwoFactorEnrollResponse(secret=result.secret, uri=result.uri)


@router.post("/2fa/verify")
async def verify_2fa(
    body: TwoFactorVerifyRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    await service.verify_2fa(user.id, body.totp_code)
    return {"message": "2FA activado correctamente."}


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    service = _build_service(db, tenant_id)
    enabled = await service.get_2fa_status(user.id)
    return TwoFactorStatusResponse(enabled=enabled)


# ── Impersonation ───────────────────────────────────────────────────────


def _build_impersonation_service(db: AsyncSession, tenant_id: UUID) -> ImpersonationService:
    user_repo = UserRepository(db, tenant_id)
    audit_repo = AuditLogRepository(db)
    audit_service = AuditService(audit_repo)
    return ImpersonationService(user_repo, audit_service)


@router.post("/impersonate/stop")
async def impersonate_stop(
    request: Request,
    _: None = Depends(resolve_impersonation),
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    actor_id: UUID | None = request.state.actor_id
    svc = _build_impersonation_service(db, tenant_id)
    token = await svc.stop_impersonation(
        current_user_id=user.id,
        actor_id=actor_id,
        tenant_id=tenant_id,
        request=request,
    )
    await db.commit()
    return {"access_token": token, "token_type": "bearer"}


@router.post("/impersonate/{user_id}")
async def impersonate_start(
    user_id: UUID,
    request: Request,
    user: UserInfo = Depends(require_permission("impersonacion:usar")),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    svc = _build_impersonation_service(db, tenant_id)
    token = await svc.start_impersonation(
        actor_user_id=user.id,
        target_user_id=user_id,
        tenant_id=tenant_id,
        request=request,
    )
    await db.commit()
    return {"access_token": token, "token_type": "bearer"}
