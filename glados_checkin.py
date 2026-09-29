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
    
    # 模拟真实浏览器请求头（Windows Edge）
    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://glados.one",
        "Referer": "https://glados.one/console",
        "Sec-Ch-Ua": '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=1, i",
    }
    
    try:
        # 使用 session 保持连接
        session = requests.Session()
        
        # 先访问首页建立会话
        session.get("https://glados.one/console", headers={
            "Cookie": cookie,
            "User-Agent": headers["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }, timeout=30)
        
        # 再签到
        resp = session.post(url, headers=headers, json={}, timeout=30)
        
        # 检查响应内容
        if resp.status_code != 200:
            return {
                "success": False,
                "message": f"❌ HTTP {resp.status_code}",
                "data": {}
            }
        
        try:
            data = resp.json()
        except:
            # 非 JSON 响应（可能是登录页）
            return {
                "success": False,
                "message": f"❌ 响应非JSON，Cookie可能已失效。响应前100字符: {resp.text[:100]}",
                "data": {}
            }
        
        if data.get("code") == 0 or data.get("code") == 1:
            points = data.get("points", 0)
            streak = data.get("streak", 0)
            message = data.get("message", "签到成功")
            return {
                "success": True,
                "message": f"✅ {message}！获得 {points} 积分，连续 {streak} 天",
                "data": data
            }
        elif "already" in data.get("message", "").lower() or "logged" in data.get("message", "").lower() or "today" in data.get("message", "").lower():
            # 已签到，不算失败
            return {
                "success": True,
                "message": f"ℹ️ 今日已签到：{data.get('message', '')}",
                "data": data
            }
        elif "automated" in data.get("message", "").lower():
            # 自动化检测
            return {
                "success": False,
                "message": f"⚠️ 自动化检测：{data.get('message', '')}。请在浏览器手动登录一次后重试。",
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
