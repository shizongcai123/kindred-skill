#!/usr/bin/env python3
"""
Kindred Skill Writer
创建和更新亲人人格目录结构与文件。
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOVED_ONES_DIR = os.path.join(SKILL_DIR, "loved_ones")


def slugify(name: str) -> str:
    """将姓名/称呼转换为 slug。"""
    try:
        from pypinyin import lazy_pinyin
        slug = "".join(lazy_pinyin(name))
    except ImportError:
        slug = name
    return slug.lower().strip().replace(" ", "_").replace("-", "_")


def create_skill(args):
    """创建新的人格目录。"""
    slug = args.slug or slugify(args.name)
    person_dir = os.path.join(LOVED_ONES_DIR, slug)

    if os.path.exists(person_dir):
        print(f"这个名字已经存在了: {person_dir}")
        print("可以换一个称呼，或者直接在已有的基础上继续补充。")
        sys.exit(1)

    # 创建目录结构
    dirs = [
        person_dir,
        os.path.join(person_dir, "versions"),
        os.path.join(person_dir, "knowledge", "messages"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 创建 meta.json
    now = datetime.now(timezone.utc).isoformat()
    meta = {
        "name": args.name,
        "slug": slug,
        "relationship": getattr(args, "relationship", ""),
        "created_at": now,
        "updated_at": now,
        "version": "v1",
        "profile": {
            "age": getattr(args, "age", ""),
            "gender": getattr(args, "gender", ""),
            "dialect": getattr(args, "dialect", ""),
            "occupation": getattr(args, "occupation", ""),
        },
        "impression": getattr(args, "impression", ""),
        "corrections_count": 0,
        "memory_count": 0,
    }

    meta_path = os.path.join(person_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"已经为「{args.name}」创建好了空间: {person_dir}")
    return slug


def update_skill(args):
    """更新文件，自动存档当前版本。"""
    slug = args.slug
    person_dir = os.path.join(LOVED_ONES_DIR, slug)

    if not os.path.exists(person_dir):
        print(f"找不到: {person_dir}")
        sys.exit(1)

    meta_path = os.path.join(person_dir, "meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    old_version = meta.get("version", "v1")
    old_num = int(old_version.lstrip("v"))
    new_version = f"v{old_num + 1}"

    # 存档当前版本
    version_dir = os.path.join(person_dir, "versions", old_version)
    os.makedirs(version_dir, exist_ok=True)
    for fname in ["persona.md", "memories.md", "SKILL.md", "meta.json"]:
        src = os.path.join(person_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(version_dir, fname))

    # 更新 meta
    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"更新到了 {new_version}（{old_version} 已存档）")


def list_loved_ones(args):
    """列出所有已保存的人。"""
    if not os.path.exists(LOVED_ONES_DIR):
        print("还没有保存任何人的记忆。")
        return

    entries = []
    for slug in sorted(os.listdir(LOVED_ONES_DIR)):
        meta_path = os.path.join(LOVED_ONES_DIR, slug, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            entries.append(meta)

    if not entries:
        print("还没有保存任何人的记忆。")
        return

    print(f"一共保存了 {len(entries)} 个人的记忆：\n")
    for m in entries:
        print(f"  [{m['slug']}] {m['name']} — {m.get('relationship', '')}")
        print(f"    版本: {m.get('version', 'v1')} | 记忆数: {m.get('memory_count', 0)} | 修正数: {m.get('corrections_count', 0)}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Kindred Skill Writer")
    sub = parser.add_subparsers(dest="command")

    # create
    p_create = sub.add_parser("create")
    p_create.add_argument("--slug", default="")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--relationship", default="")
    p_create.add_argument("--age", default="")
    p_create.add_argument("--gender", default="")
    p_create.add_argument("--dialect", default="")
    p_create.add_argument("--occupation", default="")
    p_create.add_argument("--impression", default="")

    # update
    p_update = sub.add_parser("update")
    p_update.add_argument("--slug", required=True)

    # list
    sub.add_parser("list")

    args = parser.parse_args()

    if args.command == "create":
        create_skill(args)
    elif args.command == "update":
        update_skill(args)
    elif args.command == "list":
        list_loved_ones(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
