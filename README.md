# Python Package Schedule

## Introducción

Esta librería contiene funciones para el manejo de tiempos y fechas.



## Desarrollo

Crear archivo `requirements.txt`:

```bash
pipenv requirements > requirements.txt
```

Si en el archivo `requirements.txt` hay una dependencia que viene de Github, deberá estar definida de la siguiente manera:
```txt
<name> @ git+https://github.com/<user>/<repo_name>.git@<id>#egg=<package>
```



Tests:

```bash
python -m unittest discover -s 'tests' -p 'test_schedule.py'
```



### Control de versiones:

```bash
Primero, actualizar la versión en el setup.py.

git tag -a <tag> -m "<descripcion>" # Crear tag local
git push origin <tag> 				# Subir tag a repositorio remoto
git tag -d <tag> 					# Eliminar tag en forma local
git push --delete origin <tag>      # Subir tag a repositorio remoto
```



## Instalación

```bash
pipenv install git+https://github.com/lcastiglione/pp-schedule.git@<tag>#egg=schedule
```



## Ejemplo de uso

```python
from schedule import schedule

print(schedule.today())
```