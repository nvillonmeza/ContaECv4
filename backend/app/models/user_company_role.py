"""
ContaEC - Modelo de Roles por Empresa
UserCompanyRole: Permite asignar diferentes roles a los usuarios por empresa
"""
import enum
import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CompanyRole(str, enum.Enum):
    """Roles disponibles dentro de una empresa"""
    OWNER = "owner"              # Propietario de la empresa
    ADMIN = "admin"              # Administrador con acceso total
    ACCOUNTANT = "accountant"    # Contador - gestión contable y facturación
    VIEWER = "viewer"            # Solo lectura / visualización
    SALES = "sales"              # Ventas - facturación y proformas
    HR_MANAGER = "hr_manager"    # Recursos humanos - nómina y empleados


class Permission(str, enum.Enum):
    """Permisos granulares que pueden asignarse a un rol dentro de una empresa"""
    CAN_CREATE_INVOICES = "can_create_invoices"
    CAN_APPROVE = "can_approve"
    CAN_DELETE = "can_delete"
    CAN_VIEW_REPORTS = "can_view_reports"
    CAN_MANAGE_EMPLOYEES = "can_manage_employees"
    CAN_MANAGE_PRODUCTS = "can_manage_products"
    CAN_MANAGE_CLIENTS = "can_manage_clients"
    CAN_MANAGE_ACCOUNTING = "can_manage_accounting"
    CAN_MANAGE_PAYROLL = "can_manage_payroll"
    CAN_EXPORT_DATA = "can_export_data"


# Permisos por defecto según el rol
DEFAULT_PERMISSIONS: dict[CompanyRole, dict[str, bool]] = {
    CompanyRole.OWNER: {
        "can_create_invoices": True,
        "can_approve": True,
        "can_delete": True,
        "can_view_reports": True,
        "can_manage_employees": True,
        "can_manage_products": True,
        "can_manage_clients": True,
        "can_manage_accounting": True,
        "can_manage_payroll": True,
        "can_export_data": True,
    },
    CompanyRole.ADMIN: {
        "can_create_invoices": True,
        "can_approve": True,
        "can_delete": True,
        "can_view_reports": True,
        "can_manage_employees": True,
        "can_manage_products": True,
        "can_manage_clients": True,
        "can_manage_accounting": True,
        "can_manage_payroll": True,
        "can_export_data": True,
    },
    CompanyRole.ACCOUNTANT: {
        "can_create_invoices": True,
        "can_approve": True,
        "can_delete": False,
        "can_view_reports": True,
        "can_manage_employees": False,
        "can_manage_products": False,
        "can_manage_clients": True,
        "can_manage_accounting": True,
        "can_manage_payroll": False,
        "can_export_data": True,
    },
    CompanyRole.VIEWER: {
        "can_create_invoices": False,
        "can_approve": False,
        "can_delete": False,
        "can_view_reports": True,
        "can_manage_employees": False,
        "can_manage_products": False,
        "can_manage_clients": False,
        "can_manage_accounting": False,
        "can_manage_payroll": False,
        "can_export_data": False,
    },
    CompanyRole.SALES: {
        "can_create_invoices": True,
        "can_approve": False,
        "can_delete": False,
        "can_view_reports": True,
        "can_manage_employees": False,
        "can_manage_products": True,
        "can_manage_clients": True,
        "can_manage_accounting": False,
        "can_manage_payroll": False,
        "can_export_data": True,
    },
    CompanyRole.HR_MANAGER: {
        "can_create_invoices": False,
        "can_approve": False,
        "can_delete": False,
        "can_view_reports": True,
        "can_manage_employees": True,
        "can_manage_products": False,
        "can_manage_clients": False,
        "can_manage_accounting": False,
        "can_manage_payroll": True,
        "can_export_data": True,
    },
}


class UserCompanyRole(Base):
    """
    Modelo de Rol de Usuario por Empresa.

    Permite que un usuario tenga diferentes roles en diferentes empresas,
    con permisos granulares configurables por rol y empresa.
    """
    __tablename__ = "user_company_roles"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario al que se asigna el rol",
    )
    company_id: Mapped[str] = mapped_column(
        PG_UUID(),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la empresa en la que el usuario tiene el rol",
    )
    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Rol del usuario en la empresa (owner, admin, accountant, viewer, sales, hr_manager)",
    )
    permissions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Permisos granulares en formato JSON",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si la asignación de rol está activa",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de creación del registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha de última actualización",
    )

    # Restricción única: un usuario solo puede tener un rol por empresa
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company_roles_user_id_company_id"),
    )

    # Relaciones
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="company_roles",
        lazy="selectin",
    )
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company",
        back_populates="user_roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserCompanyRole(id={self.id}, user_id={self.user_id}, company_id={self.company_id}, role={self.role})>"

    def get_permissions(self) -> dict[str, bool]:
        """
        Obtiene los permisos como diccionario.
        Si no hay permisos configurados, retorna los permisos por defecto del rol.
        """
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except (json.JSONDecodeError, TypeError):
                pass
        # Retornar permisos por defecto según el rol
        try:
            role_enum = CompanyRole(self.role)
            return DEFAULT_PERMISSIONS.get(role_enum, {}).copy()
        except ValueError:
            return {}

    def set_permissions(self, perms: dict[str, bool]) -> None:
        """Establece los permisos desde un diccionario, serializándolos a JSON"""
        self.permissions = json.dumps(perms)

    def has_permission(self, permission_name: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico en esta empresa.

        Args:
            permission_name: Nombre del permiso a verificar (ej: 'can_create_invoices')

        Returns:
            True si tiene el permiso, False en caso contrario
        """
        perms = self.get_permissions()
        return perms.get(permission_name, False)
