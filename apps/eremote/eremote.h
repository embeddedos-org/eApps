// SPDX-License-Identifier: MIT
// eRemote — EoS LVGL Application

/**
 * @file eremote.h
 * @brief Public API for the eRemote universal-remote app and its engine.
 *
 * The engine in eremote_engine.c implements four IR protocols, a Pronto-style
 * code database, a learning mode, a command dispatcher across IR/BLE/Wi-Fi and
 * a hub relay, plus scene and schedule tables. Every declaration below is
 * reconstructed from that translation unit's own usage; the header had been
 * reduced to the app-registration boilerplate, which left the engine
 * uncompilable.
 *
 * Command ordering is load-bearing: eremote_dispatch_cmd() indexes an
 * eremote_ir_db_entry_t::codes[] array directly with an eremote_cmd_id_t, and
 * the database in eremote_ir_db_init() stores Power, Vol+, Vol-, Ch+ and Ch-
 * at indices 0-4. Do not reorder the first five enumerators.
 */

#pragma once

#include "lvgl.h"
#include "eapps_core.h"

#include <stdbool.h>
#include <stdint.h>

/* ---- Capacity limits ---------------------------------------------------- */

#define EREMOTE_IR_DB_SIZE   16   /**< Code-database rows; init() fills 6.   */
#define MAX_DEVICES          16   /**< Configured devices; init() fills 2.   */
#define MAX_LEARNED          16   /**< Learned codes retained per device.    */
#define MAX_SCENES            8   /**< Scene slots; init() fills 3.          */
#define MAX_SCHEDULES         8   /**< Schedule slots; init() fills 2.       */
#define MAX_SCENE_STEPS       8   /**< Steps per scene; longest built-in = 3.*/
#define EREMOTE_MAX_PULSES  256   /**< Raw capture buffer, mark/space pairs. */
#define EREMOTE_HEX_LEN      24   /**< Room for Pronto hex and LEARN_xxxx.   */
#define EREMOTE_NAME_LEN     32   /**< strncpy(..., 31) throughout engine.   */

/** Default IR carrier used when a learned frame has no decoded protocol. */
#define IR_CARRIER_FREQ_HZ  38000u

/* ---- IR protocols ------------------------------------------------------- */

/** Wire protocol of a stored or captured IR frame. */
typedef enum {
    IR_PROTO_NEC = 0,   /**< 38 kHz, 9ms+4.5ms leader, 32-bit frame.  */
    IR_PROTO_RC5,       /**< 36 kHz, Manchester, 889us half-bit.      */
    IR_PROTO_SONY_SIRC, /**< 40 kHz, 2400us leader, 12/15/20-bit.     */
    IR_PROTO_RAW,       /**< Undecoded pulse train from learning mode.*/
    IR_PROTO_COUNT
} eremote_ir_proto_t;

/** A single IR command: protocol-specific fields plus a printable hex form. */
typedef struct {
    eremote_ir_proto_t proto;
    uint32_t           carrier_hz;
    char               hex_code[EREMOTE_HEX_LEN];
    union {
        struct { uint8_t address, address_inv, command, command_inv; } nec;
        struct { uint8_t toggle, address, command; }                  rc5;
        struct { uint8_t command, address, bit_count; }               sirc;
        struct {
            uint16_t pulses[EREMOTE_MAX_PULSES]; /**< Durations in us. */
            uint16_t pulse_count;
        } raw;
    };
} eremote_ir_code_t;

/* ---- Devices ----------------------------------------------------------- */

/** Device class, which selects the on-screen remote layout. */
typedef enum {
    EREMOTE_DEV_TV = 0,
    EREMOTE_DEV_SOUNDBAR,
    EREMOTE_DEV_STREAMING,
    EREMOTE_DEV_AC,
    EREMOTE_DEV_CUSTOM,
    EREMOTE_DEV_COUNT
} eremote_device_type_t;

/** Transport flags; a device may advertise several at once. */
#define EREMOTE_CONN_IR    0x01u
#define EREMOTE_CONN_BLE   0x02u
#define EREMOTE_CONN_WIFI  0x04u

/** Whether commands are emitted locally or relayed through an eRemote Hub. */
typedef enum {
    EREMOTE_MODE_DIRECT = 0,
    EREMOTE_MODE_HUB
} eremote_op_mode_t;

/**
 * Commands addressable on a device.
 *
 * The first five enumerators must stay in this order — see the file comment.
 * Only the enumerators referenced by the engine are defined; extending the
 * on-screen layouts described in README.md will require adding more, which
 * must be appended after CMD_TEMP_DOWN so database indices stay valid.
 */
typedef enum {
    CMD_POWER = 0,
    CMD_VOL_UP,
    CMD_VOL_DOWN,
    CMD_CH_UP,
    CMD_CH_DOWN,
    CMD_INPUT,
    CMD_TEMP_UP,
    CMD_TEMP_DOWN,
    CMD_COUNT
} eremote_cmd_id_t;

/** A configured device: identity, transports, and any learned codes. */
typedef struct {
    char                  name[EREMOTE_NAME_LEN];
    char                  brand[EREMOTE_NAME_LEN];
    char                  model[EREMOTE_NAME_LEN];
    eremote_device_type_t type;
    uint8_t               conn;      /**< Bitwise OR of EREMOTE_CONN_*.  */
    eremote_op_mode_t     op_mode;
    bool                  two_way;   /**< Transport reports device state. */
    eremote_ir_code_t     learned[MAX_LEARNED];
    int                   learned_count;
    /* Last known device state. Only meaningful when two_way is set; for
     * send-only transports these track what we last commanded. */
    bool                  power_on;
    uint8_t               volume;      /**< 0-100. */
    uint16_t              channel;     /**< 1-based; 0 means unknown. */
    int8_t                temperature; /**< Degrees C; AC devices only. */
    uint8_t               fan_speed;   /**< 0 = auto; AC devices only. */
} eremote_device_t;

/** One row of the shipped code database. */
typedef struct {
    const char           *brand;
    const char           *model;
    eremote_device_type_t type;
    eremote_ir_code_t     codes[CMD_COUNT];
    int                   code_count;
} eremote_ir_db_entry_t;

/* ---- Learning mode ----------------------------------------------------- */

/** Learning-mode progression: idle → waiting → capturing → done. */
typedef enum {
    LEARN_IDLE = 0,
    LEARN_WAITING,
    LEARN_CAPTURING,
    LEARN_DONE
} eremote_learn_state_t;

/* ---- Scenes and schedules ---------------------------------------------- */

/** One command in a scene macro, with a pre-delay in milliseconds. */
typedef struct {
    int              device_idx;
    eremote_cmd_id_t cmd;
    int              param;     /**< Target value, e.g. volume or degrees. */
    int              delay_ms;  /**< Wait before issuing this step.        */
} eremote_scene_step_t;

/** A named macro: an ordered list of device commands. */
typedef struct {
    char                 name[EREMOTE_NAME_LEN];
    eremote_scene_step_t steps[MAX_SCENE_STEPS];
    int                  step_count;
} eremote_scene_t;

/** A time-of-day automation entry. */
typedef struct {
    char             name[EREMOTE_NAME_LEN];
    uint8_t          hour;       /**< 0-23. */
    uint8_t          minute;     /**< 0-59. */
    uint8_t          days;       /**< Bit 0 = Monday; 0x7F = daily.  */
    int              device_idx;
    eremote_cmd_id_t cmd;
    int              param;
    bool             enabled;
} eremote_schedule_t;

/* ---- Engine API -------------------------------------------------------- */

/**
 * Human-readable protocol name.
 * @param p Protocol to name.
 * @return "NEC", "RC5", "SIRC", "RAW", or "?" if @p p is out of range.
 */
const char *eremote_proto_name(eremote_ir_proto_t p);

/**
 * Human-readable transport summary for a connection bitmask.
 * @param c Bitwise OR of EREMOTE_CONN_* flags.
 * @return A static string such as "IR+BLE", or "None" if no flag is set.
 */
const char *eremote_conn_label(uint8_t c);

/**
 * Render a decoded description of an IR code.
 * @param code Code to describe.
 * @param out  Destination buffer.
 * @param len  Size of @p out in bytes.
 */
void eremote_ir_dispatch(const eremote_ir_code_t *code, char *out, int len);

/** Populate the built-in code database. Call once before eremote_ir_db_find(). */
void eremote_ir_db_init(void);

/**
 * Look up a database row.
 * @param brand Brand string, matched exactly.
 * @param type  Device class to match.
 * @return The matching row, or NULL if none matches.
 */
const eremote_ir_db_entry_t *eremote_ir_db_find(const char *brand,
                                                eremote_device_type_t type);

/** @return The current learning-mode state. */
eremote_learn_state_t eremote_learn_get_state(void);

/**
 * Arm learning mode for one command.
 * @param cmd Command the next captured frame will be bound to.
 */
void eremote_learn_start(eremote_cmd_id_t cmd);

/** Inject a synthetic NEC pulse train; advances LEARN_WAITING to LEARN_DONE. */
void eremote_learn_simulate_capture(void);

/**
 * Commit a completed capture to a device.
 * @param dev Device receiving the learned code.
 * @return true on success; false if no capture is pending or @p dev is full.
 */
bool eremote_learn_store(eremote_device_t *dev);

/**
 * Send a command over the device's best available transport.
 * @param dev Target device.
 * @param cmd Command to send.
 * @param fb  Buffer receiving user-facing feedback text.
 * @param len Size of @p fb in bytes.
 */
void eremote_dispatch_cmd(eremote_device_t *dev, eremote_cmd_id_t cmd,
                          char *fb, int len);

/** Populate the built-in scene table. */
void eremote_scenes_init(void);
/** @return Number of populated scenes. */
int eremote_scene_count(void);
/**
 * @param idx Zero-based scene index.
 * @return The scene, or NULL if @p idx is out of range.
 */
const eremote_scene_t *eremote_scene_get(int idx);

/** Populate the built-in schedule table. */
void eremote_schedules_init(void);
/** @return Number of populated schedules. */
int eremote_schedule_count(void);
/**
 * @param idx Zero-based schedule index.
 * @return The schedule, or NULL if @p idx is out of range.
 */
const eremote_schedule_t *eremote_schedule_get(int idx);

/* ---- App registration -------------------------------------------------- */

extern const eapps_app_info_t      eremote_info;
extern const eapps_app_lifecycle_t eremote_lifecycle;
