# Repo guardian

Una utilidad CLI/TUI para auditar, reparar y re-lineralizar la integridad de directorios `.git`.

## Proposito

Visualizar el historial del repositorio con git, automatizar problemas relacionados al manejo de fusiones y deteccion de re-escritura.


## Instalacion

```bash
git clone https://github.com/axvg/repo-guardian-alexvega.git repo-guardian
cd repo-guardian
pip install -e .
```
Tambien se puede instalar si se descarga un archivo wheel de acuerdo a tu sistema operativo:

```bash
pip install <wheel-file>
```

## Comandos

Repo-guardian proporciona varios comandos CLI para auditar y reparar repositorios Git. Los comandos principales son:

- **scan**  
  Escanea un repositorio Git para objetos loose y packfiles.  
  Ejemplo:
  ```bash
  repo-guardian scan /ruta/al/repo
  ```

- **build-dag**  
  Construye un DAG (grafo dirigido acíclico) de los commits y lo exporta como archivo GraphML.  
  Ejemplo:
  ```bash
  repo-guardian build-dag /ruta/al/repo
  ```

- **detect-rewrites**  
  Detecta posibles reescrituras de historia usando la distancia Jaro-Winkler.  
  Ejemplo:
  ```bash
  repo-guardian detect-rewrites /ruta/al/repo
  ```

- **bisect**  
  Asiste en la busqueda de commits problemáticos usando git bisect de forma interactiva.  
  Ejemplo:
  ```bash
  repo-guardian bisect /ruta/al/repo
  ```

- **generate-script**  
  Genera scripts de reparacion para cherry-pick, rebase o reset.  
  Ejemplo:
  ```bash
  repo-guardian generate-script /ruta/al/repo
  ```

- **merge**  
  Realiza un merge de tres vias entre dos ramas, con opcion de estrategia.  
  Ejemplo:
  ```bash
  repo-guardian merge /ruta/al/repo
  ```

Para mas detalles sobre cada comando y sus opciones:
```bash
repo-guardian --help
```
