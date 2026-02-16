from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        p = get_redis_connection("default").pubsub()
        p.subscribe('comments')
        self.stdout.write("Listening for comments...")
        for m in p.listen():
            if m['type'] == 'message': print(f"New: {m['data'].decode()}")
