// SPDX-License-Identifier: MIT
#ifndef EAPPS_APP_EREMOTE_H
#define EAPPS_APP_EREMOTE_H
#include "eapps/types.h"
#include <stdint.h>
#include <stdbool.h>

/* ================================================================
 * eRemote — Universal Smart Remote
 *
 * Supports two operation modes:
 *   1. Direct Mode  — Phone IR blaster / BLE / Wi-Fi to device
 *   2. Hub Mode     — Phone → Wi-Fi → eRemote Hub → IR/RF blast
 *
 * IR Protocols:  NEC, RC5 (Philips), Sony SIRC, RAW (learned)
 * Smart Protos:  BLE GATT, Wi-Fi (SSDP/UPnP), mDNS
 * ================================================================ */

/* ---- IR Protocol Types ---- */

typedef enum {
    IR_PROTO_NEC,
    IR_PROTO_RC5,
    IR_PROTO_SONY_SIRC,
    IR_PROTO_RAW,
    IR_PROTO_COUNT,
} eremote_ir_proto_t;

/* ---- IR Signal Representation ---- */

#define IR_RAW_MAX_PULSES 256
#define IR_CARRIER_FREQ_HZ 38000

typedef struct {
    eremote_ir_proto_t proto;
    uint32_t           carrier_hz;
    union {
        struct {
            uint8_t  address;
            uint8_t  address_inv;
            uint8_t  command;
            uint8_t  command_inv;
        } nec;
        struct {
            uint8_t  toggle;
            uint8_t  address;
            uint8_t  command;
        } rc5;
        struct {
            uint8_t  command;
            uint8_t  address;
            uint8_t  extended;
            uint8_t  bit_count;
        } sirc;
        struct {
            uint16_t pulses[IR_RAW_MAX_PULSES];
            uint16_t pulse_count;
        } raw;
    };
    char hex_code[64];
} eremote_ir_code_t;

/* ---- Connection / Transport ---- */

typedef enum {
    EREMOTE_CONN_NONE    = 0,
    EREMOTE_CONN_IR      = (1 << 0),
    EREMOTE_CONN_BLE     = (1 << 1),
    EREMOTE_CONN_WIFI    = (1 << 2),
    EREMOTE_CONN_RF433   = (1 << 3),
} eremote_conn_mode_t;

typedef enum {
    EREMOTE_MODE_DIRECT,
    EREMOTE_MODE_HUB,
} eremote_op_mode_t;

/* ---- Device Types ---- */

typedef enum {
    EREMOTE_DEV_TV,
    EREMOTE_DEV_SOUNDBAR,
    EREMOTE_DEV_STREAMING,
    EREMOTE_DEV_AC,
    EREMOTE_DEV_FAN,
    EREMOTE_DEV_PROJECTOR,
    EREMOTE_DEV_STB,
    EREMOTE_DEV_CUSTOM,
    EREMOTE_DEV_TYPE_COUNT,
} eremote_device_type_t;

/* ---- Command IDs ---- */

typedef enum {
    CMD_POWER,
    CMD_VOL_UP, CMD_VOL_DOWN, CMD_MUTE,
    CMD_CH_UP, CMD_CH_DOWN,
    CMD_UP, CMD_DOWN, CMD_LEFT, CMD_RIGHT, CMD_OK,
    CMD_MENU, CMD_BACK, CMD_HOME, CMD_INPUT,
    CMD_NUM_0, CMD_NUM_1, CMD_NUM_2, CMD_NUM_3,
    CMD_NUM_4, CMD_NUM_5, CMD_NUM_6, CMD_NUM_7,
    CMD_NUM_8, CMD_NUM_9,
    CMD_PLAY, CMD_PAUSE, CMD_STOP,
    CMD_FF, CMD_REW, CMD_SKIP,
    CMD_TEMP_UP, CMD_TEMP_DOWN,
    CMD_FAN_SPEED, CMD_AC_MODE, CMD_SWING,
    CMD_COUNT,
} eremote_cmd_id_t;

/* ---- IR Code Database Entry ---- */

#define EREMOTE_MAX_CODES_PER_DEVICE 40

typedef struct {
    const char         *brand;
    const char         *model;
    eremote_device_type_t type;
    eremote_ir_code_t  codes[EREMOTE_MAX_CODES_PER_DEVICE];
    int                code_count;
} eremote_ir_db_entry_t;

/* ---- Device Instance ---- */

#define MAX_DEVICES     8
#define MAX_LEARNED     16

typedef struct {
    char                  name[32];
    char                  brand[24];
    char                  model[24];
    eremote_device_type_t type;
    uint8_t               conn;
    eremote_op_mode_t     op_mode;
    bool                  power_on;
    int                   volume;
    int                   channel;
    int                   temperature;
    int                   fan_speed;
    int                   ac_mode;
    bool                  two_way;
    int                   db_index;
    eremote_ir_code_t     learned[MAX_LEARNED];
    int                   learned_count;
} eremote_device_t;

/* ---- Scene / Macro ---- */

#define MAX_SCENES       8
#define MAX_SCENE_STEPS  8

typedef struct {
    int              device_idx;
    eremote_cmd_id_t cmd;
    int              param;
    uint16_t         delay_ms;
} eremote_scene_step_t;

typedef struct {
    char                 name[32];
    eremote_scene_step_t steps[MAX_SCENE_STEPS];
    int                  step_count;
} eremote_scene_t;

/* ---- Schedule ---- */

#define MAX_SCHEDULES 8

typedef struct {
    char    name[32];
    uint8_t hour;
    uint8_t minute;
    uint8_t days;
    int     device_idx;
    eremote_cmd_id_t cmd;
    int     param;
    bool    enabled;
} eremote_schedule_t;

/* ---- Learning Mode State ---- */

typedef enum {
    LEARN_IDLE,
    LEARN_WAITING,
    LEARN_CAPTURING,
    LEARN_DONE,
    LEARN_FAILED,
} eremote_learn_state_t;

/* ---- IR DB Size ---- */

#define EREMOTE_IR_DB_SIZE 6

/* ---- Engine API ---- */

const char *eremote_proto_name(eremote_ir_proto_t p);
const char *eremote_conn_label(uint8_t conn);
void eremote_ir_dispatch(const eremote_ir_code_t *code, char *out, int len);
void eremote_ir_db_init(void);
const eremote_ir_db_entry_t *eremote_ir_db_find(const char *brand,
                                                  eremote_device_type_t type);
eremote_learn_state_t eremote_learn_get_state(void);
void eremote_learn_start(eremote_cmd_id_t cmd);
void eremote_learn_simulate_capture(void);
bool eremote_learn_store(eremote_device_t *dev);
void eremote_dispatch_cmd(eremote_device_t *dev, eremote_cmd_id_t cmd,
                           char *fb, int len);
void eremote_scenes_init(void);
int  eremote_scene_count(void);
const eremote_scene_t *eremote_scene_get(int idx);
void eremote_schedules_init(void);
int  eremote_schedule_count(void);
const eremote_schedule_t *eremote_schedule_get(int idx);

/* ---- App Registration ---- */

extern const eapps_app_info_t      eremote_info;
extern const eapps_app_lifecycle_t eremote_lifecycle;

#endif
