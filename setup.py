from setuptools import setup, find_packages

setup(
    name="smart-parking-sensor-api",
    version="1.0.0",
    description="REST API сервер для генерації емульованих даних сенсорів",
    author="Smart Parking System",
    py_modules=["sensor_api_server"],
    install_requires=[
        "Flask==3.0.0",
        "flask-cors==4.0.0",
        "firebase-admin==6.5.0",
        "gunicorn==21.2.0",
    ],
    python_requires=">=3.10",
)

