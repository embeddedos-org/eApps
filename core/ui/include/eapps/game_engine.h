// SPDX-License-Identifier: MIT
#ifndef EAPPS_GAME_ENGINE_H
#define EAPPS_GAME_ENGINE_H

#include "eapps/types.h"
#include <stdbool.h>

#define EAPPS_GAME_MAX_OBJECTS 128

typedef struct {
    float x, y;
} eapps_vec2_t;

eapps_vec2_t eapps_vec2_add(eapps_vec2_t a, eapps_vec2_t b);
eapps_vec2_t eapps_vec2_sub(eapps_vec2_t a, eapps_vec2_t b);
eapps_vec2_t eapps_vec2_mul(eapps_vec2_t v, float s);
float        eapps_vec2_len(eapps_vec2_t v);
eapps_vec2_t eapps_vec2_normalize(eapps_vec2_t v);
float        eapps_vec2_dot(eapps_vec2_t a, eapps_vec2_t b);

typedef struct {
    eapps_vec2_t pos;
    eapps_vec2_t vel;
    eapps_vec2_t size;
    bool         active;
    int          type;
    void        *user_data;
} eapps_game_obj_t;

typedef struct {
    float gravity;
    float friction;
    float bounce;
} eapps_physics_config_t;

typedef struct eapps_game eapps_game_t;

typedef void (*eapps_game_update_fn)(eapps_game_t *g, float dt);
typedef void (*eapps_game_draw_fn)(eapps_game_t *g);
typedef void (*eapps_game_input_fn)(eapps_game_t *g, int key, bool pressed);

struct eapps_game {
    eapps_game_obj_t     objects[EAPPS_GAME_MAX_OBJECTS];
    int                  object_count;
    eapps_physics_config_t physics;
    bool                 running;
    bool                 paused;
    float                elapsed;
    int                  score;
    int                  width;
    int                  height;
    eapps_game_update_fn on_update;
    eapps_game_draw_fn   on_draw;
    eapps_game_input_fn  on_input;
    void                *user_data;
};

eapps_game_t *eapps_game_create(int w, int h);
void          eapps_game_destroy(eapps_game_t *g);
void          eapps_game_start(eapps_game_t *g);
void          eapps_game_pause(eapps_game_t *g);
void          eapps_game_tick(eapps_game_t *g, float dt);
eapps_game_obj_t *eapps_game_add_obj(eapps_game_t *g);
void          eapps_physics_step(eapps_game_t *g, float dt);
bool          eapps_aabb_overlap(const eapps_game_obj_t *a, const eapps_game_obj_t *b);

void eapps_draw_rect(int x, int y, int w, int h, uint32_t color);
void eapps_draw_circle(int cx, int cy, int r, uint32_t color);
void eapps_draw_line(int x1, int y1, int x2, int y2, uint32_t color);
void eapps_draw_text(int x, int y, const char *text, uint32_t color);

#endif /* EAPPS_GAME_ENGINE_H */
