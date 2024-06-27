#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>
#include <WiFiClientSecure.h>
#include <esp32-hal-ledc.h> //for servo
#include <SPIFFS.h>
#include <SPI.h>
#include <TFT_eSPI.h> // Hardware-specific library

TFT_eSPI tft = TFT_eSPI(); // Invoke custom library

#define LIGHT_SENSE_PIN 34
#define LED_RED 4
#define LED_GREEN 17
#define LED_BLUE 16
#define SERVO_PIN 21
#define BACKLIGHT_PIN 27
#define MID_POS 95 // The middle position for the servo that has the heart pointing down

#include <PNGdec.h>
#include <AnimatedGIF.h>
AnimatedGIF gif;
PNG png;
#define MAX_IMAGE_WIDTH 320 // Adjust for your images

int16_t xpos = 0;
int16_t ypos = 0;

#include <DNSServer.h>
#include <AsyncTCP.h>
#include "ESPAsyncWebServer.h"

DNSServer dnsServer;
AsyncWebServer server(80);

String ssid;
String password;

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html><head>
  <title>Configuration du wifi</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  </head><body>
  <h3>Configuration</h3>
  <br><br>
  <form action="/get">
    <br>
    Nom du wifi: <input type="text" name="ssid">
    <br>
    <br>
    Mot de passe: <input type="text" name="password">
    <br>
    <input type="submit" value="Submit">
  </form>
</body></html>)rawliteral";

class CaptiveRequestHandler : public AsyncWebHandler {
public:
  CaptiveRequestHandler() {}
  virtual ~CaptiveRequestHandler() {}

  bool canHandle(AsyncWebServerRequest *request) {
    return true;
  }

  void handleRequest(AsyncWebServerRequest *request) {
    request->send_P(200, "text/html", index_html);
  }
};

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), password.c_str());

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 30000) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to WiFi.");
  }
}

void setupServer() {
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send_P(200, "text/html", index_html);
    Serial.println("Client Connected");
  });

  server.on("/get", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam("ssid")) {
      ssid = request->getParam("ssid")->value();
      Serial.println("SSID: " + ssid);
    }

    if (request->hasParam("password")) {
      password = request->getParam("password")->value();
      Serial.println("Password: " + password);
    }

    request->send(200, "text/html", "<center>C'est tout bon !<br><br>Tu peux te reconnecter à ton wifi 'normal'</center>");

    xTaskCreate([](void *parameter) {
      connectToWiFi();
      vTaskDelete(NULL);
    }, "WiFiTask", 4096, NULL, 1, NULL);
  });
}


const char *render_site = "https://love-box-noa.onrender.com//longPoll";

enum displayState {
  WAITING_FOR_IMAGE,
  WAITING_TO_DISPLAY_GIF,
  WAITING_TO_DISPLAY_PNG,
  DISPLAYING_GIF,
  DISPLAYING_PNG
};

displayState currState = WAITING_FOR_IMAGE;

// holds the current upload
File fsUploadFile;
File gifFile; // Global File object for the GIF file

void setClock() {
  configTime(0, 0, "pool.ntp.org");

  Serial.print(F("Waiting for NTP time sync: "));
  time_t nowSecs = time(nullptr);
  while (nowSecs < 8 * 3600 * 2) {
    delay(500);
    Serial.print(F("."));
    yield();
    nowSecs = time(nullptr);
  }

  Serial.println();
  struct tm timeinfo;
  gmtime_r(&nowSecs, &timeinfo);
  Serial.print(F("Current time: "));
  Serial.print(asctime(&timeinfo));
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up AP Mode");
  WiFi.mode(WIFI_AP);
  WiFi.softAP("Projet Marmotte");
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
  Serial.println("Setting up Async WebServer");
  setupServer();
  Serial.println("Starting DNS Server");
  dnsServer.start(53, "*", WiFi.softAPIP());
  server.addHandler(new CaptiveRequestHandler()).setFilter(ON_AP_FILTER); // only when requested from AP
  server.begin();
  Serial.println("All Done!");

  Serial.println("Starting");
  if (!SPIFFS.begin(true)) {
    Serial.println("An Error has occurred while mounting SPIFFS");
    return;
  }
  SPIFFS.format();

  Serial.printf("Connecting to %s\n", ssid.c_str());
  if (String(WiFi.SSID()) != String(ssid)) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
  }

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  // Initialise the TFT
  tft.begin();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLACK);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_BLUE, HIGH);
  gif.begin(BIG_ENDIAN_PIXELS);
  setClock();
  pinMode(BACKLIGHT_PIN, OUTPUT);
  digitalWrite(BACKLIGHT_PIN, HIGH);
  ledcSetup(0, 50, 16);
  ledcAttachPin(SERVO_PIN, 0);
  ledcWrite(0, pulseWidth(MID_POS));
}

void loop() {
  dnsServer.processNextRequest();

  switch (currState) {
    case WAITING_FOR_IMAGE:
      pollForImage();
      digitalWrite(BACKLIGHT_PIN, LOW);
      break;
    case WAITING_TO_DISPLAY_GIF:
      if (analogRead(LIGHT_SENSE_PIN) < 5) {
        digitalWrite(BACKLIGHT_PIN, HIGH);
        showGif(true);
        currState = DISPLAYING_GIF;
      } else {
        servoWiggle();
      }
      break;
    case WAITING_TO_DISPLAY_PNG:
      if (analogRead(LIGHT_SENSE_PIN) < 5) {
        digitalWrite(BACKLIGHT_PIN, HIGH);
        showImage();
        currState = DISPLAYING_PNG;
      } else {
        servoWiggle();
      }
      break;
    case DISPLAYING_GIF:
      showGif(false);
      if (analogRead(LIGHT_SENSE_PIN) > 5) {
        currState = WAITING_FOR_IMAGE;
        tft.fillScreen(TFT_BLACK);
        ledcWrite(0, pulseWidth(MID_POS));
      }
      break;
    case DISPLAYING_PNG:
      if (analogRead(LIGHT_SENSE_PIN) > 5) {
        currState = WAITING_FOR_IMAGE;
        tft.fillScreen(TFT_BLACK);
        ledcWrite(0, pulseWidth(MID_POS));
      }
      break;
  }
}

void pollForImage() {
  WiFiClientSecure *client = new WiFiClientSecure;
  if (client) {
    client->setInsecure();

    HTTPClient http;
    http.begin(*client, render_site);

    const char *headerKeys[] = {"imgname"};
    const size_t headerKeysCount = sizeof(headerKeys) / sizeof(headerKeys[0]);
    http.collectHeaders(headerKeys, headerKeysCount);
    int httpCode = http.GET();

    int numHeaders = http.headers();
    String fileName = http.header("imgname");
    fileName.toLowerCase();

    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        Serial.print("Got image: ");
        Serial.println(fileName);
        SPIFFS.remove("/image.gif");
        SPIFFS.remove("/image.png");
        if (fileName.endsWith(".gif")) {
          fsUploadFile = SPIFFS.open("/image.gif", "w");
        } else if (fileName.endsWith(".png")) {
          fsUploadFile = SPIFFS.open("/image.png", "w");
        } else {
          Serial.print("unknown file: ");
          Serial.println(fileName);
          http.end();
          return;
        }

        int len = http.getSize();
        uint8_t buff[2048] = {0};
        WiFiClient *stream = http.getStreamPtr();

        while (http.connected() && (len > 0 || len == -1)) {
          size_t size = stream->available();

          if (size) {
            int c = stream->readBytes(buff, ((size > sizeof(buff)) ? sizeof(buff) : size));
            fsUploadFile.write(buff, c);
            if (len > 0) {
              len -= c;
            }
          }
          delay(1);
        }

        Serial.println();
        Serial.print("[HTTP] connection closed or file end.\n");
        fsUploadFile.close();
        if (fileName.endsWith(".gif")) {
          currState = WAITING_TO_DISPLAY_GIF;
        } else if (fileName.endsWith(".png")) {
          currState = WAITING_TO_DISPLAY_PNG;
        }
      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
    delete client;
  } else {
    Serial.println("Unable to create client");
  }
}

void showGif(bool clearScreen) {
  if (clearScreen) {
    tft.fillScreen(TFT_BLACK);
  }
  Serial.println("Displaying GIF");
  if (gif.open("/image.gif", fileOpen, fileClose, fileRead, fileSeek, GIFDraw)) {
    tft.startWrite();
    int frameRes;
    do {
      frameRes = gif.playFrame(true, NULL);
    } while (frameRes);
    gif.close();
    tft.endWrite();
  } else {
    Serial.println("/image.gif did not work");
  }
}

void showImage() {
  tft.fillScreen(TFT_BLACK);
  Serial.println("Loading image");
  File file = SPIFFS.open("/image.png", "r");
  String strname = file.name();
  strname = "/" + strname;
  Serial.println(file.name());

  if (!file.isDirectory() && strname.endsWith(".png")) {
    int16_t rc = png.open(strname.c_str(), pngOpen, pngClose, pngRead, pngSeek, pngDraw);
    if (rc == PNG_SUCCESS) {
      tft.startWrite();
      Serial.printf("image specs: (%d x %d), %d bpp, pixel type: %d\n", png.getWidth(), png.getHeight(), png.getBpp(), png.getPixelType());

      xpos = 320 / 2 - png.getWidth() / 2;
      ypos = 480 / 2 - png.getHeight() / 2;
      uint32_t dt = millis();
      if (png.getWidth() > MAX_IMAGE_WIDTH) {
        Serial.println("Image too wide for allocated line buffer size!");
      } else {
        rc = png.decode(NULL, 0);
        png.close();
      }
      tft.endWrite();
      Serial.print(millis() - dt);
      Serial.println("ms");
    } else {
      Serial.println(rc);
      Serial.println("Failed to load image");
    }
  }
}

void servoWiggle() {
  ledcWrite(0, pulseWidth(0));
  delay(1000);

  ledcWrite(0, pulseWidth(180));
  delay(1000);

  ledcWrite(0, pulseWidth(MID_POS));
  delay(1000);
}

int pulseWidth(int angle) {
  int pulse_wide = map(angle, 0, 180, 1638, 8191);
  return pulse_wide;
}

void pngDraw(PNGDRAW *pDraw) {
  uint16_t lineBuffer[MAX_IMAGE_WIDTH];
  png.getLineAsRGB565(pDraw, lineBuffer, PNG_RGB565_BIG_ENDIAN, 0xffffffff);
  tft.pushImage(xpos, ypos + pDraw->y, pDraw->iWidth, 1, lineBuffer);
}

void *fileOpen(const char *filename, int32_t *pFileSize) {
  gifFile = SPIFFS.open(filename, FILE_READ);
  *pFileSize = gifFile.size();
  if (!gifFile) {
    Serial.println("Failed to open GIF file from SPIFFS!");
  }
  return &gifFile;
}

void fileClose(void *pHandle) {
  gifFile.close();
}

int32_t fileRead(GIFFILE *pFile, uint8_t *pBuf, int32_t iLen) {
  int32_t iBytesRead;
  iBytesRead = iLen;
  if ((pFile->iSize - pFile->iPos) < iLen)
    iBytesRead = pFile->iSize - pFile->iPos;
  if (iBytesRead <= 0)
    return 0;

  gifFile.seek(pFile->iPos);
  int32_t bytesRead = gifFile.read(pBuf, iLen);
  pFile->iPos += iBytesRead;

  return bytesRead;
}

int32_t fileSeek(GIFFILE *pFile, int32_t iPosition) {
  if (iPosition < 0)
    iPosition = 0;
  else if (iPosition >= pFile->iSize)
    iPosition = pFile->iSize - 1;
  pFile->iPos = iPosition;
  gifFile.seek(pFile->iPos);
  return iPosition;
}
