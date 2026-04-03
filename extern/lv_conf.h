#ifndef LV_CONF_H
#define LV_CONF_H

#define LV_COLOR_DEPTH          16
#define LV_COLOR_16_SWAP        0

#define LV_MEM_CUSTOM           0
#define LV_MEM_SIZE             (64U * 1024U)

#define LV_DPI_DEF              130

#define LV_USE_LOG              1
#define LV_LOG_LEVEL            LV_LOG_LEVEL_WARN
#define LV_LOG_PRINTF           1

#define LV_TICK_CUSTOM          1
#define LV_TICK_CUSTOM_INCLUDE  <stdint.h>
extern uint32_t eapps_tick_get_ms(void);
#define LV_TICK_CUSTOM_SYS_TIME_EXPR (eapps_tick_get_ms())

#define LV_USE_ASSERT_NULL          1
#define LV_USE_ASSERT_MALLOC        1
#define LV_USE_ASSERT_STYLE         0
#define LV_USE_ASSERT_MEM_INTEGRITY 0
#define LV_USE_ASSERT_OBJ           0

#define LV_FONT_MONTSERRAT_14   1
#define LV_FONT_MONTSERRAT_16   1
#define LV_FONT_MONTSERRAT_20   1
#define LV_FONT_MONTSERRAT_24   1
#define LV_FONT_MONTSERRAT_28   1
#define LV_FONT_DEFAULT         &lv_font_montserrat_16

#define LV_USE_BTNMATRIX        1
#define LV_USE_TEXTAREA         1
#define LV_USE_DROPDOWN         1
#define LV_USE_TABVIEW          1
#define LV_USE_LIST             1
#define LV_USE_SLIDER           1
#define LV_USE_SWITCH           1
#define LV_USE_ARC              1
#define LV_USE_BAR              1
#define LV_USE_CANVAS           1
#define LV_USE_COLORWHEEL       1
#define LV_USE_CHECKBOX         1
#define LV_USE_KEYBOARD         1
#define LV_USE_LABEL            1
#define LV_USE_LINE             1
#define LV_USE_ROLLER           1
#define LV_USE_TABLE            1
#define LV_USE_BTN              1
#define LV_USE_IMG              1
#define LV_USE_LED              1
#define LV_USE_SPAN             1
#define LV_USE_METER            1
#define LV_USE_CHART            1
#define LV_USE_CALENDAR         1
#define LV_USE_SPINBOX          1
#define LV_USE_MSGBOX           1
#define LV_USE_WIN              1
#define LV_USE_TILEVIEW         1

#define LV_USE_ANIM             1
#define LV_USE_SHADOW           1
#define LV_USE_BLEND_MODES      1
#define LV_USE_OPA_SCALE        1
#define LV_USE_GROUP            1
#define LV_USE_GPU_STM32_DMA2D  0
#define LV_USE_FILESYSTEM       0

#endif /* LV_CONF_H */
