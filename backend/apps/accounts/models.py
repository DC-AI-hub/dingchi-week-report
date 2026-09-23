"""Logical organization models.

The project intentionally does not declare Django ForeignKey fields.  All
relationships are logical IDs so organizational data can be synchronized from
an external HR system without database-level coupling.
"""

from django.db import models

from apps.core.models.base import SnowflakeIdModel
from apps.core.security.fields import EncryptedPasswordField


class OrganizationGroup(SnowflakeIdModel):
    group_code = models.CharField(max_length=64, unique=True)
    group_name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, default="")
    parent_group_id = models.BigIntegerField(null=True, blank=True)
    is_system = models.BooleanField(default=False)
    status = models.CharField(max_length=16, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organization_group"
        ordering = ["group_code"]


class Role(SnowflakeIdModel):
    role_code = models.CharField(max_length=64, unique=True)
    role_name = models.CharField(max_length=128)
    scope = models.CharField(max_length=16, default="self")
    description = models.CharField(max_length=255, blank=True, default="")
    # 角色可以暂不绑定模板；填写或查看周报时由业务层明确提示配置模板，
    # 不再隐式落到已经废弃的通用周报页面。
    report_template_code = models.CharField(max_length=64, blank=True, default="")
    role_group_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="角色所属分组编码，逻辑关联 organization_group.group_code。",
    )
    status = models.CharField(max_length=16, default="active")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "role"
        ordering = ["sort_order", "id"]


class UserAccount(SnowflakeIdModel):
    username = models.CharField(max_length=64, unique=True)
    employee_no = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=128)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")
    password_ciphertext = EncryptedPasswordField()
    manager_id = models.BigIntegerField(null=True, blank=True)
    group_id = models.BigIntegerField(null=True, blank=True)
    avatar_color = models.CharField(max_length=16, default="#2f80ed")
    status = models.CharField(max_length=16, default="active")
    is_demo = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_account"
        ordering = ["employee_no"]


class UserRole(SnowflakeIdModel):
    user_id = models.BigIntegerField()
    role_id = models.BigIntegerField()
    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=16, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_role"
        constraints = [
            models.UniqueConstraint(fields=["user_id", "role_id"], name="uq_user_role_pair"),
        ]


class UserGroupMembership(SnowflakeIdModel):
    """Optional multi-group membership while UserAccount keeps a primary group."""

    user_id = models.BigIntegerField()
    group_id = models.BigIntegerField()
    is_primary = models.BooleanField(default=False)
    status = models.CharField(max_length=16, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_group_membership"
        constraints = [
            models.UniqueConstraint(fields=["user_id", "group_id"], name="uq_user_group_pair"),
        ]
