# state-management Specification

## Purpose
Definir la validació de l'estat desitjat, les transicions seqüencials i l'actualització atòmica de state.json per la CLI.

## Requirements

### Requirement: Estats inicials vàlids

Els identificadors vàlids SHALL ser `classe`, `test` i `practica`. El nucli SHALL validar qualsevol estat rebut abans de resoldre i executar el plugin corresponent.

#### Scenario: Estat conegut
- WHEN `state.json` conté un estat vàlid diferent de l'actual
- THEN el daemon resol el plugin i inicia la transició.

#### Scenario: Estat conegut idèntic a l'actual
- WHEN `state.json` conté un estat vàlid idèntic a l'estat lògic actiu
- THEN no s'executa cap transició ni s'invoquen els hooks de sortida o entrada.

#### Scenario: Estat desconegut
- WHEN el fitxer conté un identificador desconegut
- THEN es rebutja la lectura, es conserva l'estat lògic i es registra l'error.

### Requirement: Ordre i confirmació de transicions

El nucli SHALL executar les transicions de manera seqüencial, respectant l'ordre dels hooks i confirmant el canvi d'estat únicament quan la inicialització del nou estat hagi finalitzat correctament.

#### Scenario: Transició correcta
- WHEN FOCUS canvia d'estat
- THEN executa `on_exit()` de l'actual abans de `on_enter()` del destí
- AND confirma el nou estat només després de l'èxit de `on_enter()`.

#### Scenario: Error en la sortida
- WHEN falla `on_exit()` de l'estat actual
- THEN no s'executa `on_enter()` del destí
- AND s'aplica la recuperació especificada a `error-handling`.

### Requirement: `state.json` és l'estat desitjat

El fitxer `state.json` SHALL representar exclusivament l'estat desitjat per l'usuari o per la CLI, sense garantir que les restriccions efectives del sistema coincideixin amb aquest estat.

#### Scenario: Lectura invàlida durant execució
- WHEN el fitxer és inaccessible o conté JSON invàlid
- THEN es conserva l'últim estat lògic vàlid
- AND es registra l'error i es reintenta la lectura.

### Requirement: CLI amb escriptura atòmica

La CLI SHALL validar els identificadors d'estat abans d'escriure'ls i SHALL utilitzar escriptura atòmica per actualitzar `state.json`, evitant que una interrupció durant l'escriptura deixi un fitxer parcial o corrupte.

#### Scenario: Sol·licitud vàlida
- WHEN la CLI rep un estat vàlid
- THEN valida l'identificador i escriu temporal al mateix directori abans de substituir atòmicament el fitxer.

#### Scenario: Sol·licitud invàlida
- WHEN la CLI rep un estat desconegut
- THEN retorna un error i no modifica el fitxer.
