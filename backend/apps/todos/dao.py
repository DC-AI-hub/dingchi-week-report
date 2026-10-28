from calendar import monthrange

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone

from .models import TodoItem


def ensure_item(recipient_id, role_code, dedupe_key, **fields):
    item, created = TodoItem.objects.get_or_create(
        recipient_id=recipient_id, role_code=role_code, dedupe_key=dedupe_key, defaults=fields
    )
    if created:
        return item
    changed = []
    if item.title != fields["title"]:
        item.title = fields["title"]
        changed.append("title")
    if item.status == "completed":
        item.status, item.read_at, item.completed_at = "pending", None, None
        changed.extend(["status", "read_at", "completed_at"])
    if changed:
        item.save(update_fields=[*changed, "updated_at"])
    return item


def complete_key(recipient_id, role_code, dedupe_key):
    return TodoItem.objects.filter(
        recipient_id=recipient_id, role_code=role_code, dedupe_key=dedupe_key, status="pending"
    ).update(status="completed", completed_at=timezone.now(), updated_at=timezone.now())


def complete_stale(recipient_id, role_code, source, active_keys):
    return (
        TodoItem.objects.filter(
            recipient_id=recipient_id, role_code=role_code, source=source, status="pending"
        )
        .exclude(dedupe_key__in=active_keys)
        .update(status="completed", completed_at=timezone.now(), updated_at=timezone.now())
    )


def read_history_cutoff():
    now = timezone.now()
    month_index = now.year * 12 + now.month - 1 - 3
    year, month = divmod(month_index, 12)
    month += 1
    return now.replace(year=year, month=month, day=min(now.day, monthrange(year, month)[1]))


def paginated_items(recipient_id, role_code, page):
    rows = (
        TodoItem.objects.filter(
            recipient_id=recipient_id,
            role_code__in=[role_code] if isinstance(role_code, str) else role_code,
            status="pending",
        )
        .filter(Q(read_at__isnull=True) | Q(created_at__gte=read_history_cutoff()))
        .annotate(
            read_priority=Case(
                When(read_at__isnull=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("read_priority", "-created_at", "-id")
    )
    return rows.count(), list(rows[(page - 1) * 10 : page * 10])


def unread_count(recipient_id, role_code):
    return TodoItem.objects.filter(
        recipient_id=recipient_id,
        role_code__in=[role_code] if isinstance(role_code, str) else role_code,
        status="pending",
        read_at__isnull=True,
    ).count()


def mark_read(recipient_id, role_code, item_id):
    rows = TodoItem.objects.filter(
        id=item_id,
        recipient_id=recipient_id,
        role_code__in=[role_code] if isinstance(role_code, str) else role_code,
    )
    if not rows.exists():
        raise LookupError("待办事项不存在。")
    rows.filter(read_at__isnull=True).update(read_at=timezone.now(), updated_at=timezone.now())
    return rows.get()
