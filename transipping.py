#!/usr/bin/python3
import subprocess
import re

def get_interfaces_and_ip_addresses():
    interfaces = {}
    result = subprocess.run(['ip', '-4', 'addr'], stdout=subprocess.PIPE, text=True)
    addresses = result.stdout.splitlines()

    current_interface = None
    for line in addresses:
        if line.startswith(' '):
            if 'inet ' in line and current_interface:
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', line)
                if match:
                    ip_address = match.group(1)
                    interfaces[current_interface].append(ip_address)
        else:
            match = re.search(r'^\d+: (\w+):', line)
            if match:
                current_interface = match.group(1)
                interfaces[current_interface] = []

    return interfaces

def get_gateway(interface):
    result = subprocess.run(['ip', 'route', 'show', 'dev', interface, 'default'], stdout=subprocess.PIPE, text=True)
    routes = result.stdout.splitlines()
    for route in routes:
        parts = route.split()
        if 'default' in parts:
            gateway = parts[2]
            return gateway
    return None

def ping_gateway(source_ip, gateway):
    try:
        result = subprocess.run(['ping', '-I', source_ip, '-c', '4', gateway], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Ping to {gateway} from IP {source_ip} was successful.")
        else:
            print(f"Ping to {gateway} from IP {source_ip} failed.")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"Error pinging {gateway} from IP {source_ip}: {e}")

def main():
    interfaces = get_interfaces_and_ip_addresses()
    for interface, ip_addresses in interfaces.items():
        gateway = get_gateway(interface)
        if gateway:
            for ip_address in ip_addresses:
                print(f"Pinging gateway {gateway} from IP {ip_address} on interface {interface}")
                ping_gateway(ip_address, gateway)
        else:
            print(f"No gateway found for interface {interface}")

if __name__ == '__main__':
    main()

