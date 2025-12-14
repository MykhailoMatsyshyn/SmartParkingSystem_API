# 🚀 Деплой Python сервера

## ✅ Переваги деплою

- ✅ Доступний з будь-якої мережі (не потрібна одна Wi-Fi)
- ✅ Не потрібно налаштовувати firewall
- ✅ Стабільна IP адреса (не змінюється)
- ✅ Працює 24/7 (якщо використовуєте платний план)

---

## 🎯 Варіанти деплою

### 1. Railway.app (⭐ Рекомендовано - найпростіший)

**Переваги:**

- ✅ Безкоштовний tier (500 годин/місяць)
- ✅ Простий деплой через GitHub
- ✅ Автоматичний HTTPS
- ✅ Автоматичні деплої при push

**Інструкція:**

1. **Створіть обліковий запис:** https://railway.app

2. **Створіть новий проект:**

   - New Project → Deploy from GitHub repo
   - Виберіть ваш репозиторій

3. **Додайте файл `Procfile`** в `sensor-api-server/`:

   ```
   web: python sensor_api_server.py
   ```

4. **Оновіть `sensor_api_server.py`** - додайте підтримку змінної `PORT`:

   ```python
   import os

   # В кінці файлу замість:
   # app.run(host='0.0.0.0', port=5000, debug=True)

   # Використайте:
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port, debug=False)
   ```

5. **Railway автоматично:**

   - Встановить залежності з `requirements_api.txt`
   - Запустить сервер
   - Надасть публічну URL (наприклад: `https://your-app.railway.app`)

6. **Оновіть `ApiClient.kt`:**
   ```kotlin
   private const val BASE_URL = "https://your-app.railway.app/"
   ```

---

### 2. Render.com (⭐ Також простий)

**Переваги:**

- ✅ Безкоштовний tier
- ✅ Автоматичний HTTPS
- ✅ Простий деплой

**Інструкція:**

1. **Створіть обліковий запис:** https://render.com

2. **Створіть новий Web Service:**

   - New → Web Service
   - Connect GitHub repo
   - Виберіть ваш репозиторій

3. **Налаштування:**

   - **Build Command:** `pip install -r sensor-api-server/requirements_api.txt`
   - **Start Command:** `cd sensor-api-server && python sensor_api_server.py`
   - **Environment:** Python 3

4. **Додайте змінну середовища:**

   - `PORT` = `5000` (Render автоматично надасть порт)

5. **Оновіть `sensor_api_server.py`** (як для Railway)

6. **Отримайте URL:** `https://your-app.onrender.com`

---

### 3. PythonAnywhere (⭐ Спеціально для Python)

**Переваги:**

- ✅ Безкоштовний tier
- ✅ Простий для Python
- ⚠️ Трохи складніший налаштування

**Інструкція:**

1. **Створіть обліковий запис:** https://www.pythonanywhere.com

2. **Завантажте файли:**

   - Files → Upload файли з `sensor-api-server/`

3. **Створіть Web App:**

   - Web → Add a new web app
   - Flask → Python 3.10
   - Вкажіть шлях до `sensor_api_server.py`

4. **Налаштуйте WSGI:**

   ```python
   import sys
   path = '/home/yourusername/sensor-api-server'
   if path not in sys.path:
       sys.path.append(path)

   from sensor_api_server import app as application
   ```

5. **Отримайте URL:** `https://yourusername.pythonanywhere.com`

---

### 4. Fly.io (⭐ Швидкий)

**Переваги:**

- ✅ Безкоштовний tier
- ✅ Швидкий деплой
- ⚠️ Потрібен Dockerfile

**Інструкція:**

1. **Встановіть Fly CLI:**

   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Створіть `Dockerfile`** в `sensor-api-server/`:

   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app
   COPY requirements_api.txt .
   RUN pip install --no-cache-dir -r requirements_api.txt

   COPY sensor_api_server.py .

   EXPOSE 5000
   CMD ["python", "sensor_api_server.py"]
   ```

3. **Деплой:**
   ```bash
   cd sensor-api-server
   fly launch
   ```

---

## 🔧 Оновлення коду для деплою

### 1. Оновіть `sensor_api_server.py`:

```python
import os

# В кінці файлу замість:
# app.run(host='0.0.0.0', port=5000, debug=True)

# Використайте:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### 2. Додайте `Procfile` (для Railway/Heroku):

```
web: python sensor_api_server.py
```

### 3. Оновіть `requirements_api.txt` (якщо потрібно):

```
flask==3.0.0
flask-cors==4.0.0
firebase-admin==6.5.0
gunicorn==21.2.0  # Для production
```

### 4. Для production додайте gunicorn:

**Оновіть `Procfile`:**

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT sensor_api_server:app
```

---

## 📱 Оновлення Android додатку

Після деплою оновіть `ApiClient.kt`:

```kotlin
// Для Railway
private const val BASE_URL = "https://your-app.railway.app/"

// Для Render
private const val BASE_URL = "https://your-app.onrender.com/"

// Для PythonAnywhere
private const val BASE_URL = "https://yourusername.pythonanywhere.com/"
```

Також оновіть `SensorDataStream.kt`:

```kotlin
private val baseUrl: String = "https://your-app.railway.app"
```

---

## ⚠️ Важливо для Firebase

Якщо використовуєте Firebase, потрібно:

1. **Завантажити `firebase-credentials.json`** на сервер
2. **Додати як змінну середовища** (безпечніше) або
3. **Використати секрети платформи** (Railway Secrets, Render Environment Variables)

**Для Railway:**

- Variables → Add Variable
- `FIREBASE_CREDENTIALS` = вміст JSON файлу

**Для Render:**

- Environment → Add Environment Variable
- `FIREBASE_CREDENTIALS` = вміст JSON файлу

**Оновіть код:**

```python
import os
import json

# Замість:
# cred = credentials.Certificate('firebase-credentials.json')

# Використайте:
firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_creds:
    cred_data = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_data)
else:
    # Fallback на файл (для локальної розробки)
    if os.path.exists('firebase-credentials.json'):
        cred = credentials.Certificate('firebase-credentials.json')
```

---

## 🎯 Рекомендація

**Для швидкого тестування:** Railway.app або Render.com

- Найпростіший деплой
- Безкоштовний tier
- Автоматичний HTTPS

**Для production:** Railway.app (платний план)

- Стабільність
- Більше ресурсів
- Підтримка

---

## 📋 Швидкий старт (Railway)

1. Створіть обліковий запис на https://railway.app
2. New Project → Deploy from GitHub
3. Додайте `Procfile` в `sensor-api-server/`
4. Оновіть `sensor_api_server.py` (додайте підтримку PORT)
5. Railway автоматично задеплоїть
6. Оновіть `BASE_URL` в Android додатку

**Готово!** 🎉
