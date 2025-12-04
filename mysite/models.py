from django.db import models

class User(models.Model):
    name = models.CharField('Имя', max_length=50)
    surname = models.CharField('Фамилия', max_length=50)
    middle_name = models.CharField('Отчество', max_length=50, blank=True)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20)
    points = models.IntegerField('Баллы', default=0)
    registration_date = models.DateTimeField('Дата регистрации', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def str(self):
        return f"{self.surname} {self.name}"

class Room(models.Model):
    ROOM_TYPES = [
        ('common', 'Обычная комната'),
        ('vip', 'VIP комната'),
        ('tournament', 'Турнирная комната'),
    ]
    
    name = models.CharField('Название комнаты', max_length=100)
    number = models.IntegerField('Номер комнаты', unique=True)
    number_of_seats = models.IntegerField('Количество мест')
    room_type = models.CharField('Тип комнаты', max_length=20, choices=ROOM_TYPES)
    has_playstation = models.BooleanField('Наличие PS', default=False)
    description = models.TextField('Описание', blank=True)
    hourly_rate = models.DecimalField('Ставка за час', max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
    
    def str(self):
        return f"Комната {self.number} - {self.name}"

class PC(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('occupied', 'Занят'),
        ('maintenance', 'На обслуживании'),
        ('broken', 'Сломан'),
    ]
    
    name = models.CharField('Название ПК', max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Комната', related_name='computers')
    processor = models.CharField('Процессор', max_length=100)
    video_card = models.CharField('Видеокарта', max_length=100)
    ram = models.CharField('Оперативная память', max_length=50)
    storage = models.CharField('Накопитель', max_length=100)
    cooler = models.CharField('Охлаждение', max_length=100, blank=True)
    system_block = models.CharField('Системный блок', max_length=100, blank=True)
    screen = models.CharField('Монитор', max_length=100)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
    
    class Meta:
        verbose_name = 'Компьютер'
        verbose_name_plural = 'Компьютеры'
    
    def str(self):
        return f"{self.name} (Комната {self.room.number})"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
        ('no_show', 'Неявка'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Комната')
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='active')
    total_cost = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ['-date', 'start_time']
    
    def str(self):
        return f"Бронь {self.user.name} - {self.date} {self.start_time}"
class Session(models.Model):
    SESSION_STATUS = [
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('paused', 'Приостановлена'),
    ]
    
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, verbose_name='Бронь', related_name='session')
    pc = models.ForeignKey(PC, on_delete=models.CASCADE, verbose_name='Компьютер')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    start_time = models.DateTimeField('Время начала сессии', auto_now_add=True)
    end_time = models.DateTimeField('Время окончания сессии', null=True, blank=True)
    status = models.CharField('Статус сессии', max_length=20, choices=SESSION_STATUS, default='active')
    total_cost = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Игровая сессия'
        verbose_name_plural = 'Игровые сессии'
    
    def str(self):
        return f"Сессия {self.user.name} - {self.start_time}"