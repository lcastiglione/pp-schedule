import functools
import gc
import itertools
import sys
import time as tm
import math
import pytz
from datetime import datetime, timedelta, date
from typing import List, Union, Optional

tz_default = pytz.timezone('America/Argentina/Buenos_Aires')


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


def is_bussines_day(actual_day: datetime = today(), holidays: dict = {}) -> bool:
    """
    Determina si un día es laborable.

    Args:
        actualDay (datetime, opcional): Día a verificar. Por defecto es el día actual.
        holidays (List[datetime], opcional): Lista de días festivos. Por defecto es una lista vacía.

    Returns:
        bool: True si el día es laborable, False de lo contrario.
    """
    if date.weekday(actual_day) > 4:
        return False
    if actual_day.year in holidays:
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


def convert_string_to_date(stringDate: Union[str, List[str]]) -> Union[datetime, List[datetime], None]:
    """
    Convierte una cadena o lista de cadenas en formato 'yyyy-mm-dd' o 'yyyy-mm-dd HH:MM:SS' a una fecha o lista de fechas datetime.

    Args:
        stringDate (Union[str, List[str]]): Cadena o lista de cadenas en formato 'yyyy-mm-dd' o 'yyyy-mm-dd HH:MM:SS'.

    Returns:
        Union[datetime, List[datetime], None]: Fecha o lista de fechas datetime correspondiente(s) a la cadena o lista de cadenas dada(s),
                                               o None si la cadena no se pudo convertir a fecha.
    """
    if isinstance(stringDate, list):
        return [convert_string_to_date(x) for x in stringDate]
    try:
        return datetime.strptime(stringDate, '%Y-%m-%d %H:%M:%S')
    except Exception:
        try:
            return datetime.strptime(stringDate, '%Y-%m-%d')
        except Exception:
            return None


def get_last_business_day() -> datetime:
    """
    Obtiene la última fecha laborable (hasta el día actual).

    Returns:
        datetime: Última fecha laborable (hasta el día actual).
    """
    # Agregar a futuro los feriados nacionales
    lastBusinessDay = today()
    numberDay = date.weekday(lastBusinessDay)
    if numberDay > 4:  # Si es sábado y domingo
        # entonces devuelvo el día viernes
        lastBusinessDay -= timedelta(days=numberDay - 4)
    return datetime.combine(lastBusinessDay, datetime.min.time())


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
    newValue = value + timedelta(days=-1)
    while not is_bussines_day(newValue):
        newValue += timedelta(days=-1)
    return newValue


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
    newValue = value + timedelta(days=1)
    while not is_bussines_day(newValue):
        newValue += timedelta(days=1)
    return newValue


def get_business_days_between(start: datetime, end: datetime) -> List[datetime]:
    """
    Obtiene una lista de las fechas laborables en el intervalo dado.

    Args:
        start (datetime): Fecha de inicio del intervalo.
        end (datetime): Fecha de fin del intervalo.

    Returns:
        List[datetime]: Lista de las fechas laborables en el intervalo dado.
    """
    arrayDates = []
    aux = start + timedelta(days=1)
    while (aux <= end):
        numberDay = date.weekday(aux)
        if numberDay <= 4:
            arrayDates.append(datetime.combine(aux, datetime.min.time()))
        aux += timedelta(days=1)
    return arrayDates


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
    newMonth = month + months
    newYear = year + years
    try:
        return datetime(newYear + math.floor((newMonth - 1) / 12), (newMonth % 12) or 12, day) + timedelta(days=days)
    except ValueError as e:
        if str(e) == 'day is out of range for month':
            return datetime(newYear + math.floor((newMonth - 1) / 12), (newMonth + 1 % 12) or 12, 1) + timedelta(days=days)
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


def get_min_between_times(start: datetime.time, end: datetime.time) -> float:
    """
    Obtiene la cantidad de minutos que hay entre dos horas dadas.

    Args:
        start (datetime.time): Hora de inicio.
        end (datetime.time): Hora de fin.

    Returns:
        float: Cantidad de minutos que hay entre las dos horas dadas.
    """
    r = datetime.combine(date.min, end) - datetime.combine(date.min, start)
    return r.total_seconds() / 60 / 5
