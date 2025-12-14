# 🔧 Фінальне виправлення Railway

## ❌ Проблема

Railway не може визначити Python проект, навіть якщо є `requirements_api.txt`.

## ✅ Рішення

### Варіант 1: Використайте `requirements.txt` (⭐ Рекомендовано)

Railway автоматично визначає Python проект, якщо є файл `requirements.txt` (не `requirements_api.txt`).

**Я створив `requirements.txt`** - спробуйте перезапустити деплой!

---

### Варіант 2: Налаштуйте вручну

1. **Settings → Build → Builder:** `Nixpacks` (не Railpack!)
2. **Settings → Source → Root Directory:** `sensor-api-server`
3. **Settings → Build → Build Command:** `pip install -r requirements.txt`
4. **Settings → Deploy → Start Command:** `python sensor_api_server.py`

---

### Варіант 3: Створіть Dockerfile

Якщо нічого не допомагає, створіть `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sensor_api_server.py .

EXPOSE 5000

CMD ["python", "sensor_api_server.py"]
```

Потім в Railway:
- **Settings → Build → Builder:** `Dockerfile`

---

## 📋 Перевірка

Переконайтеся, що в `sensor-api-server/` є:

- ✅ `requirements.txt` (не `requirements_api.txt` для автоматичного визначення)
- ✅ `Procfile` з `web: python sensor_api_server.py`
- ✅ `sensor_api_server.py`
- ✅ `.python-version` або `runtime.txt`

---

## 🚀 Спробуйте зараз

1. **Перезапустіть деплой** (Redeploy)
2. Railway має автоматично визначити Python проект через `requirements.txt`

---

## 💡 Порада

Railway (Railpack) шукає стандартні файли:
- `requirements.txt` - для Python
- `package.json` - для Node.js
- `go.mod` - для Go
- тощо

Якщо файл називається по-іншому (`requirements_api.txt`), Railway може не визначити проект автоматично.

