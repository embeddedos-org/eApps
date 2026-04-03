/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2024 Meta Platforms, Inc. and affiliates.
 *
 * Android native activity entry point for eApps.
 */

#include <android/native_activity.h>
#include <android/looper.h>
#include <android/log.h>
#include <android_native_app_glue.h>
#include "lvgl.h"

#define ANDROID_DISP_HOR_RES 800
#define ANDROID_DISP_VER_RES 480

#define LOG_TAG "eApps"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

extern void lv_port_disp_android_init(void);
extern void lv_port_disp_android_deinit(void);
extern void lv_port_indev_android_init(void);
extern void lv_port_indev_android_deinit(void);
extern void lv_port_indev_android_process_event(AInputEvent *event);
extern void eapps_suite_init(void);

static void handle_cmd(struct android_app *app, int32_t cmd)
{
    (void)app;
    switch(cmd) {
        case APP_CMD_INIT_WINDOW:
            LOGI("Window initialized");
            break;
        case APP_CMD_TERM_WINDOW:
            LOGI("Window terminated");
            break;
        case APP_CMD_DESTROY:
            LOGI("App destroy requested");
            break;
        default:
            break;
    }
}

static int32_t handle_input(struct android_app *app, AInputEvent *event)
{
    (void)app;
    lv_port_indev_android_process_event(event);
    return 1;
}

void android_main(struct android_app *app)
{
    LOGI("eApps starting on Android");

    app->onAppCmd = handle_cmd;
    app->onInputEvent = handle_input;

    lv_init();
    LOGI("LVGL initialized");

    lv_port_disp_android_init();
    LOGI("Display port initialized (%dx%d)", ANDROID_DISP_HOR_RES, ANDROID_DISP_VER_RES);

    lv_port_indev_android_init();
    LOGI("Input port initialized");

    eapps_suite_init();
    LOGI("eApps suite initialized");

    int running = 1;
    while(running) {
        int events;
        struct android_poll_source *source;

        while(ALooper_pollAll(5, NULL, &events, (void **)&source) >= 0) {
            if(source != NULL) {
                source->process(app, source);
            }
            if(app->destroyRequested) {
                LOGI("Destroy requested, shutting down");
                running = 0;
                break;
            }
        }

        lv_timer_handler();
    }

    lv_port_indev_android_deinit();
    lv_port_disp_android_deinit();
    lv_deinit();
    LOGI("eApps shutdown complete");
}
