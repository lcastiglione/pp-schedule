# Python Package Schedule

## Introducción

Esta librería contiene funciones para el manejo de tiempos y fechas.



## Desarrollo

Crear archivo `requirements.txt`: 

```bash
pipenv requirements > requirements.txt
```

Tests:

```bash
python -m unittest discover -s 'tests' -p 'test_schedule.py'
```



## Instalación

```bash
pipenv install git+https://github.com/lcastiglione/pp-schedule#egg=schedule
```



## Aplicación

```python
from schedule import schedule

print(schedule.today())
```