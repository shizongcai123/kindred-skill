#!/usr/bin/env python3
"""
Kindred Skill — 微信聊天记录解析器

推荐导出工具：
- weflow— 导出为 txt

"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOVED_ONES_DIR = os.path.join(SKILL_DIR, "loved_ones")


def classify_content(content: str) -> str:
    """判断消息内容的类型。"""
    if not content:
        return "empty"
    if content.startswith("../voices/") or content.endswith(".wav") or content.endswith(".amr"):
        return "voice"
    if content == "[图片]":
        return "image"
    if content == "[通话]":
        return "call"
    if content.startswith("[转账]") or content.startswith("[转账收款]"):
        return "transfer"
    if content.startswith("["):
        return "special"
    return "text"


def parse_txt(file_path: str) -> list:
    """解析 txt 格式聊天记录。

    支持两种格式：
    格式 1（PyWxDump 导出）：
    2025-04-25 15:09:26 '妈'
    内容

    格式 2（通用）：
    2024-01-15 09:32:15 奶奶
    内容
    """
    messages = []
    current_msg = None
    # 匹配带引号和不带引号的发送人
    header_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'?([^']+)'?$")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            match = header_pattern.match(line)
            if match:
                if current_msg:
                    current_msg["content_type"] = classify_content(current_msg["content"])
                    messages.append(current_msg)
                current_msg = {
                    "timestamp": match.group(1),
                    "sender": match.group(2).strip(),
                    "content": "",
                    "content_type": "text",
                }
            elif current_msg and line.strip():
                if current_msg["content"]:
                    current_msg["content"] += "\n"
                current_msg["content"] += line.strip()

    if current_msg:
        current_msg["content_type"] = classify_content(current_msg["content"])
        messages.append(current_msg)
    return messages


def parse_html(file_path: str) -> list:
    """解析 html 格式聊天记录。"""
    messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 适配多种导出工具的 HTML 结构
    patterns = [
        # WeChatExporter 格式
        re.compile(
            r'<div class="message"[^>]*>.*?'
            r'<span class="sender">([^<]+)</span>.*?'
            r'<span class="time">([^<]+)</span>.*?'
            r'<div class="content">([^<]+)</div>',
            re.DOTALL,
        ),
        # PyWxDump 格式
        re.compile(
            r'<td[^>]*>(\d{4}-\d{2}-\d{2}[^<]*)</td>\s*'
            r'<td[^>]*>([^<]+)</td>\s*'
            r'<td[^>]*>([^<]+)</td>',
            re.DOTALL,
        ),
    ]

    for pattern in patterns:
        for match in pattern.finditer(content):
            messages.append({
                "sender": match.group(1).strip() if "@" not in match.group(1) else match.group(2).strip(),
                "timestamp": match.group(2).strip() if "@" not in match.group(1) else match.group(1).strip(),
                "content": match.group(3).strip(),
            })
        if messages:
            break

    return messages


def parse_csv(file_path: str) -> list:
    """解析 csv 格式聊天记录。"""
    import csv
    messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            messages.append({
                "timestamp": row.get("timestamp", row.get("时间", row.get("StrTime", ""))),
                "sender": row.get("sender", row.get("发送者", row.get("NickName", row.get("talker", "")))),
                "content": row.get("content", row.get("内容", row.get("StrContent", ""))),
            })
    return messages


def analyze_messages(messages: list) -> dict:
    """分析消息特征，为后续灵魂提取做准备。"""

    # 分离发送者
    senders = {}
    for msg in messages:
        sender = msg.get("sender", "未知")
        if sender not in senders:
            senders[sender] = []
        senders[sender].append(msg)

    # 统计每个发送者
    stats = {}
    for sender, msgs in senders.items():
        # 按内容类型分类统计
        text_msgs = [m for m in msgs if m.get("content_type") == "text"]
        voice_msgs = [m for m in msgs if m.get("content_type") == "voice"]
        image_msgs = [m for m in msgs if m.get("content_type") == "image"]
        call_msgs = [m for m in msgs if m.get("content_type") == "call"]
        transfer_msgs = [m for m in msgs if m.get("content_type") == "transfer"]

        # 只统计文字消息的文本特征
        contents = [m["content"] for m in text_msgs if m.get("content")]
        total_chars = sum(len(c) for c in contents)
        avg_len = total_chars / len(contents) if contents else 0

        # 高频词提取
        all_text = " ".join(contents)
        mood_words = {}
        for word in ["哈哈", "嗯", "哦", "呢", "吧", "啊", "嘛", "呀", "噢",
                      "哎", "唉", "嘿", "喂", "晓得", "要的", "好",
                      "算了", "行了", "中", "得劲", "老火"]:
            count = all_text.count(word)
            if count > 0:
                mood_words[word] = count

        # 检测句尾特征（如方言中句尾加 "a"）
        trailing_a_count = sum(1 for c in contents if re.search(r'[a-zA-Z]$', c))

        # 表情使用
        emoji_pattern = re.compile(r'\[[\u4e00-\u9fff]+\]')
        emojis = emoji_pattern.findall(all_text)
        emoji_count = len(emojis)

        stats[sender] = {
            "message_count": len(msgs),
            "text_count": len(text_msgs),
            "voice_count": len(voice_msgs),
            "image_count": len(image_msgs),
            "call_count": len(call_msgs),
            "transfer_count": len(transfer_msgs),
            "total_chars": total_chars,
            "avg_length": round(avg_len, 1),
            "mood_words": mood_words,
            "trailing_a_count": trailing_a_count,
            "emoji_count": emoji_count,
            "top_emojis": list(set(emojis))[:10],
        }

    return {
        "total_messages": len(messages),
        "senders": stats,
        "date_range": {
            "earliest": messages[0].get("timestamp", "") if messages else "",
            "latest": messages[-1].get("timestamp", "") if messages else "",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Kindred Skill 微信聊天记录解析器")
    parser.add_argument("--input", required=True, help="聊天记录文件路径")
    parser.add_argument("--slug", required=True, help="loved one slug")
    parser.add_argument("--format", choices=["txt", "html", "csv", "auto"], default="auto")

    args = parser.parse_args()

    file_path = args.input
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        sys.exit(1)

    # 自动检测格式
    fmt = args.format
    if fmt == "auto":
        ext = os.path.splitext(file_path)[1].lower()
        fmt = {".txt": "txt", ".html": "html", ".htm": "html", ".csv": "csv"}.get(ext, "txt")

    # 解析
    print(f"正在读取聊天记录: {file_path}")
    parsers = {"txt": parse_txt, "html": parse_html, "csv": parse_csv}
    messages = parsers[fmt](file_path)
    print(f"读到了 {len(messages)} 条消息")

    # 分析
    analysis = analyze_messages(messages)
    for sender, stats in analysis["senders"].items():
        print(f"  {sender}: {stats['message_count']} 条, 平均 {stats['avg_length']} 字/条")

    # 保存
    output_dir = os.path.join(LOVED_ONES_DIR, args.slug, "knowledge", "messages")
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存原始消息
    msg_file = os.path.join(output_dir, f"wechat_messages_{ts}.json")
    with open(msg_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    # 保存分析结果
    analysis_file = os.path.join(output_dir, f"wechat_analysis_{ts}.json")
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n消息保存到: {msg_file}")
    print(f"分析保存到: {analysis_file}")


if __name__ == "__main__":
    main()
