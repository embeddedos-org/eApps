// SPDX-License-Identifier: MIT
// eTrack — Package & Logistics Tracking (Mock Data)
#include "etrack.h"
#include "eapps/theme.h"
#include "eapps/widgets.h"
#include "eapps/date_utils.h"
#include "lvgl.h"
#include <time.h>
#include <stdio.h>
#include <string.h>

#define MAX_ITEMS 20
#define MAX_S 32
#define MAX_L 64

static lv_color_t hx(uint32_t h){return lv_color_make((h>>16)&0xFF,(h>>8)&0xFF,h&0xFF);}
typedef enum{S_PEND,S_IN,S_OUT,S_DELV,S_FAIL}st_t;
typedef enum{C_FEDEX,C_UPS,C_DHL,C_AMZ,C_OTHER}car_t;
typedef enum{T_PKG,T_FLT,T_CASE}typ_t;
typedef struct{char st[MAX_S];char loc[MAX_S];char ex[MAX_L];time_t ts;}evt_t;
typedef struct{char num[MAX_S];char lbl[MAX_S];car_t car;typ_t typ;st_t st;char stx[MAX_L];time_t ct;bool act;evt_t ev[10];int evc;}item_t;

static lv_obj_t*s_root=NULL;static lv_obj_t*s_vw=NULL;static item_t s_items[MAX_ITEMS];static int s_cnt=0;
static lv_obj_t*s_nta=NULL;static lv_obj_t*s_lta=NULL;static lv_obj_t*s_dlbl=NULL;static car_t s_ac=C_OTHER;static typ_t s_at=T_PKG;

static const char*cn(car_t c){switch(c){case C_FEDEX:return "FedEx";case C_UPS:return "UPS";case C_DHL:return "DHL";case C_AMZ:return "Amazon";default:return "Other";}}
static const char*ci(car_t c){switch(c){case C_FEDEX:return LV_SYMBOL_TRASH;case C_UPS:return LV_SYMBOL_HOME;case C_DHL:return LV_SYMBOL_CHARGE;case C_AMZ:return LV_SYMBOL_SHOPPING_CART;default:return LV_SYMBOL_GPS;}}
static const char*se(st_t s){switch(s){case S_PEND:return "Pending";case S_IN:return "In Transit";case S_OUT:return "Out for Delivery";case S_DELV:return "Delivered";default:return "Failed";}}
static const char*sl(st_t s){switch(s){case S_PEND:return "🕓";case S_IN:return "🚚";case S_OUT:return "🏠";case S_DELV:return "✅";default:return "❌";}}
static uint32_t sc(st_t s){switch(s){case S_PEND:return 0xFFB300;case S_IN:return 0x1E88E5;case S_OUT:return 0x8E24AA;case S_DELV:return 0x43A047;default:return 0xE53935;}}

static car_t det(const char*n,typ_t*t){*t=T_PKG;if(strstr(n,"1Z"))return C_UPS;if(strlen(n)==12)return C_FEDEX;if(strlen(n)==10)return C_DHL;if(strstr(n,"TBA"))return C_AMZ;return C_OTHER;}
static void clr(void){if(s_vw){lv_obj_del(s_vw);s_vw=NULL;}s_nta=NULL;s_lta=NULL;s_dlbl=NULL;}
static void save(void){}
static void load(void){if(s_cnt>0)return;s_cnt=2;
    strcpy(s_items[0].num,"1Z999AA10123456784");strcpy(s_items[0].lbl,"eOffice Pro Laptop");s_items[0].car=C_UPS;s_items[0].st=S_OUT;strcpy(s_items[0].stx,"Estimated 2:00 PM today");s_items[0].act=true;s_items[0].evc=1;strcpy(s_items[0].ev[0].st,"Out for Delivery");strcpy(s_items[0].ev[0].loc,"San Francisco, CA");s_items[0].ev[0].ts=time(NULL)-3600;
    strcpy(s_items[1].num,"456789012345");strcpy(s_items[1].lbl,"EoS Dev Kit");s_items[1].car=C_FEDEX;s_items[1].st=S_IN;strcpy(s_items[1].stx,"Departed Memphis, TN");s_items[1].act=true;s_items[1].evc=0;}

static void show_list(void);static void show_detail(int idx);static void show_add(void);
static void on_ac(lv_event_t*e){(void)e;show_add();}
static void on_ic(lv_event_t*e){show_detail((int)(intptr_t)lv_event_get_user_data(e));}

static void show_list(void){clr();const eapps_palette_t*p=eapps_theme_get_palette();
    s_vw=lv_obj_create(s_root);lv_obj_set_size(s_vw,LV_PCT(100),LV_PCT(100));lv_obj_set_style_bg_opa(s_vw,LV_OPA_TRANSP,0);
    lv_obj_set_style_border_width(s_vw,0,0);lv_obj_set_style_pad_all(s_vw,8,0);lv_obj_set_flex_flow(s_vw,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(s_vw,8,0);
    lv_obj_t*h=lv_obj_create(s_vw);lv_obj_set_size(h,LV_PCT(100),48);lv_obj_set_style_bg_opa(h,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(h,0,0);
    lv_obj_set_flex_flow(h,LV_FLEX_FLOW_ROW);lv_obj_set_flex_align(h,LV_FLEX_ALIGN_SPACE_BETWEEN,LV_FLEX_ALIGN_CENTER,LV_FLEX_ALIGN_CENTER);
    lv_obj_t*t=lv_label_create(h);lv_label_set_text(t,LV_SYMBOL_GPS " eTrack");
    lv_obj_set_style_text_font(t,&lv_font_montserrat_14,0);lv_obj_set_style_text_color(t,hx(p->on_surface),0);
    lv_obj_t*ab=lv_btn_create(h);lv_obj_set_size(ab,LV_SIZE_CONTENT,32);lv_obj_set_style_bg_color(ab,hx(p->primary),0);
    lv_obj_set_style_radius(ab,16,0);lv_obj_t*al=lv_label_create(ab);lv_label_set_text(al,LV_SYMBOL_PLUS " Track");
    lv_obj_set_style_text_color(al,hx(p->on_primary),0);lv_obj_center(al);
    lv_obj_add_event_cb(ab,on_ac,LV_EVENT_CLICKED,NULL);
    if(s_cnt==0){lv_obj_t*em=lv_label_create(s_vw);lv_label_set_text(em,LV_SYMBOL_GPS "\n\nNo tracking items\nTap + Track to add");
        lv_obj_set_style_text_align(em,LV_TEXT_ALIGN_CENTER,0);lv_obj_set_style_text_color(em,hx(p->border),0);return;}
    for(int i=0;i<s_cnt;i++){item_t*it=&s_items[i];if(!it->act)continue;
        lv_obj_t*c=lv_obj_create(s_vw);lv_obj_set_size(c,LV_PCT(100),LV_SIZE_CONTENT);
        lv_obj_set_style_bg_color(c,hx(p->card),0);lv_obj_set_style_bg_opa(c,LV_OPA_COVER,0);
        lv_obj_set_style_radius(c,12,0);lv_obj_set_style_border_color(c,hx(p->border),0);
        lv_obj_set_style_border_width(c,1,0);lv_obj_set_style_pad_all(c,10,0);
        lv_obj_set_flex_flow(c,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(c,4,0);
        lv_obj_add_event_cb(c,on_ic,LV_EVENT_CLICKED,(void*)(intptr_t)i);
        lv_obj_t*r=lv_obj_create(c);lv_obj_set_size(r,LV_PCT(100),LV_SIZE_CONTENT);
        lv_obj_set_style_bg_opa(r,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(r,0,0);lv_obj_set_style_pad_all(r,0,0);
        lv_obj_set_flex_flow(r,LV_FLEX_FLOW_ROW);lv_obj_set_flex_align(r,LV_FLEX_ALIGN_SPACE_BETWEEN,LV_FLEX_ALIGN_CENTER,LV_FLEX_ALIGN_CENTER);
        char b[128];snprintf(b,128,"%s %s",ci(it->car),it->lbl[0]?it->lbl:cn(it->car));
        lv_obj_t*n=lv_label_create(r);lv_label_set_text(n,b);lv_obj_set_style_text_font(n,&lv_font_montserrat_12,0);lv_obj_set_style_text_color(n,hx(p->on_surface),0);
        snprintf(b,128,"%s %s",se(it->st),sl(it->st));
        lv_obj_t*s2=lv_label_create(r);lv_label_set_text(s2,b);lv_obj_set_style_text_color(s2,hx(sc(it->st)),0);lv_obj_set_style_text_font(s2,&lv_font_montserrat_12,0);
        lv_obj_t*n2=lv_label_create(c);lv_label_set_text(n2,it->num);lv_obj_set_style_text_color(n2,hx(p->border),0);lv_obj_set_style_text_font(n2,&lv_font_montserrat_12,0);
    }
}
static void on_bk(lv_event_t*e){(void)e;show_list();}
static void show_detail(int idx){clr();const eapps_palette_t*p=eapps_theme_get_palette();item_t*it=&s_items[idx];
    s_vw=lv_obj_create(s_root);lv_obj_set_size(s_vw,LV_PCT(100),LV_PCT(100));lv_obj_set_style_bg_opa(s_vw,LV_OPA_TRANSP,0);
    lv_obj_set_style_pad_all(s_vw,8,0);lv_obj_set_flex_flow(s_vw,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(s_vw,8,0);
    lv_obj_t*bb=lv_btn_create(s_vw);lv_obj_set_size(bb,LV_SIZE_CONTENT,30);lv_obj_t*bl=lv_label_create(bb);lv_label_set_text(bl,LV_SYMBOL_LEFT " Back");lv_obj_add_event_cb(bb,on_bk,LV_EVENT_CLICKED,NULL);
    lv_obj_t*hd=lv_obj_create(s_vw);lv_obj_set_size(hd,LV_PCT(100),LV_SIZE_CONTENT);lv_obj_set_style_bg_color(hd,hx(p->card),0);
    lv_obj_set_style_border_width(hd,1,0);lv_obj_set_style_pad_all(12,0);lv_obj_set_flex_flow(hd,LV_FLEX_FLOW_COLUMN);
    lv_obj_t*cl=lv_label_create(hd);lv_label_set_text(cl,cn(it->car));
}
static void on_sv(lv_event_t*e){(void)e;show_list();}
static void show_add(void){clr();s_vw=lv_obj_create(s_root);lv_obj_t*sv=lv_btn_create(s_vw);lv_obj_add_event_cb(sv,on_sv,LV_EVENT_CLICKED,NULL);}
static bool etrack_init(lv_obj_t*par){s_root=par;load();show_list();return true;}
static void etrack_deinit(void){s_root=NULL;clr();}
const eapps_app_info_t etrack_info={.id="etrack",.name="eTrack",.icon=LV_SYMBOL_GPS,.category=EAPPS_CAT_CONNECTIVITY,.version="1.0.0"};
const eapps_app_lifecycle_t etrack_lifecycle={.init=etrack_init,.deinit=etrack_deinit};
