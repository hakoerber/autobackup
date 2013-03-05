Dieses Programm dient der automatischen und regelmäßigen Sicherung lokaler Daten auf einem Wechseldatenträger.

Es sollte stündlich durch cron ausgeführt werden. Der Eintrag in der crontab könnte folgendermaßen lauten:

0 */1 * * * root <Pfad zum Skript> <Pfad zur config-Datei> &>><Logdatei>

Die erste Zahl (0-59) gibt dabei an, zu welcher Minute das Backup angelegt werden soll. Wenn es etwa zu jeder halben Stunde ausgeführt werden soll,
müsste "30" eingetragen werden.

Die hauptsächliche Konfiguration geschieht über die config-Datei, die dem Programm übergeben wird.
Die ..._MAX-Einträge sind dabei folgendermaßen zu verstehen:
Wenn der jeweilige Wert auf "0" steht, werden alle gefundenen Backups dieses Typs gelöscht.

Bei einer "1" wird immer ein Backup solange behalten, bis ein neues Backup des Typs angelegt wird.
Bsp: Es wurde ein stündliches Backup angelegt. Dieses wird solange behalten, bis eine Stunde vergangen ist.
Hinweis: Wenn das Skript ausschließlich stündlich ausgeführt wird, unterscheidet sich das Verhalten bei "0" und "1" nicht.

YEAR DAY_OF_YEAR -> MONTH
date --date="1.1.$YEAR + $DAY_OF_YEAR days" +%m

YEAR DAY_OF_YEAR -> DAY
date --date="1.1.$YEAR + $DAY_OF_YEAR days" +%d

Normaler Zeitpunkt des Backups:

Y:  ########### -   DAY_OF_YEAR -           HOUR_OF_DAY :   MINUTE_OF_HOUR
M:  ########### -   ########### -   DAY_OF_MONTH    HOUR_OF_DAY :   MINUTE_OF_HOUR
D:  ########### -   ########### ############    HOUR_OF_DAY :   MINUTE_OF_HOUR
H:  ########### -   ########### -   ############    ########### :   MINUTE_OF_HOUR
W:                  # WEEK #####    HOUR_OF_DAY :   MINUTE_OF_HOUR

#5------#4------#3------#2------#1----jetzt

Zeitpunkt #1:

Es wird ein neues Backup angelegt, wenn kein Backup vorhanden ist, das neuer als #1 ist.

bei "0" werden alle Backups gelöscht
bei "1" werden alle Backups, die nicht von diesem jahr/monat... sind
y: älter als 1.1. diesen/letzten/vorletzten... jahres um 0:00
jahr: thisyear-maxyear+1
m: älter als 1. diesen/letzten/vorletzten... monats um 0:00
monat: thismonth-maxmonth+1
w: älter als diesen/letzten/vorletzten... montag um 0:00
woche: thismonday-7*maxweek+7
d: älter als heute/gestern/vorgestern... um 0:00
tag: thisday-maxday+1
h: älter als diese/letzte/vorletzte... stunde

es wird immer nur dann ein backup gelöscht, wenn noch mindestens ein weiteres des gleichen typs vorhanden ist

bei "2" werden alle Backups, die älter als #2 sind, gelöscht usw

Die Einstellung 0 im expirationDateDict macht nur Sinn, wenn keine weiteren Backups des Typs angelegt werden, zB um alte Backups des Typs
zu löschen. Andernfalls kann es passieren, dass ein Backup angelegt und sofort wieder gelöscht wird.

n monate in der vergangenheit:


nmonat: (monat - n) % 12
njahr : jahr - (n - monat) / 12 + 1

backupTypeDict:
0 = kein Backup anlegen
1 = Vollbackup anlegen
2 = differentielles Backup anlegen
3 = inkrementelles Backup anlegen

Größere Intervalle haben dabei Vorrang von kleineren Intervallen.
Wenn zB das Monatsbackup inkrementell sein sollte, aber das Jahresbackup als Vollbackup angelegt werden soll, so wird am 1.1. des Jahres
trotzdem ein Vollbackup angelegt.



evtl noch zu implementierende funktionen:

ping zu remote host bevor verbindung hergestellt wird

paketliste mitsichern

warnung bei sich füllender partition (du usw)

logdatei ans backup anhängen

LVM-support

verbosity-option für log/konsole conf

timeout-parameter für rsync in conf




































