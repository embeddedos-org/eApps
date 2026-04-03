/* LVGL configuration for eBrowser */
#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/* Color depth: 16 (RGB565) for embedded, 32 (ARGB8888) for desktop */
#define LV_COLOR_DEPTH 16

/* Memory */
#define LV_MEM_CUSTOM 0
#define LV_MEM_SIZE (256 * 1024)

/* HAL */
#define LV_TICK_CUSTOM 0

/* Display */
#define LV_DPI_DEF 130

/* Draw */
#define LV_USE_DRAW_SW 1
#define LV_USE_DRAW_SW_ASM LV_DRAW_SW_ASM_NONE
#define LV_DRAW_SW_ASM_NONE 0
#define LV_USE_DRAW_ARM2D 0
#define LV_USE_NATIVE_HELIUM_ASM 0

/* Logging */
#define LV_USE_LOG 0

/* Asserts */
#define LV_USE_ASSERT_NULL          1
#define LV_USE_ASSERT_MALLOC        1
#define LV_USE_ASSERT_STYLE         0
#define LV_USE_ASSERT_MEM_INTEGRITY 0
#define LV_USE_ASSERT_OBJ           0

/* Fonts — enable all sizes used by eBrowser */
#define LV_FONT_MONTSERRAT_8   0
#define LV_FONT_MONTSERRAT_10  0
#define LV_FONT_MONTSERRAT_12  1
#define LV_FONT_MONTSERRAT_14  1
#define LV_FONT_MONTSERRAT_16  1
#define LV_FONT_MONTSERRAT_18  0
#define LV_FONT_MONTSERRAT_20  1
#define LV_FONT_MONTSERRAT_22  0
#define LV_FONT_MONTSERRAT_24  0
#define LV_FONT_MONTSERRAT_26  0
#define LV_FONT_MONTSERRAT_28  1
#define LV_FONT_MONTSERRAT_30  0
#define LV_FONT_MONTSERRAT_32  0
#define LV_FONT_MONTSERRAT_34  0
#define LV_FONT_MONTSERRAT_36  0
#define LV_FONT_MONTSERRAT_38  0
#define LV_FONT_MONTSERRAT_40  0
#define LV_FONT_MONTSERRAT_42  0
#define LV_FONT_MONTSERRAT_44  0
#define LV_FONT_MONTSERRAT_46  0
#define LV_FONT_MONTSERRAT_48  0

#define LV_FONT_DEFAULT &lv_font_montserrat_14

/* Text */
#define LV_TXT_ENC LV_TXT_ENC_UTF8

/* Widgets — enable all core widgets */
#define LV_USE_ARC        1
#define LV_USE_BAR        1
#define LV_USE_BUTTON     1
#define LV_USE_BUTTONMATRIX 1
#define LV_USE_CANVAS     1
#define LV_USE_CHECKBOX   1
#define LV_USE_DROPDOWN   1
#define LV_USE_IMAGE      1
#define LV_USE_LABEL      1
#define LV_USE_LINE       1
#define LV_USE_ROLLER     1
#define LV_USE_SCALE      1
#define LV_USE_SLIDER     1
#define LV_USE_SWITCH     1
#define LV_USE_TABLE      1
#define LV_USE_TEXTAREA   1

/* Extra widgets */
#define LV_USE_ANIMIMG    0
#define LV_USE_CALENDAR   0
#define LV_USE_CHART      0
#define LV_USE_COLORWHEEL 0
#define LV_USE_IMGBTN     0
#define LV_USE_KEYBOARD   1
#define LV_USE_LED        0
#define LV_USE_LIST       1
#define LV_USE_MENU       0
#define LV_USE_MSGBOX     1
#define LV_USE_SPAN       1
#define LV_USE_SPINBOX    0
#define LV_USE_SPINNER    1
#define LV_USE_TABVIEW    1
#define LV_USE_TILEVIEW   0
#define LV_USE_WIN        0

/* Layouts */
#define LV_USE_FLEX 1
#define LV_USE_GRID 1

/* SDL2 display driver */
#define LV_USE_SDL 0

/* File system */
#define LV_USE_FS_STDIO 0

/* Others */
#define LV_USE_SNAPSHOT      0
#define LV_USE_SYSMON        0
#define LV_USE_PROFILER      0
#define LV_USE_OBJ_ID        0
#define LV_USE_OBJ_PROPERTY  0

#define LV_BUILD_EXAMPLES 0

#endif /* LV_CONF_H */
