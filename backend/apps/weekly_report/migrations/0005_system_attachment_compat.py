from django.db import migrations


def _copy_legacy_weekly_attachments(apps, schema_editor):
    """为已经执行旧版 0004 迁移的数据库补迁周报附件。"""
    table_names = {
        str(name).lower() for name in schema_editor.connection.introspection.table_names()
    }
    if "weekly_report_attachment" not in table_names:
        return
    insert_ignore = (
        "INSERT OR IGNORE"
        if schema_editor.connection.vendor == "sqlite"
        else "INSERT IGNORE"
    )
    schema_editor.execute(
        f"""
        {insert_ignore} INTO system_attachment
            (id, attachment_type, relation_id, relation_sub_id, storage_key,
             file_url, file_name, mime_type, file_size, description,
             created_at, updated_at)
        SELECT
            id, 'weekly_report', report_id, item_id, storage_key,
            file_url, file_name, mime_type, file_size, description,
            created_at, updated_at
        FROM weekly_report_attachment
        """
    )


def _noop_reverse(apps, schema_editor):
    """旧表仅作兼容读取，不在回滚时删除通用附件数据。"""


class Migration(migrations.Migration):
    """为旧版周报专用附件表补做通用附件迁移。"""

    dependencies = [("weekly_report", "0004_weekly_report_attachment")]

    operations = [
        migrations.RunPython(
            _copy_legacy_weekly_attachments,
            _noop_reverse,
            hints={"target_db": "default"},
        ),
    ]
