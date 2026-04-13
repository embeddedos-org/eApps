// SPDX-License-Identifier: MIT
#include "etrack.h"
#include "eapps/widgets.h"
#include "eapps/theme.h"
#include "eapps/prefs.h"
#include "eapps/string_utils.h"
#include "eapps/date_utils.h"
#include "lvgl.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <ctype.h>

#define MAX_ITEMS  50
#define MAX_EVENTS 10
#define MAX_S      64
#define MAX_L      128

typedef enum { C_USPS,C_UPS,C_FEDEX,C_DHL,C_USCIS,C_FLIGHT,C_OTHER } carrier_t;
typedef enum { T_PKG,T_FLT,T_CASE } ttype_t;
typedef enum { S_UNK,S_PEND,S_PRE,S_TRANS,S_OFD,S_DELIV,S_FAIL,S_DELAY,S_RET } tstat_t;

typedef struct { char st[MAX_L]; char ex[MAX_L]; char loc[MAX_S]; time_t ts; } evt_t;
typedef struct {
    char num[MAX_S]; char lbl[MAX_S]; carrier_t car; ttype_t typ;
    tstat_t st; char stx[MAX_L]; evt_t ev[MAX_EVENTS]; int evc;
    time_t ct; bool act;
} item_t;

static item_t s_items[MAX_ITEMS];
static int s_cnt=0;
static eapps_prefs_t *s_p=NULL;
static lv_obj_t *s_root=NULL, *s_vw=NULL;
static lv_obj_t *s_nta=NULL, *s_lta=NULL, *s_dlbl=NULL;
static carrier_t s_ac=C_OTHER; static ttype_t s_at=T_PKG;

static lv_color_t hx(uint32_t h){return lv_color_make((h>>16)&0xFF,(h>>8)&0xFF,h&0xFF);}
static const char*cn(carrier_t c){const char*n[]={"USPS","UPS","FedEx","DHL","USCIS","Flight","Other"};return n[c];}
static const char*ci(carrier_t c){const char*i[]={LV_SYMBOL_ENVELOPE,LV_SYMBOL_UPLOAD,LV_SYMBOL_CHARGE,LV_SYMBOL_SHUFFLE,LV_SYMBOL_FILE,LV_SYMBOL_GPS,LV_SYMBOL_LIST};return i[c];}
static const char*sl(tstat_t s){const char*l[]={"Unknown","Pending","Pre-Transit","In Transit","Out for Delivery","Delivered","Failed","Delayed","Returned"};return l[s];}
static const char*se(tstat_t s){const char*e[]={LV_SYMBOL_DUMMY,LV_SYMBOL_REFRESH,LV_SYMBOL_REFRESH,LV_SYMBOL_RIGHT,LV_SYMBOL_DOWNLOAD,LV_SYMBOL_OK,LV_SYMBOL_CLOSE,LV_SYMBOL_WARNING,LV_SYMBOL_LEFT};return e[s];}
static uint32_t sc(tstat_t s){switch(s){case S_DELIV:return 0x4CAF50;case S_TRANS:case S_OFD:return 0x2962FF;case S_PEND:case S_PRE:return 0xFF9800;case S_FAIL:case S_RET:return 0xF44336;case S_DELAY:return 0xFF5722;default:return 0x9E9E9E;}}

/* Carrier detection */
static bool ad(const char*s,int n){for(int i=0;i<n;i++)if(!isdigit((unsigned char)s[i]))return false;return true;}
static carrier_t det(const char*num,ttype_t*t){
    char u[MAX_S];size_t l=strlen(num);if(l>=MAX_S)l=MAX_S-1;
    for(size_t i=0;i<l;i++)u[i]=toupper((unsigned char)num[i]);u[l]=0;*t=T_PKG;
    if(l==18&&u[0]=='1'&&u[1]=='Z')return C_UPS;
    if(l==13&&isalpha((unsigned char)u[0])&&isalpha((unsigned char)u[1])&&isalpha((unsigned char)u[2])&&ad(u+3,10)){*t=T_CASE;return C_USCIS;}
    if(l>=3&&l<=6&&isalpha((unsigned char)u[0])&&isalpha((unsigned char)u[1])&&ad(u+2,(int)(l-2))){*t=T_FLT;return C_FLIGHT;}
    if((l==12||l==15)&&ad(u,(int)l))return C_FEDEX;
    if(l>=20&&l<=22&&(u[0]=='9'&&(u[1]=='6'||u[1]=='8'))&&ad(u,(int)l))return C_FEDEX;
    if(l>=20&&l<=22&&ad(u,(int)l))return C_USPS;
    if(l>=10&&u[0]=='J'&&u[1]=='J'&&u[2]=='D')return C_DHL;
    if(l==10&&ad(u,10))return C_DHL;
    return C_OTHER;
}

/* Status engine */
typedef struct{const char*k;const char*v;tstat_t s;}sm_t;
static const sm_t SM[]={
    {"DELIVERED","Package delivered",S_DELIV},{"OUT FOR DELIVERY","Arriving today",S_OFD},
    {"IN TRANSIT","On its way",S_TRANS},{"ARRIVED AT FACILITY","At processing facility",S_TRANS},
    {"ARRIVAL AT UNIT","At local post office",S_TRANS},{"DEPARTED FACILITY","Left facility",S_TRANS},
    {"SHIPPING LABEL CREATED","Label created, awaiting pickup",S_PRE},{"PRE-SHIPMENT","Not yet shipped",S_PRE},
    {"DELIVERY ATTEMPTED","Attempted, no one home",S_DELAY},{"DELIVERY EXCEPTION","Delivery problem",S_DELAY},
    {"RETURN TO SENDER","Returning to sender",S_RET},{"PICKED UP","Picked up by carrier",S_TRANS},
    {"DESTINATION SCAN","Scanned near you",S_TRANS},{"CUSTOMS CLEARANCE","Going through customs",S_TRANS},
    {"CASE WAS RECEIVED","USCIS received case",S_PEND},{"CASE WAS APPROVED","Case approved",S_DELIV},
    {"CASE WAS DENIED","Case denied",S_FAIL},{"CARD IS BEING PRODUCED","Card being made",S_TRANS},
    {"CARD WAS MAILED","Card mailed to you",S_OFD},{"CARD WAS DELIVERED","Card delivered",S_DELIV},
    {"REQUEST FOR EVIDENCE","USCIS needs documents",S_DELAY},{NULL,NULL,S_UNK}
};
static tstat_t expl(const char*r,char*o,size_t ol){
    char u[MAX_L];eapps_str_truncate(r,u,sizeof(u));eapps_str_to_upper(u);
    for(int i=0;SM[i].k;i++)if(strstr(u,SM[i].k)){snprintf(o,ol,"%s",SM[i].v);return SM[i].s;}
    if(strstr(u,"DELIVER")){snprintf(o,ol,"Delivered");return S_DELIV;}
    if(strstr(u,"TRANSIT")){snprintf(o,ol,"In transit");return S_TRANS;}
    if(strstr(u,"FAIL")||strstr(u,"DENIED")){snprintf(o,ol,"Problem with shipment");return S_FAIL;}
    if(strstr(u,"DELAY")){snprintf(o,ol,"Delayed");return S_DELAY;}
    snprintf(o,ol,"%s",r);return S_UNK;
}

/* Persistence */
static void save(void){
    if(!s_p)return;eapps_prefs_set_int(s_p,"c",s_cnt);
    for(int i=0;i<s_cnt;i++){char k[32];item_t*it=&s_items[i];
        snprintf(k,32,"i%dn",i);eapps_prefs_set_string(s_p,k,it->num);
        snprintf(k,32,"i%dl",i);eapps_prefs_set_string(s_p,k,it->lbl);
        snprintf(k,32,"i%dc",i);eapps_prefs_set_int(s_p,k,(int)it->car);
        snprintf(k,32,"i%dt",i);eapps_prefs_set_int(s_p,k,(int)it->typ);
        snprintf(k,32,"i%ds",i);eapps_prefs_set_int(s_p,k,(int)it->st);
        snprintf(k,32,"i%dx",i);eapps_prefs_set_string(s_p,k,it->stx);
        snprintf(k,32,"i%dT",i);eapps_prefs_set_int(s_p,k,(int)it->ct);
        snprintf(k,32,"i%de",i);eapps_prefs_set_int(s_p,k,it->evc);
        for(int j=0;j<it->evc&&j<MAX_EVENTS;j++){
            snprintf(k,32,"i%de%ds",i,j);eapps_prefs_set_string(s_p,k,it->ev[j].st);
            snprintf(k,32,"i%de%dx",i,j);eapps_prefs_set_string(s_p,k,it->ev[j].ex);
            snprintf(k,32,"i%de%dl",i,j);eapps_prefs_set_string(s_p,k,it->ev[j].loc);
            snprintf(k,32,"i%de%dt",i,j);eapps_prefs_set_int(s_p,k,(int)it->ev[j].ts);
    }}eapps_prefs_save(s_p);
}
static void load(void){
    if(!s_p)return;s_cnt=eapps_prefs_get_int(s_p,"c",0);if(s_cnt>MAX_ITEMS)s_cnt=MAX_ITEMS;
    for(int i=0;i<s_cnt;i++){char k[32];item_t*it=&s_items[i];memset(it,0,sizeof(*it));it->act=true;
        snprintf(k,32,"i%dn",i);snprintf(it->num,MAX_S,"%s",eapps_prefs_get_string(s_p,k,""));
        snprintf(k,32,"i%dl",i);snprintf(it->lbl,MAX_S,"%s",eapps_prefs_get_string(s_p,k,""));
        snprintf(k,32,"i%dc",i);it->car=(carrier_t)eapps_prefs_get_int(s_p,k,C_OTHER);
        snprintf(k,32,"i%dt",i);it->typ=(ttype_t)eapps_prefs_get_int(s_p,k,T_PKG);
        snprintf(k,32,"i%ds",i);it->st=(tstat_t)eapps_prefs_get_int(s_p,k,S_UNK);
        snprintf(k,32,"i%dx",i);snprintf(it->stx,MAX_L,"%s",eapps_prefs_get_string(s_p,k,""));
        snprintf(k,32,"i%dT",i);it->ct=(time_t)eapps_prefs_get_int(s_p,k,0);
        snprintf(k,32,"i%de",i);it->evc=eapps_prefs_get_int(s_p,k,0);if(it->evc>MAX_EVENTS)it->evc=MAX_EVENTS;
        for(int j=0;j<it->evc;j++){
            snprintf(k,32,"i%de%ds",i,j);snprintf(it->ev[j].st,MAX_L,"%s",eapps_prefs_get_string(s_p,k,""));
            snprintf(k,32,"i%de%dx",i,j);snprintf(it->ev[j].ex,MAX_L,"%s",eapps_prefs_get_string(s_p,k,""));
            snprintf(k,32,"i%de%dl",i,j);snprintf(it->ev[j].loc,MAX_S,"%s",eapps_prefs_get_string(s_p,k,""));
            snprintf(k,32,"i%de%dt",i,j);it->ev[j].ts=(time_t)eapps_prefs_get_int(s_p,k,0);
    }}
}

static void show_list(void);
static void show_detail(int);
static void show_add(void);
static void clr(void){if(s_vw){lv_obj_delete(s_vw);s_vw=NULL;}}

/* ---- LIST VIEW ---- */
static void on_ic(lv_event_t*e){show_detail((int)(intptr_t)lv_event_get_user_data(e));}
static void on_ac(lv_event_t*e){(void)e;show_add();}
static void show_list(void){
    clr();const eapps_palette_t*p=eapps_theme_get_palette();
    s_vw=lv_obj_create(s_root);lv_obj_set_size(s_vw,LV_PCT(100),LV_PCT(100));
    lv_obj_set_style_bg_opa(s_vw,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(s_vw,0,0);
    lv_obj_set_style_pad_all(s_vw,8,0);lv_obj_set_flex_flow(s_vw,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(s_vw,6,0);
    lv_obj_t*h=lv_obj_create(s_vw);lv_obj_set_size(h,LV_PCT(100),40);
    lv_obj_set_style_bg_opa(h,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(h,0,0);lv_obj_set_style_pad_all(h,0,0);
    lv_obj_set_flex_flow(h,LV_FLEX_FLOW_ROW);lv_obj_set_flex_align(h,LV_FLEX_ALIGN_SPACE_BETWEEN,LV_FLEX_ALIGN_CENTER,LV_FLEX_ALIGN_CENTER);
    lv_obj_t*t=lv_label_create(h);lv_label_set_text(t,LV_SYMBOL_GPS " eTrack");
    lv_obj_set_style_text_font(t,&lv_font_montserrat_28,0);lv_obj_set_style_text_color(t,hx(p->on_surface),0);
    lv_obj_t*ab=lv_button_create(h);lv_obj_set_size(ab,LV_SIZE_CONTENT,32);lv_obj_set_style_bg_color(ab,hx(p->primary),0);
    lv_obj_set_style_radius(ab,16,0);lv_obj_set_style_pad_hor(ab,14,0);
    lv_obj_t*al=lv_label_create(ab);lv_label_set_text(al,LV_SYMBOL_PLUS " Track");
    lv_obj_set_style_text_color(al,hx(p->on_primary),0);lv_obj_center(al);
    lv_obj_add_event_cb(ab,on_ac,LV_EVENT_CLICKED,NULL);
    if(s_cnt==0){lv_obj_t*em=lv_label_create(s_vw);lv_label_set_text(em,LV_SYMBOL_GPS "\n\nNo tracking items\nTap + Track to add");
        lv_obj_set_style_text_align(em,LV_TEXT_ALIGN_CENTER,0);lv_obj_set_style_text_color(em,hx(p->border),0);
        lv_obj_set_width(em,LV_PCT(100));lv_obj_set_style_pad_top(em,60,0);return;}
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
        lv_obj_t*n=lv_label_create(r);lv_label_set_text(n,b);lv_obj_set_style_text_font(n,&lv_font_montserrat_14,0);lv_obj_set_style_text_color(n,hx(p->on_surface),0);
        snprintf(b,128,"%s %s",se(it->st),sl(it->st));
        lv_obj_t*s2=lv_label_create(r);lv_label_set_text(s2,b);lv_obj_set_style_text_color(s2,hx(sc(it->st)),0);lv_obj_set_style_text_font(s2,&lv_font_montserrat_12,0);
        lv_obj_t*n2=lv_label_create(c);lv_label_set_text(n2,it->num);lv_obj_set_style_text_color(n2,hx(p->border),0);lv_obj_set_style_text_font(n2,&lv_font_montserrat_12,0);
        if(it->stx[0]){lv_obj_t*sx=lv_label_create(c);lv_label_set_text(sx,it->stx);lv_obj_set_style_text_color(sx,hx(p->on_surface),0);lv_obj_set_style_text_font(sx,&lv_font_montserrat_12,0);}
    }
}

/* ---- DETAIL VIEW ---- */
static void on_bk(lv_event_t*e){(void)e;show_list();}
static void on_del(lv_event_t*e){int i=(int)(intptr_t)lv_event_get_user_data(e);
    if(i>=0&&i<s_cnt){for(int j=i;j<s_cnt-1;j++)s_items[j]=s_items[j+1];s_cnt--;save();}show_list();}
static void show_detail(int idx){
    if(idx<0||idx>=s_cnt)return;clr();const eapps_palette_t*p=eapps_theme_get_palette();item_t*it=&s_items[idx];
    s_vw=lv_obj_create(s_root);lv_obj_set_size(s_vw,LV_PCT(100),LV_PCT(100));
    lv_obj_set_style_bg_opa(s_vw,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(s_vw,0,0);
    lv_obj_set_style_pad_all(s_vw,8,0);lv_obj_set_flex_flow(s_vw,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(s_vw,8,0);
    lv_obj_t*bb=lv_button_create(s_vw);lv_obj_set_size(bb,LV_SIZE_CONTENT,30);lv_obj_set_style_bg_opa(bb,LV_OPA_TRANSP,0);lv_obj_set_style_shadow_width(bb,0,0);
    lv_obj_t*bl=lv_label_create(bb);lv_label_set_text(bl,LV_SYMBOL_LEFT " Back");lv_obj_set_style_text_color(bl,hx(p->primary),0);
    lv_obj_add_event_cb(bb,on_bk,LV_EVENT_CLICKED,NULL);
    lv_obj_t*hd=lv_obj_create(s_vw);lv_obj_set_size(hd,LV_PCT(100),LV_SIZE_CONTENT);lv_obj_set_style_bg_color(hd,hx(p->card),0);
    lv_obj_set_style_bg_opa(hd,LV_OPA_COVER,0);lv_obj_set_style_radius(hd,12,0);lv_obj_set_style_border_color(hd,hx(p->border),0);
    lv_obj_set_style_border_width(hd,1,0);lv_obj_set_style_pad_all(hd,12,0);lv_obj_set_flex_flow(hd,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(hd,4,0);
    char b[128];snprintf(b,128,"%s %s",ci(it->car),cn(it->car));
    lv_obj_t*cl=lv_label_create(hd);lv_label_set_text(cl,b);lv_obj_set_style_text_font(cl,&lv_font_montserrat_16,0);lv_obj_set_style_text_color(cl,hx(p->on_surface),0);
    lv_obj_t*nl=lv_label_create(hd);lv_label_set_text(nl,it->num);lv_obj_set_style_text_color(nl,hx(p->border),0);
    if(it->lbl[0]){lv_obj_t*ll=lv_label_create(hd);lv_label_set_text(ll,it->lbl);lv_obj_set_style_text_color(ll,hx(p->on_surface),0);}
    snprintf(b,128,"%s %s",se(it->st),sl(it->st));lv_obj_t*stl=lv_label_create(hd);lv_label_set_text(stl,b);
    lv_obj_set_style_text_color(stl,hx(sc(it->st)),0);lv_obj_set_style_text_font(stl,&lv_font_montserrat_14,0);
    if(it->stx[0]){lv_obj_t*sx=lv_label_create(hd);lv_label_set_text(sx,it->stx);lv_obj_set_style_text_color(sx,hx(p->on_surface),0);}
    lv_obj_t*tlt=lv_label_create(s_vw);lv_label_set_text(tlt,"Tracking Timeline");lv_obj_set_style_text_font(tlt,&lv_font_montserrat_14,0);lv_obj_set_style_text_color(tlt,hx(p->on_surface),0);
    if(it->evc==0){lv_obj_t*ne=lv_label_create(s_vw);lv_label_set_text(ne,"No events yet.\nRefresh for updates.");
        lv_obj_set_style_text_color(ne,hx(p->border),0);lv_obj_set_style_text_align(ne,LV_TEXT_ALIGN_CENTER,0);lv_obj_set_width(ne,LV_PCT(100));}
    else{for(int j=0;j<it->evc;j++){evt_t*ev=&it->ev[j];
        lv_obj_t*er=lv_obj_create(s_vw);lv_obj_set_size(er,LV_PCT(100),LV_SIZE_CONTENT);lv_obj_set_style_bg_opa(er,LV_OPA_TRANSP,0);
        lv_obj_set_style_border_width(er,0,0);lv_obj_set_style_pad_all(er,0,0);lv_obj_set_flex_flow(er,LV_FLEX_FLOW_ROW);lv_obj_set_style_pad_gap(er,8,0);
        lv_obj_t*dot=lv_obj_create(er);lv_obj_set_size(dot,10,10);lv_obj_set_style_radius(dot,5,0);
        lv_obj_set_style_bg_color(dot,hx(j==0?p->primary:p->border),0);lv_obj_set_style_bg_opa(dot,LV_OPA_COVER,0);
        lv_obj_set_style_border_width(dot,0,0);lv_obj_set_style_margin_top(dot,4,0);
        lv_obj_t*ec=lv_obj_create(er);lv_obj_set_flex_grow(ec,1);lv_obj_set_size(ec,LV_PCT(80),LV_SIZE_CONTENT);
        lv_obj_set_style_bg_opa(ec,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(ec,0,0);lv_obj_set_style_pad_all(ec,0,0);lv_obj_set_flex_flow(ec,LV_FLEX_FLOW_COLUMN);
        lv_obj_t*et=lv_label_create(ec);lv_label_set_text(et,ev->ex[0]?ev->ex:ev->st);lv_obj_set_style_text_color(et,hx(p->on_surface),0);
        lv_obj_set_style_text_font(et,j==0?&lv_font_montserrat_14:&lv_font_montserrat_12,0);
        if(ev->loc[0]){snprintf(b,128,LV_SYMBOL_GPS " %s",ev->loc);lv_obj_t*lc=lv_label_create(ec);lv_label_set_text(lc,b);lv_obj_set_style_text_color(lc,hx(p->border),0);lv_obj_set_style_text_font(lc,&lv_font_montserrat_12,0);}
        if(ev->ts>0){char tb[48];eapps_date_format(ev->ts,"%b %d %H:%M",tb,48);lv_obj_t*tl=lv_label_create(ec);lv_label_set_text(tl,tb);lv_obj_set_style_text_color(tl,hx(p->border),0);lv_obj_set_style_text_font(tl,&lv_font_montserrat_12,0);}
    }}
    lv_obj_t*db=lv_button_create(s_vw);lv_obj_set_size(db,LV_PCT(100),36);lv_obj_set_style_bg_color(db,hx(p->error),0);
    lv_obj_set_style_bg_opa(db,LV_OPA_20,0);lv_obj_set_style_radius(db,8,0);
    lv_obj_t*dl=lv_label_create(db);lv_label_set_text(dl,LV_SYMBOL_TRASH " Delete");lv_obj_set_style_text_color(dl,hx(p->error),0);lv_obj_center(dl);
    lv_obj_add_event_cb(db,on_del,LV_EVENT_CLICKED,(void*)(intptr_t)idx);
}

/* ---- ADD VIEW ---- */
static void on_nc(lv_event_t*e){(void)e;const char*t=lv_textarea_get_text(s_nta);
    if(strlen(t)>=4){s_ac=det(t,&s_at);char b[96];const char*tn=s_at==T_FLT?"Flight":s_at==T_CASE?"Case":"Package";
        snprintf(b,96,"Detected: %s %s (%s)",ci(s_ac),cn(s_ac),tn);lv_label_set_text(s_dlbl,b);}
    else lv_label_set_text(s_dlbl,"Enter 4+ chars to auto-detect carrier");}
static void on_sv(lv_event_t*e){(void)e;const char*n=lv_textarea_get_text(s_nta);const char*l=lv_textarea_get_text(s_lta);
    if(!n||strlen(n)<4||s_cnt>=MAX_ITEMS)return;item_t*it=&s_items[s_cnt];memset(it,0,sizeof(*it));
    snprintf(it->num,MAX_S,"%s",n);snprintf(it->lbl,MAX_S,"%s",l?l:"");
    it->car=s_ac;it->typ=s_at;it->st=S_PEND;snprintf(it->stx,MAX_L,"Added — refresh for live updates");
    it->ct=time(NULL);it->act=true;it->evc=0;s_cnt++;save();show_list();}
static void on_ab(lv_event_t*e){(void)e;show_list();}
static void show_add(void){
    clr();const eapps_palette_t*p=eapps_theme_get_palette();s_ac=C_OTHER;s_at=T_PKG;
    s_vw=lv_obj_create(s_root);lv_obj_set_size(s_vw,LV_PCT(100),LV_PCT(100));
    lv_obj_set_style_bg_opa(s_vw,LV_OPA_TRANSP,0);lv_obj_set_style_border_width(s_vw,0,0);
    lv_obj_set_style_pad_all(s_vw,12,0);lv_obj_set_flex_flow(s_vw,LV_FLEX_FLOW_COLUMN);lv_obj_set_style_pad_gap(s_vw,10,0);
    lv_obj_t*bb=lv_button_create(s_vw);lv_obj_set_size(bb,LV_SIZE_CONTENT,30);lv_obj_set_style_bg_opa(bb,LV_OPA_TRANSP,0);lv_obj_set_style_shadow_width(bb,0,0);
    lv_obj_t*bbl=lv_label_create(bb);lv_label_set_text(bbl,LV_SYMBOL_LEFT " Back");lv_obj_set_style_text_color(bbl,hx(p->primary),0);
    lv_obj_add_event_cb(bb,on_ab,LV_EVENT_CLICKED,NULL);
    lv_obj_t*ttl=lv_label_create(s_vw);lv_label_set_text(ttl,"Add Tracking");lv_obj_set_style_text_font(ttl,&lv_font_montserrat_16,0);lv_obj_set_style_text_color(ttl,hx(p->on_surface),0);
    lv_obj_t*nl=lv_label_create(s_vw);lv_label_set_text(nl,"Tracking Number");lv_obj_set_style_text_color(nl,hx(p->on_surface),0);
    s_nta=lv_textarea_create(s_vw);lv_textarea_set_one_line(s_nta,true);lv_textarea_set_placeholder_text(s_nta,"e.g. 1Z999AA10123456784");
    lv_obj_set_width(s_nta,LV_PCT(100));lv_obj_add_event_cb(s_nta,on_nc,LV_EVENT_VALUE_CHANGED,NULL);
    s_dlbl=lv_label_create(s_vw);lv_label_set_text(s_dlbl,"Enter 4+ chars to auto-detect carrier");
    lv_obj_set_style_text_color(s_dlbl,hx(p->primary),0);lv_obj_set_style_text_font(s_dlbl,&lv_font_montserrat_12,0);
    lv_obj_t*ll=lv_label_create(s_vw);lv_label_set_text(ll,"Label (optional)");lv_obj_set_style_text_color(ll,hx(p->on_surface),0);
    s_lta=lv_textarea_create(s_vw);lv_textarea_set_one_line(s_lta,true);lv_textarea_set_placeholder_text(s_lta,"e.g. Mom's birthday gift");
    lv_obj_set_width(s_lta,LV_PCT(100));
    lv_obj_t*sv=lv_button_create(s_vw);lv_obj_set_size(sv,LV_PCT(100),44);lv_obj_set_style_bg_color(sv,hx(p->primary),0);lv_obj_set_style_radius(sv,12,0);
    lv_obj_t*svl=lv_label_create(sv);lv_label_set_text(svl,LV_SYMBOL_PLUS " Add Tracking");lv_obj_set_style_text_color(svl,hx(p->on_primary),0);lv_obj_center(svl);
    lv_obj_add_event_cb(sv,on_sv,LV_EVENT_CLICKED,NULL);
}

/* ---- LIFECYCLE ---- */
static bool etrack_init(lv_obj_t*parent){
    s_p=eapps_prefs_init("etrack");load();s_root=parent;
    s_vw=NULL;s_nta=NULL;s_lta=NULL;s_dlbl=NULL;show_list();return true;}
static void etrack_deinit(void){save();if(s_p){eapps_prefs_deinit(s_p);s_p=NULL;}
    s_root=NULL;s_vw=NULL;s_nta=NULL;s_lta=NULL;s_dlbl=NULL;}
static void etrack_on_show(void){}
static void etrack_on_hide(void){}

const eapps_app_info_t etrack_info={
    .id="etrack",.name="eTrack",.icon="trk",
    .description="Universal package, flight & case tracking",
    .category=EAPPS_CAT_PRODUCTIVITY,.version="1.0.0",
};
const eapps_app_lifecycle_t etrack_lifecycle={
    .init=etrack_init,.deinit=etrack_deinit,
    .on_show=etrack_on_show,.on_hide=etrack_on_hide,
};
