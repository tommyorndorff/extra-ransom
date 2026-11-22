#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>

// Full refresh of the frame from the API payload (see workers/eink-frame).
void renderFrame(JsonObjectConst frame, int batteryMv);
// Centered title + lines, for setup / charge / not-registered screens.
void renderNotice(const char *title, const char *const *lines, size_t n, const char *footer);
// Put the panel into deep sleep (it keeps the image with no power).
void displayOff();
