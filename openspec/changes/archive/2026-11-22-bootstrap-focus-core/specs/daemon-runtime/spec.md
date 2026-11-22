## ADDED Requirements

### Requirement: El daemon funciona localment

FOCUS SHALL executar-se com a daemon local independent a cada ordinador. La primera versió SHALL NOT requerir servidor central, API ni connexió pròpia de xarxa.

#### Scenario: Arrencada vàlida
- WHEN el daemon s'inicia amb configuració i estat inicial vàlids
- THEN carrega el plugin i n'executa `on_enter()`
- AND només declara l'estat actiu després de l'èxit.

#### Scenario: Estat inicial absent o invàlid
- WHEN no es pot llegir un estat inicial vàlid
- THEN el daemon no inventa un estat per defecte
- AND registra l'error, entra en `ERROR` i no executa ticks.

### Requirement: Polling i ticks configurables

El daemon SHALL comprovar `state.json` cada 0,5 segons per defecte i executar `on_tick()` cada 3 segons per defecte. Els intervals SHALL ser configurables. El daemon SHALL gestionar l'aturada ordenada mitjançant senyals del sistema.

#### Scenario: Tick periòdic
- WHEN el nucli és en `RUNNING` i venç l'interval
- THEN executa `on_tick()` del plugin actiu.

#### Scenario: Hook més llarg que l'interval
- WHEN un tick dura més que l'interval
- THEN no s'inicia cap tick concurrent
- AND s'ometen els ticks vençuts durant l'execució.

#### Scenario: Aturada ordenada per senyal
- WHEN el daemon rep un senyal d'interrupció (SIGINT o SIGTERM)
- THEN finalitza ordenadament el bucle actual i registra l'aturada.

### Requirement: Aïllament de fallades de plugins

El nucli SHALL aïllar les excepcions produïdes pels hooks dels plugins i aplicar la política de gestió d'errors definida, evitant que una excepció no gestionada provoqui la finalització inesperada del daemon.

#### Scenario: Hook llança una excepció
- WHEN un hook llança una excepció gestionable
- THEN el nucli aplica la política d'errors
- AND el daemon no finalitza per aquella excepció.