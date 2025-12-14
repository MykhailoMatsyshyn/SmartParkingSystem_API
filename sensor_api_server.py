"""
Простий REST API сервер для генерації емульованих даних сенсорів
Запуск: python sensor_api_server.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import random
import time
import os
import logging
from datetime import datetime

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Ініціалізація Firebase (якщо є credentials)
    FIREBASE_ENABLED = False
    db = None
    
    if os.path.exists('firebase-credentials.json'):
        try:
            # Перевіряємо, чи файл правильний
            with open('firebase-credentials.json', 'r') as f:
                cred_data = json.load(f)
                if cred_data.get('type') == 'service_account':
                    cred = credentials.Certificate('firebase-credentials.json')
                    firebase_admin.initialize_app(cred)
                    db = firestore.client()
                    FIREBASE_ENABLED = True
                    print("✅ Firebase підключено")
                else:
                    print("⚠️  firebase-credentials.json не є Service Account key (type != 'service_account')")
                    print("   Отримайте Service Account key з Firebase Console → Project Settings → Service accounts")
        except json.JSONDecodeError:
            print("⚠️  firebase-credentials.json не є валідним JSON файлом")
        except Exception as e:
            print(f"⚠️  Помилка ініціалізації Firebase: {e}")
            print("   Перевірте правильність firebase-credentials.json")
    else:
        print("⚠️  Firebase не налаштовано (firebase-credentials.json не знайдено)")
        print("   Сервер працюватиме без синхронізації з Firebase")
        
except ImportError:
    FIREBASE_ENABLED = False
    db = None
    print("⚠️  Firebase Admin SDK не встановлено. Встановіть: pip install firebase-admin")
    print("   Сервер працюватиме без синхронізації з Firebase")

app = Flask(__name__)
CORS(app)  # Дозволяє запити з мобільного додатку

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Додаємо middleware для логування всіх запитів
@app.before_request
def log_request_info():
    """Логує інформацію про вхідний запит"""
    logger.info(f"📥 {request.method} {request.path}")
    logger.info(f"   IP: {request.remote_addr}")
    if request.is_json:
        logger.info(f"   Body: {json.dumps(request.get_json(), indent=2)}")
    elif request.args:
        logger.info(f"   Query params: {dict(request.args)}")

@app.after_request
def log_response_info(response):
    """Логує інформацію про відповідь"""
    logger.info(f"📤 {request.method} {request.path} → {response.status_code}")
    if response.is_json:
        try:
            data = response.get_json()
            # Обмежуємо розмір логу для великих відповідей
            if isinstance(data, dict) and 'parking_sensors' in data:
                log_data = {**data, 'parking_sensors': f"[{len(data['parking_sensors'])} elements]"}
            else:
                log_data = data
            logger.info(f"   Response: {json.dumps(log_data, indent=2)}")
        except:
            pass
    return response

# Стан системи для реалістичної поведінки
state = {
    'free_spots': 50,
    'co_level': 50.0,
    'nox_level': 30.0,
    'temperature': 15.0,
    'time_counter': 0
}

# Стан пристроїв (Компонент 3)
device_states = {
    'direction_panels_1': {
        'device_id': 'direction_panels_1',
        'device_type': 'DIRECTION_PANELS',
        'enabled': False,
        'brightness': 50,
        'last_updated': int(time.time() * 1000)
    },
    'ventilation_1': {
        'device_id': 'ventilation_1',
        'device_type': 'VENTILATION',
        'enabled': False,
        'fan_speed': 1,
        'last_updated': int(time.time() * 1000)
    },
    'heating_1': {
        'device_id': 'heating_1',
        'device_type': 'HEATING',
        'enabled': False,
        'heating_power': 1,
        'last_updated': int(time.time() * 1000)
    }
}

def generate_sensor_data():
    """Генерує наступні дані сенсорів з реалістичною поведінкою"""
    state['time_counter'] += 1
    
    # Генеруємо вільні місця
    change = random.randint(-3, 3)
    state['free_spots'] = max(0, min(100, state['free_spots'] + change))
    
    # Генеруємо CO залежно від кількості машин
    occupied_spots = 100 - state['free_spots']
    base_co = (occupied_spots / 100.0) * 200.0 + 20.0
    noise = random.uniform(-10, 10)
    anomaly = random.uniform(-50, 50) if random.random() < 0.05 else 0
    state['co_level'] = max(0, min(500, base_co + noise + anomaly))
    
    # Генеруємо NOx
    base_nox = (occupied_spots / 100.0) * 150.0 + 15.0
    noise = random.uniform(-8, 8)
    state['nox_level'] = max(0, min(500, base_nox + noise))
    
    # Генеруємо температуру (симуляція денного циклу)
    day_progress = (state['time_counter'] % 17280) / 17280.0
    if day_progress < 0.25:
        day_temp = -10 + day_progress * 60
    elif day_progress < 0.5:
        day_temp = 5 + (day_progress - 0.25) * 80
    elif day_progress < 0.75:
        day_temp = 25 + (day_progress - 0.5) * 60
    else:
        day_temp = 40 - (day_progress - 0.75) * 120
    
    co_effect = (state['co_level'] / 500.0) * 5.0
    noise = random.uniform(-2, 2)
    state['temperature'] = max(-10, min(40, day_temp + co_effect + noise))
    
    # Генеруємо масив датчиків для кожного місця парковки (100 місць)
    # 0 = вільне місце, 1 = зайняте місце
    parking_sensors = [0] * 100
    occupied_indices = random.sample(range(100), occupied_spots)
    for idx in occupied_indices:
        parking_sensors[idx] = 1
    
    # Додаємо невеликий шум (можливість зміни стану окремих місць)
    for i in range(100):
        if random.random() < 0.05:  # 5% шанс зміни стану
            parking_sensors[i] = 1 - parking_sensors[i]
    
    # Обчислюємо похідні значення
    parking_occupied = occupied_spots / 100.0
    
    return {
        'timestamp': int(time.time() * 1000),
        'parking_sensors': parking_sensors,  # Масив з 100 елементів [0,1,0,1,1,...]
        'parking_occupied': parking_occupied,
        'free_spots': state['free_spots'],
        'co_level': round(state['co_level'], 2),
        'nox_level': round(state['nox_level'], 2),
        'temperature': round(state['temperature'], 2)
    }

@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    """Endpoint для отримання поточних даних сенсорів"""
    logger.info("🔍 Генерую дані сенсорів...")
    data = generate_sensor_data()
    logger.info(f"✅ Дані згенеровано: free_spots={data['free_spots']}, co={data['co_level']}, temp={data['temperature']}")
    return jsonify(data)

@app.route('/api/sensor-data/stream', methods=['GET'])
def stream_sensor_data():
    """Endpoint для потокової передачі даних (SSE)"""
    logger.info("🌊 SSE stream підключено")
    def generate():
        counter = 0
        while True:
            try:
                counter += 1
                logger.info(f"📡 Генерую дані для SSE (пакет #{counter})...")
                data = generate_sensor_data()
                json_data = json.dumps(data)
                logger.info(f"✅ Відправляю SSE пакет #{counter}: free_spots={data['free_spots']}, co={data['co_level']}")
                yield f"data: {json_data}\n\n"
                time.sleep(5)  # Оновлення кожні 5 секунд
            except GeneratorExit:
                logger.info("🔌 SSE stream закрито клієнтом")
                break
            except Exception as e:
                logger.error(f"❌ Помилка в SSE stream: {e}")
                yield f"error: {str(e)}\n\n"
                break
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream'
    )

# ========== Компонент 3: Керування пристроями ==========

@app.route('/api/devices', methods=['GET'])
def get_all_devices():
    """Отримати стан всіх пристроїв"""
    logger.info("📋 Запит на отримання всіх пристроїв")
    devices = list(device_states.values())
    logger.info(f"✅ Повертаю {len(devices)} пристроїв")
    for device in devices:
        logger.info(f"   - {device['device_id']}: enabled={device['enabled']}, type={device['device_type']}")
    return jsonify({
        'devices': devices
    })

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Отримати стан конкретного пристрою"""
    logger.info(f"🔍 Запит на отримання пристрою: {device_id}")
    if device_id not in device_states:
        logger.warning(f"❌ Пристрій не знайдено: {device_id}")
        return jsonify({'error': 'Device not found'}), 404
    
    device = device_states[device_id]
    logger.info(f"✅ Знайдено пристрій: {device_id}, enabled={device['enabled']}, type={device['device_type']}")
    return jsonify(device)

def sync_device_to_firebase(device):
    """Синхронізувати стан пристрою з Firebase"""
    if FIREBASE_ENABLED and db:
        try:
            logger.info(f"☁️  Синхронізую пристрій з Firebase: {device['device_id']}")
            # Підготовка даних для Firebase
            firebase_data = {
                'device_id': device['device_id'],
                'device_type': device['device_type'],
                'enabled': device['enabled'],
                'last_updated': device['last_updated'],
                'synced': True
            }
            
            # Додаємо специфічні поля залежно від типу
            if device['device_type'] == 'DIRECTION_PANELS':
                firebase_data['brightness'] = device['brightness']
                logger.info(f"   Дані: enabled={device['enabled']}, brightness={device['brightness']}")
            elif device['device_type'] == 'VENTILATION':
                firebase_data['fan_speed'] = device['fan_speed']
                logger.info(f"   Дані: enabled={device['enabled']}, fan_speed={device['fan_speed']}")
            elif device['device_type'] == 'HEATING':
                firebase_data['heating_power'] = device['heating_power']
                logger.info(f"   Дані: enabled={device['enabled']}, heating_power={device['heating_power']}")
            
            # Зберігаємо в Firebase
            db.collection('device_states').document(device['device_id']).set(firebase_data)
            logger.info(f"✅ Успішно синхронізовано з Firebase: {device['device_id']}")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка синхронізації з Firebase: {e}")
            return False
    else:
        logger.debug("⚠️  Firebase не увімкнено, пропускаю синхронізацію")
    return False

def load_devices_from_firebase():
    """Завантажити стани пристроїв з Firebase при старті"""
    if FIREBASE_ENABLED and db:
        try:
            logger.info("📥 Завантажую стани пристроїв з Firebase...")
            devices_ref = db.collection('device_states')
            docs = devices_ref.stream()
            
            loaded_count = 0
            for doc in docs:
                data = doc.to_dict()
                device_id = data.get('device_id')
                
                if device_id and device_id in device_states:
                    # Оновлюємо локальний стан з Firebase
                    old_enabled = device_states[device_id]['enabled']
                    device_states[device_id]['enabled'] = data.get('enabled', False)
                    device_states[device_id]['last_updated'] = data.get('last_updated', int(time.time() * 1000))
                    
                    if device_states[device_id]['device_type'] == 'DIRECTION_PANELS':
                        device_states[device_id]['brightness'] = data.get('brightness', 50)
                        logger.info(f"   Завантажено {device_id}: enabled={device_states[device_id]['enabled']}, brightness={device_states[device_id]['brightness']}")
                    elif device_states[device_id]['device_type'] == 'VENTILATION':
                        device_states[device_id]['fan_speed'] = data.get('fan_speed', 1)
                        logger.info(f"   Завантажено {device_id}: enabled={device_states[device_id]['enabled']}, fan_speed={device_states[device_id]['fan_speed']}")
                    elif device_states[device_id]['device_type'] == 'HEATING':
                        device_states[device_id]['heating_power'] = data.get('heating_power', 1)
                        logger.info(f"   Завантажено {device_id}: enabled={device_states[device_id]['enabled']}, heating_power={device_states[device_id]['heating_power']}")
                    
                    loaded_count += 1
            
            logger.info(f"✅ Завантажено {loaded_count} пристроїв з Firebase")
            return True
        except Exception as e:
            logger.error(f"⚠️  Не вдалося завантажити з Firebase: {e}")
            return False
    return False

@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Змінити стан пристрою"""
    logger.info(f"🔄 Оновлення пристрою: {device_id}")
    
    if device_id not in device_states:
        logger.warning(f"❌ Пристрій не знайдено: {device_id}")
        return jsonify({'error': 'Device not found'}), 404
    
    device = device_states[device_id]
    data = request.get_json()
    logger.info(f"   Отримано дані: {json.dumps(data, indent=2)}")
    
    # Зберігаємо старі значення для логування
    old_state = {
        'enabled': device['enabled'],
        'last_updated': device['last_updated']
    }
    if device['device_type'] == 'DIRECTION_PANELS':
        old_state['brightness'] = device['brightness']
    elif device['device_type'] == 'VENTILATION':
        old_state['fan_speed'] = device['fan_speed']
    elif device['device_type'] == 'HEATING':
        old_state['heating_power'] = device['heating_power']
    
    # Оновлюємо стан залежно від типу пристрою
    if device['device_type'] == 'DIRECTION_PANELS':
        if 'enabled' in data:
            device['enabled'] = bool(data['enabled'])
        if 'brightness' in data:
            device['brightness'] = max(0, min(100, int(data['brightness'])))
        logger.info(f"   Зміни: enabled {old_state['enabled']} → {device['enabled']}, brightness {old_state.get('brightness')} → {device['brightness']}")
    
    elif device['device_type'] == 'VENTILATION':
        if 'enabled' in data:
            device['enabled'] = bool(data['enabled'])
        if 'fan_speed' in data:
            device['fan_speed'] = max(1, min(3, int(data['fan_speed'])))
        logger.info(f"   Зміни: enabled {old_state['enabled']} → {device['enabled']}, fan_speed {old_state.get('fan_speed')} → {device['fan_speed']}")
    
    elif device['device_type'] == 'HEATING':
        if 'enabled' in data:
            device['enabled'] = bool(data['enabled'])
        if 'heating_power' in data:
            device['heating_power'] = max(1, min(2, int(data['heating_power'])))
        logger.info(f"   Зміни: enabled {old_state['enabled']} → {device['enabled']}, heating_power {old_state.get('heating_power')} → {device['heating_power']}")
    
    device['last_updated'] = int(time.time() * 1000)
    
    # Синхронізуємо з Firebase
    sync_success = sync_device_to_firebase(device)
    
    logger.info(f"✅ Пристрій оновлено: {device_id}, Firebase sync: {sync_success}")
    
    return jsonify({
        **device,
        'status': 'updated',
        'firebase_synced': sync_success
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Перевірка стану сервера"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("\n" + "="*50)
    logger.info("  Smart Parking System API Server")
    logger.info("="*50)
    
    # Завантажуємо стани пристроїв з Firebase при старті
    if FIREBASE_ENABLED:
        load_devices_from_firebase()
    
    logger.info("\n\nКомпонент 1: Дані сенсорів")
    logger.info("  - GET  http://localhost:5000/api/sensor-data")
    logger.info("  - GET  http://localhost:5000/api/sensor-data/stream (SSE)")
    logger.info("\n\nКомпонент 3: Керування пристроями")
    logger.info("  - GET  http://localhost:5000/api/devices")
    logger.info("  - GET  http://localhost:5000/api/devices/{deviceId}")
    logger.info("  - PUT  http://localhost:5000/api/devices/{deviceId}")
    if FIREBASE_ENABLED:
        logger.info("  - ✅ Синхронізація з Firebase увімкнена")
    else:
        logger.info("  - ⚠️  Синхронізація з Firebase вимкнена")
    logger.info("\n" + "="*50)
    
    # Підтримка змінної PORT для деплою (Railway, Render, Heroku тощо)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Сервер запущено на http://0.0.0.0:{port}")
    logger.info(f"📝 Логи активні - всі запити будуть відображатися")
    logger.info(f"🔧 Debug mode: {debug}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

