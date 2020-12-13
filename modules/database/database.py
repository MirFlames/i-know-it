import sqlite3
from datetime import datetime, timedelta


class Database:
    """ Класс взаимодействия с базой данных """
    try:
        def __init__(self):
            """ Конструктор класса базы данных """
            self.connection = sqlite3.connect('modules/database/i-know-db.db')
            self.cursor = self.connection.cursor()

        def exit(self):
            """ Закрывает соединение с базой данных """
            self.connection.close()

        def get_deck_status(self, deck_id: int):
            """
            Возвращает статус колоды

            :param deck_id: идентификатор колоды
            :return: 0 - подписки открыты, 1 - подписки закрыты, -1 - колода доступная по подписке
            """
            self.cursor.execute('SELECT status FROM decks WHERE rowid=:deck_id AND deleted=0', {"deck_id": deck_id})
            result = self.cursor.fetchall()
            return int(result[0])

        def show_decks_by_user(self, user_id: int):
            """ Возвращает строку колод пользователя по идентификатору ВК """
            self.cursor.execute('SELECT name, status, rowid FROM decks WHERE owner=:id AND deleted=0', {"id": user_id})
            results = self.cursor.fetchall()
            decks = ''
            print(results)
            if len(results) == 0:
                decks = 'Колоды отсутствуют'
            else:
                decks = 'Ваши колоды:\n\n'
                for result in results:
                    sub_str = ''
                    if result[1] == 1:
                        sub_str = 'Подписки разрешены'
                    elif result[1] == 0:
                        sub_str = 'Подписки запрещены'
                    elif result[1] == -1:
                        sub_str = 'Доступ по подписке'
                    decks += str(result[0]) + ' | ID: ' + str(result[2]) + ' | ' + sub_str + '\n'
            return decks

        def check_subscribe(self, deck_id: int, user_id: int):
            self.cursor.execute('SELECT * FROM decks WHERE root_deck=:deck_id AND owner=:owner AND deleted=0',
                                {"deck_id": deck_id, "owner": user_id})
            result = self.cursor.fetchall()
            return len(result) != 0

        def unfollow_deck(self, deck_id: int):
            self.cursor.execute('DELETE FROM decks WHERE rowid=:id', {"id": deck_id})
            self.connection.commit()

        def change_deck_name(self, deck_id: int, name: str):
            self.cursor.execute('UPDATE decks SET name = :name WHERE rowid = :deck_id',
                                {"name": name, "deck_id": deck_id})
            self.connection.commit()

        def follow_deck(self, deck_id: int, user_id: int):
            self.cursor.execute('INSERT INTO decks (name, status, owner, root_deck) VALUES '
                                '((SELECT name FROM decks WHERE rowid==:deck_id), :status, :owner, :deck_id);',
                                {"deck_id": deck_id, "status": -1, "owner": user_id})
            self.connection.commit()

        def remove_deck(self, deck_id: int):
            self.cursor.execute('UPDATE decks SET deleted = 1 WHERE rowid = :deck_id',
                                {"deck_id": deck_id})
            self.connection.commit()

        def show_cards_in_deck(self, deck_id: int):
            """ Получение карточек в колоде """
            self.cursor.execute('SELECT question, rowid FROM cards WHERE deck=:id AND deleted=0', {"id": deck_id})
            results = self.cursor.fetchall()
            cards = ''
            if len(results) == 0:
                cards = 'Колода пуста'
            else:
                cards = 'Карточки:\n\n'
                for result in results:
                    cards += str(result[0]) + ' | ID: ' + str(result[1]) + '\n'
            return cards

        def get_card_by_id(self, card_id):
            """Получение карточки по уникальному идентификатору"""
            self.cursor.execute('SELECT question, answer, deck FROM cards WHERE rowid=:id AND deleted = 0',
                                {"id": card_id})
            result = self.cursor.fetchall()
            if not result:
                return None, None, None
            question = result[0][0]
            answer = result[0][1]
            deck = result[0][2]
            return question, answer, deck

        def get_deck_by_id(self, deck_id):
            """Получение колоды по уникальному идентификатору"""
            self.cursor.execute('SELECT name, status, owner, deleted FROM decks WHERE rowid=:id AND deleted=0', {"id": deck_id})
            result = self.cursor.fetchall()
            if not result:
                return None, None, None, None
            name = result[0][0]
            status = result[0][1]
            owner = result[0][2]
            deleted = result[0][3]
            return name, status, owner, deleted

        def delete_card_by_id(self, card_id):
            """ Удаление карточки по идентификатору """
            self.cursor.execute('UPDATE cards SET deleted = 1 WHERE rowid = :card_id',
                                {"card_id": card_id})
            self.connection.commit()

        def insert_card(self, question, answer, deck):
            """ Добавление новой карточки """
            time = datetime.now().strftime("%Y-%m-%d %I:%M")
            self.cursor.execute(
                'INSERT INTO cards (question, answer, deck, time) VALUES (:question, :answer, :deck, :time)',
                {"question": question, "answer": answer, "deck": deck, "time": time})
            self.connection.commit()

        def insert_deck(self, name, owner):
            """ Добавление новой карточки """
            self.cursor.execute(
                'INSERT INTO decks (name, owner) VALUES (:name, :owner)',
                {"name": name, "owner": owner})
            self.connection.commit()

        def change_deck_status(self, deck_id, status):
            self.cursor.execute('UPDATE decks SET status = :status WHERE rowid = :deck_id',
                                {"status": status, "deck_id": deck_id})
            self.connection.commit()

        def edit_card_question(self, card_id, question):
            """ Редактирование вопроса карточки по идентификатору карточки """
            self.cursor.execute('UPDATE cards SET question = :question WHERE rowid = :card_id',
                                {"question": question, "card_id": card_id})
            self.connection.commit()

        def edit_card_answer(self, card_id, answer):
            """ Редактирование ответа карточки по идентификатору карточки """
            self.cursor.execute('UPDATE cards SET answer = :answer WHERE rowid = :card_id',
                                {"answer": answer, "card_id": card_id})
            self.connection.commit()

        def up_card_time(self, card_id, time_multiplier):
            """ Увеличение времени показа карточки """
            time = datetime.now().strftime("%Y-%m-%d %I:%M")
            self.cursor.execute('UPDATE cards SET time = :time WHERE rowid = :card_id',
                                {"card_id": card_id, "time": time})
            self.connection.commit()

        def get_repeat_card(self, user_id):
            self.cursor.execute('SELECT question, answer, rowid FROM cards WHERE deck IN (SELECT rowid FROM decks WHERE'
                                ' owner=:user_id AND deleted=0) AND '
                                'datetime(\'now\',\'localtime\') > datetime(time, delta)', {'user_id': user_id})
            results = self.cursor.fetchall()
            cards_for_repeat = len(results)

            if not results:
                return None, None, cards_for_repeat, None

            question = results[0][0]
            answer = results[0][1]
            card_id = results[0][2]
            return question, answer, cards_for_repeat, card_id

    except sqlite3.DatabaseError as err:
        print("Error: ", err)
