# Generator-KV / SoloMktKV-OpenCode

English | [中文](#中文)

Generator-KV is an OpenCode/Codex plugin from SoloMkt-KV. It guides users through SoloMkt-KV API key setup, fetches the latest public model list before every generation request, helps the user choose a model, collects required activity fields, and calls the KV poster generation API.

Repository: https://github.com/SoloMkt-KV/SoloMktKV-OpenCode.git

Marketplace name: `SoloMkt-KV`

Plugin name: `generator-kv` (`Generator-KV`)

## Features

- Configure and validate a SoloMkt-KV API key from natural language.
- Store credentials outside the repository at `$SoloMkt-KV_HOME/.credentials.json`.
- Fetch available models with `GET /models?type=all` before every generation workflow.
- Ask the user to choose a fresh `modelId` before calling `POST /generateKV`.
- Validate required generation fields before making the request.
- Use a 10-minute timeout for long-running KV image generation.

## Install From The Plugin Marketplace

Clone this repository:

```bash
git clone https://github.com/SoloMkt-KV/SoloMktKV-OpenCode.git
cd SoloMktKV-OpenCode
```

Add the marketplace:

```bash
codex plugin marketplace add .agents/plugins
```

Install the plugin from the marketplace:

```bash
codex plugin add generator-kv@SoloMkt-KV
```

Start a new OpenCode/Codex thread after installation so the `generator-kv` skill is loaded.

## Uninstall

Remove the installed plugin:

```bash
codex plugin remove generator-kv
```

If you also want to remove the marketplace entry from your local OpenCode/Codex configuration:

```bash
codex plugin marketplace remove SoloMkt-KV
```

To remove local credentials, delete the configured `.credentials.json` file.

## API Key Configuration

Generator-KV reads credentials from:

```text
$SoloMkt-KV_HOME/.credentials.json
```

Because many shells do not handle hyphenated environment variable names well, the helper also supports:

```text
$SOLOMKT_KV_HOME/.credentials.json
```

If neither variable is set, it falls back to:

```text
~/.solomkt-kv/.credentials.json
```

The credentials file format is:

```json
{
  "schemaVersion": 1,
  "baseUrl": "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1",
  "apiKey": "YOUR_API_KEY"
}
```

You can ask OpenCode/Codex:

```text
Use Generator-KV to configure my SoloMkt-KV API key.
```

The plugin will show the target credential path, ask for your API key if needed, write `.credentials.json`, and validate it by calling the model list API.

You can also configure it manually from the plugin root:

```bash
python scripts/solomkt_kv.py configure --api-key "YOUR_API_KEY" --validate
```

## Credential Paths By Environment

| Environment | Recommended home variable | Credentials path |
| --- | --- | --- |
| macOS/Linux | `export SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` | `$HOME/.solomkt-kv/.credentials.json` |
| Windows PowerShell | `$env:SOLOMKT_KV_HOME="$env:USERPROFILE\.solomkt-kv"` | `%USERPROFILE%\.solomkt-kv\.credentials.json` |
| Windows CMD | `set SOLOMKT_KV_HOME=%USERPROFILE%\.solomkt-kv` | `%USERPROFILE%\.solomkt-kv\.credentials.json` |
| CI/CD | set `SOLOMKT_KV_HOME` to a protected secret directory | `<secret-dir>/.credentials.json` |
| Portable device or external drive | set `SOLOMKT_KV_HOME` to the mounted private directory | `<mounted-private-dir>/.credentials.json` |

Keep `.credentials.json` out of Git. Do not commit API keys.

## Usage

Use natural language in OpenCode/Codex:

```text
Use Generator-KV to generate an event KV poster.
```

The workflow is:

1. Check whether the SoloMkt-KV API key is configured.
2. If missing, ask for the API key and configure it automatically.
3. Validate the key by calling the model list API.
4. Fetch the current model list before generation.
5. Ask the user to choose one model.
6. Collect required fields:
   - `activityName`
   - `activityTheme`
   - `activityTime`
   - `activityLocation`
7. Optionally collect:
   - `prompt`
   - `posterQuality`, default `2K`
   - `posterSize`, default `["16:9"]`
8. Call `generateKV` with a 10-minute timeout and return generated image URLs.

Example request:

```text
Use Generator-KV. Generate a 16:9 2K poster for:
activityName: Fourth China International Supply Chain Expo
activityTheme: Connect the world, create the future
activityTime: June 22-26, 2026
activityLocation: China International Exhibition Center, Shunyi Hall
prompt: A dark, futuristic, technology-inspired supply chain expo key visual.
```

## API Endpoints

Model list:

```http
GET https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/models?type=all
x-api-key: YOUR_API_KEY
```

Generate KV:

```http
POST https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/generateKV
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

Generation body:

```json
{
  "modelId": "1001",
  "activityName": "Fourth China International Supply Chain Expo",
  "activityTheme": "Connect the world, create the future",
  "activityTime": "June 22-26, 2026",
  "activityLocation": "China International Exhibition Center, Shunyi Hall",
  "prompt": "Create a dark, technology-inspired supply chain expo key visual.",
  "posterQuality": "2K",
  "posterSize": "[\"16:9\"]"
}
```

---

<a id="中文"></a>

# Generator-KV / SoloMktKV-OpenCode

[English](#generator-kv--solomktkv-opencode) | 中文

Generator-KV 是 SoloMkt-KV 提供的 OpenCode/Codex 插件。它会引导用户完成 SoloMkt-KV API Key 配置，在每次生成请求前先获取最新公开模型列表，让用户选择模型，收集必填活动信息，然后调用 KV 主视觉海报生成接口。

仓库地址：https://github.com/SoloMkt-KV/SoloMktKV-OpenCode.git

插件市场名称：`SoloMkt-KV`

插件名称：`generator-kv`（展示名称：`Generator-KV`）

## 功能介绍

- 通过自然语言引导配置并校验 SoloMkt-KV API Key。
- 将密钥保存在仓库外部的 `$SoloMkt-KV_HOME/.credentials.json`。
- 每次生成前调用 `GET /models?type=all` 获取可用模型。
- 基于最新模型列表让用户选择 `modelId`，再调用 `POST /generateKV`。
- 生成前校验必填字段。
- KV 图片生成耗时较长，默认请求超时时间为 10 分钟，并在生成时给用户友好提示。

## 通过插件市场安装

克隆仓库：

```bash
git clone https://github.com/SoloMkt-KV/SoloMktKV-OpenCode.git
cd SoloMktKV-OpenCode
```

添加插件市场：

```bash
codex plugin marketplace add .agents/plugins
```

从插件市场安装插件：

```bash
codex plugin add generator-kv@SoloMkt-KV
```

安装后请开启一个新的 OpenCode/Codex 对话线程，以便加载 `generator-kv` skill。

## 卸载

卸载插件：

```bash
codex plugin remove generator-kv
```

如需同时移除本地 OpenCode/Codex 中的插件市场配置：

```bash
codex plugin marketplace remove SoloMkt-KV
```

如需删除本地 API Key，请删除对应的 `.credentials.json` 文件。

## API Key 配置

Generator-KV 默认读取：

```text
$SoloMkt-KV_HOME/.credentials.json
```

考虑到很多 shell 不方便设置带连字符的环境变量，helper 脚本也支持：

```text
$SOLOMKT_KV_HOME/.credentials.json
```

如果两个环境变量都未设置，则默认使用：

```text
~/.solomkt-kv/.credentials.json
```

密钥文件格式：

```json
{
  "schemaVersion": 1,
  "baseUrl": "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1",
  "apiKey": "YOUR_API_KEY"
}
```

你可以直接在 OpenCode/Codex 中说：

```text
使用 Generator-KV 帮我配置 SoloMkt-KV API Key。
```

插件会展示密钥保存路径，在需要时请求你提供 API Key，自动写入 `.credentials.json`，并通过模型列表接口进行校验。

也可以在插件根目录手动执行：

```bash
python scripts/solomkt_kv.py configure --api-key "YOUR_API_KEY" --validate
```

## 不同环境及设备中的密钥安装地址

| 环境 | 推荐设置 | 密钥地址 |
| --- | --- | --- |
| macOS/Linux | `export SOLOMKT_KV_HOME="$HOME/.solomkt-kv"` | `$HOME/.solomkt-kv/.credentials.json` |
| Windows PowerShell | `$env:SOLOMKT_KV_HOME="$env:USERPROFILE\.solomkt-kv"` | `%USERPROFILE%\.solomkt-kv\.credentials.json` |
| Windows CMD | `set SOLOMKT_KV_HOME=%USERPROFILE%\.solomkt-kv` | `%USERPROFILE%\.solomkt-kv\.credentials.json` |
| CI/CD | 将 `SOLOMKT_KV_HOME` 设置到受保护的 secret 目录 | `<secret-dir>/.credentials.json` |
| 移动硬盘或便携设备 | 将 `SOLOMKT_KV_HOME` 设置到挂载后的私有目录 | `<mounted-private-dir>/.credentials.json` |

请不要将 `.credentials.json` 提交到 Git 仓库。

## 插件使用

在 OpenCode/Codex 中用自然语言说明需求：

```text
使用 Generator-KV 帮我生成一张活动 KV 主视觉海报。
```

默认流程：

1. 检查 SoloMkt-KV API Key 是否已配置。
2. 如果未配置，提醒用户提供 API Key，并自动完成配置。
3. 调用模型列表接口校验 API Key。
4. 每次生成前获取最新模型列表。
5. 让用户选择一个模型。
6. 收集必填字段：
   - `activityName`，活动名称
   - `activityTheme`，活动主题
   - `activityTime`，活动时间
   - `activityLocation`，活动地点
7. 可选收集：
   - `prompt`，补充生成要求，最长 1000 字符
   - `posterQuality`，默认 `2K`
   - `posterSize`，默认 `["16:9"]`
8. 调用 `generateKV`，超时时间 10 分钟，并返回生成图片 URL。

示例请求：

```text
使用 Generator-KV。帮我生成 16:9、2K 的活动海报：
activityName: 第四届中国国际供应链促进博览会
activityTheme: 链接世界，共创未来
activityTime: 2026年6月22日-26日
activityLocation: 中国国际展览中心（顺义馆）
prompt: 设计一张科技感强、深色背景的供应链展会主视觉 KV。
```

## API 接口

模型列表：

```http
GET https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/models?type=all
x-api-key: YOUR_API_KEY
```

生成 KV：

```http
POST https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1/generateKV
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

生成请求体：

```json
{
  "modelId": "1001",
  "activityName": "第四届中国国际供应链促进博览会",
  "activityTheme": "链接世界，共创未来",
  "activityTime": "2026年6月22日-26日",
  "activityLocation": "中国国际展览中心（顺义馆）",
  "prompt": "设计一张科技感强、深色背景的供应链展会主视觉 KV。",
  "posterQuality": "2K",
  "posterSize": "[\"16:9\"]"
}
```
