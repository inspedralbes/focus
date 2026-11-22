# FOCUS core

Nucli local de FOCUS per a Python 3.10 o superior. Els plugins inicials (`classe`, `test`, `practica`) només registren activitat: no canvien la configuració ni les restriccions del sistema.

## Desenvolupament

En PowerShell, des de l'arrel del repositori, crea l'entorn i executa els tests amb **el mateix intèrpret**:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m pytest -q
```

Pytest crea una carpeta temporal nova dins del repositori per a cada execució i la neteja en acabar. Això evita problemes de permisos amb la carpeta temporal global de Windows o amb directoris temporals compartits entre comptes.
La memòria cau de pytest està desactivada per evitar avisos de permisos quan s'executen els tests amb comptes diferents.

En altres sistemes, les ordres equivalents són:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

En un terminal, des de l'arrel del repositori:

```sh
focus-daemon --state-file config/state.json
```

En un segon terminal:

```sh
focus test --state-file config/state.json
focus practica --state-file config/state.json
focus classe --state-file config/state.json
```

`focus-daemon` consulta el fitxer cada 0,5 segons i executa un tick cada 3 segons. Es poden canviar amb `--poll-interval` i `--tick-interval`. `Ctrl+C` o `SIGTERM` aturen el bucle després del hook en curs. La CLI escriu l'estat desitjat de manera atòmica; el daemon conserva l'estat lògic actual si el fitxer és invàlid durant l'execució.

Una fallada de transició inicia un intent de restauració de l'estat anterior. Si no es pot confirmar, el daemon entra en `ERROR`, continua viu i no fa ticks ni transicions. Aquesta versió no té una ordre de recuperació explícita des d'`ERROR`: cal corregir la causa i reiniciar el procés. Tampoc implementa restriccions reals, reconciliació després d'un reinici, servei systemd, journald ni integració central.
