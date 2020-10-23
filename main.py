import vk_api, vk, sqlite3, datetime
from enum import Enum, auto
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType

COMMAND_I_KNOW_IT = 'Я это знаю'
COMMAND_REPEAT = 'Повторить'
COMMAND_MENU = 'Меню'
COMMAND_SHOW_CARDS = 'Показать текущие карточки'
COMMAND_ADD_NEW_CARD = 'Добавить новую карточку'
COMMAND_DELETE_CARD = 'Удалить существующую карточку'

vk_session = vk_api.VkApi(token='b37fdc569c3c9319c3a57340e5de04667a62c8a2d57cbf118f3346a59c276fd013cf5c6156eac4783a74d')
# Токен группы с ботом

users = dict()  # Словарь для работы с каждым пользователем отдельно


class mode(Enum):
    menu = auto()
    type_add_trigger = auto()
    type_add_answer = auto()
    type_remove_card = auto()


class User:
    def __init__(self, id=0, trigger='', answer='', mode=mode.menu):
        self.id = id
        self.trigger = trigger
        self.answer = answer
        self.mode = mode


longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

# Панель диалога при повторении карточки
dialogboard = VkKeyboard(one_time=True)
dialogboard.add_button(COMMAND_I_KNOW_IT, color=VkKeyboardColor.POSITIVE)
dialogboard.add_button(COMMAND_REPEAT, color=VkKeyboardColor.DEFAULT)
dialogboard.add_line()
dialogboard.add_button(COMMAND_MENU, color=VkKeyboardColor.PRIMARY)

# Панель главного меню
menuboard = VkKeyboard(one_time=False)
menuboard.add_button(COMMAND_SHOW_CARDS, color=VkKeyboardColor.DEFAULT)
menuboard.add_line()
menuboard.add_button(COMMAND_ADD_NEW_CARD, color=VkKeyboardColor.DEFAULT)
menuboard.add_line()
menuboard.add_button(COMMAND_DELETE_CARD, color=VkKeyboardColor.DEFAULT)
menuboard.add_line()
menuboard.add_vkpay_button(hash="action=transfer-to-group&group_id=198420977")

# Создаем соединение с нашей базой данных
# В данном случае файл расположен в той же папке что и main.py
conn = sqlite3.connect('modules/database/i-know-db.db')

# Создаем курсор - это специальный объект который делает запросы и получает их результаты
cursor = conn.cursor()

# Структура таблицы с карточками 'answers'
# 0 поле - триггер
# 1 поле - ответ
# 2 поле - дата
# 3 поле - чья карточка

for event in longpoll.listen():
    if users[event.user_id].mode == mode.menu:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            vars1 = ['Привет', 'Ку', 'Хай', 'Хеллоу']
            if event.text in vars1:
                if event.from_user:
                    cur_date = datetime.datetime.today()
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Привет)',
                        random_id=get_random_id()
                    )
            vars2 = ['Клавиатура', 'клавиатура']
            if event.text in vars2:
                if event.from_user:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        keyboard=dialogboard.get_keyboard(),
                    )
            if event.text == COMMAND_MENU:
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    keyboard=menuboard.get_keyboard(),
                )
            if event.text == COMMAND_SHOW_CARDS:
                try:

                    results = cursor.fetchall()  # Получаем результат сделанного запроса
                except sqlite3.DatabaseError as err:
                    print("Error: ", err)
                cards = ''
                if len(results) == 0:
                    cards = 'Вы до сих пор не создали ни единой карточки. Как же так??? :\\'
                else:
                    cards = 'Ваши карточки:\n\n'
                    for result in results:
                        cards += str(result[0]) + '\n' + str(result[1]) + '\nСледующий показ:' + str(result[2]) + '\n\n'

                vk.messages.send(
                    user_id=event.user_id,
                    message=cards,
                    random_id=get_random_id()
                )
            if event.text == COMMAND_ADD_NEW_CARD:
                try:
                    cursor.execute("insert into answers values (:trigger, :answer, :date, :id) ",
                                   {"trigger": 'Какой-то триггер',
                                    "answer": 'Какой-то ответ',
                                    "date": 214214,
                                    "id": event.user_id})
                except sqlite3.DatabaseError as err:
                    print("Error: ", err)
                else:
                    conn.commit()
                vk.messages.send(
                    user_id=event.user_id,
                    message='Введите вопрос заметки',
                    random_id=get_random_id()
                )
                current_user = User()
                current_user.mode = mode.type_add_trigger
                users[event.user_id] = current_user
            if event.text == COMMAND_DELETE_CARD:
                vk.messages.send(
                    user_id=event.user_id,
                    message='Функция в разработке',
                    random_id=get_random_id()
                )
        elif users[event.user_id].mode == mode.type_add_trigger:


# Не забываем закрыть соединение с базой данных
conn.close()
