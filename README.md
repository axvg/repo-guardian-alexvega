
![License](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg) [![CI](https://github.com/axvg/repo-guardian-alexvega/actions/workflows/ci.yml/badge.svg)](https://github.com/axvg/repo-guardian-alexvega/actions/workflows/ci.yml)

# Repo-guardian

Una utilidad CLI/TUI para auditar, reparar y re-lineralizar la integridad de directorios `.git`.

## Proposito

Asegurar la integridad del historial del repositorio con git, identificando y corrigiendo corrupciones de datos.

## Caracteristicas

- Escaneo de objetos Git (loose y packfiles)
- Construccion de DAG (Directed Acyclic Graph) de commits
- Calculo de Generation Numbers (GN)
- Deteccion de reescritura de historia mediante algoritmo Jaro-Winkler
- Exportacion de grafos en formato GraphML

## Instalacion

```sh
git clone https://github.com/axvg/repo-guardian-alexvega.git repo-guardian
cd repo-guardian
# TODO
```

## Uso

```sh
# TODO
```