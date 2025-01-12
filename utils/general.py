from django.utils import timezone
from datetime import timedelta

class DateTimeUtils:
    @staticmethod
    def get_current_date(date):
        """
        Retorna la fecha actual en formato YYYY-MM-DD.
        """
        if not date:
            return '--/--/----'
            
        return timezone.localtime(date).strftime('%d-%m-%Y')

    @staticmethod
    def get_current_time(time):
        """
        Retorna la hora actual en formato HH:MM:SS.
        """
        if not time:
            return '--:--:--'
        return timezone.localtime(time).strftime('%H:%M:%S')

    @staticmethod
    def get_current_datetime(datetime):
        """
        Retorna la fecha y hora actuales en formato YYYY-MM-DD HH:MM:SS.
        """
        if not datetime:
            return '--/--/---- --:--:--'
        return timezone.localtime(datetime).strftime('%d-%m-%Y %H:%M:%S')   
    
    @staticmethod
    def get_format_duration(duration):
        """
        Retorna la duración en formato dias, horas y minutos.
        """
        duration = timedelta(minutes=duration)
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60

        if days > 0:
            return f"{days} día{'s' if days > 1 else ''}, {hours} hora{'s' if hours > 1 else ''} y {minutes} minuto{'s' if minutes != 1 else ''}"
        elif hours > 0:
            return f"{hours} hora{'s' if hours > 1 else ''} y {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"