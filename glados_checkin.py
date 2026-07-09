#!/usr/bin/env python3
"""
GLaDOS 自动签到脚本
支持飞书通知
"""

import os
import sys
import requests
import json
from datetime import datetime


def checkin(cookie: str) -> dict:
    """
    执行签到
    
    Args:
        cookie: GLaDOS 的完整 cookie 字符串
    
    Returns:
        dict: {"success": bool, "message": str, "data": dict}
    """
    url = "https://glados.one/api/user/checkin"
    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.post(url, headers=headers, json={}, timeout=30)
        data = resp.json()
        
        if data.get("code") == 0:
            points = data.get("points", 0)
            streak = data.get("streak", 0)
            return {
                "success": True,
                "message": f"✅ 签到成功！获得 {points} 积分，连续 {streak} 天",
                "data": data
            }
        else:
            msg = data.get("message", "未知错误")
            return {
                "success": False,
                "message": f"❌ 签到失败：{msg}",
                "data": data
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 请求异常：{str(e)}",
            "data": {}
        }


def send_feishu(webhook: str, title: str, content: str, success: bool = True):
    """
    发送飞书通知
    
    Args:
        webhook: 飞书 webhook URL
        title: 标题
        content: 内容（支持 lark_md）
        success: 是否成功（影响颜色）
    """
    if not webhook:
        print("[飞书] 未配置 FEISHU_WEBHOOK，跳过通知")
        return
    
    color = "green" if success else "red"
    
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"GLaDOS Auto Checkin | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        resp = requests.post(webhook, json=card, timeout=10)
        if resp.status_code == 200:
            print("[飞书] 通知发送成功")
        else:
            print(f"[飞书] 通知发送失败: {resp.status_code}")
    except Exception as e:
        print(f"[飞书] 通知异常: {e}")


def main():
    """主函数"""
    # 从环境变量获取配置
    cookie = os.environ.get("GLADOS_COOKIE", "")
    webhook = os.environ.get("FEISHU_WEBHOOK", "")
    
    if not cookie:
        print("❌ 错误: 未配置 GLADOS_COOKIE 环境变量")
        sys.exit(1)
    
    # 执行签到
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始签到...")
    result = checkin(cookie)
    print(result["message"])
    
    # 发送飞书通知
    if webhook:
        title = "🎯 GLaDOS 签到成功" if result["success"] else "⚠️ GLaDOS 签到失败"
        
        content = result["message"]
        if result["success"] and result["data"]:
            data = result["data"]
            content += f"\n\n**签到详情**:"
            content += f"\n- 获得积分: {data.get('points', 0)}"
            content += f"\n- 连续天数: {data.get('streak', 0)}"
            content += f"\n- 当前余额: {data.get('list', [{}])[0].get('balance', 'N/A')}"
        
        send_feishu(webhook, title, content, result["success"])
    
    # 退出码
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
