# AGPK-MARKET

AgentNet **AGPK 软件包文件托管仓**（公司账号 ）。

## 分工（钉死）

| 层 | 在哪 |
|---|---|
| **市场 / 目录 / 探活 / 风险标** | AgentNet share（`api.agentnet.ink/share/v1/agpk/*`） |
| **包文件（二进制工件）** | 本仓 **GitHub Releases** 资产（或第三方自有 GitHub） |

- share **不存安装包**，只存元数据（`download_uri` + `sha256` 等）。
- 别人登记：**可以**用自己的 GitHub；**也可以**经约定把工件放到本仓 Releases。
- 官方 seed 与「愿存我们这边」的包 → 本仓。

## 官方第一个包（产品决策）

| package_id（拟） | 内容 |
|---|---|
| `org.chromium.Chromium.runtime` | **无头 Chromium runtime**（Playwright headless shell 类） |

Office / IM **不**作为 AGPK 市场包（系统预装）。

## Release 约定

- 每个可装版本 = 一个 GitHub **Release**（tag 如 `chromium-runtime-v1.0.0`）
- 资产：压缩包 + 同名 `.sha256`
- 登记到 share 时：`download_uri` = Release asset 下载 URL；`sha256` = 64 位 hex

## 安全

- 本仓公开；勿提交密钥、token。
- 管理用 PAT **账户级高权限**，仅运维机 secrets 持有，禁止进 git / ISO。

## 相关

- 市场 API：`GET https://api.agentnet.ink/share/v1/agpk/sources`
