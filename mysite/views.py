from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Room, Seat, Reservation
from django.shortcuts import render
from datetime import datetime

def index(request):
    rooms = Room.objects.all()
    for room in rooms:
        room.free_seats = room.seats.filter(status='available').count()
        room.occupied_seats = room.seats.filter(status='occupied').count()
    return render(request, 'web.html', {'rooms': rooms})

@csrf_exempt
def get_rooms_data(request):
    rooms = Room.objects.all()
    data = []
    
    for room in rooms:
        seats = room.seats.all()
        seats_data = []
        
        for seat in seats:
            pc_data = None
            try:
                pc = seat.pc
                pc_data = {
                    'name': pc.name,
                    'processor': pc.processor,
                    'video_card': pc.video_card,
                    'ram': pc.ram
                }
            except:
                pass
            
            seats_data.append({
                'id': seat.id,
                'number': seat.seat_number,
                'name': seat.name,
                'status': seat.status,
                'pc': pc_data
            })
        
        data.append({
            'id': room.id,
            'name': room.name,
            'type': room.room_type,
            'hourly_rate': float(room.hourly_rate),
            'total_seats': room.number_of_seats,
            'free_seats': room.seats.filter(status='available').count(),
            'occupied_seats': room.seats.filter(status='occupied').count(),
            'seats': seats_data
        })
    
    return JsonResponse({'rooms': data})

@csrf_exempt
def book_seat(request):
    """Бронирование места"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['name'].split()[0] if data['name'] else '',
                    'last_name': data['name'].split()[1] if len(data['name'].split()) > 1 else '',
                    'phone': data['phone'],
                    'username': data['email']
                }
            )
            
            room = Room.objects.get(id=data['room_id'])
            seat = Seat.objects.get(room=room, seat_number=data['seat_number'])
            
            reservation = Reservation.objects.create(
                user=user,
                room=room,
                seat=seat,
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
                total_cost=data.get('cost', 0)
            )
            
            seat.status = 'reserved'
            seat.save()
            
            try:
                pc = seat.pc
                pc.status = 'occupied'
                pc.save()
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'reservation_id': reservation.id,
                'message': 'Место успешно забронировано!'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def update_seat_status(request):
    """Обновление статуса места (для админа)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            seat = Seat.objects.get(id=data['seat_id'])
            seat.status = data['status']
            seat.save()
            
            try:
                pc = seat.pc
                if data['status'] in ['occupied', 'reserved']:
                    pc.status = 'occupied'
                elif data['status'] == 'available':
                    pc.status = 'available'
                pc.save()
            except:
                pass
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def check_expired_reservations():
    """Проверка истекших бронирований"""
    now = datetime.now()
    expired_reservations = Reservation.objects.filter(
        status='active',
        date__lt=now.date()
    ).exclude(
        date=now.date(),
        end_time__gte=now.time()
    )
    
    for reservation in expired_reservations:
        reservation.status = 'completed'
        reservation.save()
        
        if reservation.seat:
            reservation.seat.status = 'available'
            reservation.seat.save()
            
            try:
                pc = reservation.seat.pc
                pc.status = 'available'
                pc.save()
            except:
                pass