// SPDX-License-Identifier: MIT
#include "eapps/game_engine.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

eapps_vec2_t eapps_vec2_add(eapps_vec2_t a, eapps_vec2_t b) { return (eapps_vec2_t){a.x + b.x, a.y + b.y}; }
eapps_vec2_t eapps_vec2_sub(eapps_vec2_t a, eapps_vec2_t b) { return (eapps_vec2_t){a.x - b.x, a.y - b.y}; }
eapps_vec2_t eapps_vec2_mul(eapps_vec2_t v, float s) { return (eapps_vec2_t){v.x * s, v.y * s}; }
float        eapps_vec2_len(eapps_vec2_t v) { return sqrtf(v.x * v.x + v.y * v.y); }
float        eapps_vec2_dot(eapps_vec2_t a, eapps_vec2_t b) { return a.x * b.x + a.y * b.y; }

eapps_vec2_t eapps_vec2_normalize(eapps_vec2_t v) {
    float l = eapps_vec2_len(v);
    if (l < 0.0001f) return (eapps_vec2_t){0, 0};
    return (eapps_vec2_t){v.x / l, v.y / l};
}

eapps_game_t *eapps_game_create(int w, int h) {
    eapps_game_t *g = (eapps_game_t *)calloc(1, sizeof(eapps_game_t));
    if (!g) return NULL;
    g->width = w;
    g->height = h;
    g->physics.gravity = 0;
    g->physics.friction = 0;
    g->physics.bounce = 0.5f;
    return g;
}

void eapps_game_destroy(eapps_game_t *g) { free(g); }

void eapps_game_start(eapps_game_t *g) {
    if (g) { g->running = true; g->paused = false; }
}

void eapps_game_pause(eapps_game_t *g) {
    if (g) g->paused = !g->paused;
}

eapps_game_obj_t *eapps_game_add_obj(eapps_game_t *g) {
    if (!g || g->object_count >= EAPPS_GAME_MAX_OBJECTS) return NULL;
    eapps_game_obj_t *obj = &g->objects[g->object_count++];
    memset(obj, 0, sizeof(*obj));
    obj->active = true;
    return obj;
}

void eapps_physics_step(eapps_game_t *g, float dt) {
    if (!g) return;
    for (int i = 0; i < g->object_count; i++) {
        eapps_game_obj_t *o = &g->objects[i];
        if (!o->active) continue;
        o->vel.y += g->physics.gravity * dt;
        o->vel.x *= (1.0f - g->physics.friction * dt);
        o->pos.x += o->vel.x * dt;
        o->pos.y += o->vel.y * dt;
    }
}

void eapps_game_tick(eapps_game_t *g, float dt) {
    if (!g || !g->running || g->paused) return;
    g->elapsed += dt;
    if (g->on_update) g->on_update(g, dt);
}

bool eapps_aabb_overlap(const eapps_game_obj_t *a, const eapps_game_obj_t *b) {
    if (!a || !b || !a->active || !b->active) return false;
    return a->pos.x < b->pos.x + b->size.x &&
           a->pos.x + a->size.x > b->pos.x &&
           a->pos.y < b->pos.y + b->size.y &&
           a->pos.y + a->size.y > b->pos.y;
}

void eapps_draw_rect(int x, int y, int w, int h, uint32_t color) { (void)x; (void)y; (void)w; (void)h; (void)color; }
void eapps_draw_circle(int cx, int cy, int r, uint32_t color) { (void)cx; (void)cy; (void)r; (void)color; }
void eapps_draw_line(int x1, int y1, int x2, int y2, uint32_t color) { (void)x1; (void)y1; (void)x2; (void)y2; (void)color; }
void eapps_draw_text(int x, int y, const char *text, uint32_t color) { (void)x; (void)y; (void)text; (void)color; }
