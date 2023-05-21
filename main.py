def AbstandInfoSenden():
    serial.write_string("<")
    serial.write_string("Start")
    serial.write_string("Sensorabstand ")
    serial.write_number(Abstand)
    serial.write_string("  Millimeter")
    serial.write_string(">")
def Initialisierung():
    global LS_Frei, LS_unterbrochen, Schritt, Abstand
    # Variable die Schaltzustand 
    # Lichtschranke NICHT unterbrochen bedeutet
    LS_Frei = 0
    # Variable die Schaltzustand 
    # Lichtschranke IST unterbrochen bedeutet
    LS_unterbrochen = 1
    # Variable die den Programmablauf steuert
    # Je nachdem ob die Variable den Wert 0, 1 oder 2 hat werden bestimmte Programmteile ausgeführt
    Schritt = 0
    # Pin "P0" ist die gelbe Leuchtdiode
    # Sie zeigt an das das Programm bereit ist für eine neue Geschwindigkeitsmessung
    # Wert 1 bedeutet die LED soll leuchten
    # (Wert 0 bedeutet LED aus)
    pins.digital_write_pin(DigitalPin.P0, 1)
    # Mit Pin "P8" wird die erste Lichtschranke ein/aus- geschaltet
    # Wert 1 bedeutet Lichtschranke ist eingeschaltet
    # Wert 0 bedeutet Lichtschranke ist ausgeschaltet
    pins.digital_write_pin(DigitalPin.P8, 1)
    # Mit Pin "P16" wird die zweite Lichtschranke ein/aus- geschaltet
    # Wert 1 bedeutet Lichtschranke ist eingeschaltet
    # Wert 0 bedeutet Lichtschranke ist ausgeschaltet
    pins.digital_write_pin(DigitalPin.P16, 0)
    # Variable die zur Berechnung der Geschwindigkeit benötigt wird
    # Geschwindigkeit: v
    # Abstand: S
    # Zeit. t
    # v = S / t
    # 
    Abstand = 10000
    DatenSendenEinstellen()
def BerechneGeschwindigkeit():
    global ZeitDifferenz, Geschw_mm_sec, Geschwindigkeit_km_h
    # Berechne die Differenz aus EndZeit Minus StartZeit
    # Diese Differenz ist die Zeit die das Auto gebraucht hat um durch die Lichtschranke 1 und die Lichtschranke 2 zu fahren.
    # Diese Zeit wird benötigt um die Geschwindigkeit zu berechnen
    ZeitDifferenz = EndZeit - StartZeit
    # erster Rechenschritt um die Geschwindigkeit in km/h zu berechnen.
    # Der Abstand ist in Millimetern angeben. 
    # Abstand / ZeitDifferenz = Geschwindigkeit in mm / millisekunde
    # Das entspricht auch m/sec
    Geschw_mm_sec = Abstand / ZeitDifferenz
    # Wenn eine Geschwindigkeit angegeben in m/sec mit 36 multipliziert bekommt man die Geschwindigkeit in Hektometer/h
    # diesen Wert muss man noch durch 10 teilen um die Einheit km/h zu bekommen
    Geschwindigkeit_km_h = Geschw_mm_sec * 36
    # Im vorigen Schritt wurde die Geschwindigkeit in Hektometer / h berechnen. 
    # Dieser Wert muss noch durch 10 geteilt werden um km/h zu bekommen
    Geschwindigkeit_km_h = Math.round(Geschwindigkeit_km_h) / 10
def PruefeLichtschranke2():
    global EndZeit, Schritt
    # Da das Schaltsignal auf dem gleichen Anschluss liegt wie Taster B kann auch die Abfrage Taster B gedrückt verwendet werden
    if input.button_is_pressed(Button.B):
        # speichere die "Uhrzeit" wenn die zweite Lichtschranke unterbrochen wurde in der Variablen "EndZeit"
        EndZeit = control.millis()
        # Schalte die Lichtschranke 2 aus
        pins.digital_write_pin(DigitalPin.P16, 0)
        Schritt = 2
def SendeMesswert():
    serial.write_string("<")
    serial.write_string("V=")
    serial.write_number(Geschwindigkeit_km_h)
    serial.write_string(" km/h")
    serial.write_string(">")
def DatenSendenEinstellen():
    serial.redirect(SerialPin.P14, SerialPin.P15, BaudRate.BAUD_RATE19200)
def MessungStarten():
    global StartZeit, Schritt
    # An "P5" ist der Schaltausgang der ersten Lichtschranke angeschlossen
    # Wenn die Lichtschranke unterbrochen wird werden die Befehle ausgeführt
    if pins.digital_read_pin(DigitalPin.P5) == LS_unterbrochen:
        # In der Variable StartZeit wird die "Uhrzeit" gespeichert. Es sind aber keine Stunden:Mnuten sondern es sind Millisekunden.
        StartZeit = control.millis()
        # schalte gelbe LED aus um anzuzeigen erste Lichtschranke wurde unterbrochen
        pins.digital_write_pin(DigitalPin.P0, 0)
        # Schalte die rote LED ein um anzuzeigen Messung läuft
        # warte auf Signal von Lichtschranke 2
        pins.digital_write_pin(DigitalPin.P1, 1)
        # Schalte Lichtschranke 1 aus
        pins.digital_write_pin(DigitalPin.P8, 0)
        # Schalte Lichtschranke 2 ein
        pins.digital_write_pin(DigitalPin.P16, 1)
        Schritt = 1
Geschwindigkeit_km_h = 0
Geschw_mm_sec = 0
StartZeit = 0
EndZeit = 0
ZeitDifferenz = 0
Schritt = 0
LS_unterbrochen = 0
LS_Frei = 0
Abstand = 0
Initialisierung()
AbstandInfoSenden()

def on_forever():
    global Schritt
    if Schritt == 0:
        MessungStarten()
    if Schritt == 1:
        PruefeLichtschranke2()
    if Schritt == 2:
        BerechneGeschwindigkeit()
        SendeMesswert()
        Schritt = 0
        basic.show_number(Geschwindigkeit_km_h)
        pins.digital_write_pin(DigitalPin.P1, 0)
        pins.digital_write_pin(DigitalPin.P0, 1)
        pins.digital_write_pin(DigitalPin.P8, 1)
        basic.pause(100)
basic.forever(on_forever)
