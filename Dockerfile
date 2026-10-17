FROM rust:bookworm AS builder
WORKDIR /src
COPY Cargo.toml ./
COPY src ./src
RUN cargo build --release
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/target/release/daily-wechat /usr/local/bin/daily-wechat
ENV TZ=Asia/Shanghai
VOLUME ["/data"]
ENTRYPOINT ["/usr/local/bin/daily-wechat"]
