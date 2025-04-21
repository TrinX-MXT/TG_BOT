import telebot
from telebot import types
import csv
import os
import uuid

# Инициализация бота
bot = telebot.TeleBot('7529834494:AAEb6UzguoSBiCh3A2vR-B9ppz8wQMZY2F8')

# Словарь для хранения состояния пользователей
user_data = {}

# Администраторы (пароль для доступа к админ-панели)
ADMIN_PASSWORD = "123"  # Задайте свой пароль здесь
admin_users = set()  # Хранение ID администраторов

# Пути к CSV-файлам
COCKTAILS_CSV = "cocktails.csv"
ORDERS_CSV = "orders.csv"

# Создание CSV-файлов, если они не существуют
if not os.path.exists(COCKTAILS_CSV):
    with open(COCKTAILS_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "price", "ingredients", "popularity"])
        writer.writerows([
            ["Мимоза", 150, "Просекко, Лимон", 10],
            ["Крёстный отец", 200, "Виски, Амаретто", 15],
            ["Куба Либре", 180, "Ром, Кола, Лайм", 25],
            ["Пиницилин", 220, "Виски, Мёд, Груша", 5],
        ])

if not os.path.exists(ORDERS_CSV):
    with open(ORDERS_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "user_name", "drink_name", "address", "status"])

# Функция для чтения данных из CSV
def read_csv(filename):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Функция для записи данных в CSV
def write_csv(filename, data, fieldnames):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Функция для рекомендации коктейлей по ингредиентам
def recommend_cocktail(alco, alco2, fruit):
    if alco == 'Просекко' and alco2 == '-' and fruit == "Лимон":
        return "Мимоза", "mimosa.jpeg", "mimosa.mp4"
    elif alco == 'Виски' and alco2 == 'Амаретто' and fruit == "-":
        return "Крёстный отец", "godfather.jpeg", "godfather.mp4"
    elif alco == 'Кола' and alco2 == 'Ром' and fruit == 'Лайм':
        return "Куба Либре", "cuba_libre.jpeg", "cuba_libre.mp4"
    elif alco == 'Виски' and alco2 == 'Мёд' and fruit == 'Груша':
        return "Пиницилин", "penicillin.jpeg", "penicillin.mp4"
    else:
        return "Попробуйте другой набор ингредиентов.", None, None

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Инициализируем данные для пользователя
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Напиток по ингредиентам", callback_data="choose_by_ingredients"))
    markup.add(types.InlineKeyboardButton("Заказать популярный напиток", callback_data="order_popular"))
    if chat_id in admin_users:
        markup.add(types.InlineKeyboardButton("Админ-панель", callback_data="admin_panel"))
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Обработчик команды /adminpanel
@bot.message_handler(commands=['adminpanel'])
def adminpanel(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите пароль для доступа к админ-панели:")
    bot.register_next_step_handler(message, check_admin_password)

# Проверка пароля для доступа к админ-панели
def check_admin_password(message):
    chat_id = message.chat.id
    password = message.text
    if password == ADMIN_PASSWORD:
        admin_users.add(chat_id)  # Добавляем пользователя в список администраторов
        bot.send_message(chat_id, "Доступ к админ-панели предоставлен.")
    else:
        bot.send_message(chat_id, "Неверный пароль. Доступ запрещен.")

# Обработчик команды /a (админ-меню)
@bot.message_handler(commands=['a'])
def admin_menu(message):
    chat_id = message.chat.id
    if chat_id not in admin_users:
        bot.send_message(chat_id, "У вас нет доступа к админ-меню. Зарегистрируйтесь как администратор через /adminpanel.")
        return
    # Открываем админ-панель
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Управление напитками", callback_data="manage_cocktails"))
    markup.add(types.InlineKeyboardButton("Управление заказами", callback_data="manage_orders"))
    markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
    bot.send_message(chat_id, "Админ-меню:", reply_markup=markup)

# Обработчик нажатия на инлайн кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if chat_id not in user_data:
        user_data[chat_id] = {}
    
    if data == "choose_by_ingredients":
        # Начинаем процесс выбора напитка по ингредиентам
        user_data[chat_id] = {}
        markup = types.InlineKeyboardMarkup()
        options = ["Просекко", "Виски", "Кола", "-"]
        for option in options:
            markup.add(types.InlineKeyboardButton(option, callback_data=f"alco_{option}"))
        markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.edit_message_text("Выберите первый напиток:", chat_id, call.message.id, reply_markup=markup)
    
    elif data.startswith("alco_") or data.startswith("alco2_") or data.startswith("fruit_"):
        key, value = data.split("_", 1)
        if key == "alco":
            user_data[chat_id]["alco"] = value
            markup = types.InlineKeyboardMarkup()
            options = ["Амаретто", "Ром", "Мёд", "-"]
            for option in options:
                markup.add(types.InlineKeyboardButton(option, callback_data=f"alco2_{option}"))
            markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
            bot.edit_message_text("Выберите второй напиток:", chat_id, call.message.id, reply_markup=markup)
        elif key == "alco2":
            user_data[chat_id]["alco2"] = value
            markup = types.InlineKeyboardMarkup()
            options = ["Лайм", "Лимон", "Груша", "-"]
            for option in options:
                markup.add(types.InlineKeyboardButton(option, callback_data=f"fruit_{option}"))
            markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
            bot.edit_message_text("Выберите фрукт:", chat_id, call.message.id, reply_markup=markup)
        elif key == "fruit":
            user_data[chat_id]["fruit"] = value
            alco = user_data[chat_id].get("alco", "-")
            alco2 = user_data[chat_id].get("alco2", "-")
            fruit = user_data[chat_id].get("fruit", "-")
            recommendation, image_file, video_file = recommend_cocktail(alco, alco2, fruit)
            bot.edit_message_text(recommendation, chat_id, call.message.id)
            if image_file:
                with open(image_file, "rb") as photo:
                    bot.send_photo(chat_id, photo)
            if video_file:
                with open(video_file, "rb") as video:
                    bot.send_video(chat_id, video)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
            bot.send_message(chat_id, "Что дальше?", reply_markup=markup)
    
    elif data == "order_popular":
        # Рекомендуем популярный напиток
        cocktails = read_csv(COCKTAILS_CSV)
        popular_drink = max(cocktails, key=lambda x: int(x["popularity"]))
        markup = types.InlineKeyboardMarkup()
        for drink in cocktails:
            markup.add(types.InlineKeyboardButton(drink["name"], callback_data=f"select_drink_{drink['name']}"))
        markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.edit_message_text(f"Популярный напиток: {popular_drink['name']}. Выберите напиток для заказа:", chat_id, call.message.id, reply_markup=markup)
    
    elif data.startswith("select_drink_"):
        # Сохраняем выбранный напиток
        drink_name = data.split("_", 2)[2]
        user_data[chat_id]["selected_drink"] = drink_name
        bot.edit_message_text(f"Вы выбрали {drink_name}. Введите адрес доставки или нажмите «Отмена»:", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel_order"))
        bot.send_message(chat_id, "Введите адрес доставки:", reply_markup=markup)
        bot.register_next_step_handler(call.message, process_address)
    
    elif data == "cancel_order":
        # Отмена заказа
        bot.edit_message_text("Заказ отменен.", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.send_message(chat_id, "Что дальше?", reply_markup=markup)
    
    elif data == "main_menu":
        # Возвращаемся в главное меню
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Напиток по ингредиентам", callback_data="choose_by_ingredients"))
        markup.add(types.InlineKeyboardButton("Заказать популярный напиток", callback_data="order_popular"))
        if chat_id in admin_users:
            markup.add(types.InlineKeyboardButton("Админ-панель", callback_data="admin_panel"))
        bot.edit_message_text("Выберите действие:", chat_id, call.message.id, reply_markup=markup)
    
    elif data == "admin_panel":
        # Админ-панель
        if chat_id not in admin_users:
            bot.edit_message_text("У вас нет доступа к админ-панели.", chat_id, call.message.id)
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Управление напитками", callback_data="manage_cocktails"))
        markup.add(types.InlineKeyboardButton("Управление заказами", callback_data="manage_orders"))
        markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.edit_message_text("Админ-панель:", chat_id, call.message.id, reply_markup=markup)
    
    elif data == "manage_cocktails":
        # Управление напитками
        cocktails = read_csv(COCKTAILS_CSV)
        markup = types.InlineKeyboardMarkup()
        for drink in cocktails:
            markup.add(types.InlineKeyboardButton(drink["name"], callback_data=f"edit_drink_{drink['name']}"))
        markup.add(types.InlineKeyboardButton("Добавить напиток", callback_data="add_cocktail"))
        markup.add(types.InlineKeyboardButton("В админ-панель", callback_data="admin_panel"))
        bot.edit_message_text("Список напитков:", chat_id, call.message.id, reply_markup=markup)
    
    elif data.startswith("edit_drink_"):
        # Редактирование напитка
        drink_name = data.split("_", 2)[2]
        cocktails = read_csv(COCKTAILS_CSV)
        drink = next((d for d in cocktails if d["name"] == drink_name), None)
        bot.edit_message_text(f"Напиток: {drink['name']}\nЦена: {drink['price']}\nИнгредиенты: {drink['ingredients']}", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить цену", callback_data=f"change_price_{drink_name}"))
        markup.add(types.InlineKeyboardButton("Изменить ингредиенты", callback_data=f"change_ingredients_{drink_name}"))
        markup.add(types.InlineKeyboardButton("Удалить напиток", callback_data=f"delete_cocktail_{drink_name}"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_cocktails"))
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    
    elif data.startswith("change_price_"):
        # Изменение цены напитка
        drink_name = data.split("_", 2)[2]
        user_data[chat_id]["edit_drink"] = drink_name
        bot.edit_message_text(f"Введите новую цену для {drink_name}:", chat_id, call.message.id)
        bot.register_next_step_handler(call.message, change_price)
    
    elif data.startswith("change_ingredients_"):
        # Изменение ингредиентов напитка
        drink_name = data.split("_", 2)[2]
        user_data[chat_id]["edit_drink"] = drink_name
        bot.edit_message_text(f"Введите новые ингредиенты для {drink_name}:", chat_id, call.message.id)
        bot.register_next_step_handler(call.message, change_ingredients)
    
    elif data.startswith("delete_cocktail_"):
        # Удаление напитка
        drink_name = data.split("_", 2)[2]
        cocktails = read_csv(COCKTAILS_CSV)
        cocktails = [d for d in cocktails if d["name"] != drink_name]
        write_csv(COCKTAILS_CSV, cocktails, ["name", "price", "ingredients", "popularity"])
        bot.edit_message_text(f"Напиток {drink_name} удален.", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_cocktails"))
        bot.send_message(chat_id, "Что дальше?", reply_markup=markup)
    
    elif data == "add_cocktail":
        # Добавление нового напитка
        bot.edit_message_text("Введите название нового напитка:", chat_id, call.message.id)
        bot.register_next_step_handler(call.message, add_cocktail_name)
    
    elif data == "manage_orders":
        # Управление заказами
        orders = read_csv(ORDERS_CSV)
        markup = types.InlineKeyboardMarkup()
        for order in orders:
            markup.add(types.InlineKeyboardButton(f"{order['user_name']} - {order['drink_name']} ({order['status']})", callback_data=f"edit_order_{order['id']}"))
        markup.add(types.InlineKeyboardButton("В админ-панель", callback_data="admin_panel"))
        bot.edit_message_text("Список заказов:", chat_id, call.message.id, reply_markup=markup)
    
    elif data.startswith("edit_order_"):
        # Редактирование статуса заказа
        order_id = data.split("_", 2)[2]
        orders = read_csv(ORDERS_CSV)
        order = next((o for o in orders if o["id"] == order_id), None)
        bot.edit_message_text(f"Заказ №{order_id}: {order['user_name']} - {order['drink_name']}\nТекущий статус: {order['status']}", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("В обработке", callback_data=f"update_status_pending_{order_id}"))
        markup.add(types.InlineKeyboardButton("Доставлен", callback_data=f"update_status_delivered_{order_id}"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_orders"))
        bot.send_message(chat_id, "Выберите новый статус:", reply_markup=markup)
    
    elif data.startswith("update_status_"):
        # Обновление статуса заказа
        status, order_id = data.split("_", 3)[2:]
        orders = read_csv(ORDERS_CSV)
        for order in orders:
            if order["id"] == order_id:
                order["status"] = status
                break
        write_csv(ORDERS_CSV, orders, ["id", "user_name", "drink_name", "address", "status"])
        bot.edit_message_text(f"Статус заказа №{order_id} изменен на {status}.", chat_id, call.message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_orders"))
        bot.send_message(chat_id, "Что дальше?", reply_markup=markup)
        
        
def create_fake_payment_link(order_id):
    # Генерируем URL-ссылку с идентификатором заказа
    fake_payment_url = f"https://your-bot-url.com/fake_payment/{order_id}"
    return fake_payment_url

# Обработчик адреса доставки
def process_address(message):
    chat_id = message.chat.id
    address = message.text
    if chat_id not in user_data:
        user_data[chat_id] = {}
    
    if address.lower() == "отмена":
        bot.send_message(chat_id, "Заказ отменен.")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("В главное меню", callback_data="main_menu"))
        bot.send_message(chat_id, "Что дальше?", reply_markup=markup)
        return
    
    drink_name = user_data[chat_id].get("selected_drink")
    user_name = message.from_user.first_name
    
    # Получаем цену напитка
    cocktails = read_csv(COCKTAILS_CSV)
    drink = next((d for d in cocktails if d["name"] == drink_name), None)
    price = float(drink["price"])
    
    # Генерация уникального ID заказа
    order_id = str(uuid.uuid4())
    user_data[chat_id]["pending_order"] = {
        "id": order_id,
        "user_name": user_name,
        "drink_name": drink_name,
        "address": address,
        "price": price
    }
    
    # Создание фейковой ссылки на оплату
    fake_payment_link = f"https://your-bot-url.com/fake_payment/{order_id}"
    bot.send_message(chat_id, f"Для оплаты заказа перейдите по ссылке: {fake_payment_link}")

@bot.message_handler(commands=['fake_payment'])
def handle_fake_payment(message):
    chat_id = message.chat.id
    try:
        # Извлекаем order_id из текста команды
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(chat_id, "Пожалуйста, укажите ID заказа после команды /fake_payment.")
            return
        order_id = parts[1]  # Второй элемент - это order_id
        pending_order = user_data.get(chat_id, {}).get("pending_order")

        if not pending_order or pending_order["id"] != order_id:
            bot.send_message(chat_id, "Неверный или просроченный заказ.")
            return

        # Сохраняем заказ в CSV
        orders = read_csv(ORDERS_CSV)
        orders.append({
            "id": pending_order["id"],
            "user_name": pending_order["user_name"],
            "drink_name": pending_order["drink_name"],
            "address": pending_order["address"],
            "status": "paid"
        })
        write_csv(ORDERS_CSV, orders, ["id", "user_name", "drink_name", "address", "status"])

        # Увеличиваем популярность напитка
        cocktails = read_csv(COCKTAILS_CSV)
        for c in cocktails:
            if c["name"] == pending_order["drink_name"]:
                c["popularity"] = str(int(c["popularity"]) + 1)
                break
        write_csv(COCKTAILS_CSV, cocktails, ["name", "price", "ingredients", "popularity"])

        # Отправляем подтверждение
        bot.send_message(chat_id, "Заказ успешно оплачен и оформлен!")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка при обработке оплаты: {str(e)}")

# Обработчик изменения цены напитка
def change_price(message):
    chat_id = message.chat.id
    new_price = message.text
    drink_name = user_data[chat_id]["edit_drink"]
    cocktails = read_csv(COCKTAILS_CSV)
    for c in cocktails:
        if c["name"] == drink_name:
            c["price"] = new_price
            break
    write_csv(COCKTAILS_CSV, cocktails, ["name", "price", "ingredients", "popularity"])
    bot.send_message(chat_id, f"Цена напитка {drink_name} изменена на {new_price}.")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_cocktails"))
    bot.send_message(chat_id, "Что дальше?", reply_markup=markup)

# Обработчик изменения ингредиентов напитка
def change_ingredients(message):
    chat_id = message.chat.id
    new_ingredients = message.text
    drink_name = user_data[chat_id]["edit_drink"]
    cocktails = read_csv(COCKTAILS_CSV)
    for c in cocktails:
        if c["name"] == drink_name:
            c["ingredients"] = new_ingredients
            break
    write_csv(COCKTAILS_CSV, cocktails, ["name", "price", "ingredients", "popularity"])
    bot.send_message(chat_id, f"Ингредиенты напитка {drink_name} изменены на {new_ingredients}.")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_cocktails"))
    bot.send_message(chat_id, "Что дальше?", reply_markup=markup)

# Обработчик добавления нового напитка
def add_cocktail_name(message):
    chat_id = message.chat.id
    cocktail_name = message.text
    user_data[chat_id]["new_cocktail_name"] = cocktail_name
    bot.send_message(chat_id, "Введите цену нового напитка:")
    bot.register_next_step_handler(message, add_cocktail_price)

def add_cocktail_price(message):
    chat_id = message.chat.id
    cocktail_price = message.text
    user_data[chat_id]["new_cocktail_price"] = cocktail_price
    bot.send_message(chat_id, "Введите ингредиенты нового напитка:")
    bot.register_next_step_handler(message, add_cocktail_ingredients)

def add_cocktail_ingredients(message):
    chat_id = message.chat.id
    cocktail_ingredients = message.text
    cocktail_name = user_data[chat_id]["new_cocktail_name"]
    cocktail_price = user_data[chat_id]["new_cocktail_price"]
    
    # Добавляем новый напиток в CSV
    cocktails = read_csv(COCKTAILS_CSV)
    cocktails.append({
        "name": cocktail_name,
        "price": cocktail_price,
        "ingredients": cocktail_ingredients,
        "popularity": "0"
    })
    write_csv(COCKTAILS_CSV, cocktails, ["name", "price", "ingredients", "popularity"])
    bot.send_message(chat_id, f"Новый напиток {cocktail_name} добавлен.")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Назад", callback_data="manage_cocktails"))
    bot.send_message(chat_id, "Что дальше?", reply_markup=markup)

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)