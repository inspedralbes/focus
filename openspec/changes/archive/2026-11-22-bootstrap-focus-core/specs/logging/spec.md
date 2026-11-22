## ADDED Requirements

### Requirement: Cicle de vida

FOCUS SHALL registrar els esdeveniments principals del cicle de vida del daemon, incloent-hi l'arrencada i l'aturada, així com el resultat de cada operació.

#### Scenario: Arrencada o aturada
- WHEN el daemon s'inicia o s'atura
- THEN registra l'esdeveniment i el resultat.

### Requirement: Transicions

FOCUS SHALL registrar les transicions d'estat, incloent-hi els estats implicats, el resultat de l'operació i les causes de fallada o rebuig quan correspongui.

#### Scenario: Transició completada
- WHEN una transició acaba correctament
- THEN registra estat d'origen, destí i resultat.

#### Scenario: Transició fallida o rebutjada
- WHEN una transició falla o es rebutja
- THEN registra la causa i la fase.

### Requirement: Context d'errors

FOCUS SHALL proporcionar informació contextual suficient als registres d'errors per identificar el plugin, el hook i l'estat implicats en una fallada, sempre que aquesta informació estigui disponible.

#### Scenario: Hook falla
- WHEN un hook llança una excepció
- THEN el registre inclou nivell, plugin, hook, estat i excepció quan estiguin disponibles.

### Requirement: Protecció de dades

FOCUS SHALL protegir la informació sensible durant el registre d'operacions i SHALL evitar l'emmagatzematge de credencials o dades personals innecessàries.

#### Scenario: Registre d'operació
- WHEN FOCUS registra una operació
- THEN no registra contrasenyes, credencials ni dades personals innecessàries.

### Requirement: Backend portable inicial

La primera versió de FOCUS SHALL utilitzar el mòdul `logging` estàndard de Python com a backend de registre, amb sortida a `stderr` o consola, sense dependències de serveis específics del sistema operatiu.

#### Scenario: Execució en desenvolupament
- WHEN el daemon s'executa des del repositori
- THEN utilitza `logging` estàndard i escriu a stderr/consola
- AND deixa journald per a un canvi posterior.