// SPDX-License-Identifier: MIT
#include "eBrowser/http.h"
#include "eBrowser/url.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
typedef SOCKET eb_socket_t;
#define EB_INVALID_SOCKET INVALID_SOCKET
#define eb_close_socket closesocket
#elif defined(eBrowser_PLATFORM_EOS) || defined(eBrowser_PLATFORM_WEB)
typedef int eb_socket_t;
#define EB_INVALID_SOCKET (-1)
#define eb_close_socket(s) ((void)(s))
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
typedef int eb_socket_t;
#define EB_INVALID_SOCKET (-1)
#define eb_close_socket close
#endif

#define HTTP_BUF_SIZE 8192

static eb_socket_t connect_to_host(const char *host, int port) {
#if defined(eBrowser_PLATFORM_EOS) || defined(eBrowser_PLATFORM_WEB)
    (void)host; (void)port;
    return EB_INVALID_SOCKET;
#else
    char port_str[16];
    snprintf(port_str, sizeof(port_str), "%d", port);

    struct addrinfo hints, *result;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port_str, &hints, &result) != 0) return EB_INVALID_SOCKET;

    eb_socket_t sock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (sock == EB_INVALID_SOCKET) { freeaddrinfo(result); return EB_INVALID_SOCKET; }

    if (connect(sock, result->ai_addr, (int)result->ai_addrlen) != 0) {
        eb_close_socket(sock);
        freeaddrinfo(result);
        return EB_INVALID_SOCKET;
    }
    freeaddrinfo(result);
    return sock;
#endif
}

static int send_all(eb_socket_t sock, const char *data, size_t len) {
#if defined(eBrowser_PLATFORM_EOS) || defined(eBrowser_PLATFORM_WEB)
    (void)sock; (void)data; (void)len;
    return -1;
#else
    size_t sent = 0;
    while (sent < len) {
        int n = send(sock, data + sent, (int)(len - sent), 0);
        if (n <= 0) return -1;
        sent += (size_t)n;
    }
    return 0;
#endif
}

static int recv_response(eb_socket_t sock, char **out, size_t *out_len) {
#if defined(eBrowser_PLATFORM_EOS) || defined(eBrowser_PLATFORM_WEB)
    (void)sock; (void)out; (void)out_len;
    return -1;
#else
    size_t capacity = HTTP_BUF_SIZE;
    size_t total = 0;
    char *buf = (char *)malloc(capacity);
    if (!buf) return -1;

    while (1) {
        if (total + HTTP_BUF_SIZE > capacity) {
            capacity *= 2;
            char *tmp = (char *)realloc(buf, capacity);
            if (!tmp) { free(buf); return -1; }
            buf = tmp;
        }
        int n = recv(sock, buf + total, HTTP_BUF_SIZE - 1, 0);
        if (n <= 0) break;
        total += (size_t)n;
    }
    buf[total] = '\0';
    *out = buf;
    *out_len = total;
    return 0;
#endif
}

static int parse_response(const char *raw, size_t raw_len, eb_http_response_t *resp) {
    if (!raw || !resp) return -1;
    const char *header_end = strstr(raw, "\r\n\r\n");
    if (!header_end) return -1;

    sscanf(raw, "HTTP/%*d.%*d %d", &resp->status_code);

    size_t header_len = (size_t)(header_end - raw);
    resp->headers = (char *)malloc(header_len + 1);
    if (resp->headers) { memcpy(resp->headers, raw, header_len); resp->headers[header_len] = '\0'; }

    const char *ct = strstr(raw, "Content-Type: ");
    if (!ct) ct = strstr(raw, "content-type: ");
    if (ct) {
        ct += 14;
        const char *ct_end = strstr(ct, "\r\n");
        if (ct_end) {
            size_t ct_len = (size_t)(ct_end - ct);
            resp->content_type = (char *)malloc(ct_len + 1);
            if (resp->content_type) { memcpy(resp->content_type, ct, ct_len); resp->content_type[ct_len] = '\0'; }
        }
    }

    const char *body_start = header_end + 4;
    resp->body_len = raw_len - (size_t)(body_start - raw);
    resp->body = (char *)malloc(resp->body_len + 1);
    if (resp->body) { memcpy(resp->body, body_start, resp->body_len); resp->body[resp->body_len] = '\0'; }

    return 0;
}

int eb_http_get(const char *url, eb_http_response_t *resp) {
    if (!url || !resp) return -1;
    memset(resp, 0, sizeof(eb_http_response_t));

    eb_url_t parsed;
    if (!eb_url_parse(url, &parsed)) return -1;

    eb_socket_t sock = connect_to_host(parsed.host, parsed.port);
    if (sock == EB_INVALID_SOCKET) return -1;

    char request[2048];
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: eBrowser/0.1\r\n"
             "Accept: text/html,application/xhtml+xml,*/*\r\n"
             "Connection: close\r\n"
             "\r\n",
             parsed.path[0] ? parsed.path : "/", parsed.host);

    if (send_all(sock, request, strlen(request)) != 0) {
        eb_close_socket(sock);
        return -1;
    }

    char *raw = NULL;
    size_t raw_len = 0;
    if (recv_response(sock, &raw, &raw_len) != 0) {
        eb_close_socket(sock);
        return -1;
    }
    eb_close_socket(sock);

    int rc = parse_response(raw, raw_len, resp);
    free(raw);
    return rc;
}

int eb_http_post(const char *url, const char *body, size_t body_len, eb_http_response_t *resp) {
    if (!url || !resp) return -1;
    memset(resp, 0, sizeof(eb_http_response_t));

    eb_url_t parsed;
    if (!eb_url_parse(url, &parsed)) return -1;

    eb_socket_t sock = connect_to_host(parsed.host, parsed.port);
    if (sock == EB_INVALID_SOCKET) return -1;

    char header[2048];
    snprintf(header, sizeof(header),
             "POST %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: eBrowser/0.1\r\n"
             "Content-Length: %zu\r\n"
             "Content-Type: application/x-www-form-urlencoded\r\n"
             "Connection: close\r\n"
             "\r\n",
             parsed.path[0] ? parsed.path : "/", parsed.host, body_len);

    if (send_all(sock, header, strlen(header)) != 0 ||
        (body && body_len > 0 && send_all(sock, body, body_len) != 0)) {
        eb_close_socket(sock);
        return -1;
    }

    char *raw = NULL;
    size_t raw_len = 0;
    if (recv_response(sock, &raw, &raw_len) != 0) {
        eb_close_socket(sock);
        return -1;
    }
    eb_close_socket(sock);

    int rc = parse_response(raw, raw_len, resp);
    free(raw);
    return rc;
}

void eb_http_response_free(eb_http_response_t *resp) {
    if (!resp) return;
    free(resp->body);
    free(resp->content_type);
    free(resp->headers);
    memset(resp, 0, sizeof(eb_http_response_t));
}
