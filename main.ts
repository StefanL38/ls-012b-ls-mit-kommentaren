function AbstandInfoSenden () {
    serial.writeString("<")
    serial.writeString("Start")
    serial.writeString("Sensorabstand ")
    serial.writeNumber(Abstand)
    serial.writeString("  Millimeter")
    serial.writeString(">")
}
function Initialisierung () {
    // Variable die Schaltzustand 
    // Lichtschranke NICHT unterbrochen bedeutet
    LS_Frei = 0
    // Variable die Schaltzustand 
    // Lichtschranke IST unterbrochen bedeutet
    LS_unterbrochen = 1
    // Variable die den Programmablauf steuert
    // Je nachdem ob die Variable den Wert 0, 1 oder 2 hat werden bestimmte Programmteile ausgeführt
    Schritt = 0
    // Pin "P0" ist die gelbe Leuchtdiode
    // Sie zeigt an das das Programm bereit ist für eine neue Geschwindigkeitsmessung
    // Wert 1 bedeutet die LED soll leuchten
    // (Wert 0 bedeutet LED aus)
    pins.digitalWritePin(DigitalPin.P0, 1)
    // Mit Pin "P8" wird die erste Lichtschranke ein/aus- geschaltet
    // Wert 1 bedeutet Lichtschranke ist eingeschaltet
    // Wert 0 bedeutet Lichtschranke ist ausgeschaltet
    pins.digitalWritePin(DigitalPin.P8, 1)
    // Mit Pin "P16" wird die zweite Lichtschranke ein/aus- geschaltet
    // Wert 1 bedeutet Lichtschranke ist eingeschaltet
    // Wert 0 bedeutet Lichtschranke ist ausgeschaltet
    pins.digitalWritePin(DigitalPin.P16, 0)
    // Variable die zur Berechnung der Geschwindigkeit benötigt wird
    // Geschwindigkeit: v
    // Abstand: S
    // Zeit. t
    // v = S / t
    // 
    Abstand = 10000
    DatenSendenEinstellen()
}
function BerechneGeschwindigkeit () {
    // Berechne die Differenz aus EndZeit Minus StartZeit
    // Diese Differenz ist die Zeit die das Auto gebraucht hat um durch die Lichtschranke 1 und die Lichtschranke 2 zu fahren.
    // Diese Zeit wird benötigt um die Geschwindigkeit zu berechnen
    ZeitDifferenz = EndZeit - StartZeit
    // erster Rechenschritt um die Geschwindigkeit in km/h zu berechnen.
    // Der Abstand ist in Millimetern angeben. 
    // Abstand / ZeitDifferenz = Geschwindigkeit in mm / millisekunde
    // Das entspricht auch m/sec
    Geschw_mm_sec = Abstand / ZeitDifferenz
    // Wenn eine Geschwindigkeit angegeben in m/sec mit 36 multipliziert bekommt man die Geschwindigkeit in Hektometer/h
    // diesen Wert muss man noch durch 10 teilen um die Einheit km/h zu bekommen
    Geschwindigkeit_km_h = Geschw_mm_sec * 36
    // Im vorigen Schritt wurde die Geschwindigkeit in Hektometer / h berechnen. 
    // Dieser Wert muss noch durch 10 geteilt werden um km/h zu bekommen
    Geschwindigkeit_km_h = Math.round(Geschwindigkeit_km_h) / 10
}
function PruefeLichtschranke2 () {
    // Da das Schaltsignal auf dem gleichen Anschluss liegt wie Taster B kann auch die Abfrage Taster B gedrückt verwendet werden
    if (input.buttonIsPressed(Button.B)) {
        // speichere die "Uhrzeit" wenn die zweite Lichtschranke unterbrochen wurde in der Variablen "EndZeit"
        EndZeit = control.millis()
        // Schalte die Lichtschranke 2 aus
        pins.digitalWritePin(DigitalPin.P16, 0)
        Schritt = 2
    }
}
function SendeMesswert () {
    serial.writeString("<")
    serial.writeString("V=")
    serial.writeNumber(Geschwindigkeit_km_h)
    serial.writeString(" km/h")
    serial.writeString(">")
}
function DatenSendenEinstellen () {
    serial.redirect(
    SerialPin.P14,
    SerialPin.P15,
    BaudRate.BaudRate19200
    )
}
function MessungStarten () {
    // An "P5" ist der Schaltausgang der ersten Lichtschranke angeschlossen
    // Wenn die Lichtschranke unterbrochen wird werden die Befehle ausgeführt
    if (pins.digitalReadPin(DigitalPin.P5) == LS_unterbrochen) {
        // In der Variable StartZeit wird die "Uhrzeit" gespeichert. Es sind aber keine Stunden:Mnuten sondern es sind Millisekunden.
        StartZeit = control.millis()
        // schalte gelbe LED aus um anzuzeigen erste Lichtschranke wurde unterbrochen
        pins.digitalWritePin(DigitalPin.P0, 0)
        // Schalte die rote LED ein um anzuzeigen Messung läuft
        // warte auf Signal von Lichtschranke 2
        pins.digitalWritePin(DigitalPin.P1, 1)
        // Schalte Lichtschranke 1 aus
        pins.digitalWritePin(DigitalPin.P8, 0)
        // Schalte Lichtschranke 2 ein
        pins.digitalWritePin(DigitalPin.P16, 1)
        Schritt = 1
    }
}
let Geschwindigkeit_km_h = 0
let Geschw_mm_sec = 0
let StartZeit = 0
let EndZeit = 0
let ZeitDifferenz = 0
let Schritt = 0
let LS_unterbrochen = 0
let LS_Frei = 0
let Abstand = 0
Initialisierung()
AbstandInfoSenden()
basic.forever(function () {
    if (Schritt == 0) {
        MessungStarten()
    }
    if (Schritt == 1) {
        PruefeLichtschranke2()
    }
    if (Schritt == 2) {
        BerechneGeschwindigkeit()
        SendeMesswert()
        Schritt = 0
        basic.showNumber(Geschwindigkeit_km_h)
        pins.digitalWritePin(DigitalPin.P1, 0)
        pins.digitalWritePin(DigitalPin.P0, 1)
        pins.digitalWritePin(DigitalPin.P8, 1)
        basic.pause(100)
    }
})
