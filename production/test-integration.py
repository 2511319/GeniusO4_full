#!/usr/bin/env python3
"""
Интеграционный тест для ChartGenius Production
Проверяет все компоненты системы
"""

import requests
import json
import time
from typing import Dict, Any

class ChartGeniusIntegrationTest:
    def __init__(self):
        self.api_url = "https://chartgenius-api-169129692197.europe-west1.run.app"
        self.frontend_url = "https://chartgenius-frontend-169129692197.europe-west1.run.app"
        self.bot_url = "https://chartgenius-bot-169129692197.europe-west1.run.app"
        self.results = {}
        
    def test_api_health(self) -> Dict[str, Any]:
        """Тест health endpoint API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
    
    def test_api_testdata(self) -> Dict[str, Any]:
        """Тест testdata endpoint API"""
        try:
            response = requests.get(f"{self.api_url}/testdata", timeout=10)
            return {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "response_size": len(response.content),
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
    
    def test_frontend_static(self) -> Dict[str, Any]:
        """Тест статических файлов frontend"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            return {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', 'unknown'),
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
    
    def test_frontend_build_info(self) -> Dict[str, Any]:
        """Тест build-info frontend"""
        try:
            response = requests.get(f"{self.frontend_url}/build-info.json", timeout=10)
            return {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "build_info": response.json() if response.status_code == 200 else None,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
    
    def test_cors_direct_api(self) -> Dict[str, Any]:
        """Тест прямого вызова API с CORS заголовками"""
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET'
            }
            response = requests.options(f"{self.api_url}/health", headers=headers, timeout=10)
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-credentials': response.headers.get('access-control-allow-credentials')
            }
            return {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code,
                "cors_headers": cors_headers,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск интеграционных тестов ChartGenius Production")
        print("=" * 60)
        
        tests = [
            ("API Health", self.test_api_health),
            ("API TestData", self.test_api_testdata),
            ("Frontend Static", self.test_frontend_static),
            ("Frontend Build Info", self.test_frontend_build_info),
            ("CORS Direct API", self.test_cors_direct_api),
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 Тест: {test_name}")
            result = test_func()
            self.results[test_name] = result
            
            print(f"   Статус: {result['status']}")
            if 'status_code' in result:
                print(f"   HTTP код: {result['status_code']}")
            if 'response_time' in result:
                print(f"   Время ответа: {result['response_time']:.2f}s")
            if 'error' in result:
                print(f"   Ошибка: {result['error']}")
        
        self.print_summary()
    
    def print_summary(self):
        """Печать сводки результатов"""
        print("\n" + "=" * 60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        passed = sum(1 for r in self.results.values() if r['status'] == '✅ PASS')
        failed = sum(1 for r in self.results.values() if r['status'] in ['❌ FAIL', '❌ ERROR'])
        
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {failed}")
        print(f"📈 Успешность: {passed/(passed+failed)*100:.1f}%")
        
        if failed > 0:
            print("\n🔍 ПРОБЛЕМЫ:")
            for test_name, result in self.results.items():
                if result['status'] in ['❌ FAIL', '❌ ERROR']:
                    print(f"   • {test_name}: {result.get('error', 'HTTP ' + str(result.get('status_code', 'unknown')))}")

if __name__ == "__main__":
    test = ChartGeniusIntegrationTest()
    test.run_all_tests()
