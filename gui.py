#!/usr/bin/env python3
"""
Точка входа для игры про шарики.
Запускает основную игру с графическим интерфейсом.
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from game import main as run_game
    
    if __name__ == "__main__":
        print("🎮 Запуск игры про шарики...")
        run_game()
        
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("💡 Убедитесь, что установлен pygame: pip install pygame")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка запуска игры: {e}")
    sys.exit(1)

