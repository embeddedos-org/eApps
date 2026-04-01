// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <math.h>
#include "../core/ui/include/eapps/game_engine.h"

#define EAPPS_ASSERT(cond, msg) do { \
    if (!(cond)) { fprintf(stderr, "FAIL: %s (%s:%d)\n", msg, __FILE__, __LINE__); failures++; } \
    else { passes++; } \
} while(0)

static int passes = 0, failures = 0;

static void test_vec2(void) {
    eapps_vec2_t a = {3, 4};
    eapps_vec2_t b = {1, 2};

    eapps_vec2_t sum = eapps_vec2_add(a, b);
    EAPPS_ASSERT(sum.x == 4.0f && sum.y == 6.0f, "vec2 add");

    eapps_vec2_t diff = eapps_vec2_sub(a, b);
    EAPPS_ASSERT(diff.x == 2.0f && diff.y == 2.0f, "vec2 sub");

    eapps_vec2_t scaled = eapps_vec2_mul(a, 2.0f);
    EAPPS_ASSERT(scaled.x == 6.0f && scaled.y == 8.0f, "vec2 mul");

    float len = eapps_vec2_len(a);
    EAPPS_ASSERT(fabsf(len - 5.0f) < 0.001f, "vec2 len (3,4)=5");

    float dot = eapps_vec2_dot(a, b);
    EAPPS_ASSERT(dot == 11.0f, "vec2 dot");

    eapps_vec2_t norm = eapps_vec2_normalize(a);
    EAPPS_ASSERT(fabsf(eapps_vec2_len(norm) - 1.0f) < 0.001f, "vec2 normalize");

    eapps_vec2_t zero = {0, 0};
    eapps_vec2_t nz = eapps_vec2_normalize(zero);
    EAPPS_ASSERT(nz.x == 0.0f && nz.y == 0.0f, "normalize zero");
}

static void test_aabb(void) {
    eapps_game_obj_t a = { .pos={0,0}, .size={10,10}, .active=true };
    eapps_game_obj_t b = { .pos={5,5}, .size={10,10}, .active=true };
    eapps_game_obj_t c = { .pos={20,20}, .size={5,5}, .active=true };

    EAPPS_ASSERT(eapps_aabb_overlap(&a, &b) == true, "overlap ab");
    EAPPS_ASSERT(eapps_aabb_overlap(&a, &c) == false, "no overlap ac");

    eapps_game_obj_t d = { .pos={5,5}, .size={10,10}, .active=false };
    EAPPS_ASSERT(eapps_aabb_overlap(&a, &d) == false, "inactive no overlap");
}

static void test_game_lifecycle(void) {
    eapps_game_t *g = eapps_game_create(800, 480);
    EAPPS_ASSERT(g != NULL, "game create");
    EAPPS_ASSERT(g->width == 800 && g->height == 480, "game dimensions");

    eapps_game_obj_t *obj = eapps_game_add_obj(g);
    EAPPS_ASSERT(obj != NULL && obj->active, "add obj");
    EAPPS_ASSERT(g->object_count == 1, "obj count");

    eapps_game_start(g);
    EAPPS_ASSERT(g->running && !g->paused, "started");

    eapps_game_pause(g);
    EAPPS_ASSERT(g->paused, "paused");

    eapps_game_destroy(g);
}

static void test_physics(void) {
    eapps_game_t *g = eapps_game_create(100, 100);
    g->physics.gravity = 10.0f;
    eapps_game_obj_t *obj = eapps_game_add_obj(g);
    obj->pos = (eapps_vec2_t){50, 0};
    obj->vel = (eapps_vec2_t){0, 0};

    eapps_physics_step(g, 1.0f);
    EAPPS_ASSERT(obj->vel.y == 10.0f, "gravity applied");
    EAPPS_ASSERT(obj->pos.y == 10.0f, "position updated");

    eapps_game_destroy(g);
}

int main(void) {
    test_vec2();
    test_aabb();
    test_game_lifecycle();
    test_physics();
    printf("test_game_engine: %d passed, %d failed\n", passes, failures);
    return failures > 0 ? 1 : 0;
}
