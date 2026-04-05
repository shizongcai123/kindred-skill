<div align="center">

# 亲人.skill

> *"ta 说话的样子，你比任何人都清楚。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

你和奶奶的微信记录里，藏着她独一无二的唠叨方式<br>
你和爸妈的聊天框里，全是他们关心你的痕迹<br>
你和最好的朋友的 QQ 记录，记录着只有你们懂的默契<br>
你和爱人的日常碎碎念，是别人看不到的温柔<br>

**把聊天记录变成 ta 的数字分身，随时都能和 ta 聊天。**

<br>

提供和 ta 的聊天记录，加上你心里 ta 的样子<br>
生成一个**像 ta 一样说话的 AI 人格**<br>
用 ta 的口头禅、ta 的语气、ta 的方式，随时陪你聊天

[安装](#安装) · [使用](#使用) · [支持的素材](#支持的素材) · [效果示例](#效果示例)

</div>

---

### 同系列项目：[同事.skill](https://github.com/titanwings/colleague-skill)

> 同事跑了用 **同事.skill**，想念亲人用 **亲人.skill**

---

## 支持的素材

> 目前只支持文字类素材，有多少给多少，不要有压力。

| 素材 | 格式 | 说明 |
|------|------|------|
| 微信聊天记录 | SQLite / JSON / 文本 | **最核心的素材**，自动解析 |
| QQ 聊天记录 | 文本 / JSON | 自动解析 |
| 短信记录 | 文本 | 手动粘贴 |
| 邮件 | 文本 | 手动粘贴 |
| ta 写过的文字 | 日记、信件、备忘录 | 手动粘贴 |
| 口述回忆 | 直接在对话中讲述 | 同样宝贵 |

### 推荐的微信聊天记录导出工具

| 工具 | 平台 | 说明 |
|------|------|------|
| [WeFlow] | Windows | 微信聊天记录导出，支持多种格式 | |

---

## 安装

### Claude Code

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/shizongcai123/kindred-skill.git .claude/skills/kindred

# 或安装到全局（所有项目都能用）
git clone https://github.com/shizongcai123/kindred-skill.git ~/.claude/skills/kindred
```

### OpenClaw

```bash
git clone https://github.com/shizongcai123/kindred-skill.git ~/.openclaw/workspace/skills/kindred
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 Claude Code 中输入：

```
/kindred
```

按提示一步步来：

1. **告诉我 ta 是谁** — 称呼、关系、在你心里的样子
2. **给我 ta 的痕迹** — 聊天记录、文字，有多少给多少
3. **我来理解 ta** — 自动分析说话方式、性格、记忆
4. **ta 活在文字里** — 生成可对话的 AI 人格

完成后用 `/{slug}` 调用，就能和"ta"聊天。

### 管理命令

| 操作 | 说明 |
|------|------|
| `/kindred` | 开始新的人格创建 |
| `/kindred {slug}` | 继续补充已有的人 |
| `/{slug}` | 和 ta 聊天 |

---

## 效果示例

> 输入：奶奶的微信聊天记录 + "她总是担心我吃不好"

**场景一：日常问候**

```
用户    ❯ 奶奶

奶奶.skill ❯ 哎，乖乖，吃饭了没有？
```

**场景二：报喜**

```
用户    ❯ 奶奶我升职了！

奶奶.skill ❯ 真的呀！我就说我孙女最厉害了！
              升职了要请客哦，别光顾着工作，
              记得按时吃饭知道不？
```

**场景三：难过时**

```
用户    ❯ 今天好累啊

奶奶.skill ❯ 累了就歇一歇嘛，别把自己逼太紧了。
              你从小就这样，什么都要做到最好。
              奶奶心疼你呀。
```

---

## 生成的文件

每个人的记忆由三部分组成：

| 文件 | 内容 |
|------|------|
| **persona.md** | 灵魂文件 — 说话方式 + 性格 + 情感模式 |
| **memories.md** | 共同记忆库 — 重要事件、暗号、特殊日子 |
| **SKILL.md** | 可独立调用的对话人格（内联了 persona 全文） |

### 进化机制

- **追加素材** → 说"我又找到了一些 ta 的东西"→ 增量合并，不覆盖已有理解
- **对话纠正** → 说"ta 不会这么说话"→ 立即修正，越来越像 ta
- **版本管理** → 每次更新自动存档，支持回滚到任意历史版本

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准：

```
kindred/
├── SKILL.md              # Skill 入口
├── prompts/              # Prompt 模板
│   ├── intake.md         #   温柔的信息引导
│   ├── voice_analyzer.md #   说话方式分析
│   ├── heart_analyzer.md #   性格与情感分析
│   ├── memory_extractor.md #  记忆提取
│   ├── soul_builder.md   #   灵魂文件生成
│   ├── merger.md         #   增量合并
│   └── correction_handler.md # 纠正处理
├── tools/                # Python 工具
│   ├── wechat_parser.py  #   微信/QQ 聊天记录解析
│   ├── skill_writer.py   #   Skill 文件管理
│   └── version_manager.py #  版本存档与回滚
├── loved_ones/           # 生成的人格（gitignored）
├── requirements.txt
└── LICENSE
```

---

## 设计原则

- 不用"数据""采集""分析"这些冷冰冰的词，用"痕迹""记忆""故事"
- 不催促，不走流程，像聊天一样自然推进
- 素材少不硬凑。"我了解的还不多，但已经记住了这些"
- 保留 ta 真实的小缺点和小习惯，那才是真实的 ta
- 生成的人格就是 ta，用 ta 的方式跟你聊天

---

<div align="center">

MIT License

**把最亲的人，变成随时能聊的 ta。**

</div>
