# Disseny tècnic: bootstrap-focus-core

## 1. Arquitectura
FOCUS és un procés local per ordinador. Components:
- **Daemon:** inicialització, bucle principal, polling, ticks i transicions.
- **State manager:** llegeix l'estat desitjat i coordina transicions.
- **Plugin loader/registry:** resol l'estat al plugin i valida el contracte.
- **Plugins:** implementen el comportament de cada estat.
- **CLI:** valida i escriu l'estat desitjat.
- **Logging:** registra arrencada, transicions, errors i recuperacions.

Els components s'han de poder provar sense privilegis ni efectes reals al sistema.

## 2. Tecnologia
Python 3.10 o superior. Evitar dependències runtime externes al nucli. El projecte s'ha de poder executar des del repositori, preferiblement amb instal·lació editable configurada a `pyproject.toml`, definint punts d'entrada (`[project.scripts]`) per a la comanda CLI `focus` i el servei `focus-daemon`. Tests i eines de desenvolupament seran dependències de desenvolupament (ex. `pytest`).

## 3. Estructura suggerida
```text
src/focus/
  main.py
  cli.py
  core/
    daemon.py
    state_manager.py
    plugin_loader.py
    plugin_contract.py
    errors.py
    logging_config.py
  plugins/
    classe.py
    test.py
    practica.py
config/state.json
tests/unit/
tests/integration/
```
És orientativa; no afegir abstraccions sense necessitat.

## 4. Contracte de plugins
Cada plugin exposa `on_enter(context)`, `on_tick(context)` i `on_exit(context)`. Els hooks són síncrons en la primera versió. Les excepcions es propaguen al nucli perquè les gestioni. Els plugins no finalitzen el procés ni modifiquen l'estat global del daemon.

L'objecte `context` (`PluginContext`) és una estructura immutable (com una dataclass) que proporciona com a mínim:
- `current_state`: estat lògic actual.
- `target_state`: estat lògic de destinació (o `None` en ticks).
- `logger`: instància de logger del sistema configurada per al plugin.

Els hooks han de ser idempotents sempre que sigui possible. Reexecutar `on_enter()` durant una recuperació ha de reconciliar l'entorn sense duplicar efectes.

Els plugins inicials només registren activitat mitjançant el logger.

## 5. Estat i transicions
Estats inicials vàlids: `classe`, `test`, `practica`. `state.json` representa l'estat desitjat, no l'estat real del sistema.

Si l'estat sol·licitat a `state.json` és idèntic a l'estat lògic actiu actual, l'operació és un no-op: no s'executa cap transició ni s'invoquen els hooks de sortida o entrada.

Valors per defecte: polling 0,5 s; tick 3 s. Ambdós configurables (per arguments d'inicialització o CLI flags).

Transició:
1. Validar i carregar el plugin de destinació abans de tocar l'actual.
2. Marcar `TRANSITIONING`.
3. Executar `on_exit()` de l'actual.
4. Executar `on_enter()` del destí.
5. Confirmar l'estat lògic només després de l'èxit del nou `on_enter()`.

Si falla `on_exit()`, no s'executa el `on_enter()` del destí; es prova de reconciliar l'origen tornant a executar-ne `on_enter()`. Si no es pot confirmar, `ERROR`.

Si falla `on_enter()` del destí, s'intenta restaurar l'estat anterior amb el seu `on_enter()`. Si falla la restauració, `ERROR`.

## 6. Estats interns
- `RUNNING`: funcionament normal.
- `TRANSITIONING`: transició en curs.
- `ERROR`: no es pot garantir la coherència de l'estat real; cal recuperació explícita.

L'estat `DEGRADED` és un indicador operatiu d'avís dins de `RUNNING` que s'activa quan un plugin acumula 5 errors consecutius de `on_tick()`. No canvia l'estat lògic ni atura el daemon.

Cal distingir **estat lògic actiu** de **restriccions reals**. En `ERROR`, el daemon continua viu per permetre diagnòstic, però no executa ticks ni transicions ordinàries i no modifica restriccions automàticament.

La primera versió no implementa encara la interfície de recuperació explícita des de `ERROR`. Cal definir-la abans d'introduir plugins amb efectes reals.

## 7. Política d'errors
### `on_tick()`
Registrar l'error, mantenir estat lògic, reintentar al tick següent. Reiniciar el comptador quan un tick tingui èxit. Després de 5 errors consecutius, marcar `DEGRADED` i avisar; el llindar serà configurable. No canviar d'estat automàticament.

### `on_exit()`
Cancel·lar la transició; no executar el destí; intentar reconciliar l'origen amb `on_enter()`. Si no es confirma la recuperació, `ERROR`.

### `on_enter()`
No confirmar el destí; intentar restaurar l'estat anterior amb `on_enter()`. Si falla la restauració, `ERROR`.

### Plugin invàlid
Rebutjar abans d'executar `on_exit()` de l'estat actual.

### Fitxer d'estat
Durant l'execució, una lectura invàlida s'ignora i es reintenta. A l'arrencada, si no hi ha un estat inicial vàlid, no s'inventa un valor per defecte: s'entra en `ERROR` i no s'executen ticks.

## 8. Política de fallada per plugin
- `preserve`: no retirar restriccions automàticament; després d'una fallada parcial, l'estat real pot ser desconegut.
- `manual`: no fer compensació automàtica; requereix intervenció.
- `cleanup`: reservat per a una fase posterior, quan hi hagi una compensació idempotent i provada.

Per defecte: `preserve`. No s'afegeix un quart hook `on_failure()` en aquesta fase. La compensació específica s'ha de dissenyar en un canvi posterior si cal.

Política inicial: `classe`, `test` i `practica` utilitzen `preserve`. Això evita desactivar automàticament restriccions d'examen o pràctica en cas d'error.

## 9. Arrencada i recuperació
1. Carregar i validar configuració.
2. Llegir estat desitjat.
3. Carregar/validar plugin.
4. Executar `on_enter()`.
5. Declarar estat actiu només si l'entrada té èxit.

Una fallada essencial provoca `ERROR`, sense ticks. La reconciliació de restriccions reals després d'un reinici queda ajornada perquè els plugins inicials no tenen efectes reals.

## 10. Fitxer d'estat i CLI
La CLI accepta només estats coneguts. Escriu un temporal al mateix directori i substitueix el destí atòmicament (`os.replace`). La CLI no executa hooks: només comunica l'estat desitjat.

Format inicial:
```json
{"state": "classe"}
```
Ruta configurable; `./config/state.json` en desenvolupament. La ruta de producció es decidirà amb el paquet Debian.

## 11. Planificació
Polling cada 0,5 s i tick cada 3 s per defecte. No hi ha ticks concurrents. Si un hook supera l'interval, s'ometen ticks pendents. El daemon implementa una aturada ordenada capturant els senyals POSIX `SIGINT` i `SIGTERM`, completant l'operació en curs i tancant netament el cicle de vida.

## 12. Logging
Utilitzar `logging` de la biblioteca estàndard. En desenvolupament, escriure a stderr/consola. journald queda per a un canvi posterior.

Registrar arrencada/aturada, estat inicial, transicions, transicions rebutjades, errors de hooks, recuperacions i entrada a `ERROR`. Incloure estat origen/destí, plugin i hook quan sigui possible. No registrar credencials ni dades personals innecessàries.

## 13. Tests
Separar tests unitaris de state manager, plugin loader, scheduler i CLI, i tests d'integració del daemon. Els plugins demostratius no han de fer accions del sistema operatiu.

## 14. Decisions ajornades
Abans d'afegir efectes reals, crear canvis per definir:
- recuperació explícita des de `ERROR`;
- reconciliació després de reiniciar daemon o ordinador;
- contracte de compensació `cleanup`;
- privilegis i límits de seguretat dels plugins;
- systemd/journald;
- integració Veyon i paquet Debian.
