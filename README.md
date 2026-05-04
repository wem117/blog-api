# HW4 Verification

1. **Proxy check**: `curl -I http://localhost/admin/login/`
   Должно быть `200 OK` и заголовок `Server: nginx/...`.

2. **Static check**: `curl -I http://localhost/static/admin/css/base.css`
   Должно быть `200 OK` и `Cache-Control: max-age=2592000` (или 30 days).

3. **API check**: `curl http://localhost/api/posts/`
   Должен прийти JSON со списком постов.

4. **502 check**: 
   `docker compose stop web`
   `curl -I http://localhost/api/posts/` -> должно быть `502 Bad Gateway`.
   После проверки: `docker compose start web`.

5. **Port 8000 check**: `curl http://localhost:8000/`
   Должно быть `Connection refused`.

6. **WebSockets check**:
   `wscat -c "ws://localhost/ws/posts/<slug>/comments/?token=<jwt>"`
   Должен быть статус `101 Switching Protocols`.
