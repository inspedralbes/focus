# Tasques: bootstrap-focus-core

Executar en ordre. No marcar cap tasca com a completada sense executar la verificació.

## 1. Estructura del projecte
- [x] 1.1 Crear estructura Python amb `src/` i `tests/`.
- [x] 1.2 Configurar `pyproject.toml` amb Python mínim 3.10 i entry points (`focus`, `focus-daemon`).
- [x] 1.3 Configurar dependències de desenvolupament i tests (`pytest`).
- [x] 1.4 Configurar mòdul base de `logging` (`core/logging_config.py`).
- [x] 1.5 Verificar instal·lació editable i importació del paquet.

## 2. Contracte i plugins
- [x] 2.1 Definir contracte de plugin i estructura `PluginContext`.
- [x] 2.2 Implementar registre/carregador de plugins.
- [x] 2.3 Validar els tres hooks obligatoris (`on_enter`, `on_tick`, `on_exit`).
- [x] 2.4 Crear `classe`, `test` i `practica`.
- [x] 2.5 Fer que els plugins registrin activitat mitjançant el logger.
**Verificació:** tests de càrrega, contracte i invocació dels hooks.

## 3. Estat i transicions
- [x] 3.1 Definir estats vàlids i enumeració d'estats interns (`RUNNING`, `TRANSITIONING`, `ERROR`).
- [x] 3.2 Llegir i validar `state.json`.
- [x] 3.3 Implementar gestió d'idempotència (no-op si l'estat és l'actual) i ordre `on_exit()` → `on_enter()`.
- [x] 3.4 Confirmar estat només després d'un `on_enter()` correcte.
- [x] 3.5 Validar plugin destí abans de tocar el plugin actual.
- [x] 3.6 Gestionar lectures invàlides durant l'execució.
**Verificació:** tests d'ordre, transició, plugin invàlid, no-op i JSON invàlid.

## 4. Daemon i planificació
- [x] 4.1 Implementar inicialització i entrada a estat inicial.
- [x] 4.2 Implementar polling configurable (0,5 s per defecte).
- [x] 4.3 Implementar tick configurable (3 s per defecte).
- [x] 4.4 Evitar ticks concurrents i descartar ticks perduts.
- [x] 4.5 Implementar aturada ordenada amb captura de senyals `SIGINT` i `SIGTERM`.
**Verificació:** tests de cicle de vida, polling, scheduler i aturada per senyal.

## 5. Gestió d'errors
- [x] 5.1 Implementar cicle de vida d'estats interns i transicions d'error.
- [x] 5.2 Implementar comptador de ticks fallits i estat `DEGRADED`.
- [x] 5.3 Recuperar l'origen si falla `on_exit()`.
- [x] 5.4 Restaurar estat anterior si falla `on_enter()` del destí.
- [x] 5.5 Entrar en `ERROR` si la recuperació no es confirma.
- [x] 5.6 En `ERROR`, aturar ticks/transicions ordinàries i no modificar restriccions.
- [x] 5.7 Implementar política per defecte `preserve`.
- [x] 5.8 Evitar que excepcions de hooks finalitzin el daemon.
**Verificació:** tests de tots els escenaris de `error-handling/spec.md`.

## 6. CLI i persistència
- [x] 6.1 Implementar CLI per `classe`, `test`, `practica`.
- [x] 6.2 Validar arguments abans d'escriure.
- [x] 6.3 Implementar temporal + substitució atòmica (`tempfile` + `os.replace`).
- [x] 6.4 Permetre configurar la ruta de l'estat.
- [x] 6.5 Documentar execució en un segon terminal.
**Verificació:** tests CLI, estat invàlid, errors d'escriptura i atomicitat.

## 7. Logging
- [x] 7.1 Verificar configuració i format de `logging` estàndard segons especificació.
- [x] 7.2 Assegurar registre complet d'arrencada, estat inicial i transicions.
- [x] 7.3 Assegurar registre complet d'errors, recuperacions i entrada a `ERROR`.
- [x] 7.4 Incloure plugin/hook/estats quan sigui possible i verificar no registre de dades sensibles.
**Verificació:** tests de logs amb `caplog` o handler equivalent.

## 8. Verificació final
- [x] 8.1 Executar tota la suite de tests.
- [x] 8.2 Revisar dependències runtime (confirmar que només s'usa biblioteca estàndard).
- [x] 8.3 Provar `classe` → `test` → `practica` → `classe`.
- [x] 8.4 Verificar que cap plugin demostratiu modifica el sistema.
- [x] 8.5 Actualitzar README i documentar limitacions.

**Finalització:** totes les tasques completades, tests verds i implementació coherent amb les especificacions.
