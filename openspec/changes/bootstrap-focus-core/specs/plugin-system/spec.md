## ADDED Requirements

### Requirement: Contracte comú

Cada plugin SHALL proporcionar `on_enter(context)`, `on_tick(context)` i `on_exit(context)`. El nucli SHALL gestionar la invocació d'aquests hooks segons el cicle de vida de l'estat corresponent.

#### Scenario: Entrada a un estat
- WHEN un plugin és el destí d'una transició vàlida
- THEN el nucli invoca `on_enter()` després de l'èxit de `on_exit()` de l'anterior.

#### Scenario: Tick
- WHEN venç l'interval de tick i el nucli és en `RUNNING`
- THEN invoca `on_tick()` del plugin actiu.

#### Scenario: Sortida
- WHEN s'inicia una transició
- THEN invoca `on_exit()` de l'actual abans de `on_enter()` del destí.

### Requirement: Els plugins no controlen el daemon

Els plugins SHALL encapsular el comportament de l'estat i SHALL NOT finalitzar el procés ni modificar directament l'estat global del nucli. La gestió del cicle de vida i de les transicions correspon exclusivament al nucli.

#### Scenario: Plugin de destí invàlid
- WHEN el plugin de destí no es pot carregar o validar
- THEN la transició es rebutja abans de cridar `on_exit()` de l'actual
- AND l'estat lògic actual es conserva.

### Requirement: Els hooks són idempotents quan sigui possible

Els hooks SHALL implementar comportaments idempotents sempre que sigui possible, especialment en operacions d'entrada i recuperació, per evitar duplicacions d'efectes o inconsistències en els recursos gestionats.

#### Scenario: Reexecució d'entrada
- WHEN `on_enter()` es torna a executar durant una recuperació
- THEN no duplica efectes ni deixa recursos inconsistents.

### Requirement: Plugins inicials sense efectes reals

Els plugins `classe`, `test` i `practica` SHALL operar en mode simulat durant la primera fase de desenvolupament. Només podran registrar activitat i SHALL NOT executar accions que modifiquin el comportament real del sistema operatiu.

#### Scenario: Execució de plugins inicials
- WHEN s'executa `classe`, `test` o `practica` en la primera fase
- THEN només es registra activitat
- AND no es tanquen aplicacions ni es modifica el firewall o la configuració del sistema.