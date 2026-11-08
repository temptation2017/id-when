# id-when

把 UUID / ULID / KSUID / MongoDB ObjectId / Snowflake 等带时间戳的 ID 贴进来，在浏览器里本地解码出生成时间与字段结构。**纯前端，不上传。**

在线试用：<https://temptation2017.github.io/id-when/>

## 做什么

- 粘贴一个 ID，自动识别类型并解码
- 支持 UUIDv1 / v6 / v7、ULID、KSUID、MongoDB ObjectId、Snowflake（十进制或 `0x` 十六进制）
- 显示 UTC、北京时间（UTC+8）、浏览器本地时区，以及 Unix 秒 / 毫秒和相对时间
- 拆解时间戳、worker、序列号、随机段等字段，并用色块画出比特 / 字节布局
- UUIDv4 等无时间戳的 UUID 会明确提示「无内嵌时间戳」，不会编造时间
- 一键复制 Markdown 摘要

全部在本机解码，不发网络请求。

## 怎么打开

- 打开 GitHub Pages：<https://temptation2017.github.io/id-when/>
- 或本地下载后双击 `index.html`，或：

```bash
python3 -m http.server 8080
# 浏览器访问 http://127.0.0.1:8080/
```

无需构建、无需 npm。

可选校验（零依赖）：

```bash
python3 test_vectors.py
```

## 怎么用

1. 把 ID 粘贴到输入框（会去掉首尾空白），页面会自动识别并解码。
2. 若是 Snowflake，可切换纪元预设：Twitter（默认，`1288834974657`）、Discord、Instagram，或填写自定义纪元毫秒。
3. 查看类型、三时区时间、Unix 时间、相对年龄、字段表和色块布局。
4. 需要带走结果时，点「复制 Markdown」。
5. 可用页面上的示例按钮填入虚构样本，或点「生成 UUIDv7 / ULID」用浏览器 `crypto.getRandomValues` 在本地生成一条。

## 示例

下列样本均为虚构或公开文档中的例子，预期时间均为 UTC。

| 类型 | 示例 | 预期 |
| --- | --- | --- |
| ObjectId | `507f1f77bcf86cd799439011` | `2012-10-17T21:13:27.000Z`（MongoDB 文档示例；前 4 字节 `0x507f1f77` = 1350508407） |
| UUIDv7 | `018bcfe5-6800-7000-8000-000000000001` | `2023-11-14T22:13:20.000Z`（前 48 bit = `1700000000000`） |
| ULID | `01HF7YAT000123456789ABCDEF` | `2023-11-14T22:13:20.000Z` |
| KSUID | `2YBXZHsLO8MUtQ9MmLrFm4Unt79` | `2023-11-14T22:13:20.000Z` |
| Twitter Snowflake | `1724551110456250369` | `2023-11-14T22:13:20.000Z`，worker = 1，sequence = 1 |
| UUIDv1 | `04afc000-833b-11ee-8001-000000000001` | `2023-11-14T22:13:20.000Z` |
| UUIDv6 | `1ee833b0-4afc-6000-8001-000000000001` | `2023-11-14T22:13:20.000Z` |
| UUIDv4 | `f47ac10b-58cc-4372-a567-0e02b2c3d479` | 无内嵌时间戳 |

北京时间对照：`2023-11-14T22:13:20.000Z` = `2023-11-15 06:13:20`（UTC+8）。

Snowflake 由 `((1700000000000 - 1288834974657) << 22) | (1 << 12) | 1` 构造。

## 限制与可改进点

- Snowflake 必须选对纪元；默认按 Twitter 纪元解释。不同平台的 worker / 序列划分可能不同，本页按 `(id >> 22)`、worker 10 bit、sequence 12 bit 拆解。
- KSUID 使用官方纪元 `1400000000`（2014-05-13T16:53:20Z），不是当天 00:00:00Z。
- ObjectId / KSUID 只精确到秒，毫秒位显示为 `.000`。ObjectId 中间字节按旧文档标成机器标识 / PID / 计数器，**不代表真实主机**；较新的驱动把中间 5 字节视为随机值。
- UUIDv8 等自定义布局不会猜测时间戳。UUIDv1 的 node 字段在现代实现里多为随机，不当作 MAC 地址。
- 不做联网查询，也不验证某个 ID 是否真的在某个系统里存在。
- 可改进：Sonyflake / Xid / CUID2、Instagram 的 13+10 分片拆分、批量解码、从日志里扫出 ID。
- `test_vectors.py` 可在本地跑一遍上述构造样本（可选，零依赖）。

## License

MIT
