"""Django 管理命令：清理过期回收站记录"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Student
from core.utils import delete_media_files


class Command(BaseCommand):
    help = '清理回收站中超过10天的记录'

    def handle(self, *args, **options):
        expired = Student.objects.filter(
            is_deleted=True,
            restore_deadline__lt=timezone.now()
        )
        count = expired.count()
        for student in expired:
            delete_media_files(student.media_files.all())
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f'已清理 {count} 条过期回收站记录'))
