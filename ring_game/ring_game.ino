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

unsigned long interval = 80;

const int SPEED_UP = 15;
const int MIN_INTERVAL = 20;

// チャタリング防止（押し・離しの両方）
const unsigned long DEBOUNCE_MS = 50;

int currentLed = 1;
int visibleLed = 1;

// 何回挑戦したか
int roundCount = 0;

// 何回成功したか
int successCount = 0;

bool gameOver = false;
bool lastButtonState = HIGH;

unsigned long previousMillis = 0;


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

  previousMillis = millis();
}


// ==========================
// メイン
// ==========================

void loop() {

  bool buttonState = digitalRead(BUTTON_PIN);


  // ==========================
  // ボタンを押した瞬間だけ
  // ==========================

  if (lastButtonState == HIGH &&
      buttonState == LOW) {

    // ゲーム終了後なら再スタート
    if (gameOver) {

      resetGame();
      waitForButtonRelease();
      lastButtonState = HIGH;
      return;
    }


    // ==========================
    // 今回の結果を判定
    // ==========================

    bool success =
      (visibleLed == TARGET_LED);


    // 挑戦回数を必ず1増やす
    roundCount++;


    // ==========================
    // 成功
    // ==========================

    if (success) {

      successCount++;

      successEffect();


      // まだ3回目ではない場合だけ加速
      if (roundCount < 3) {

        if (interval > MIN_INTERVAL) {

          interval -= SPEED_UP;

          if (interval < MIN_INTERVAL) {
            interval = MIN_INTERVAL;
          }
        }
      }
    }


    // ==========================
    // 失敗
    // ==========================

    else {

      failEffect();
    }


    // ==========================
    // ★ ここが重要 ★
    //
    // 3回目が終わるまでは
    // 絶対ゲーム終了しない
    // ==========================

    if (roundCount < 3) {

      prepareNextRound();

    }

    // ==========================
    // 3回目だけ最終判定
    // ==========================

    else {

      if (successCount == 3) {

        rainbowClear();

      } else {

        gameOverRed();

      }
    }


    // 離されるまで待たないと、成功エフェクト直後の
    // チャタリングが「次のラウンドの失敗」として判定される
    waitForButtonRelease();
    lastButtonState = HIGH;
    return;
  }


  lastButtonState = buttonState;


  // ==========================
  // 終了中
  // ==========================

  if (gameOver) {
    return;
  }


  // ==========================
  // LEDを回転
  // ==========================

  unsigned long now = millis();

  if (now - previousMillis >= interval) {

    previousMillis = now;

    ring.clear();


    // 緑の当たり位置
    ring.setPixelColor(
      TARGET_LED,
      ring.Color(0, 80, 0)
    );


    // 赤い移動LED
    ring.setPixelColor(
      currentLed,
      ring.Color(100, 0, 0)
    );


    ring.show();


    visibleLed = currentLed;


    currentLed++;

    if (currentLed >= LED_COUNT) {
      currentLed = 0;
    }
  }
}


// ==========================
// ボタンが離されるまで待つ
// ==========================
//
// 以前は判定後に lastButtonState を
// 「押した瞬間の古い値」のまま更新していた。
// そのせいで、離したときのチャタリングが
// 次の挑戦（失敗）としてカウントされていた。
// 2回成功した直後に3回目が自動失敗し、
// ゲームオーバーになっていたのがこのバグ。

void waitForButtonRelease() {

  delay(DEBOUNCE_MS);

  while (digitalRead(BUTTON_PIN) == LOW) {
    delay(5);
  }

  delay(DEBOUNCE_MS);
}


// ==========================
// 成功エフェクト
// ==========================

void successEffect() {

  tone(BUZZER_PIN, 1000);
  delay(80);

  tone(BUZZER_PIN, 1500);
  delay(80);

  tone(BUZZER_PIN, 2000);
  delay(120);

  noTone(BUZZER_PIN);


  // 全部緑
  ring.clear();

  for (int i = 0; i < LED_COUNT; i++) {

    ring.setPixelColor(
      i,
      ring.Color(0, 100, 0)
    );
  }

  ring.show();

  delay(250);
}


// ==========================
// 失敗エフェクト
// ==========================

void failEffect() {

  tone(BUZZER_PIN, 300);
  delay(120);

  noTone(BUZZER_PIN);


  // 全部赤
  ring.clear();

  for (int i = 0; i < LED_COUNT; i++) {

    ring.setPixelColor(
      i,
      ring.Color(100, 0, 0)
    );
  }

  ring.show();

  delay(250);
}


// ==========================
// 次のラウンド
// ==========================

void prepareNextRound() {

  currentLed = 1;
  visibleLed = 1;

  ring.clear();
  ring.show();

  delay(200);

  previousMillis = millis();
}


// ==========================
// 🌈 3回全部成功
// ==========================

void rainbowClear() {

  gameOver = true;


  // パーフェクト音
  tone(BUZZER_PIN, 1200);
  delay(100);

  tone(BUZZER_PIN, 1600);
  delay(100);

  tone(BUZZER_PIN, 2000);
  delay(100);

  tone(BUZZER_PIN, 2400);
  delay(300);

  noTone(BUZZER_PIN);


  // ==========================
  // 🌈 レインボーを回転
  // ==========================

  for (int rotation = 0;
       rotation < LED_COUNT * 5;
       rotation++) {

    for (int i = 0;
         i < LED_COUNT;
         i++) {

      uint16_t hue =
        ((long)(i + rotation) * 65536L)
        / LED_COUNT;

      ring.setPixelColor(
        i,
        ring.gamma32(
          ring.ColorHSV(hue)
        )
      );
    }

    ring.show();

    delay(20);
  }


  // ==========================
  // 🌈 最後はレインボー固定
  // ==========================

  for (int i = 0;
       i < LED_COUNT;
       i++) {

    uint16_t hue =
      ((long)i * 65536L)
      / LED_COUNT;

    ring.setPixelColor(
      i,
      ring.gamma32(
        ring.ColorHSV(hue)
      )
    );
  }

  ring.show();
}


// ==========================
// 🔴 3回終了・失敗あり
// ==========================

void gameOverRed() {

  gameOver = true;

  ring.clear();

  for (int i = 0;
       i < LED_COUNT;
       i++) {

    ring.setPixelColor(
      i,
      ring.Color(120, 0, 0)
    );
  }

  ring.show();


  tone(BUZZER_PIN, 500);
  delay(200);

  tone(BUZZER_PIN, 350);
  delay(200);

  tone(BUZZER_PIN, 200);
  delay(400);

  noTone(BUZZER_PIN);
}


// ==========================
// 🔄 最初から
// ==========================

void resetGame() {

  roundCount = 0;
  successCount = 0;

  gameOver = false;

  interval = 80;

  currentLed = 1;
  visibleLed = 1;

  ring.clear();
  ring.show();

  previousMillis = millis();
}
