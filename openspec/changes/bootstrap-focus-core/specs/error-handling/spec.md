## ADDED Requirements

### Requirement: Estats interns i estat real

El nucli SHALL distingir `RUNNING`, `TRANSITIONING` i `ERROR`, així com l'estat lògic actiu de les restriccions reals del sistema.

#### Scenario: Efectes parcials
- WHEN un hook pot haver modificat parcialment el sistema abans de fallar
- THEN l'estat real es marca com a desconegut/no verificat
- AND no s'infereix a partir de l'estat lògic.

### Requirement: Errors de tick recuperables

El nucli SHALL tractar els errors de `on_tick()` com a recuperables, mantenint l'estat lògic actiu i permetent nous intents d'execució. També SHALL controlar els errors consecutius per detectar plugins degradats.

#### Scenario: Un tick falla
- WHEN `on_tick()` llança una excepció
- THEN es registra, es manté l'estat lògic i es reintenta al tick següent.

#### Scenario: Cinc errors consecutius
- WHEN un plugin acumula cinc errors consecutius de tick
- THEN es marca `DEGRADED`, es registra un avís d'alta severitat i no es canvia automàticament d'estat.

#### Scenario: Tick correcte després d'errors
- WHEN un tick acaba correctament
- THEN es reinicia el comptador d'errors consecutius.

### Requirement: Fallada de `on_exit()`

El nucli SHALL impedir la confirmació d'una transició quan falla `on_exit()` de l'estat actual i SHALL intentar recuperar l'estat d'origen abans de continuar l'execució.

#### Scenario: Error en sortir
- WHEN falla `on_exit()` de l'actual
- THEN no s'executa `on_enter()` del destí
- AND s'intenta reconciliar l'origen amb el seu `on_enter()`
- AND si no es confirma la recuperació, el nucli entra en `ERROR`.

### Requirement: Fallada de `on_enter()`

El nucli SHALL impedir la confirmació d'un nou estat quan falla el seu `on_enter()` i SHALL intentar restaurar l'estat anterior abans de reprendre l'execució.

#### Scenario: Error en entrar al destí
- WHEN falla `on_enter()` del destí
- THEN no es confirma el nou estat
- AND s'intenta restaurar l'estat anterior amb el seu `on_enter()`
- AND si la restauració té èxit, es torna a `RUNNING` amb l'estat anterior
- AND si falla, s'entra en `ERROR`.

### Requirement: Política de fallada prudent

La política per defecte SHALL ser `preserve`. `cleanup` només s'habilitarà amb compensació idempotent i provada. `manual` requereix intervenció explícita.

#### Scenario: Política preserve
- WHEN falla un plugin amb política `preserve`
- THEN no s'eliminen automàticament restriccions
- AND l'estat real es considera potencialment desconegut si hi ha hagut efectes parcials.

#### Scenario: Sense compensació segura
- WHEN no hi ha compensació segura i provada
- THEN el nucli no improvisa una neteja genèrica.

### Requirement: Comportament en ERROR

El nucli SHALL mantenir un comportament conservador quan entra en `ERROR`, impedint operacions ordinàries que puguin modificar les restriccions del sistema i preservant la possibilitat de diagnòstic.

#### Scenario: Nucli en ERROR
- WHEN el nucli entra en `ERROR`
- THEN atura els ticks i rebutja transicions ordinàries
- AND no afegeix ni elimina restriccions automàticament
- AND manté el procés viu per permetre diagnòstic.

### Requirement: Fallada d'arrencada

El nucli SHALL gestionar les fallades durant l'arrencada sense declarar actiu un estat que no s'ha pogut inicialitzar correctament.

#### Scenario: `on_enter()` inicial falla
- WHEN falla el `on_enter()` inicial
- THEN l'estat no es declara actiu
- AND el nucli entra en `ERROR` i no executa ticks.

### Requirement: Logging d'errors

El nucli SHALL registrar les fallades dels hooks i dels processos de recuperació amb informació suficient per facilitar-ne el diagnòstic i la traçabilitat.

#### Scenario: Hook o recuperació falla
- WHEN falla un hook o una recuperació
- THEN el log inclou, quan sigui possible, plugin, hook, estats, excepció i resultat de recuperació.