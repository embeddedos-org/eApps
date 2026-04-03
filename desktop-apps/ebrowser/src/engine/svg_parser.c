// SPDX-License-Identifier: MIT
#include "eBrowser/svg.h"
#include "eBrowser/compat.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

static void skip_ws(const char **p, const char *end) {
    while (*p < end && isspace((unsigned char)**p)) (*p)++;
}

static int parse_int(const char **p, const char *end) {
    skip_ws(p, end);
    int sign = 1;
    if (*p < end && **p == '-') { sign = -1; (*p)++; }
    int val = 0;
    while (*p < end && isdigit((unsigned char)**p)) { val = val * 10 + (**p - '0'); (*p)++; }
    if (*p < end && **p == '.') { (*p)++; while (*p < end && isdigit((unsigned char)**p)) (*p)++; }
    return val * sign;
}

static bool find_attr(const char *ts, const char *te, const char *name, char *out, size_t out_size) {
    if (!ts||!te||!name||!out) return false;
    out[0] = '\0';
    size_t nlen = strlen(name);
    const char *p = ts;
    while (p + nlen < te) {
        if (strncasecmp(p, name, nlen) == 0 && (p[nlen] == '=' || isspace((unsigned char)p[nlen]))) {
            p += nlen;
            while (p < te && isspace((unsigned char)*p)) p++;
            if (p < te && *p == '=') {
                p++;
                while (p < te && isspace((unsigned char)*p)) p++;
                char q = 0;
                if (p < te && (*p == '"' || *p == '\'')) { q = *p; p++; }
                size_t i = 0;
                while (p < te && i < out_size - 1) {
                    if (q && *p == q) break;
                    if (!q && (isspace((unsigned char)*p) || *p == '>' || *p == '/')) break;
                    out[i++] = *p++;
                }
                out[i] = '\0';
                return true;
            }
        }
        p++;
    }
    return false;
}

static int get_int_attr(const char *ts, const char *te, const char *name, int def) {
    char buf[64]; if (find_attr(ts,te,name,buf,sizeof(buf))) return atoi(buf); return def;
}

static eb_color_t get_color_attr(const char *ts, const char *te, const char *name, eb_color_t def, bool *found) {
    char buf[64];
    if (find_attr(ts,te,name,buf,sizeof(buf))) {
        if (strcasecmp(buf,"none")==0) { if (found) *found=false; return def; }
        if (found) *found=true; return eb_css_parse_color(buf);
    }
    if (found) *found=false; return def;
}

static void parse_points(const char *pts, eb_svg_point_t *out, int *count, int max) {
    if (!pts||!out||!count) return;
    *count = 0;
    const char *p = pts, *end = pts + strlen(pts);
    while (p < end && *count < max) {
        skip_ws(&p, end); if (p >= end) break;
        int x = parse_int(&p, end);
        while (p < end && (*p == ',' || isspace((unsigned char)*p))) p++;
        int y = parse_int(&p, end);
        out[*count].x = x; out[*count].y = y; (*count)++;
        while (p < end && (*p == ',' || isspace((unsigned char)*p))) p++;
    }
}

static void parse_path_data(const char *d, eb_svg_point_t *out, int *count, int max) {
    if (!d||!out||!count) return;
    *count = 0;
    const char *p = d, *end = d + strlen(d);
    int cx = 0, cy = 0;
    while (p < end && *count < max) {
        skip_ws(&p, end); if (p >= end) break;
        char cmd = *p;
        if (isalpha((unsigned char)cmd)) p++; else cmd = 'L';
        skip_ws(&p, end);
        switch (cmd) {
            case 'M': cx=parse_int(&p,end); while(p<end&&(*p==','||isspace((unsigned char)*p)))p++; cy=parse_int(&p,end); break;
            case 'm': cx+=parse_int(&p,end); while(p<end&&(*p==','||isspace((unsigned char)*p)))p++; cy+=parse_int(&p,end); break;
            case 'L': cx=parse_int(&p,end); while(p<end&&(*p==','||isspace((unsigned char)*p)))p++; cy=parse_int(&p,end); break;
            case 'l': cx+=parse_int(&p,end); while(p<end&&(*p==','||isspace((unsigned char)*p)))p++; cy+=parse_int(&p,end); break;
            case 'H': cx=parse_int(&p,end); break;
            case 'h': cx+=parse_int(&p,end); break;
            case 'V': cy=parse_int(&p,end); break;
            case 'v': cy+=parse_int(&p,end); break;
            case 'Z': case 'z': if(*count>0){cx=out[0].x;cy=out[0].y;} break;
            default: p++; continue;
        }
        out[*count].x=cx; out[*count].y=cy; (*count)++;
        while(p<end&&(*p==','||isspace((unsigned char)*p)))p++;
    }
}

bool eb_svg_parse(eb_svg_element_t *svg, const char *content, size_t len) {
    if (!svg||!content||len==0) return false;
    memset(svg, 0, sizeof(eb_svg_element_t));
    svg->width = 300; svg->height = 150;
    const char *p = content, *end = content + len;
    while (p < end) {
        if (*p != '<') { p++; continue; }
        p++; if (p >= end) break;
        if (*p=='/'||*p=='!') { while(p<end&&*p!='>') p++; if(p<end) p++; continue; }
        char tag[32]={0}; size_t ti=0;
        while(p<end&&ti<sizeof(tag)-1&&(isalnum((unsigned char)*p)||*p=='-'||*p=='_')) tag[ti++]=(char)tolower((unsigned char)*p++);
        tag[ti]='\0';
        const char *tcs=p; while(p<end&&*p!='>') p++; const char *tce=p; if(p<end) p++;
        if (strcmp(tag,"svg")==0) {
            svg->width=get_int_attr(tcs,tce,"width",300); svg->height=get_int_attr(tcs,tce,"height",150);
            char vb[128];
            if(find_attr(tcs,tce,"viewBox",vb,sizeof(vb))||find_attr(tcs,tce,"viewbox",vb,sizeof(vb)))
                sscanf(vb,"%d %d %d %d",&svg->viewbox_x,&svg->viewbox_y,&svg->viewbox_width,&svg->viewbox_height);
            continue;
        }
        if (svg->shape_count>=EB_SVG_MAX_SHAPES) continue;
        eb_svg_shape_t *sh = &svg->shapes[svg->shape_count];
        memset(sh, 0, sizeof(eb_svg_shape_t));
        sh->fill=get_color_attr(tcs,tce,"fill",(eb_color_t){0,0,0,255},&sh->has_fill);
        sh->stroke=get_color_attr(tcs,tce,"stroke",(eb_color_t){0,0,0,255},&sh->has_stroke);
        sh->stroke_width=get_int_attr(tcs,tce,"stroke-width",1);
        if(!sh->has_fill&&!sh->has_stroke){sh->has_fill=true;sh->fill=(eb_color_t){0,0,0,255};}
        if (strcmp(tag,"rect")==0) { sh->type=EB_SVG_RECT; sh->data.rect.x=get_int_attr(tcs,tce,"x",0); sh->data.rect.y=get_int_attr(tcs,tce,"y",0); sh->data.rect.width=get_int_attr(tcs,tce,"width",0); sh->data.rect.height=get_int_attr(tcs,tce,"height",0); sh->data.rect.rx=get_int_attr(tcs,tce,"rx",0); sh->data.rect.ry=get_int_attr(tcs,tce,"ry",0); svg->shape_count++; }
        else if (strcmp(tag,"circle")==0) { sh->type=EB_SVG_CIRCLE; sh->data.circle.cx=get_int_attr(tcs,tce,"cx",0); sh->data.circle.cy=get_int_attr(tcs,tce,"cy",0); sh->data.circle.r=get_int_attr(tcs,tce,"r",0); svg->shape_count++; }
        else if (strcmp(tag,"ellipse")==0) { sh->type=EB_SVG_ELLIPSE; sh->data.ellipse.cx=get_int_attr(tcs,tce,"cx",0); sh->data.ellipse.cy=get_int_attr(tcs,tce,"cy",0); sh->data.ellipse.rx=get_int_attr(tcs,tce,"rx",0); sh->data.ellipse.ry=get_int_attr(tcs,tce,"ry",0); svg->shape_count++; }
        else if (strcmp(tag,"line")==0) { sh->type=EB_SVG_LINE; sh->data.line.x1=get_int_attr(tcs,tce,"x1",0); sh->data.line.y1=get_int_attr(tcs,tce,"y1",0); sh->data.line.x2=get_int_attr(tcs,tce,"x2",0); sh->data.line.y2=get_int_attr(tcs,tce,"y2",0); if(!sh->has_stroke){sh->has_stroke=true;sh->stroke=(eb_color_t){0,0,0,255};} svg->shape_count++; }
        else if (strcmp(tag,"polyline")==0) { sh->type=EB_SVG_POLYLINE; char pts[1024]; if(find_attr(tcs,tce,"points",pts,sizeof(pts))) parse_points(pts,sh->data.poly.points,&sh->data.poly.count,EB_SVG_MAX_POINTS); svg->shape_count++; }
        else if (strcmp(tag,"polygon")==0) { sh->type=EB_SVG_POLYGON; char pts[1024]; if(find_attr(tcs,tce,"points",pts,sizeof(pts))) parse_points(pts,sh->data.poly.points,&sh->data.poly.count,EB_SVG_MAX_POINTS); svg->shape_count++; }
        else if (strcmp(tag,"path")==0) { sh->type=EB_SVG_PATH; char d[2048]; if(find_attr(tcs,tce,"d",d,sizeof(d))) parse_path_data(d,sh->data.path.points,&sh->data.path.count,EB_SVG_MAX_POINTS); svg->shape_count++; }
    }
    return svg->shape_count > 0 || svg->width > 0;
}
