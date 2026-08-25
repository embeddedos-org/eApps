// SPDX-License-Identifier: MIT
#include "eapps_test.h"
#include "../apps/ewifi/ewifi.h"

/* ---- Scanner Tests ---- */

static void test_scan(void) {
    ewifi_engine_init();
    ewifi_network_t nets[EWIFI_MAX_NETWORKS];
    int n = ewifi_scan(nets, EWIFI_MAX_NETWORKS);
    ASSERT_EQ(n, 8, "scan returns 8 networks");
}

/* ---- Signal Quality Tests ---- */

static void test_signal_quality(void) {
    ASSERT_EQ(ewifi_signal_quality(-42), EWIFI_SIGNAL_EXCELLENT,
              "rssi -42 = EXCELLENT");
    ASSERT_EQ(ewifi_signal_quality(-65), EWIFI_SIGNAL_FAIR,
              "rssi -65 = FAIR");
    ASSERT_EQ(ewifi_signal_quality(-85), EWIFI_SIGNAL_VERY_WEAK,
              "rssi -85 = VERY_WEAK");
}

static void test_rssi_to_pct(void) {
    ASSERT_EQ(ewifi_rssi_to_pct(-30), 100, "rssi -30 = 100%");
    ASSERT_EQ(ewifi_rssi_to_pct(-90), 0, "rssi -90 = 0%");
}

/* ---- String Conversion Tests ---- */

static void test_security_str(void) {
    ASSERT_STR_EQ(ewifi_security_str(EWIFI_SEC_WPA3_SAE), "WPA3-SAE",
                  "security_str WPA3_SAE");
}

static void test_standard_str(void) {
    ASSERT_STR_EQ(ewifi_standard_str(EWIFI_STD_AX), "802.11ax (WiFi 6)",
                  "standard_str AX");
}

static void test_band_str(void) {
    ASSERT_STR_EQ(ewifi_band_str(EWIFI_BAND_5G), "5 GHz",
                  "band_str 5G");
}

/* ---- Channel Analysis Tests ---- */

static void test_channel_analysis(void) {
    ewifi_channel_t chans[EWIFI_MAX_CHANNELS];
    int n = ewifi_channel_analysis(chans, EWIFI_MAX_CHANNELS);
    ASSERT_GT(n, 0, "channel analysis returns > 0 channels");
}

static void test_best_channel(void) {
    int ch = ewifi_best_channel(EWIFI_BAND_5G);
    ASSERT_GT(ch, 0, "best channel returns valid number");
}

/* ---- Security Assessment Tests ---- */

static void test_assessment_open_network(void) {
    ewifi_network_t net = {0};
    strncpy(net.ssid, "FreeWiFi", EWIFI_SSID_MAX - 1);
    net.security = EWIFI_SEC_OPEN;
    net.rssi     = -50;
    net.channel  = 6;

    ewifi_assessment_t assess = {0};
    ewifi_assess_network(&net, &assess);
    ASSERT_LT(assess.score, 60, "open network score < 60");
}

static void test_assessment_wpa3_network(void) {
    ewifi_network_t net = {0};
    strncpy(net.ssid, "SecureNet", EWIFI_SSID_MAX - 1);
    net.security = EWIFI_SEC_WPA3_SAE;
    net.rssi     = -40;
    net.channel  = 36;

    ewifi_assessment_t assess = {0};
    ewifi_assess_network(&net, &assess);
    ASSERT_GTE(assess.score, 90, "WPA3 network score >= 90");
}

/* ---- Handshake Education Tests ---- */

static void test_handshake_step_count(void) {
    ASSERT_EQ(ewifi_handshake_step_count(), 6, "handshake step count = 6");
}

static void test_handshake_get_step(void) {
    const ewifi_handshake_info_t *info =
        ewifi_handshake_get_step(EWIFI_HS_MSG1_ANONCE);
    ASSERT_NOT_NULL(info, "handshake get step MSG1 returns non-NULL");
}

/* ---- Password Vault Tests ---- */

static void test_vault_add_find(void) {
    ewifi_vault_t v;
    ewifi_vault_init(&v);
    ewifi_vault_add(&v, "HomeNet", "secret123", "home router", true);
    int idx = ewifi_vault_find(&v, "HomeNet");
    ASSERT_GTE(idx, 0, "vault find added entry returns index >= 0");
}

static void test_vault_remove(void) {
    ewifi_vault_t v;
    ewifi_vault_init(&v);
    ewifi_vault_add(&v, "TempNet", "pass456", "temp", false);
    int idx = ewifi_vault_find(&v, "TempNet");
    ASSERT_GTE(idx, 0, "vault find before remove");
    ewifi_vault_remove(&v, idx);
    ASSERT_EQ(ewifi_vault_find(&v, "TempNet"), -1,
              "vault find after remove returns -1");
}

static void test_vault_pin_lock_unlock(void) {
    ewifi_vault_t v;
    ewifi_vault_init(&v);

    bool pin_ok = ewifi_vault_set_pin(&v, "1234");
    ASSERT_TRUE(pin_ok, "vault set PIN succeeds");

    ewifi_vault_lock(&v);
    ASSERT_FALSE(v.unlocked, "vault is locked after lock()");

    bool unlock_ok = ewifi_vault_unlock(&v, "1234");
    ASSERT_TRUE(unlock_ok, "vault unlock with correct PIN succeeds");
    ASSERT_TRUE(v.unlocked, "vault is unlocked after correct PIN");
}

static void test_vault_wrong_pin(void) {
    ewifi_vault_t v;
    ewifi_vault_init(&v);
    ewifi_vault_set_pin(&v, "1234");
    ewifi_vault_lock(&v);

    bool unlock_ok = ewifi_vault_unlock(&v, "9999");
    ASSERT_FALSE(unlock_ok, "vault unlock with wrong PIN fails");
    ASSERT_FALSE(v.unlocked, "vault remains locked after wrong PIN");
}

static void test_vault_encrypt_decrypt_roundtrip(void) {
    ewifi_vault_t v;
    ewifi_vault_init(&v);
    ewifi_vault_set_pin(&v, "1234");
    ewifi_vault_add(&v, "CryptoNet", "mypassword", "test", false);

    ewifi_vault_encrypt_all(&v);
    ASSERT_TRUE(v.entries[0].is_encrypted,
                "entry is encrypted after encrypt_all");

    ewifi_vault_decrypt_all(&v);
    ASSERT_STR_EQ(v.entries[0].password, "mypassword",
                  "password preserved after encrypt/decrypt roundtrip");
}

/* ---- Pre-Connect Validation (6 Red Flags) Tests ---- */

static void test_validation_wep_flag(void) {
    ewifi_network_t net = {0};
    strncpy(net.ssid, "OldRouter", EWIFI_SSID_MAX - 1);
    strncpy(net.bssid, "AA:BB:CC:DD:EE:01", EWIFI_BSSID_LEN - 1);
    net.security = EWIFI_SEC_WEP;
    net.rssi     = -55;
    net.channel  = 1;

    ewifi_validation_t val = {0};
    ewifi_validate_network(&net, &net, 1, &val);
    ASSERT_TRUE(val.flags[EWIFI_FLAG_WEP_INSECURE].triggered,
                "WEP network triggers WEP insecure flag");
}

static void test_validation_evil_twin_flag(void) {
    ewifi_network_t nets[2] = {0};

    strncpy(nets[0].ssid, "CoffeeShop", EWIFI_SSID_MAX - 1);
    strncpy(nets[0].bssid, "AA:BB:CC:DD:EE:01", EWIFI_BSSID_LEN - 1);
    nets[0].security = EWIFI_SEC_WPA2_PSK;
    nets[0].rssi     = -50;
    nets[0].channel  = 6;

    strncpy(nets[1].ssid, "CoffeeShop", EWIFI_SSID_MAX - 1);
    strncpy(nets[1].bssid, "AA:BB:CC:DD:EE:02", EWIFI_BSSID_LEN - 1);
    nets[1].security = EWIFI_SEC_WPA2_PSK;
    nets[1].rssi     = -45;
    nets[1].channel  = 6;

    ewifi_validation_t val = {0};
    ewifi_validate_network(&nets[0], nets, 2, &val);
    ASSERT_TRUE(val.flags[EWIFI_FLAG_EVIL_TWIN].triggered,
                "evil twin flag triggered for duplicate SSID different BSSID");
}

static void test_validation_wpa3_passes(void) {
    ewifi_network_t net = {0};
    strncpy(net.ssid, "SecureHome", EWIFI_SSID_MAX - 1);
    strncpy(net.bssid, "11:22:33:44:55:66", EWIFI_BSSID_LEN - 1);
    net.security = EWIFI_SEC_WPA3_SAE;
    net.rssi     = -40;
    net.channel  = 36;

    ewifi_validation_t val = {0};
    ewifi_validate_network(&net, &net, 1, &val);
    ASSERT_EQ(val.flags_triggered, 0,
              "WPA3 network passes all 6 flags");
    ASSERT_TRUE(val.safe_to_connect,
                "WPA3 network is safe to connect");
}

int main(void) {
    TEST_SUITE("eWiFi Scanner");
    test_scan();

    TEST_SUITE("eWiFi Signal Quality");
    test_signal_quality();
    test_rssi_to_pct();

    TEST_SUITE("eWiFi String Conversions");
    test_security_str();
    test_standard_str();
    test_band_str();

    TEST_SUITE("eWiFi Channel Analysis");
    test_channel_analysis();
    test_best_channel();

    TEST_SUITE("eWiFi Security Assessment");
    test_assessment_open_network();
    test_assessment_wpa3_network();

    TEST_SUITE("eWiFi Handshake Education");
    test_handshake_step_count();
    test_handshake_get_step();

    TEST_SUITE("eWiFi Password Vault");
    test_vault_add_find();
    test_vault_remove();
    test_vault_pin_lock_unlock();
    test_vault_wrong_pin();
    test_vault_encrypt_decrypt_roundtrip();

    TEST_SUITE("eWiFi Pre-Connect Validation (6 Red Flags)");
    test_validation_wep_flag();
    test_validation_evil_twin_flag();
    test_validation_wpa3_passes();

    TEST_EXIT();
}
