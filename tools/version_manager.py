#!/usr/bin/env python3
"""
Kindred Skill Version Manager
管理记忆文件的历史版本。
"""

import argparse
import json
import os
import shutil
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOVED_ONES_DIR = os.path.join(SKILL_DIR, "loved_ones")
MAX_VERSIONS = 10


def get_person_dir(slug: str) -> str:
    person_dir = os.path.join(LOVED_ONES_DIR, slug)
    if not os.path.exists(person_dir):
        print(f"找不到: {slug}")
        sys.exit(1)
    return person_dir


def list_versions(args):
    person_dir = get_person_dir(args.slug)
    versions_dir = os.path.join(person_dir, "versions")

    if not os.path.exists(versions_dir):
        print("还没有历史版本。")
        return

    versions = sorted(os.listdir(versions_dir))
    if not versions:
        print("还没有历史版本。")
        return

    print(f"「{args.slug}」的历史版本：\n")
    for v in versions:
        v_dir = os.path.join(versions_dir, v)
        meta_path = os.path.join(v_dir, "meta.json")
        ts = "-"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            ts = meta.get("updated_at", "-")
        files = os.listdir(v_dir)
        print(f"  {v} | {ts} | 包含: {', '.join(files)}")


def rollback(args):
    person_dir = get_person_dir(args.slug)
    target_version = args.version
    versions_dir = os.path.join(person_dir, "versions")
    target_dir = os.path.join(versions_dir, target_version)

    if not os.path.exists(target_dir):
        avail = sorted(os.listdir(versions_dir)) if os.path.exists(versions_dir) else []
        print(f"版本 {target_version} 不存在。可用: {avail}")
        sys.exit(1)

    # 备份当前
    meta_path = os.path.join(person_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            current_meta = json.load(f)
        cv = current_meta.get("version", "v_unknown")
        backup_dir = os.path.join(versions_dir, f"{cv}_pre_rollback")
        os.makedirs(backup_dir, exist_ok=True)
        for fname in ["persona.md", "memories.md", "SKILL.md", "meta.json"]:
            src = os.path.join(person_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_dir, fname))

    # 恢复
    for fname in os.listdir(target_dir):
        shutil.copy2(os.path.join(target_dir, fname), os.path.join(person_dir, fname))

    print(f"已回到 {target_version}")


def cleanup(args):
    person_dir = get_person_dir(args.slug)
    versions_dir = os.path.join(person_dir, "versions")

    if not os.path.exists(versions_dir):
        return

    versions = sorted(os.listdir(versions_dir))
    keep = args.keep or MAX_VERSIONS

    if len(versions) <= keep:
        print(f"版本数 {len(versions)} <= {keep}，不需要清理。")
        return

    to_remove = versions[:-keep]
    for v in to_remove:
        shutil.rmtree(os.path.join(versions_dir, v))
        print(f"  已清理: {v}")

    print(f"保留了最近 {keep} 个版本。")


def main():
    parser = argparse.ArgumentParser(description="Kindred Skill Version Manager")
    parser.add_argument("--action", required=True, choices=["list", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True)
    parser.add_argument("--version", default="")
    parser.add_argument("--keep", type=int, default=MAX_VERSIONS)

    args = parser.parse_args()

    if args.action == "list":
        list_versions(args)
    elif args.action == "rollback":
        if not args.version:
            print("请指定 --version")
            sys.exit(1)
        rollback(args)
    elif args.action == "cleanup":
        cleanup(args)


if __name__ == "__main__":
    main()
