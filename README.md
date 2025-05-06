
![License](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg) [![CI](https://github.com/axvg/repo-guardian-alexvega/actions/workflows/ci.yml/badge.svg)](https://github.com/axvg/repo-guardian-alexvega/actions/workflows/ci.yml)


## Video:
<a href="http://www.youtube.com/watch?feature=player_embedded&v=axjuHYzgE1U" target="_blank">
 <img src="http://img.youtube.com/vi/axjuHYzgE1U/mqdefault.jpg" alt="Watch the video" width="240" height="180" border="10" />
</a>


# Repo-guardian

Una utilidad CLI/TUI para auditar, reparar y re-lineralizar la integridad de directorios `.git`.

## Proposito

Visualizar el historial del repositorio con git, automatizar problemas relacionados al manejo de fusiones y deteccion de re-escritura.

## Caracteristicas

- Escaneo de objetos Git (loose y packfiles)
- Construccion de DAG (Directed Acyclic Graph) de commits
- Calculo de Generation Numbers (GN)
- Deteccion de reescritura de historia mediante algoritmo Jaro-Winkler
- Exportacion de grafos en formato GraphML
- Creacion de scripts para automatizacion

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