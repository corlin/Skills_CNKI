import socket
import subprocess
import os

# 知网核心域名列表
CNKI_DOMAINS = [
    "www.cnki.net",
    "kns.cnki.net",
    "login.cnki.net",
    "piccache.cnki.net",
    "static.cnki.net",
    "my.cnki.net",
    "download.cnki.net"
]

def get_physical_gateway():
    """获取内网物理网关，通常是 en0 的网关"""
    try:
        # 获取 default 路由中属于 en0 的网关
        cmd = "netstat -rn -f inet | grep 'default' | grep 'en0' | awk '{print $2}'"
        gw = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')[0]
        if gw and gw != "link#":
            return gw
    except Exception:
        pass
    return "192.168.0.1" # 兜底常用网关

def resolve_ips(domains):
    """解析真实公网 IP 地址（使用 DoH 绕过 VPN 劫持）"""
    import json
    ips = set()
    for domain in domains:
        try:
            # 使用 curl 发送加密 DNS 请求 (使用阿里公共 DNS HTTPS 接口)
            url = f"https://dns.alidns.com/resolve?name={domain}&type=A"
            cmd = f'curl -s -H "accept: application/dns-json" "{url}"'
            output = subprocess.check_output(cmd, shell=True, timeout=5).decode()
            data = json.loads(output)
            
            if "Answer" in data:
                for ans in data["Answer"]:
                    # type 1 是 A 记录，type 5 是 CNAME（递归中可能存在）
                    if ans["type"] == 1:
                        ips.add(ans["data"])
        except Exception as e:
            print(f"# 警告: DoH 解析 {domain} 失败: {e}")
    return sorted(list(ips))

def generate_commands():
    gw = get_physical_gateway()
    ips = resolve_ips(CNKI_DOMAINS)
    
    print("=" * 60)
    print(f"🚀 [Skill_CNKI] TUN 模式直连分流脚本")
    print(f"检测到物理网关: {gw}")
    print(f"解析到目标 IP 数量: {len(ips)}")
    print("=" * 60)
    
    print("\n# --- [步骤 A] 请在终端中复制并执行以下命令来【添加】路由 ---")
    print("# 如果提示权限不足，请输入您的 macOS 开机密码")
    for ip in ips:
        print(f"sudo route add -host {ip} {gw}")
    
    print("\n# --- [步骤 B] 验证方式 ---")
    print(f"traceroute -n {CNKI_DOMAINS[0]}")
    print("# 如果第一跳地址是 {0} 而不是 198.18.x.x，则分流成功！".format(gw))
    
    print("\n# --- [步骤 C] 清理方式（当您不需要直连或更换网络时） ---")
    for ip in ips:
        print(f"sudo route delete -host {ip} {gw}")
    print("=" * 60)

if __name__ == "__main__":
    generate_commands()
