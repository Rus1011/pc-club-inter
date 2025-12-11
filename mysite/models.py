from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    ROOM_TYPES = [
        ('common', 'STANDARD ЗАЛ'),
        ('vip', 'VIP ЗАЛ'),
    ]
    
    name = models.CharField('Название комнаты', max_length=100)
    number = models.IntegerField('Номер комнаты', unique=True)
    room_type = models.CharField('Тип комнаты', max_length=20, choices=ROOM_TYPES)
    hourly_rate = models.DecimalField('Ставка за час', max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
    
    def __str__(self):
        return f"Комната {self.number} - {self.name}"

class Seat(models.Model):
    STATUS_CHOICES = [
        ('available', 'Свободно'),
        ('occupied', 'Занято'),
        ('reserved', 'Забронировано'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Комната', related_name='seats')
    seat_number = models.IntegerField('Номер места')
    name = models.CharField('Название места', max_length=50, blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
    
    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'
        unique_together = ['room', 'seat_number']
    
    def __str__(self):
        return f"Место {self.seat_number} - {self.room.name}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Комната')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, verbose_name='Место', null=True, blank=True)
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='active')
    total_cost = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
    
    def __str__(self):
        return f"Бронь {self.user.username} - {self.date}"