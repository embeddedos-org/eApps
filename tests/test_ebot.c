// SPDX-License-Identifier: MIT
// eBot client tests: list parsing against a canned loopback HTTP server.
// POSIX only (fork + BSD sockets); tests/CMakeLists.txt builds it on UNIX.
#include "eapps_test.h"
#include "ebot.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

/* Listen on 127.0.0.1 (any free port) and fork a child that answers one
 * request with `body`, then exits. Returns the child's pid, or -1. */
static pid_t serve_once(const char *body, uint16_t *port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0)
        return -1;
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    socklen_t len = sizeof(addr);
    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0 || listen(fd, 1) < 0 ||
        getsockname(fd, (struct sockaddr *)&addr, &len) < 0) {
        close(fd);
        return -1;
    }
    *port = ntohs(addr.sin_port);

    pid_t pid = fork();
    if (pid != 0) {
        close(fd);
        return pid;
    }

    int c = accept(fd, NULL, NULL);
    if (c >= 0) {
        char req[4096];
        size_t got = 0;
        while (got < sizeof(req) - 1) {
            ssize_t n = recv(c, req + got, sizeof(req) - 1 - got, 0);
            if (n <= 0)
                break;
            got += (size_t)n;
            req[got] = '\0';
            if (strstr(req, "\r\n\r\n"))
                break;
        }
        char head[128];
        int hl = snprintf(head, sizeof(head),
                          "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                          "Content-Length: %zu\r\nConnection: close\r\n\r\n", strlen(body));
        send(c, head, (size_t)hl, 0);
        send(c, body, strlen(body), 0);
        close(c);
    }
    close(fd);
    _exit(0);
}

static void reap(pid_t pid) {
    if (pid > 0)
        waitpid(pid, NULL, 0);
}

static void test_models_listed_once(void) {
    TEST_SUITE("ebot_fetch_models lists each model once");
    const char *body =
        "{\"models\":[{\"name\":\"eai-tiny\",\"tier\":\"micro\",\"params\":\"1B\"},"
        "{\"name\":\"eai-base\",\"tier\":\"standard\",\"params\":\"7B\"}]}";
    uint16_t port = 0;
    pid_t pid = serve_once(body, &port);
    ASSERT_TRUE(pid > 0, "loopback server started");
    if (pid <= 0)
        return;

    ebot_state_t s;
    ebot_state_init(&s, "127.0.0.1", port);
    int rc = ebot_fetch_models(&s);
    reap(pid);

    ASSERT_EQ(rc, 0, "fetch_models returns 0");
    ASSERT_EQ(s.model_count, 2, "two models in the reply, two listed");
    if (s.model_count >= 2) {
        ASSERT_STR_EQ(s.models[0].name, "eai-tiny", "first model");
        ASSERT_STR_EQ(s.models[1].name, "eai-base", "second model");
        ASSERT_STR_EQ(s.models[1].tier, "standard", "second model's tier");
        ASSERT_STR_EQ(s.models[1].params, "7B", "second model's params");
    }
}

static void test_tools_listed_once(void) {
    TEST_SUITE("ebot_fetch_tools lists each tool once");
    const char *body =
        "{\"tools\":[{\"name\":\"calc\",\"description\":\"Evaluate math\",\"permission\":\"none\"},"
        "{\"name\":\"files\",\"description\":\"Read files\",\"permission\":\"read\"}]}";
    uint16_t port = 0;
    pid_t pid = serve_once(body, &port);
    ASSERT_TRUE(pid > 0, "loopback server started");
    if (pid <= 0)
        return;

    ebot_state_t s;
    ebot_state_init(&s, "127.0.0.1", port);
    int rc = ebot_fetch_tools(&s);
    reap(pid);

    ASSERT_EQ(rc, 0, "fetch_tools returns 0");
    ASSERT_EQ(s.tool_count, 2, "two tools in the reply, two listed");
    if (s.tool_count >= 2) {
        ASSERT_STR_EQ(s.tools[0].name, "calc", "first tool");
        ASSERT_STR_EQ(s.tools[1].name, "files", "second tool");
        ASSERT_STR_EQ(s.tools[1].permission, "read", "second tool's permission");
    }
}

int main(void) {
    test_models_listed_once();
    test_tools_listed_once();
    TEST_EXIT();
}
