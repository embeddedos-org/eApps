FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY eosim/ eosim/
COPY platforms/ platforms/

RUN pip install --no-cache-dir build && \
    python -m build --wheel && \
    pip install --no-cache-dir dist/*.whl

FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        qemu-system-arm \
        qemu-system-aarch64 \
        qemu-system-riscv64 \
        qemu-system-x86 \
        qemu-system-mips && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/eosim /usr/local/bin/eosim
COPY platforms/ /opt/eosim/platforms/
COPY examples/ /opt/eosim/examples/

WORKDIR /opt/eosim

ENTRYPOINT ["eosim"]
CMD ["--help"]
