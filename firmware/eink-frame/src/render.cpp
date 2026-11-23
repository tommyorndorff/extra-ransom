// Screen layout for the 800x480 panel. Header: weather icon, high/low, conditions | date, place.
// Body: poem (title, lines, author) or a message, auto-sized to the largest font that fits.
// Footer: last update time and battery.
#include "render.h"
#include "config.h"
#include <GxEPD2_BW.h>
#include <U8g2_for_Adafruit_GFX.h>
#include <vector>

static GxEPD2_BW<GxEPD2_750_T7, GxEPD2_750_T7::HEIGHT> display(
    GxEPD2_750_T7(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RST, PIN_EPD_BUSY));
static U8G2_FOR_ADAFRUIT_GFX u8;

static const int W = 800, H = 480;
static const int MARGIN = 24;
static const int BODY_TOP = 84, BODY_BOTTOM = 446, BODY_W = 720;
static const uint16_t BLACK = GxEPD_BLACK, WHITE = GxEPD_WHITE;

static void begin() {
  static bool ready = false;
  if (!ready) {
    display.init(0, true, 2, false);   // short reset pulse suits the Waveshare/DESPI adapters
    u8.begin(display);
    u8.setFontMode(1);
    u8.setForegroundColor(BLACK);
    u8.setBackgroundColor(WHITE);
    ready = true;
  }
  display.setRotation(0);
  display.setFullWindow();
  display.fillScreen(WHITE);
}

void displayOff() { display.hibernate(); }

// ---- text helpers ---------------------------------------------------------------

static int textW(const String &s) { return u8.getUTF8Width(s.c_str()); }
static int lineH() { return u8.getFontAscent() - u8.getFontDescent() + 6; }
static void drawAt(int x, int y, const String &s) { u8.drawUTF8(x, y, s.c_str()); }
static void drawRight(int xr, int y, const String &s) { drawAt(xr - textW(s), y, s); }
static void drawCenter(int y, const String &s) { drawAt((W - textW(s)) / 2, y, s); }

struct Wrapped { String text; int indent; bool gap; };

// Greedy word wrap. Leading spaces become an indent; continuation lines hang by `hang` px.
static std::vector<Wrapped> wrap(const std::vector<String> &src, int maxW, int hang) {
  std::vector<Wrapped> out;
  int space = textW(" ");
  for (const String &raw : src) {
    int lead = 0;
    while (lead < (int)raw.length() && raw[lead] == ' ') lead++;
    String s = raw.substring(lead);
    s.trim();
    if (!s.length()) { out.push_back({"", 0, true}); continue; }
    int indent = lead * space;
    String cur;
    int start = 0;
    while (start <= (int)s.length()) {
      int sp = s.indexOf(' ', start);
      if (sp < 0) sp = s.length();
      String word = s.substring(start, sp);
      start = sp + 1;
      if (!word.length()) continue;
      String cand = cur.length() ? cur + " " + word : word;
      if (cur.length() && indent + textW(cand) > maxW) {
        out.push_back({cur, indent, false});
        indent = lead * space + hang;
        cur = word;
      } else {
        cur = cand;
      }
    }
    if (cur.length()) out.push_back({cur, indent, false});
  }
  return out;
}

static int blockHeight(const std::vector<Wrapped> &lines) {
  int h = 0, lh = lineH();
  for (auto &l : lines) h += l.gap ? lh / 2 : lh;
  return h;
}

static std::vector<String> splitLines(const char *s) {
  std::vector<String> v;
  String all(s ? s : "");
  int start = 0;
  while (true) {
    int nl = all.indexOf('\n', start);
    if (nl < 0) { v.push_back(all.substring(start)); break; }
    v.push_back(all.substring(start, nl));
    start = nl + 1;
  }
  return v;
}

// ---- icons (48 px box, filled shapes read best on e-paper) ------------------------

static void thickLine(int x0, int y0, int x1, int y1, int t) {
  for (int d = -t / 2; d <= t / 2; d++) {
    display.drawLine(x0 + d, y0, x1 + d, y1, BLACK);
    display.drawLine(x0, y0 + d, x1, y1 + d, BLACK);
  }
}

static void sun(int cx, int cy, int r) {
  display.fillCircle(cx, cy, r, BLACK);
  for (int i = 0; i < 8; i++) {
    float a = i * PI / 4;
    thickLine(cx + cos(a) * (r + 4), cy + sin(a) * (r + 4), cx + cos(a) * (r + 9), cy + sin(a) * (r + 9), 3);
  }
}

static void cloud(int x, int y, int w, int h, uint16_t c) {
  display.fillCircle(x + w * 0.30, y + h * 0.62, h * 0.30, c);
  display.fillCircle(x + w * 0.54, y + h * 0.42, h * 0.40, c);
  display.fillCircle(x + w * 0.76, y + h * 0.62, h * 0.28, c);
  display.fillRoundRect(x + w * 0.12, y + h * 0.55, w * 0.80, h * 0.37, h * 0.18, c);
}

static void drawIcon(const char *name, int x, int y) {
  String n(name ? name : "");
  if (n == "clear") { sun(x + 24, y + 24, 11); return; }
  if (n == "partly") {
    sun(x + 31, y + 16, 8);
    cloud(x - 2, y + 14, 44, 34, WHITE);          // white halo separates cloud from sun
    cloud(x + 1, y + 17, 38, 28, BLACK);
    return;
  }
  if (n == "fog") {
    for (int i = 0; i < 4; i++) display.fillRoundRect(x + 4 + (i % 2) * 6, y + 10 + i * 9, 34, 4, 2, BLACK);
    return;
  }
  cloud(x + 2, y + 2, 44, 30, BLACK);
  int top = y + 34;
  if (n == "rain") for (int i = 0; i < 3; i++) thickLine(x + 14 + i * 10, top, x + 10 + i * 10, top + 11, 3);
  else if (n == "drizzle") for (int i = 0; i < 3; i++) { display.fillCircle(x + 13 + i * 11, top + 3, 2, BLACK); display.fillCircle(x + 18 + i * 11, top + 10, 2, BLACK); }
  else if (n == "snow") for (int i = 0; i < 3; i++) {
    int cx = x + 13 + i * 11, cy = top + 6;
    display.drawLine(cx - 4, cy, cx + 4, cy, BLACK); display.drawLine(cx, cy - 4, cx, cy + 4, BLACK);
    display.drawLine(cx - 3, cy - 3, cx + 3, cy + 3, BLACK); display.drawLine(cx - 3, cy + 3, cx + 3, cy - 3, BLACK);
  }
  else if (n == "storm") {
    display.fillTriangle(x + 26, top - 4, x + 16, top + 8, x + 24, top + 8, BLACK);
    display.fillTriangle(x + 24, top + 6, x + 30, top + 6, x + 20, top + 14, BLACK);
  }
}

static void battery(int xr, int y, int mv) {
  if (mv <= 0) return;
  int w = 24, h = 11, x = xr - w - 3;
  display.drawRect(x, y, w, h, BLACK);
  display.fillRect(x + w, y + 3, 3, h - 6, BLACK);
  float f = constrain((mv - 3300) / 850.0f, 0.0f, 1.0f);
  display.fillRect(x + 2, y + 2, (int)((w - 4) * f + 0.5f), h - 4, BLACK);
  if (mv < BATTERY_LOW_MV) {
    u8.setFont(u8g2_font_helvR08_tf);
    drawRight(x - 8, y + 9, "Please charge me");
  }
}

// ---- screens ------------------------------------------------------------------------

static void header(JsonObjectConst f) {
  JsonObjectConst wx = f["weather"];
  if (!wx.isNull()) {
    drawIcon(wx["icon"] | "", MARGIN, 8);
    int x = MARGIN + 60;
    u8.setFont(u8g2_font_helvB24_tf);
    String temps = String((int)(wx["hi"] | 0)) + "\xC2\xB0 / " + String((int)(wx["lo"] | 0)) + "\xC2\xB0";
    drawAt(x, 46, temps);
    x += textW(temps) + 16;
    u8.setFont(u8g2_font_helvR14_tf);
    String cond;
    if (String(wx["label"] | "") == "Tomorrow") cond = "Tomorrow: ";
    cond += String(wx["text"] | "");
    if (!wx["pop"].isNull() && (int)wx["pop"] >= 20) cond += String(" \xC2\xB7 ") + String((int)wx["pop"]) + "% rain";
    drawAt(x, 45, cond);
  } else {
    u8.setFont(u8g2_font_helvR14_tf);
    drawAt(MARGIN, 40, "Weather unavailable");
  }
  u8.setFont(u8g2_font_helvR14_tf);
  drawRight(W - MARGIN, 30, f["date"] | "");
  u8.setFont(u8g2_font_helvR12_tf);
  drawRight(W - MARGIN, 53, f["place"] | "");
  display.fillRect(MARGIN, 66, W - 2 * MARGIN, 2, BLACK);
}

struct PoemFonts { const uint8_t *body, *title, *author; };
static const PoemFonts POEM_FONTS[] = {
  {u8g2_font_ncenR24_tf, u8g2_font_ncenB18_tf, u8g2_font_ncenR18_tf},
  {u8g2_font_ncenR18_tf, u8g2_font_ncenB14_tf, u8g2_font_ncenR14_tf},
  {u8g2_font_ncenR14_tf, u8g2_font_ncenB12_tf, u8g2_font_ncenR12_tf},
  {u8g2_font_ncenR12_tf, u8g2_font_ncenB10_tf, u8g2_font_ncenR10_tf},
  {u8g2_font_ncenR10_tf, u8g2_font_ncenB10_tf, u8g2_font_ncenR08_tf},
};

static void poem(JsonObjectConst b) {
  std::vector<String> src;
  for (JsonVariantConst l : b["lines"].as<JsonArrayConst>()) src.push_back(l.as<const char *>() ? l.as<const char *>() : "");
  String title = b["title"] | "", author = b["author"] | "";
  const int avail = BODY_BOTTOM - BODY_TOP;
  for (size_t i = 0; i < sizeof(POEM_FONTS) / sizeof(POEM_FONTS[0]); i++) {
    const PoemFonts &pf = POEM_FONTS[i];
    bool last = i == sizeof(POEM_FONTS) / sizeof(POEM_FONTS[0]) - 1;
    u8.setFont(pf.title);
    int th = lineH() + 10;
    u8.setFont(pf.author);
    int ah = lineH() + 8;
    u8.setFont(pf.body);
    auto lines = wrap(src, BODY_W, 28);
    int bh = blockHeight(lines);
    if (th + bh + ah > avail && !last) continue;
    // Column is centred on the widest line so short poems sit in the middle of the screen.
    int colW = 0;
    for (auto &l : lines) colW = max(colW, l.indent + textW(l.text));
    int x0 = (W - colW) / 2, y = BODY_TOP + max(0, (avail - th - bh - ah) / 2);
    u8.setFont(pf.title);
    y += u8.getFontAscent();
    drawCenter(y, title);
    y += th - u8.getFontAscent();
    u8.setFont(pf.body);
    int lh = lineH();
    for (auto &l : lines) {
      if (l.gap) { y += lh / 2; continue; }
      drawAt(x0 + l.indent, y + u8.getFontAscent(), l.text);
      y += lh;
    }
    u8.setFont(pf.author);
    if (author.length()) drawRight(x0 + colW, y + 8 + u8.getFontAscent(), "- " + author);
    return;
  }
}

static const uint8_t *MESSAGE_FONTS[] = {
  u8g2_font_fur35_tf, u8g2_font_fur30_tf, u8g2_font_fur25_tf, u8g2_font_fur20_tf,
  u8g2_font_ncenR18_tf, u8g2_font_ncenR14_tf, u8g2_font_ncenR12_tf,
};

static void message(JsonObjectConst b) {
  auto src = splitLines(b["text"] | "");
  String from = b["from"] | "";
  const int avail = BODY_BOTTOM - BODY_TOP;
  const size_t n = sizeof(MESSAGE_FONTS) / sizeof(MESSAGE_FONTS[0]);
  for (size_t i = 0; i < n; i++) {
    u8.setFont(MESSAGE_FONTS[i]);
    auto lines = wrap(src, BODY_W - 40, 0);
    int bh = blockHeight(lines), fh = from.length() ? 40 : 0;
    if (bh + fh > avail && i + 1 < n) continue;
    int y = BODY_TOP + max(0, (avail - bh - fh) / 2), lh = lineH();
    for (auto &l : lines) {
      if (l.gap) { y += lh / 2; continue; }
      drawCenter(y + u8.getFontAscent(), l.text);
      y += lh;
    }
    if (from.length()) {
      u8.setFont(u8g2_font_ncenR18_tf);
      drawCenter(y + 14 + u8.getFontAscent(), "- " + from);
    }
    return;
  }
}

void renderFrame(JsonObjectConst f, int batteryMv) {
  begin();
  header(f);
  JsonObjectConst b = f["body"];
  if (String(b["kind"] | "") == "message") message(b); else poem(b);
  u8.setFont(u8g2_font_helvR08_tf);
  drawAt(MARGIN, H - 10, String("Updated ") + (f["updated"] | ""));
  battery(W - MARGIN, H - 20, batteryMv);
  display.display(false);
}

void renderNotice(const char *title, const char *const *lines, size_t n, const char *footer) {
  begin();
  u8.setFont(u8g2_font_ncenB24_tf);
  int y = 130;
  drawCenter(y, title);
  y += 60;
  u8.setFont(u8g2_font_helvR18_tf);
  for (size_t i = 0; i < n; i++) { drawCenter(y, lines[i]); y += 40; }
  if (footer) {
    u8.setFont(u8g2_font_helvR10_tf);
    drawCenter(H - 30, footer);
  }
  display.display(false);
}
