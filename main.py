import traceback

import vk_api
import vk
from datetime import datetime, timedelta
from enum import Enum, auto
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import pyreqs

import modules.config as config
import modules.database.database as database

vk_session = vk_api.VkApi(token=config.token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

user_vars = {}  # Переменные пользователей
last_user = -1  # Последний пользователь с кем взаимодействовал бот
developer_id = 369071929  # Для отправления ошибок и т.п.

db = database.Database()  # Инициализация базы данных


class Mode(Enum):
    """
    Содержит список состояний пользователя
    """
    menu = auto()
    repeat_cards = auto()
    manage_decks = auto()
    wait_subscribe_deck_id = auto()
    wait_share_deck_id = auto()
    wait_remove_deck_id = auto()
    wait_edit_deck_id = auto()
    edit_deck = auto()
    wait_remove_card_id = auto()
    wait_add_card_question = auto()
    wait_add_card_answer = auto()
    wait_edit_card_id = auto()
    wait_edit_card_what = auto()
    wait_edit_card_question = auto()
    wait_edit_card_answer = auto()
    wait_add_deck_id = auto()
    successful_added_deck = auto()
    wait_edit_deck_name = auto()
    successful_added_card = auto()


class User:
    """
    Класс пользователя
    """
    def __init__(self, question='', answer='', mode=Mode.menu, deck_id=None, card_id=None):
        self.question = question
        self.answer = answer
        self.mode = mode
        self.deck_id = deck_id
        self.card_id = card_id


class Menu:
    """
    Класс меню позволяет формировать для пользователя клавиатуру с сообщением
    """
    def __init__(self, message=None, keyboard=None):
        self.keyboard = keyboard
        self.message = message

    def show(self, user_id):
        vk.messages.send(
            user_id=user_id,
            message=self.message,
            random_id=get_random_id(),
            keyboard=self.keyboard and self.keyboard.get_keyboard()
        )


def show_main_menu(user_id):
    _, _, cards_for_repeat, _ = db.get_repeat_card(user_id)
    menu = Menu()
    menu.message = """
    На данный момент у вас """ + (cards_for_repeat and str(cards_for_repeat) + " карточки, которые можно повторить :)"
                                  or "отсутствуют карточки для повторения!") + """
    
    1. Управление колодами
    2. Показ карточек для повторения
    """
    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('1', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_callback_button('2', VkKeyboardColor.POSITIVE)
    menu.show(user_id)
    user_vars[user_id].mode = Mode.menu


def repeat_cards(user_id):
    user_vars[user_id].question, user_vars[user_id].answer, length, user_vars[user_id].card_id = db.get_repeat_card(user_id)
    if length == 0:
        show_message(user_id, "Карточки закончились :) Заходи позже")
        show_main_menu(user_id)
    else:
        menu = Menu()
        menu.message = """
        ?????
        """ + user_vars[user_id].question + """
        
        Карточек осталось: """ + str(length)

        menu.keyboard = VkKeyboard(one_time=True)
        menu.keyboard.add_callback_button('Легко', VkKeyboardColor.POSITIVE)
        menu.keyboard.add_callback_button('Средне', VkKeyboardColor.PRIMARY)
        menu.keyboard.add_callback_button('Трудно', VkKeyboardColor.PRIMARY)
        menu.keyboard.add_callback_button('Не вспомню', VkKeyboardColor.NEGATIVE)
        menu.keyboard.add_line()
        menu.keyboard.add_callback_button('Назад')
        menu.show(user_id)
        user_vars[user_id].mode = Mode.repeat_cards


def manage_decks(user_id):
    menu = Menu()
    menu.message = """
    1. Подписаться на колоду
    2. Редактировать колоду
    3. Разрешить/запретить подписки на колоду
    4. Удалить колоду
    5. Создать колоду
    
    """ + db.show_decks_by_user(user_id)
    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('1', VkKeyboardColor.POSITIVE)
    menu.keyboard.add_callback_button('2', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_callback_button('3', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_line()
    menu.keyboard.add_callback_button('4', VkKeyboardColor.NEGATIVE)
    menu.keyboard.add_callback_button('5', VkKeyboardColor.POSITIVE)
    menu.keyboard.add_line()
    menu.keyboard.add_callback_button('Назад')
    menu.show(user_id)
    user_vars[user_id].mode = Mode.manage_decks


def subscribe_deck(user_id):
    menu = Menu()
    menu.message = """
    Подписка на колоду. Введите ID колоды
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_subscribe_deck_id


def share_deck(user_id):
    menu = Menu()
    menu.message = """
    Разрешить подписку на свою колоду. Введите ID колоды
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_share_deck_id


def remove_deck(user_id):
    menu = Menu()
    menu.message = """
    Введите ID колоды, которую Вы хотите удалить
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_remove_deck_id


def add_deck(user_id):
    menu = Menu()
    menu.message = """
         Введите название для добавляемой колоды
        """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_add_deck_id


def edit_deck(user_id):
    menu = Menu()
    menu.message = """
    1. Редактировать карточку
    2. Удалить карточку
    3. Добавить карточку
    4. Изменить название колоды
    
    """ + db.show_cards_in_deck(user_vars[user_id].deck_id)
    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('1', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_callback_button('2', VkKeyboardColor.NEGATIVE)
    menu.keyboard.add_line()
    menu.keyboard.add_callback_button('3', VkKeyboardColor.POSITIVE)
    menu.keyboard.add_callback_button('4', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_line()
    menu.keyboard.add_callback_button('Назад')
    menu.show(user_id)
    user_vars[user_id].mode = Mode.edit_deck


def remove_card(user_id):
    menu = Menu()
    menu.message = """
    Введите ID карточки, которую хотите удалить
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_remove_card_id


def add_card_answer(user_id):
    menu = Menu()
    menu.message = """
    Введите поле ответа для добавляемой карточки
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_add_card_answer


def edit_card_enter_id(user_id):
    menu = Menu()
    menu.message = """
    Введите ID карточки, которую хотите отредактировать
    """
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_edit_card_id


def edit_card_what(user_id):
    menu = Menu()
    menu.message = """
    1. Изменить вопрос
    2. Изменить ответ
    """
    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('1', VkKeyboardColor.PRIMARY)
    menu.keyboard.add_callback_button('2', VkKeyboardColor.PRIMARY)
    menu.show(user_id)
    menu.keyboard.add_line()
    menu.keyboard.add_callback_button('Назад')
    user_vars[user_id].mode = Mode.wait_edit_card_what


def edit_card_question(user_id):
    menu = Menu()
    menu.message = """
        Введите новое поле вопроса карточки.
        
        Прошлое:
        """ + user_vars[user_id].question
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_edit_card_question


def edit_card_answer(user_id):
    menu = Menu()
    menu.message = """
            Введите новое поле ответа карточки.

            Прошлое:
            """ + user_vars[user_id].answer
    menu.show(user_id)
    user_vars[user_id].mode = Mode.wait_edit_card_answer


def successful_added_card(user_id):
    menu = Menu()
    menu.message = """
                Карточка добавлена!
                
                Вопрос:
                """ + user_vars[user_id].question + """
                
                Ответ:
                """ + user_vars[user_id].answer + """
                """
    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('Добавить больше')
    menu.keyboard.add_callback_button('Вернуться к редактированию колоды')
    menu.show(user_id)
    user_vars[user_id].mode = Mode.successful_added_card


def successful_added_deck(user_id):
    menu = Menu()
    menu.message = """
                    Новая колода добавлена!
                    Для добавления карточек перейдите в раздел редактирования колод
                    
                    1. Редактирование колод
                    2. Главное меню"""

    menu.keyboard = VkKeyboard(one_time=True)
    menu.keyboard.add_callback_button('1', VkKeyboardColor.POSITIVE)
    menu.keyboard.add_callback_button('2', VkKeyboardColor.PRIMARY)
    menu.show(user_id)
    user_vars[user_id].mode = Mode.successful_added_deck


def show_message(user_id, message):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=get_random_id()
    )


try:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_user:
                last_user = event.user_id
                if not (event.user_id in user_vars):
                    user_vars[event.user_id] = User()

                if event.text in '/start' or (event.text in 'Начать' and user_vars[event.user_id].mode == Mode.menu):
                    show_main_menu(event.user_id)

                if event.text in 'Назад':
                    if user_vars[event.user_id].mode == Mode.manage_decks:
                        show_main_menu(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.edit_deck:
                        user_vars[event.user_id] = User()
                        manage_decks(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.wait_edit_card_what:
                        edit_deck(event.user_id)
                        user_vars[event.user_id].card_id = None
                    elif user_vars[event.user_id].mode == Mode.repeat_cards:
                        show_main_menu(event.user_id)

                if event.text in 'Вернуться к редактированию колоды' and \
                        user_vars[event.user_id].mode == Mode.successful_added_card:
                    edit_deck(event.user_id)

                elif user_vars[event.user_id].mode == Mode.repeat_cards:
                    if event.text == 'Легко':
                        db.up_card_time(user_vars[event.user_id].card_id, 'easy')
                    elif event.text == 'Средне':
                        db.up_card_time(user_vars[event.user_id].card_id, 'medium')
                    elif event.text == 'Трудно':
                        db.up_card_time(user_vars[event.user_id].card_id, 'hard')
                    elif event.text == 'Не вспомню':
                        db.up_card_time(user_vars[event.user_id].card_id, 'impossible')
                    repeat_cards(event.user_id)

                elif user_vars[event.user_id].mode == Mode.wait_edit_card_id:
                    selected_card = event.text
                    if selected_card.isdigit():
                        user_vars[event.user_id].question, user_vars[event.user_id].answer, card_deck = \
                            db.get_card_by_id(selected_card)
                        if user_vars[event.user_id].deck_id == card_deck:
                            user_vars[event.user_id].card_id = int(selected_card)
                            edit_card_what(event.user_id)
                        else:
                            show_message(event.user_id, "Указаная карточка не относится к этой колоде!")
                    else:
                        show_message(event.user_id, "Неверный формат ID карточки!")

                elif user_vars[event.user_id].mode == Mode.wait_edit_card_question:
                    db.edit_card_question(user_vars[event.user_id].card_id, event.text)
                    edit_card_what(event.user_id)

                elif user_vars[event.user_id].mode == Mode.wait_edit_card_answer:
                    db.edit_card_answer(user_vars[event.user_id].card_id, event.text)
                    edit_card_what(event.user_id)

                elif user_vars[event.user_id].mode == Mode.wait_add_card_question:
                    user_vars[event.user_id].question = event.text
                    show_message(event.user_id, "Введите ответ")
                    user_vars[event.user_id].mode = Mode.wait_add_card_answer

                elif user_vars[event.user_id].mode == Mode.wait_add_card_answer:
                    user_vars[event.user_id].answer = event.text
                    db.insert_card(user_vars[event.user_id].question,
                                   user_vars[event.user_id].answer,
                                   user_vars[event.user_id].deck_id)
                    successful_added_card(event.user_id)

                elif user_vars[event.user_id].mode == Mode.wait_add_deck_id:
                    db.insert_deck(event.text, event.user_id)
                    successful_added_deck(event.user_id)

                elif user_vars[event.user_id].mode == Mode.wait_remove_card_id:
                    selected_card = event.text
                    if selected_card.isdigit():
                        card_question, _, card_deck = db.get_card_by_id(selected_card)
                        if user_vars[event.user_id].deck_id == card_deck:
                            db.delete_card_by_id(int(selected_card))
                            show_message(event.user_id, """Вы удалили карточку с вопросом:
                                """ + card_question)
                            edit_deck(event.user_id)
                        else:
                            show_message(event.user_id, "Указаная карточка не относится к этой колоде!")
                    else:
                        show_message(event.user_id, "Неверный формат ID карточки!")

                elif user_vars[event.user_id].mode == Mode.wait_remove_deck_id:
                    selected_deck = event.text
                    if selected_deck.isdigit():
                        name, status, owner, deleted = db.get_deck_by_id(int(selected_deck))
                        if name and not deleted:
                            if owner == event.user_id and status != -1:
                                db.remove_deck(int(selected_deck))
                                show_message(event.user_id, "Вы удалили колоду '" + str(name) + "'!")
                                manage_decks(event.user_id)
                            else:
                                db.unfollow_deck(int(selected_deck))
                                show_message(event.user_id, "Вы успешно отписались от колоды!")
                                manage_decks(event.user_id)
                        else:
                            show_message(event.user_id, "Указаной колоды не существует!")
                    else:
                        show_message(event.user_id, "Неверный формат ID колоды!")

                elif user_vars[event.user_id].mode == Mode.wait_share_deck_id:
                    selected_deck = event.text
                    if selected_deck.isdigit():
                        name, status, owner, deleted = db.get_deck_by_id(int(selected_deck))
                        if name:
                            if owner == event.user_id and status != -1 and not deleted:
                                db.change_deck_status(int(selected_deck), status == 0 and 1 or 0)
                                show_message(event.user_id, "Теперь Ваша колода" + (status == 1 and " не" or "") +
                                             " доступна для подписок!")
                                manage_decks(event.user_id)
                            else:
                                show_message(event.user_id, "Указанная колода не принадлежит Вам!")
                        else:
                            show_message(event.user_id, "Указаной колоды не существует!")
                    else:
                        show_message(event.user_id, "Неверный формат ID колоды!")

                elif user_vars[event.user_id].mode == Mode.wait_subscribe_deck_id:
                    selected_deck = event.text
                    if selected_deck.isdigit():
                        name, status, owner, deleted = db.get_deck_by_id(int(selected_deck))
                        if name:
                            if owner != event.user_id and status == 1 and not \
                                    db.check_subscribe(int(selected_deck), event.user_id) and not deleted:
                                db.follow_deck(int(selected_deck), event.user_id)
                                show_message(event.user_id, "Вы подписались на колоду '" + name + "'!")
                                manage_decks(event.user_id)
                            else:
                                show_message(event.user_id, "Данная колода недоступна для подписок, либо она"
                                                            " уже существует в вашей библиотеке!")
                        else:
                            show_message(event.user_id, "Указаной колоды не существует!")
                    else:
                        show_message(event.user_id, "Неверный формат ID колоды!")

                elif user_vars[event.user_id].mode == Mode.wait_edit_deck_id:
                    selected_deck = event.text
                    if selected_deck.isdigit():
                        name, status, owner, deleted = db.get_deck_by_id(int(selected_deck))
                        if name:
                            print(status, deleted)
                            if status != -1 and owner == event.user_id and not deleted:
                                user_vars[event.user_id].deck_id = int(selected_deck)
                                edit_deck(event.user_id)
                            else:
                                show_message(event.user_id, "Данная колода не принадлежит Вам!")
                        else:
                            show_message(event.user_id, "Указаной колоды не существует!")
                    else:
                        show_message(event.user_id, "Неверный формат ID колоды!")

                elif user_vars[event.user_id].mode == Mode.wait_edit_deck_name:
                    db.change_deck_name(user_vars[event.user_id].deck_id, event.text)
                    edit_deck(event.user_id)

                elif event.text == '1':
                    if user_vars[event.user_id].mode == Mode.menu:
                        manage_decks(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.manage_decks:
                        subscribe_deck(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.edit_deck:
                        edit_card_enter_id(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.wait_edit_card_what:
                        edit_card_question(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.successful_added_deck:
                        manage_decks(event.user_id)

                elif event.text == '2':
                    if user_vars[event.user_id].mode == Mode.menu:
                        repeat_cards(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.manage_decks:
                        user_vars[event.user_id].mode = Mode.wait_edit_deck_id
                        show_message(event.user_id, "Введите ID колоды")
                    elif user_vars[event.user_id].mode == Mode.edit_deck:
                        show_message(event.user_id, "Введите ID карточки которую хотите удалить")
                        user_vars[event.user_id].mode = Mode.wait_remove_card_id
                    elif user_vars[event.user_id].mode == Mode.wait_edit_card_what:
                        edit_card_answer(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.successful_added_deck:
                        show_main_menu(event.user_id)

                elif event.text in '3':
                    if user_vars[event.user_id].mode == Mode.manage_decks:
                        share_deck(event.user_id)
                    elif user_vars[event.user_id].mode == Mode.edit_deck:
                        show_message(event.user_id, "Введите вопрос")
                        user_vars[event.user_id].mode = Mode.wait_add_card_question

                elif event.text in '4':
                    if user_vars[event.user_id].mode == Mode.manage_decks:
                        remove_deck(event.user_id)
                    if user_vars[event.user_id].mode == Mode.edit_deck:
                        user_vars[event.user_id].mode = Mode.wait_edit_deck_name
                        show_message(event.user_id, "Введите новое имя колоды")

                elif event.text in 'Добавить больше' and user_vars[event.user_id].mode == Mode.successful_added_card:
                    show_message(event.user_id, "Введите вопрос")
                    user_vars[event.user_id].mode = Mode.wait_add_card_question

                elif event.text in '5':
                    if user_vars[event.user_id].mode == Mode.manage_decks:
                        add_deck(event.user_id)

finally:
    show_message(last_user, "Поздравляю, тебе удалось сломать бота :)\n(не такая уж и большая заслуга, если честно c:)")
    show_message(developer_id, "Бот упал!\n\n" + traceback.format_exc())
