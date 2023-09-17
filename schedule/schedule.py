"""Módulo con funciones para manejar fechas y horas"""
from typing import List, Union, Optional
from datetime import datetime, timedelta, date
import functools
import gc
import itertools
import random
import sys
import time as tm
import math
import pytz


tz_default = pytz.timezone('America/Argentina/Buenos_Aires')
LIST_DATE_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%f','%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S']


def timeit(_func=None, *, repeat: int = 1, number: int = 1, file=sys.stdout):
    """
    Decorador que mide y muestra el tiempo de las mejores pruebas de "repetición". Imita `timeit.repeat()`, pero imprime en consola el tiempo promedio. Devuelve el resultado de la función e imprime la hora.

    Args:
        _func (Callable, opcional): Función a cronometrar. Por defecto es None.
        repeat (int, opcional): Número de veces que la función será ejecutada para obtener el tiempo promedio. Por defecto es 1.
        number (int, opcional): Número de llamadas a la función por prueba. Por defecto es 1.
        file (IO, opcional): Un archivo de flujo de texto donde se imprimirá la salida. Por defecto es sys.stdout. Si es None, muestra el resultado

    Returns:
        Callable: Función a cronometrar.
    """

    _repeat = functools.partial(itertools.repeat, None)

    def wrap(func):
        @functools.wraps(func)
        def _timeit(*args, **kwargs):
            # Apaga temporalmente la recolección de basura durante el tiempo. Hace que los tiempos independientes sean más comparables. Si estaba habilitado originalmente, vuelva a encenderlo después.
            gcold = gc.isenabled()
            gc.disable()
            try:
                # Bucle externo para el número de repeticiones.
                trials = []
                result = None
                for _ in _repeat(repeat):
                    # Bucle interno para el número de llamadas dentro de cada repetición.
                    total = 0
                    for _ in _repeat(number):
                        start = tm.time_ns()
                        result = func(*args, **kwargs)
                        total += tm.time_ns() - start
                    trials.append(total)
                # Se calcula el "tiempo promedio" de la "mejor" prueba.
                best = min(trials) / number
                message = f"La función `{func.__name__}` se ejecutó en un promedio de {get_time(best)} en {repeat} pruebas con {number} llamadas de función por prueba"
                if file:
                    print(f"\n{message}", end="\n\n", file=file)
                # El resultado se devuelve *solo una vez*
                return result
            finally:
                if gcold:
                    gc.enable()
        return _timeit

    # Para que no salte un error si no hay ninguna función a conrometrar
    return wrap if _func is None else wrap(_func)


def get_time(t: float) -> str:
    """
    Convierte un tiempo en nanosegundos a una cadena de texto con una unidad de tiempo más adecuada.

    Args:
        t (float): Tiempo en nanosegundos.

    Returns:
        str: Tiempo convertido a cadena con la unidad de tiempo más adecuada.
    """
    if t < 1000:  # menor a 1uS
        return f"{round(t, 3)}nS"
    elif t < 1000000:  # menor a 1mS
        return f"{round(t/1000, 3)}uS"
    elif t < 1000000000:  # menor a 1S
        return f"{round(t/1000000, 3)}mS"
    elif t < 60000000000:  # menor a 1min
        return f"{round(t/1000000000, 3)}S"
    return f"{round(t/60000000000, 3)}min"


def today(tz=tz_default) -> datetime:
    """
    Obtiene la fecha y hora actual en la zona horaria dada.

    Args:
        tz (tzinfo, opcional): Zona horaria.

    Returns:
        datetime: Fecha y hora actual en la zona horaria dada.
    """
    return datetime.now(tz=tz)


def is_bussines_day(actual_day: datetime = today(), holidays: dict = None) -> bool:
    """
    Determina si un día es laborable.

    Args:
        actual_day (datetime, opcional): Día a verificar. Por defecto es el día actual.
        holidays (List[datetime], opcional): Lista de días festivos. Por defecto es una lista vacía.

    Returns:
        bool: True si el día es laborable, False de lo contrario.
    """
    if date.weekday(actual_day) > 4:
        return False
    if holidays and actual_day.year in holidays:
        return actual_day.date() not in holidays[actual_day.year]
    return True


def date_to_int(value: Union[str, datetime]) -> int:
    """
    Convierte una fecha en formato 'yyyy-mm-dd' o datetime a una representación en milisegundos.

    Args:
        value (Union[str, datetime]): Fecha en formato 'yyyy-mm-dd' o datetime.

    Returns:
        int: Representación en milisegundos de la fecha dada.
    """
    if isinstance(value, str):
        return int(datetime.fromisoformat(value).timestamp() * 1000)
    return int(datetime.timestamp(value) * 1000)


def int_to_date(time_ms: int) -> datetime:
    """
    Convierte una representación en milisegundos a una fecha datetime.

    Args:
        value (int): Representación en milisegundos de una fecha.

    Returns:
        datetime: Fecha correspondiente a la representación en milisegundos.
    """
    return datetime.fromtimestamp(time_ms / 1000)


def get_seconds_by_time(value: datetime) -> int:
    """
    Obtiene la cantidad de segundos que han transcurrido desde las 00:00 horas hasta la hora de la fecha dada.

    Args:
        value (datetime): Fecha de la que obtener la cantidad de segundos.

    Returns:
        int: Cantidad de segundos que han transcurrido desde las 00:00 hasta la hora de la fecha dada.
    """
    return value.hour * 60 * 60 + value.minute * 60 + value.second


def convert_string_to_date(date_str: Union[str, List[str]]) -> Union[datetime, List[datetime], None]:
    """
    Convierte una cadena o lista de cadenas en formato 'yyyy-mm-dd' o 'yyyy-mm-dd HH:MM:SS' a una fecha o lista de fechas datetime.

    Args:
        date_str (Union[str, List[str]]): Cadena o lista de cadenas en formato 'yyyy-mm-dd' o 'yyyy-mm-dd HH:MM:SS'.

    Returns:
        Union[datetime, List[datetime], None]: Fecha o lista de fechas datetime correspondiente(s) a la cadena o lista de cadenas dada(s),
                                               o None si la cadena no se pudo convertir a fecha.
    """
    if isinstance(date_str, list):
        return [convert_string_to_date(x) for x in date_str]
    result = None
    for date_format in LIST_DATE_FORMATS:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass
    return result


def get_last_business_day() -> datetime:
    """
    Obtiene la última fecha laborable (hasta el día actual).

    Returns:
        datetime: Última fecha laborable (hasta el día actual).
    """
    # Agregar a futuro los feriados nacionales
    last_business_day = today()
    numberDay = date.weekday(last_business_day)
    if numberDay > 4:  # Si es sábado y domingo
        # entonces devuelvo el día viernes
        last_business_day -= timedelta(days=numberDay - 4)
    return datetime.combine(last_business_day, datetime.min.time())


def get_prev_business_day(value: datetime, keep: bool = False) -> datetime:
    """
    Obtiene la fecha laborable anterior a la fecha dada.

    Args:
        value (datetime): Fecha a partir de la cual obtener la fecha laborable anterior.
        keep (bool, opcional): Si es True y 'value' es un día laborable, se devuelve 'value'. Si es False, de devuleve el día hábil anterior a 'value'. Por defecto es False.

    Returns:
        datetime: Fecha laborable anterior a la fecha dada.
    """
    if keep:
        if is_bussines_day(value):
            return value
    new_value = value + timedelta(days=-1)
    while not is_bussines_day(new_value):
        new_value += timedelta(days=-1)
    return new_value


def get_next_business_day(value: datetime, keep: bool = False) -> datetime:
    """
    Obtiene la fecha laborable siguiente a la fecha dada.

    Args:
        value (datetime): Fecha a partir de la cual obtener la fecha laborable siguiente.
        keep (bool, opcional):  Si es True y 'value' es un día laborable, se devuelve 'value'. Si es False, de devuleve el día hábil posterior a 'value'. Por defecto es False.

    Returns:
        datetime: Fecha laborable siguiente a la fecha dada.
    """
    if keep:
        if is_bussines_day(value):
            return value
    new_value = value + timedelta(days=1)
    while not is_bussines_day(new_value):
        new_value += timedelta(days=1)
    return new_value


def get_business_days_between(start: datetime, end: datetime) -> List[datetime]:
    """
    Obtiene una lista de las fechas laborables en el intervalo dado.

    Args:
        start (datetime): Fecha de inicio del intervalo.
        end (datetime): Fecha de fin del intervalo.

    Returns:
        List[datetime]: Lista de las fechas laborables en el intervalo dado.
    """
    array_dates = []
    aux = start + timedelta(days=1)
    while (aux <= end):
        number_day = date.weekday(aux)
        if number_day <= 4:
            array_dates.append(datetime.combine(aux, datetime.min.time()))
        aux += timedelta(days=1)
    return array_dates


def up_date(ref: datetime, days: int = 0, months: int = 0, years: int = 0) -> datetime:
    """
    Añade una cantidad de días, meses y años a una fecha dada.

    Args:
        ref (datetime): Fecha a la cual añadir los días, meses y años.
        days (int, opcional): Cantidad de días a añadir. Por defecto es 0.
        months (int, opcional): Cantidad de meses a añadir. Por defecto es 0.
        years (int, opcional): Cantidad de años a añadir. Por defecto es 0.

    Returns:
        datetime: Fecha obtenida después de añadir la cantidad de días, meses y años dada a la fecha 'ref'.
    """
    if not months and not years and not days:
        return ref
    year, month, day = ref.timetuple()[:3]
    new_month = month + months
    new_year = year + years
    try:
        return datetime(new_year + math.floor((new_month - 1) / 12), (new_month % 12) or 12, day) + timedelta(days=days)
    except ValueError as e:
        if str(e) == 'day is out of range for month':
            return datetime(new_year + math.floor((new_month - 1) / 12), (new_month + 1 % 12) or 12, 1) + timedelta(days=days)
        raise (e)


def add_time(ref: datetime.time, hours: Optional[int] = None, minutes: Optional[int] = None, seconds: Optional[int] = None) -> datetime.time:
    """
    Añade una cantidad de horas, minutos y segundos a una hora dada.

    Args:
        ref (datetime.time): Hora a la cual añadir las horas, minutos y segundos.
        hours (Optional[int], opcional): Cantidad de horas a añadir. Por defecto es None.
        minutes (Optional[int], opcional): Cantidad de minutos a añadir. Por defecto es None.
        seconds (Optional[int], opcional): Cantidad de segundos a añadir. Por defecto es None.

    Returns:
        datetime.time: Hora obtenida después de añadir la cantidad de horas, minutos y segundos dada a la hora 'ref'.
    """
    hours = 0 if not hours else hours
    minutes = 0 if not minutes else minutes
    seconds = 0 if not seconds else seconds
    return (datetime.combine(today(), ref) + timedelta(hours=hours, minutes=minutes, seconds=seconds)).time()


def convert_seconds_to_time(seconds):
    """Convierte una cantidad de segundos a formato de tiempo (HH:MM:SS).

    Args:
        seconds (int): Cantidad de segundos.

    Returns:
        str: Cantidad de segundos convertida a formato de tiempo (HH:MM:SS).
    """
    hour = seconds / 60 / 60
    minutes = (hour - math.trunc(hour)) * 60
    sec = (min - math.trunc(min)) * 60
    return f"{math.trunc(hour)}:{math.trunc(minutes)}:{math.trunc(sec)}"


def ajust_date(date_str: str, days: int) -> str:
    """
    Ajusta una fecha en formato string sumando o restando días.

    Parámetros:
    - date_str (str): fecha en formato 'YYYY-MM-DDTHH:MM:SS'
    - days (int): número de días a sumar o restar

    Devuelve:
    - str: fecha ajustada en formato 'YYYY-MM-DDTHH:MM:SS'
    """

    # Convertir el string a un objeto datetime
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

    # Ajustar la fecha
    adjusted_date = date_obj + timedelta(days=days)

    # Convertir el objeto datetime de nuevo a string
    return adjusted_date.strftime('%Y-%m-%dT%H:%M:%S')


def get_min_between_times(start: datetime.time, end: datetime.time) -> float:
    """
    Obtiene la cantidad de minutos que hay entre dos horas dadas.

    Args:
        start (datetime.time): Hora de inicio.
        end (datetime.time): Hora de fin.

    Returns:
        float: Cantidad de minutos que hay entre las dos horas dadas.
    """
    result = datetime.combine(date.min, end) - datetime.combine(date.min, start)
    return result.total_seconds() / 60 / 5


def get_random_date(origin_date=datetime.now(), days=None):
    """Genera una fecha aleatoria en formato de string.

    Args:
        origin_date (datetime): Fecha de inicio para generar las fechas aleatorias. Por default es la fecha actual.
        days (int): Permite sumar una suma fija de días para que no sea aleatoria la fecha generada.

    Returns:
        str: Fecha y hora aleatoria en formato 'YYYY-MM-DD HH:MM:SS'.
    """
    random_days = random.randint(-365, 0) if not days else days
    random_date = origin_date + timedelta(days=random_days)

    # Devuelve la fecha en el formato '%Y-%m-%d %H:%M:%S'
    return f"{random_date.isoformat().split('T')[0]}T00:00:00"


def get_random_date_with_time(truncate=True):
    """Genera una fecha y hora aleatoria en formato de string. Opcionalmente, se
    pueden truncar los último 3 dígitos de los milisegundos.

    Args:
        truncate (boolean): Define si se truncan los dígitos de los milisegundos.
        Por default está en True.

    Returns:
        str: Fecha y hora aleatoria en formato 'YYYY-MM-DD HH:MM:SS'.
    """
    random_number_of_days = random.randint(-365, 0)
    random_date = datetime.now() + timedelta(days=random_number_of_days)

    # Devuelve la fecha en el formato '%Y-%m-%d %H:%M:%S:%f'
    full_time = random_date.isoformat().split('.')
    if truncate:
        time = full_time[1][:3]
        return f"{full_time[0]}.{time}000"
    return full_time


def get_random_time_milli():
    """Genera un valor entero aleatorio que representa el tiempo en milisegundos.

    Returns:
        int: Valor entero aleatorio que representa el tiempo en milisegundos.
    """
    return random.randint(0, (86400000 - 1))


def get_random_full_date(day=1, month=1, year=2019):
    """Genera una fecha y hora completa aleatoria en formato de cadena.

    Args:
        day (int, optional): Día de la fecha. Valor predeterminado es 1.
        month (int, optional): Mes de la fecha. Valor predeterminado es 1.
        year (int, optional): Año de la fecha. Valor predeterminado es 2019.

    Returns:
        str: Fecha y hora aleatoria completa en formato 'YYYY-MM-DD HH:MM:SS.ssssss'.
    """
    hour = random.randint(0, 23)
    minutes = random.randint(0, 59)
    sec = random.randint(0, 59)
    milli = random.randint(0, 999999)
    return f"{year}-{month}-{day} {hour}:{minutes}:{sec}.{milli}"
