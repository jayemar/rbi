char inByte;
int rx[2];
int slow_cycle = 0;

// Out Pins
int outs[] = {-1,-1,2,3,4,5,6,7,8,9,10,11,12};

// Slow Blink Pins
int sbp[]  = {0, 0, 0,0,0,0,0,0,0,0, 0, 0, 0};
// Fast Blink Pins (blink twice as fast as Blink Pins)
int fbp[]  = {0, 0, 0,0,0,0,0,0,0,0, 0, 0, 0};

long counter = 0;
const long BLINK_COUNT = 100000;

void setup() {
    for (int p = 0; p < sizeof(outs); p++) {
        pinMode(outs[p], OUTPUT);
    }
    Serial.begin(57600);
}

int doHalfBlinks() {
    for (int i = 0; i < sizeof(outs); i++) {
        if (sbp[i] == 1) {
            int new_val = digitalRead(outs[i]) ^ 1;
            digitalWrite(outs[i], new_val);
        }
    }
    return 0;
}

int doBlinks() {
    // Toggle pins for any in the fbp list
    for (int i = 0; i < sizeof(outs); i++) {
        if (fbp[i] == 1) {
            int new_val = digitalRead(outs[i]) ^ 1;
            digitalWrite(outs[i], new_val);
        }
    }
    return 0;
}

void loop() {
    if (Serial.available() > 0) {
        inByte = Serial.read();

        Serial.print("inByte: ");
        Serial.print(inByte, DEC);
        Serial.println(" <-- inByte");
        if (inByte != '\n' && inByte != '\r') {
            rx[0] = rx[1];
            rx[1] = inByte;

        } else if (inByte != '\n') {
            Serial.print(inByte);
            if (rx[1] == 0) {
                // LED Off
                sbp[rx[0]] = 0;
                fbp[rx[0]] = 0;
                digitalWrite(rx[0], LOW);
            } else if (rx[1] == 1) {
                // LED Off
                sbp[rx[0]] = 0;
                fbp[rx[0]] = 0;
                digitalWrite(rx[0], HIGH);
            } else if (rx[1] == 2) {
                // Slow blinking
                sbp[rx[0]] = 1;
                fbp[rx[0]] = 0;
            } else if (rx[1] == 3) {
                // Fast blinking
                sbp[rx[0]] = 0;
                fbp[rx[0]] = 1;
            }
        }
    }

    counter++;
    if (counter == BLINK_COUNT) {
        doHalfBlinks();
        doBlinks();
        counter = 0;
    } else if (counter == BLINK_COUNT / 2) {
        doHalfBlinks();
    }

}
