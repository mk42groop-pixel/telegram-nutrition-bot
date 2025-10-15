import os
import asyncio
import aioschedule
import logging
from datetime import datetime, timedelta
import pytz
import requests
import random

print("🚀 Запускаем систему автоматизации контента...")

# Настройки из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL = '@elixir_life_nutrition'
YANDEX_GPT_API_KEY = os.getenv('YANDEX_GPT_API_KEY')

class SimpleContentGenerator:
    def __init__(self):
        self.weekly_themes = {
            0: '🔬 Научный понедельник',
            1: '👨‍🍳 Техника шефа', 
            2: '❓ Вопрос-Ответ',
            3: '🌟 Рецепт недели',
            4: '🔥 Трендовая пятница',
            5: '⚡ Быстро & Здорово',
            6: '🏆 Воскресный дайджест'
        }
        
        self.meal_types = {
            'breakfast': '🍳 Завтрак',
            'lunch': '🍲 Обед',
            'snack': '🥜 Перекус', 
            'dinner': '🍽️ Ужин'
        }

    def get_fallback_content(self, meal_type, day_theme):
        """Простой контент без использования GPT"""
        
        recipes = {
            'breakfast': [
                "🥚 Белковый омлет с шпинатом\n\nИнгредиенты:\n• 2 яйца\n• 50г шпината\n• 30г творога\n• Специи\n\nПриготовление:\n1. Взбейте яйца с творогом\n2. Обжарьте шпинат\n3. Залейте яичной смесью\n4. Готовьте 5-7 минут",
                "🥣 Овсянка с ягодами\n\nИнгредиенты:\n• 50г овсяных хлопьев\n• 150мл миндального молока\n• Горсть ягод\n• 1 ч.л. меда\n\nПриготовление:\n1. Варите овсянку 10 минут\n2. Добавьте ягоды и мед"
            ],
            'lunch': [
                "🍲 Салат с киноа и авокадо\n\nИнгредиенты:\n• 100г киноа\n• 1 авокадо\n• Помидоры черри\n• Руккола\n• Оливковое масло\n\nПриготовление:\n1. Отварите киноа\n2. Нарежьте овощи\n3. Смешайте с заправкой",
                "🐟 Лосось с овощами\n\nИнгредиенты:\n• 150г лосося\n• Брокколи\n• Морковь\n• Лимон\n\nПриготовление:\n1. Запекайте 20 минут при 180°C\n2. Подавайте с лимоном"
            ],
            'snack': [
                "🥜 Протеиновые шарики\n\nИнгредиенты:\n• 100г овсянки\n• 50г орехов\n• Мед\n• Кокосовая стружка\n\nПриготовление:\n1. Смешайте ингредиенты\n2. Сформируйте шарики\n3. Охладите 30 минут",
                "🍎 Яблоко с миндальным маслом\n\nИнгредиенты:\n• 1 яблоко\n• 2 ст.л. миндального масла\n• Корица\n\nПриготовление:\n1. Нарежьте яблоко\n2. Намажьте маслом\n3. Посыпьте корицей"
            ],
            'dinner': [
                "🍗 Курица с киноа\n\nИнгредиенты:\n• 150г куриной грудки\n• 100г киноа\n• Специи\n• Зелень\n\nПриготовление:\n1. Обжарьте курицу\n2. Отварите киноа\n3. Подавайте с зеленью",
                "🥦 Овощное рагу\n\nИнгредиенты:\n• Кабачок\n• Баклажан\n• Перец\n• Томатный соус\n\nПриготовление:\n1. Тушите овощи 25 минут\n2. Добавьте соус"
            ]
        }
        
        facts = {
            '🔬 Научный понедельник': "💡 Научный факт: Белок из яиц усваивается на 97% - это эталонный протеин!",
            '👨‍🍳 Техника шефа': "👨‍🍳 Техника шефа: Для сочного омлета взбивайте яйца с молоком на водяной бане!",
            '❓ Вопрос-Ответ': "❓ Вопрос: А какой ваш любимый полезный завтрак? Пишите в комментариях!",
            '🌟 Рецепт недели': "🌟 Шеф-совет: Добавьте щепотку мускатного ореха для изысканного аромата!",
            '🔥 Трендовая пятница': "🔥 Тренд: Функциональное питание - когда еда становится лекарством!",
            '⚡ Быстро & Здорово': "⚡ Быстро: Этот рецепт готовится всего за 15 минут!",
            '🏆 Воскресный дайджест': "🏆 Результат: Это блюдо поможет восстановиться после тренировки!"
        }
        
        recipe = random.choice(recipes[meal_type])
        fact = facts[day_theme]
        
        return f"{self.meal_types[meal_type]}\n\n{recipe}\n\n{fact}\n\n👇 Поделитесь вашим результатом в комментариях!"

class TelegramBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.channel = TELEGRAM_CHANNEL

    def send_message(self, text):
        """Отправка сообщения в канал"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.channel,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, data=data)
            print(f"✅ Сообщение отправлено: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")

class ContentScheduler:
    def __init__(self):
        self.generator = SimpleContentGenerator()
        self.bot = TelegramBot()
        self.kemerovo_tz = pytz.timezone('Asia/Novosibirsk')
        
        # Расписание публикаций
        self.schedule = {
            'breakfast': '09:00',
            'lunch': '13:00',
            'snack': '16:00', 
            'dinner': '19:00',
            'rubric': '20:00'
        }

    def get_current_theme(self):
        """Получение темы дня"""
        now = datetime.now(self.kemerovo_tz)
        return self.generator.weekly_themes[now.weekday()]

    def schedule_posts(self):
        """Настройка расписания публикаций"""
        
        # Ежедневные рецепты
        for meal_type, time_str in self.schedule.items():
            if meal_type != 'rubric':
                aioschedule.every().day.at(time_str).do(
                    self.publish_meal, meal_type
                )
                print(f"✅ Настроена публикация {meal_type} в {time_str}")
        
        # Рубрики в 20:00
        aioschedule.every().day.at("20:00").do(
            self.publish_rubric
        )
        print("✅ Настроена публикация рубрик в 20:00")

    def publish_meal(self, meal_type):
        """Публикация рецепта"""
        theme = self.get_current_theme()
        content = self.generator.get_fallback_content(meal_type, theme)
        self.bot.send_message(content)
        
        now = datetime.now(self.kemerovo_tz).strftime("%H:%M")
        print(f"🍳 Опубликован {meal_type} в {now}")

    def publish_rubric(self):
        """Публикация рубрики"""
        theme = self.get_current_theme()
        
        rubric_content = {
            '🔬 Научный понедельник': "🔬 НАУЧНЫЙ ПОНЕДЕЛЬНИК\n\nСегодня разбираем метаболизм! 💡\n\nИнсулин - ключевой гормон в обмене веществ. Его правильная работа обеспечивает стабильную энергию и контроль веса.\n\n❓ Как вы контролируете уровень сахара в крови?",
            '👨‍🍳 Техника шефа': "👨‍🍳 TECH CHECK ОТ ШЕФА\n\nСегодня осваиваем технику 'конфи'! 🎯\n\nМедленное томление при низкой температуре сохраняет соки и питательные вещества в мясе.\n\n👇 Кто уже пробовал эту технику? Делитесь опытом!",
            '❓ Вопрос-Ответ': "❓ ВОПРОС-ОТВЕТ\n\nОтвечаем на ваши вопросы! 💬\n\nСамые популярные вопросы недели:\n• Как ускорить метаболизм?\n• Какие жиры самые полезные?\n• Как правильно сочетать продукты?\n\n💪 Задавайте свои вопросы в комментариях!",
            '🌟 Рецепт недели': "🌟 РЕЦЕПТ НЕДЕЛИ ОТ ШЕФА\n\nЛосось в кунжутной корочке с киноа! 🎨\n\nЭто блюдо уровня ресторанов Мишлен теперь доступно вам дома!\n\n📸 Готовите? Обязательно покажите результат!",
            '🔥 Трендовая пятница': "🔥 ТРЕНДОВАЯ ПЯТНИЦА\n\nРазбираем интервальное голодание! 📊\n\nНаучные плюсы и практические рекомендации.\n\n❓ Кто уже пробовал? Делитесь впечатлениями!",
            '⚡ Быстро & Здорово': "⚡ БЫСТРО & ЗДОРОВО\n\nРецепт на 15 минут! ⏰\n\nСалат с тунцом и авокадо - быстро, полезно, вкусно!\n\n💪 Идеально для занятых людей!",
            '🏆 Воскресный дайджест': "🏆 ВОСКРЕСНЫЙ ДАЙДЖЕСТ\n\nПодводим итоги недели! 📈\n\nЛучшие рецепты, ваши успехи, планы на следующую неделю!\n\n🎯 Готовы к новым свершениям?"
        }
        
        content = rubric_content.get(theme, "Интересный контент готовится для вас!")
        self.bot.send_message(content)
        
        print(f"📝 Опубликована рубрика: {theme}")

async def main():
    print("🎯 Инициализация системы контента...")
    
    # Проверяем наличие необходимых токенов
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
        return
    
    # Создаем и настраиваем планировщик
    scheduler = ContentScheduler()
    scheduler.schedule_posts()
    
    print("✅ Система запущена успешно!")
    print("📅 Расписание публикаций:")
    print("   🍳 Завтрак: 09:00")
    print("   🍲 Обед: 13:00") 
    print("   🥜 Перекус: 16:00")
    print("   🍽️ Ужин: 19:00")
    print("   📝 Рубрика: 20:00")
    print("\n🔄 Система работает...")
    
    # Бесконечный цикл проверки расписания
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Запуск системы
    asyncio.run(main())
