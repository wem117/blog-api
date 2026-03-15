import asyncio
import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Listen for comments via Redis'

    async def listen(self):
        r = redis.from_url("redis://localhost:6379/0")
        pubsub = r.pubsub()
        await pubsub.subscribe("comments")
        
        self.stdout.write(self.style.SUCCESS("Listening for comments on 'comments'..."))
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    msg = f"New comment on '{data.get('post_slug')}' by User {data.get('author_id')}: {data.get('body')}"
                    self.stdout.write(self.style.NOTICE(msg))
        except asyncio.CancelledError:
            await pubsub.unsubscribe("comments")
            await r.close()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))

    def handle(self, *args, **options):
        try:
            asyncio.run(self.listen())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nStopped."))
