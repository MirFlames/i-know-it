import sqlite3


class DatabaseConnection(object):
    """Documentation"""
    # TODO: Допилить класс базы данных
    def __init__(self):
        """Конструктор класса базы данных"""
        self.connection = sqlite3.connect('modules/database/i-know-db.db')
        self.cursor = sqlite3.connect('modules/database/i-know-db.db').cursor()


class DatabaseEntity(DatabaseConnection):
    def get_cards_in_deck(self, deck_id):
        """Получение карточек в колоде"""
        return self.cursor.execute('SELECT * FROM cards WHERE deck=:id', {"id": deck_id})

    def get_card_by_id(self, card_id):
        """Получение карточки по уникальному идентификатору"""
        return self.cursor.execute('SELECT * FROM cards WHERE rowid=:id', {"id": card_id})

    def get_deck_by_id(self, deck_id):
        """Получение колоды по уникальному идентификатору"""
        return self.cursor.execute('SELECT * FROM decks WHERE rowid=:id', {"id": deck_id})

    def get_decks_by_user(self, user_id):
        """Получение всех колод пользователя по идентификатору"""
        return self.cursor.execute('SELECT * FROM decks WHERE owner=:id', {"id": user_id})


class DatabaseRepository(DatabaseConnection):
    def delete_card_by_id(self, card_id):
        """Удаление карточки по идентификатору"""
        return self.cursor.execute('DELETE FROM decks WHERE rowid=:id', {"id": card_id})

    def insert_deck(self, name, owner):
        """Добавление новой колоды"""
        return self.cursor.execute('INSERT INTO decks (name, owner) VALUES (:name, :owner)',
                                   {"name": name, "owner": owner})

    def insert_card(self, question, answer, owner, deck):
        """Добавление новой карточки"""
        return self.cursor.execute(
            'INSERT INTO cards (question, answer, owner, deck) VALUES (:question, :answer, :owner, :deck)',
            {"question": question, "answer": answer, "owner": owner, "deck": deck})

    def edit_card_question(self, card_id, question):
        """Редактирование вопроса карточки по идентификатору карточки"""
        return self.cursor.execute('UPDATE cards SET question = :question, WHERE rowid = :card_id',
                                   {"question": question, "card_id": card_id})

    def edit_card_answer(self, card_id, answer):
        """Редактирование ответа карточки по идентификатору карточки"""
        return self.cursor.execute('UPDATE cards SET answer = :answer, WHERE rowid = :card_id',
                                   {"answer": answer, "card_id": card_id})

    def up_card_time(self, card_id, time):
        """Увеличение времени показа карточки"""
        # TODO: Доделать метод увеличение времени показа карточки

    def show_donation_top(self, count):
        """Показывает топ донатеров"""
        return self.cursor.execute(
            'SELECT id, donation_amount FROM users WHERE donation_amount>0 ORDER BY donation_amount LIMIT :count',
            {"count": count})
