# 🚀 Швидкий деплой на Railway.app

## ⚡ 5 хвилин до деплою

### Крок 1: Створіть обліковий запис
https://railway.app → Sign up (через GitHub)

### Крок 2: Створіть новий проект
1. New Project → Deploy from GitHub repo
2. Виберіть ваш репозиторій `SmartParkingSystem`
3. Railway автоматично визначить Python проект

### Крок 3: Налаштуйте деплой
1. Settings → Source → Root Directory: `sensor-api-server`
2. Settings → Deploy → Start Command: `python sensor_api_server.py`

### Крок 4: Отримайте URL
1. Settings → Networking → Generate Domain
2. Скопіюйте URL (наприклад: `https://your-app.railway.app`)

### Крок 5: Оновіть Android додаток

**ApiClient.kt:**
```kotlin
private const val BASE_URL = "https://your-app.railway.app/"
```

**SensorDataStream.kt:**
```kotlin
private val baseUrl: String = "https://your-app.railway.app"
```

### Крок 6: Firebase (якщо потрібно)

1. Variables → Add Variable
2. Name: `FIREBASE_CREDENTIALS`
3. Value: вміст вашого `firebase-credentials.json` файлу

---

## ✅ Готово!

Тепер ваш сервер доступний з будь-якої мережі!

**Перевірка:**
```
https://your-app.railway.app/api/health
```

Має показати: `{"status": "ok", ...}`

---

## 💡 Поради

- ✅ Railway автоматично перезапускає при push в GitHub
- ✅ Безкоштовний tier: 500 годин/місяць
- ✅ Автоматичний HTTPS
- ✅ Логи доступні в Railway dashboard

---

## 🔄 Оновлення коду

Просто зробіть `git push` - Railway автоматично задеплоїть нову версію!

