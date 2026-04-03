// SPDX-License-Identifier: MIT
// eRemote Engine — IR protocols, code database, learning, scenes, schedules

#include "eremote.h"
#include <string.h>
#include <stdio.h>

/* ================================================================
 *  IR PROTOCOL ENGINE
 *
 *  NEC (38 kHz): 9ms leader + 4.5ms space, 562us mark per bit
 *    Bit 0 = 562us mark + 562us space
 *    Bit 1 = 562us mark + 1687us space
 *    Frame: address(8) + ~address(8) + command(8) + ~command(8)
 *
 *  RC5 (36 kHz): Manchester encoded, 889us half-bit
 *    Frame: start(1) + field(1) + toggle(1) + address(5) + command(6)
 *
 *  Sony SIRC (40 kHz):
 *    Leader: 2400us mark + 600us space
 *    Bit 0 = 600us mark + 600us space
 *    Bit 1 = 1200us mark + 600us space
 *    Frame: command(7) + address(5/8/13)
 * ================================================================ */

const char *eremote_proto_name(eremote_ir_proto_t p)
{
    static const char *names[] = {"NEC", "RC5", "SIRC", "RAW"};
    return (p < IR_PROTO_COUNT) ? names[p] : "?";
}

const char *eremote_conn_label(uint8_t c)
{
    if ((c & EREMOTE_CONN_IR) && (c & EREMOTE_CONN_BLE))  return "IR+BLE";
    if ((c & EREMOTE_CONN_IR) && (c & EREMOTE_CONN_WIFI)) return "IR+WiFi";
    if (c & EREMOTE_CONN_IR)   return "IR";
    if (c & EREMOTE_CONN_BLE)  return "BLE";
    if (c & EREMOTE_CONN_WIFI) return "WiFi";
    return "None";
}

void eremote_ir_dispatch(const eremote_ir_code_t *code, char *out, int len)
{
    switch (code->proto) {
    case IR_PROTO_NEC:
        snprintf(out, len, "NEC 38kHz addr=0x%02X cmd=0x%02X [%s]",
                 code->nec.address, code->nec.command, code->hex_code);
        break;
    case IR_PROTO_RC5:
        snprintf(out, len, "RC5 36kHz T=%d addr=%d cmd=%d [%s]",
                 code->rc5.toggle, code->rc5.address,
                 code->rc5.command, code->hex_code);
        break;
    case IR_PROTO_SONY_SIRC:
        snprintf(out, len, "SIRC 40kHz cmd=0x%02X addr=0x%02X %dbit [%s]",
                 code->sirc.command, code->sirc.address,
                 code->sirc.bit_count, code->hex_code);
        break;
    case IR_PROTO_RAW:
        snprintf(out, len, "RAW %u pulses @ %luHz",
                 code->raw.pulse_count, (unsigned long)code->carrier_hz);
        break;
    default:
        snprintf(out, len, "(unknown)");
    }
}

/* ================================================================
 *  IR CODE DATABASE
 *
 *  Hex codes follow Pronto-style convention.
 *  Example NEC Power for Samsung: "E0E040BF"
 *    E0 = address byte, E0 = ~address, 40 = command, BF = ~command
 * ================================================================ */

static eremote_ir_code_t make_nec(uint8_t addr, uint8_t cmd, const char *hex)
{
    eremote_ir_code_t c = {0};
    c.proto = IR_PROTO_NEC;
    c.carrier_hz = 38000;
    c.nec.address     = addr;
    c.nec.address_inv = (uint8_t)~addr;
    c.nec.command     = cmd;
    c.nec.command_inv = (uint8_t)~cmd;
    snprintf(c.hex_code, sizeof(c.hex_code), "%s", hex);
    return c;
}

static eremote_ir_code_t make_sirc(uint8_t cmd, uint8_t addr,
                                    uint8_t bits, const char *hex)
{
    eremote_ir_code_t c = {0};
    c.proto = IR_PROTO_SONY_SIRC;
    c.carrier_hz = 40000;
    c.sirc.command   = cmd;
    c.sirc.address   = addr;
    c.sirc.bit_count = bits;
    snprintf(c.hex_code, sizeof(c.hex_code), "%s", hex);
    return c;
}

static eremote_ir_db_entry_t g_ir_db[EREMOTE_IR_DB_SIZE];
static int g_ir_db_count = 0;

void eremote_ir_db_init(void)
{
    int i = 0;

    /* Sony TV — SIRC 12-bit: Power, Vol+, Vol-, Ch+, Ch- */
    g_ir_db[i].brand = "Sony";
    g_ir_db[i].model = "Bravia";
    g_ir_db[i].type  = EREMOTE_DEV_TV;
    g_ir_db[i].codes[0] = make_sirc(0x15, 0x01, 12, "A90");
    g_ir_db[i].codes[1] = make_sirc(0x12, 0x01, 12, "490");
    g_ir_db[i].codes[2] = make_sirc(0x13, 0x01, 12, "C90");
    g_ir_db[i].codes[3] = make_sirc(0x10, 0x01, 12, "090");
    g_ir_db[i].codes[4] = make_sirc(0x11, 0x01, 12, "890");
    g_ir_db[i].code_count = 5;
    i++;

    /* Samsung TV — NEC: Power, Vol+, Vol-, Ch+, Ch- */
    g_ir_db[i].brand = "Samsung";
    g_ir_db[i].model = "Smart TV";
    g_ir_db[i].type  = EREMOTE_DEV_TV;
    g_ir_db[i].codes[0] = make_nec(0x07, 0x02, "E0E040BF");
    g_ir_db[i].codes[1] = make_nec(0x07, 0x07, "E0E0E01F");
    g_ir_db[i].codes[2] = make_nec(0x07, 0x0B, "E0E0D02F");
    g_ir_db[i].codes[3] = make_nec(0x07, 0x48, "E0E048B7");
    g_ir_db[i].codes[4] = make_nec(0x07, 0x08, "E0E008F7");
    g_ir_db[i].code_count = 5;
    i++;

    /* LG TV — NEC */
    g_ir_db[i].brand = "LG";
    g_ir_db[i].model = "WebOS TV";
    g_ir_db[i].type  = EREMOTE_DEV_TV;
    g_ir_db[i].codes[0] = make_nec(0x04, 0x08, "20DF10EF");
    g_ir_db[i].codes[1] = make_nec(0x04, 0x02, "20DF40BF");
    g_ir_db[i].codes[2] = make_nec(0x04, 0x03, "20DFC03F");
    g_ir_db[i].code_count = 3;
    i++;

    /* Samsung Soundbar — NEC */
    g_ir_db[i].brand = "Samsung";
    g_ir_db[i].model = "Soundbar HW-Q";
    g_ir_db[i].type  = EREMOTE_DEV_SOUNDBAR;
    g_ir_db[i].codes[0] = make_nec(0x56, 0x00, "AC000000");
    g_ir_db[i].codes[1] = make_nec(0x56, 0x01, "AC800000");
    g_ir_db[i].codes[2] = make_nec(0x56, 0x02, "AC400000");
    g_ir_db[i].code_count = 3;
    i++;

    /* Daikin AC — NEC extended */
    g_ir_db[i].brand = "Daikin";
    g_ir_db[i].model = "FTK-Series";
    g_ir_db[i].type  = EREMOTE_DEV_AC;
    g_ir_db[i].codes[0] = make_nec(0x16, 0x00, "1100A3B6");
    g_ir_db[i].codes[1] = make_nec(0x16, 0x01, "1180A3B6");
    g_ir_db[i].codes[2] = make_nec(0x16, 0x02, "1140A3B6");
    g_ir_db[i].code_count = 3;
    i++;

    /* Apple TV — BLE only, no IR codes */
    g_ir_db[i].brand = "Apple";
    g_ir_db[i].model = "Apple TV 4K";
    g_ir_db[i].type  = EREMOTE_DEV_STREAMING;
    g_ir_db[i].code_count = 0;
    i++;

    g_ir_db_count = i;
}

const eremote_ir_db_entry_t *eremote_ir_db_find(const char *brand,
                                                  eremote_device_type_t type)
{
    for (int i = 0; i < g_ir_db_count; i++)
        if (g_ir_db[i].type == type && strcmp(g_ir_db[i].brand, brand) == 0)
            return &g_ir_db[i];
    return NULL;
}

/* ================================================================
 *  LEARNING MODE
 *
 *  Flow: User taps Learn → LEARN_WAITING → IR receiver captures
 *  raw pulses → LEARN_CAPTURING → frequency + durations decoded
 *  → LEARN_DONE → hex code generated and stored in device
 * ================================================================ */

static eremote_learn_state_t g_learn_state = LEARN_IDLE;
static eremote_ir_code_t     g_learn_buf;
static eremote_cmd_id_t      g_learn_cmd = CMD_POWER;

eremote_learn_state_t eremote_learn_get_state(void) { return g_learn_state; }

void eremote_learn_start(eremote_cmd_id_t cmd)
{
    g_learn_state = LEARN_WAITING;
    g_learn_cmd = cmd;
    memset(&g_learn_buf, 0, sizeof(g_learn_buf));
    g_learn_buf.proto = IR_PROTO_RAW;
    g_learn_buf.carrier_hz = IR_CARRIER_FREQ_HZ;
}

void eremote_learn_simulate_capture(void)
{
    if (g_learn_state != LEARN_WAITING) return;
    g_learn_buf.raw.pulses[0] = 9000;  /* NEC leader mark */
    g_learn_buf.raw.pulses[1] = 4500;  /* NEC leader space */
    g_learn_buf.raw.pulses[2] = 562;   /* bit mark */
    g_learn_buf.raw.pulses[3] = 1687;  /* bit 1 space */
    g_learn_buf.raw.pulses[4] = 562;   /* bit mark */
    g_learn_buf.raw.pulses[5] = 562;   /* bit 0 space */
    g_learn_buf.raw.pulse_count = 6;
    snprintf(g_learn_buf.hex_code, sizeof(g_learn_buf.hex_code),
             "LEARN_%04X", (unsigned)g_learn_cmd);
    g_learn_state = LEARN_DONE;
}

bool eremote_learn_store(eremote_device_t *dev)
{
    if (g_learn_state != LEARN_DONE) return false;
    if (dev->learned_count >= MAX_LEARNED) return false;
    dev->learned[dev->learned_count++] = g_learn_buf;
    g_learn_state = LEARN_IDLE;
    return true;
}

/* ================================================================
 *  COMMAND DISPATCHER
 *
 *  Routes commands through active transport:
 *    IR    → modulate carrier, blast pulse sequence (line-of-sight)
 *    BLE   → GATT characteristic write (no LOS, 2-way)
 *    WiFi  → HTTP/WebSocket to smart device API (no LOS, 2-way)
 *    Hub   → forward to eRemote Hub via Wi-Fi, hub blasts IR/RF
 * ================================================================ */

void eremote_dispatch_cmd(eremote_device_t *dev, eremote_cmd_id_t cmd,
                           char *fb, int len)
{
    const char *tp = eremote_conn_label(dev->conn);
    const char *md = (dev->op_mode == EREMOTE_MODE_HUB) ? "Hub" : "Direct";

    if (dev->conn & EREMOTE_CONN_IR) {
        const eremote_ir_db_entry_t *db =
            eremote_ir_db_find(dev->brand, dev->type);
        if (db && (int)cmd < db->code_count) {
            char desc[128];
            eremote_ir_dispatch(&db->codes[cmd], desc, sizeof(desc));
            snprintf(fb, len, "[%s/%s] %s", md, tp, desc);
            return;
        }
    }

    if (dev->conn & (EREMOTE_CONN_BLE | EREMOTE_CONN_WIFI)) {
        const char *p = (dev->conn & EREMOTE_CONN_BLE) ? "BLE GATT"
                                                        : "WiFi API";
        snprintf(fb, len, "[%s/%s] %s cmd=%d %s",
                 md, tp, p, cmd, dev->two_way ? "(2-way)" : "(1-way)");
        return;
    }

    snprintf(fb, len, "[%s] No transport cmd=%d", md, cmd);
}

/* ================================================================
 *  SCENES
 * ================================================================ */

static eremote_scene_t g_scenes[MAX_SCENES];
static int g_scene_count = 0;

void eremote_scenes_init(void)
{
    strncpy(g_scenes[0].name, "Movie Mode", 31);
    g_scenes[0].steps[0] = (eremote_scene_step_t){0, CMD_POWER, 1, 0};
    g_scenes[0].steps[1] = (eremote_scene_step_t){0, CMD_INPUT, 2, 500};
    g_scenes[0].steps[2] = (eremote_scene_step_t){1, CMD_POWER, 1, 300};
    g_scenes[0].step_count = 3;

    strncpy(g_scenes[1].name, "Night Mode", 31);
    g_scenes[1].steps[0] = (eremote_scene_step_t){3, CMD_TEMP_DOWN, 20, 0};
    g_scenes[1].steps[1] = (eremote_scene_step_t){0, CMD_POWER, 0, 500};
    g_scenes[1].step_count = 2;

    strncpy(g_scenes[2].name, "Music Mode", 31);
    g_scenes[2].steps[0] = (eremote_scene_step_t){1, CMD_POWER, 1, 0};
    g_scenes[2].steps[1] = (eremote_scene_step_t){1, CMD_VOL_UP, 60, 300};
    g_scenes[2].step_count = 2;

    g_scene_count = 3;
}

int eremote_scene_count(void) { return g_scene_count; }
const eremote_scene_t *eremote_scene_get(int idx)
{
    return (idx >= 0 && idx < g_scene_count) ? &g_scenes[idx] : NULL;
}

/* ================================================================
 *  SCHEDULES
 * ================================================================ */

static eremote_schedule_t g_schedules[MAX_SCHEDULES];
static int g_schedule_count = 0;

void eremote_schedules_init(void)
{
    strncpy(g_schedules[0].name, "AC Off Timer", 31);
    g_schedules[0].hour = 23;
    g_schedules[0].minute = 0;
    g_schedules[0].days = 0x7F;
    g_schedules[0].device_idx = 3;
    g_schedules[0].cmd = CMD_POWER;
    g_schedules[0].enabled = true;

    strncpy(g_schedules[1].name, "Morning TV", 31);
    g_schedules[1].hour = 7;
    g_schedules[1].minute = 30;
    g_schedules[1].days = 0x1F;
    g_schedules[1].device_idx = 0;
    g_schedules[1].cmd = CMD_POWER;
    g_schedules[1].param = 1;
    g_schedules[1].enabled = false;

    g_schedule_count = 2;
}

int eremote_schedule_count(void) { return g_schedule_count; }
const eremote_schedule_t *eremote_schedule_get(int idx)
{
    return (idx >= 0 && idx < g_schedule_count) ? &g_schedules[idx] : NULL;
}
