#include <Adafruit_NeoPixel.h>

#define LED_PIN     6
#define BUTTON_PIN  2
#define BUZZER_PIN  3
#define LED_COUNT   24

Adafruit_NeoPixel ring(
  LED_COUNT,
  LED_PIN,
  NEO_GRB + NEO_KHZ800
);

// ==========================
// ゲーム設定
// ==========================

const int TARGET_LED = 0;

// 最初の速度
unsigned long interval = 80;

// 成功するたび15ms速くする
const int SPEED_UP = 15;

// 最速は20ms
const int MIN_INTERVAL = 20;

// 成功3回でレインボー、連続失敗3回でゲームオーバー
const int MAX_WINS = 3;
const int MAX_MISSES = 3;

int currentLed = 1;
int visibleLed = 1;

int misses = 0;
int wins = 0;

bool gameOver = false;
bool lastButtonState = HIGH;

unsigned long previousMillis = 0;


// ==========================
// 🎵 MIDIから変換した開始音
// ==========================

const int START_NOTE_COUNT = 7;

const int startMelody[] = {
  1245, // MIDI 87
  622,  // MIDI 75
  932,  // MIDI 82
  831,  // MIDI 80
  622,  // MIDI 75
  1245, // MIDI 87
  932   // MIDI 82
};

const int startDuration[] = {
  375,
  125,
  250,
  250,
  250,
  250,
  750
};


// ==========================
// 初期設定
// ==========================

void setup() {

  ring.begin();
  ring.setBrightness(60);
  ring.clear();
  ring.show();

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);

  // 🎵 起動時に開始メロディー
  playStartMelody();

  previousMillis = millis();
}


// ==========================
// メイン
// ==========================

void loop() {

  bool buttonState = digitalRead(BUTTON_PIN);

  // ボタンを押した瞬間
  if (lastButtonState == HIGH &&
      buttonState == LOW) {

    // ゲームオーバーなら再スタート
    if (gameOver) {

      resetGame();

    }

    // 当たり！
    else if (visibleLed == TARGET_LED) {

      win();

    }

    // ハズレ
    else {

      misses++;

      if (misses >= MAX_MISSES) {
        lose();
      }
      else {
        missEffect();
      }
    }

    delay(30);
  }

  lastButtonState = buttonState;


  // ゲームオーバーなら停止
  if (gameOver) {
    return;
  }


  // ==========================
  // LED回転
  // ==========================

  unsigned long now = millis();

  if (now - previousMillis >= interval) {

    previousMillis = now;

    ring.clear();

    // 当たりを緑
    ring.setPixelColor(
      TARGET_LED,
      ring.Color(0, 80, 0)
    );

    // 回転するLEDを赤
    ring.setPixelColor(
      currentLed,
      ring.Color(100, 0, 0)
    );

    ring.show();

    // 実際に表示されている位置
    visibleLed = currentLed;

    currentLed++;

    if (currentLed >= LED_COUNT) {
      currentLed = 0;
    }
  }
}


// ==========================
// 🎵 ゲーム開始メロディー
// ==========================

void playStartMelody() {

  for (int i = 0; i < START_NOTE_COUNT; i++) {

    tone(
      BUZZER_PIN,
      startMelody[i]
    );

    // 音の長さの90%を鳴らす
    delay(startDuration[i] * 9 / 10);

    noTone(BUZZER_PIN);

    // 残り10%を音と音の間隔にする
    delay(startDuration[i] / 10);
  }
}


// ==========================
// 🎯 成功
// ==========================

void win() {

  wins++;

  // 成功したら、それまでの失敗記録は捨てる
  misses = 0;

  // 成功音
  tone(BUZZER_PIN, 1000);
  delay(100);

  tone(BUZZER_PIN, 1500);
  delay(100);

  tone(BUZZER_PIN, 2000);
  delay(250);

  noTone(BUZZER_PIN);


  // 黄色で高速3周
  for (int round = 0; round < 3; round++) {

    for (int i = 0; i < LED_COUNT; i++) {

      ring.clear();

      ring.setPixelColor(
        i,
        ring.Color(100, 60, 0)
      );

      ring.show();

      delay(10);
    }
  }


  // 全部緑
  ring.clear();

  for (int i = 0; i < LED_COUNT; i++) {

    ring.setPixelColor(
      i,
      ring.Color(0, 100, 0)
    );
  }

  ring.show();

  delay(500);


  // 成功3回でレインボーフィナーレ
  if (wins >= MAX_WINS) {
    rainbowFinale();
    return;
  }


  // ==========================
  // 成功するたびに加速！
  // ==========================

  if (interval > MIN_INTERVAL) {

    interval -= SPEED_UP;

    if (interval < MIN_INTERVAL) {
      interval = MIN_INTERVAL;
    }
  }

  currentLed = 1;
  visibleLed = 1;

  ring.clear();
  ring.show();

  previousMillis = millis();
}


// ==========================
// ❌ ハズレ
// ==========================

void missEffect() {

  tone(BUZZER_PIN, 300);
  delay(100);

  noTone(BUZZER_PIN);

  ring.clear();

  for (int i = 0; i < LED_COUNT; i++) {

    ring.setPixelColor(
      i,
      ring.Color(80, 0, 0)
    );
  }

  ring.show();

  delay(150);

  ring.clear();
  ring.show();

  delay(100);

  previousMillis = millis();
}


// ==========================
// 💀 連続失敗3回
// ==========================

void lose() {

  gameOver = true;

  ring.clear();

  for (int i = 0; i < LED_COUNT; i++) {

    ring.setPixelColor(
      i,
      ring.Color(100, 0, 0)
    );
  }

  ring.show();


  // ゲームオーバー音
  tone(BUZZER_PIN, 500);
  delay(200);

  tone(BUZZER_PIN, 350);
  delay(200);

  tone(BUZZER_PIN, 200);
  delay(500);

  noTone(BUZZER_PIN);
}


// ==========================
// 🌈 成功3回：レインボー
// ==========================

uint32_t colorWheel(byte pos) {

  pos = 255 - pos;

  if (pos < 85) {
    return ring.Color(255 - pos * 3, 0, pos * 3);
  }

  if (pos < 170) {
    pos -= 85;
    return ring.Color(0, pos * 3, 255 - pos * 3);
  }

  pos -= 170;
  return ring.Color(pos * 3, 255 - pos * 3, 0);
}


void rainbowFinale() {

  gameOver = true;

  // レインボー成功音
  tone(BUZZER_PIN, 1200);
  delay(120);

  tone(BUZZER_PIN, 1600);
  delay(120);

  tone(BUZZER_PIN, 2000);
  delay(180);

  tone(BUZZER_PIN, 2400);
  delay(280);

  noTone(BUZZER_PIN);


  // レインボーがリングをくるくる回る（4周）
  const int spins = 4;

  for (int offset = 0; offset < LED_COUNT * spins; offset++) {

    for (int i = 0; i < LED_COUNT; i++) {

      byte pos = ((i + offset) * 256 / LED_COUNT) & 255;
      ring.setPixelColor(i, colorWheel(pos));
    }

    ring.show();
    delay(35);
  }


  // レインボーのまま止まる
  for (int i = 0; i < LED_COUNT; i++) {

    byte pos = (i * 256 / LED_COUNT) & 255;
    ring.setPixelColor(i, colorWheel(pos));
  }

  ring.show();
}


// ==========================
// 🔄 最初から
// ==========================

void resetGame() {

  misses = 0;
  wins = 0;

  gameOver = false;

  // 速度も最初に戻す
  interval = 80;

  currentLed = 1;
  visibleLed = 1;

  ring.clear();
  ring.show();


  // 🎵 MIDIから変換した開始メロディー
  playStartMelody();


  previousMillis = millis();
}
