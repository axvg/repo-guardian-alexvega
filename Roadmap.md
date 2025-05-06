# Roadmap repo-guardian

Este documento detalla el plan general para el proyecto Repo-guardian. Se muestra epicas conectadas a historias de usuario y tareas ademas de su prioridad y estado en el tablero Kanban.

|   Epica   |   Historia    |   Tarea   |   Prioridad   |   Etiqueta Kanban |   Issue en GitHub |
|-----------|---------------|-----------|---------------|-------------------|-------------------|
| **E-00 Configuracion**|| RX-01 Crear repo | Alta  | Done | https://github.com/axvg/repo-guardian/issues/1 |
|   | | RX-02 Configurar CI | Alta  | Done | https://github.com/axvg/repo-guardian/issues/2 |
|   | | RX-03 Crear plantillas  | Alta  | Done | https://github.com/axvg/repo-guardian/issues/3 |
|   | | RX-04 Roadmap inicial   | Alta  | Done | https://github.com/axvg/repo-guardian/issues/4 |
| **E-01 Escaneo de objetos loose**|| RX-05 Implementar lectura binaria de objetos sueltos | Alta  | Done | https://github.com/axvg/repo-guardian/issues/6 |
| **E-02 Escaneo de packfiles**|| RX-06 Implementar lectura de packfiles | Alta  | Done | https://github.com/axvg/repo-guardian/issues/9 |
|   | | RX-07 Crear feature BDD para packfile corrupto | Media  | In Progress | https://github.com/axvg/repo-guardian/issues/10 |
|   | | RX-08 Crear pruebas unitarias para parsing de packfiles | Alta  | Done | https://github.com/axvg/repo-guardian/issues/11 |
|   | | RX-09 Agregar cli para lecturas de Git objects | Alta | Done | https://github.com/axvg/repo-guardian/issues/14 |
|  **E-03 Implementacion de DAG** | | RX-10 Crear archivo mermaid con la estructura del DAG de commits | Media | Done | https://github.com/axvg/repo-guardian/issues/17 |
|   | | RX-11 Implementar estructura de DAG en dag_builder.py | Alta | Done | https://github.com/axvg/repo-guardian/issues/18 |
|   | | RX-12 Implementar construccion completa del grafo  | Alta | Done | https://github.com/axvg/repo-guardian/issues/21 |
|   | | RX-13 Implementar calculo de Generation Number (GN) | Alta | Done | https://github.com/axvg/repo-guardian/issues/22 |
| **E-04 Implementacion de JW**  | | RX-14 Implementar deteccion JW | Alta | Done | https://github.com/axvg/repo-guardian/issues/25 |
| **E-05 Script para post-merge** | | RX-15 Implementar hook post-merge | Alta | Done | https://github.com/axvg/repo-guardian/issues/23 |
| **E-06 Entrega de release de v 0.5.0**  | | RX-16 Configurar release de v0.5.0 | Alta | Done | https://github.com/axvg/repo-guardian/issues/24 |
| **E-07 Implementacion de reparacion**   | | RX-17 Implementar integracion con git bisect    | Alta | Done | https://github.com/axvg/repo-guardian/issues/31 |
|   | | RX-18 Implementar generacion scripts rebase/cherry-pick | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/33 |
|   | | RX-19 Implementar manejo de three-way merge  | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/34 |
|   | | RX-20  Implementar script recuperacion reflog+reset | Alta | In Progress |  |
| **E-08 Implementacion de interfaz de usuario**   | | RX-21 Implementar mas comandos CLI    | Alta | Done |  |
|   | | RX-22  Configurar auto-completado para CLI | Baja | In Progress |  |
|   | | RX-23  Publicar reportes JUnit para Github actions annotations | Baja | In Progress |  |
| **E-09 Implementacion de medicion de rendimiento**   | | RX-24 Implementar script benchmark vs git fsck   | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/36 |
|   | | RX-25  Integrar con en MkDocs | Media | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/37 |
|   | | RX-26  Publicar en MkDocs | Baja | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/37 |
| **E10 Preparar release v0.9.0**   | | RX-27 Preparar release v0.9.0   | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/41 |
| **E11 Preparar release v.1.0**   | | RX-28 Actualizar github actions para release | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/43 |
| | RX-29 Preparar release v1.0.0   | Alta | In Progress | https://github.com/axvg/repo-guardian-alexvega/issues/42 |

