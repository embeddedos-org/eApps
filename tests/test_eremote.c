// SPDX-License-Identifier: MIT
#include "eapps_test.h"
#include "../apps/eremote/eremote.h"

/* ---- IR Database Tests ---- */

static void test_ir_db_find_sony(void) {
    eremote_ir_db_init();
    const eremote_ir_db_entry_t *e = eremote_ir_db_find("Sony", EREMOTE_DEV_TV);
    ASSERT_NOT_NULL(e, "ir_db_find Sony TV returns non-NULL");
}

static void test_ir_db_find_samsung(void) {
    const eremote_ir_db_entry_t *e = eremote_ir_db_find("Samsung", EREMOTE_DEV_TV);
    ASSERT_NOT_NULL(e, "ir_db_find Samsung TV returns non-NULL");
}

static void test_ir_db_find_nonexistent(void) {
    const eremote_ir_db_entry_t *e = eremote_ir_db_find("Nonexistent", EREMOTE_DEV_TV);
    ASSERT_NULL(e, "ir_db_find Nonexistent returns NULL");
}

/* ---- Protocol & Connection Label Tests ---- */

static void test_proto_name(void) {
    ASSERT_STR_EQ(eremote_proto_name(IR_PROTO_NEC), "NEC", "proto_name NEC");
    ASSERT_STR_EQ(eremote_proto_name(IR_PROTO_RC5), "RC5", "proto_name RC5");
}

static void test_conn_label(void) {
    ASSERT_STR_EQ(eremote_conn_label(EREMOTE_CONN_IR), "IR", "conn_label IR");
    ASSERT_STR_EQ(eremote_conn_label(EREMOTE_CONN_BLE), "BLE", "conn_label BLE");
    ASSERT_STR_EQ(eremote_conn_label(EREMOTE_CONN_IR | EREMOTE_CONN_BLE),
                  "IR+BLE", "conn_label IR|BLE");
}

/* ---- Learning Mode Tests ---- */

static void test_learn_initial_state(void) {
    eremote_learn_state_t st = eremote_learn_get_state();
    ASSERT_EQ(st, LEARN_IDLE, "learn initial state is IDLE");
}

static void test_learn_start(void) {
    eremote_learn_start(CMD_POWER);
    eremote_learn_state_t st = eremote_learn_get_state();
    ASSERT_EQ(st, LEARN_WAITING, "learn state after start is WAITING");
}

static void test_learn_simulate_capture(void) {
    eremote_learn_simulate_capture();
    eremote_learn_state_t st = eremote_learn_get_state();
    ASSERT_EQ(st, LEARN_DONE, "learn state after capture is DONE");
}

/* ---- Scene Tests ---- */

static void test_scenes(void) {
    eremote_scenes_init();
    ASSERT_EQ(eremote_scene_count(), 3, "scene count is 3 after init");

    const eremote_scene_t *s = eremote_scene_get(0);
    ASSERT_NOT_NULL(s, "scene_get(0) non-NULL");
    ASSERT_STR_EQ(s->name, "Movie Mode", "scene 0 name is Movie Mode");
}

/* ---- Schedule Tests ---- */

static void test_schedules(void) {
    eremote_schedules_init();
    ASSERT_EQ(eremote_schedule_count(), 2, "schedule count is 2 after init");
}

/* ---- Dispatch Command Test ---- */

static void test_dispatch_cmd(void) {
    eremote_device_t dev = {0};
    strncpy(dev.name, "TestTV", sizeof(dev.name) - 1);
    strncpy(dev.brand, "Sony", sizeof(dev.brand) - 1);
    dev.type    = EREMOTE_DEV_TV;
    dev.conn    = EREMOTE_CONN_IR;
    dev.op_mode = EREMOTE_MODE_DIRECT;

    char fb[128] = {0};
    eremote_dispatch_cmd(&dev, CMD_POWER, fb, sizeof(fb));
    ASSERT_TRUE(strlen(fb) > 0, "dispatch_cmd produces feedback string");
}

int main(void) {
    TEST_SUITE("eRemote IR Database");
    test_ir_db_find_sony();
    test_ir_db_find_samsung();
    test_ir_db_find_nonexistent();

    TEST_SUITE("eRemote Protocol & Connection Labels");
    test_proto_name();
    test_conn_label();

    TEST_SUITE("eRemote Learning Mode");
    test_learn_initial_state();
    test_learn_start();
    test_learn_simulate_capture();

    TEST_SUITE("eRemote Scenes & Schedules");
    test_scenes();
    test_schedules();

    TEST_SUITE("eRemote Dispatch");
    test_dispatch_cmd();

    TEST_EXIT();
}
