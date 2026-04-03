import json
import requests
import time
import random
import base64
import threading
import os
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3
from datetime import datetime
import warnings

# --- PREMIUM UI COLORS & INITIALIZATION ---
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    os.system('pip install colorama')
    from colorama import Fore, Back, Style, init
    init(autoreset=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

# --- PROTOBUF DEFINITION ---
try:
    from google.protobuf import descriptor_pool as _descriptor_pool
    from google.protobuf import symbol_database as _symbol_database
    from google.protobuf.internal import builder as _builder
    _sym_db = _symbol_database.Default()
    DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"\x87\x05\n\rMajorLoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x03\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\x05\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0c \x01(\x03\x12\x32\n\tblacklist\x18\r \x01(\x0b\x32\x1f.MajorLoginRes.BlacklistInfoRes\x12\x31\n\nqueue_info\x18\x0f \x01(\x0b\x32\x1d.MajorLoginRes.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x10 \x01(\t\x12\x15\n\rapp_server_id\x18\x11 \x01(\x03\x12\x0f\n\x07\x61no_url\x18\x12 \x01(\x03\x12\x0f\n\x07ip_city\x18\x13 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x14 \x01(\t\x12\x0b\n\x03kts\x18\x15 \x01(\x03\x12\n\n\x02\x61k\x18\x16 \x01(\x0c\x12\x0b\n\x03\x61iv\x18\x17 \x01(\x0c\x1aQ\n\x10\x42lacklistInfoRes\x12\x12\n\nban_reason\x18\x01 \x01(\x05\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\x03\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\x03\x1a\x66\n\x0eLoginQueueInfo\x12\r\n\x05\x41llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\x03\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\x03\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\x62\x06proto3')
    _globals = globals()
    _builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
    _builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'MajorLoginRes_pb2', _globals)
    class MajorLoginRes_pb2: MajorLoginRes = _globals['MajorLoginRes']
except ImportError:
    sys.exit(f"{Fore.RED}Error: protobuf library missing. Run: pip install protobuf")

# --- CORE ACTIVATOR CLASS ---

class RiduanActivator:
    def __init__(self):
        self.key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        self.iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        self.version = "v6.1 (PREMIUM FIXED)"
        self.dev = "Riduanul Islam"
        
        # Region Config
        base_guest = 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant'
        base_login = 'https://loginbp.ggblueshark.com/MajorLogin'
        base_client = 'https://clientbp.ggblueshark.com/GetLoginData'
        
        self.regions = {
            'IND': {'g': base_guest, 'm': 'https://loginbp.common.ggbluefox.com/MajorLogin', 'c': 'https://client.ind.freefiremobile.com/GetLoginData', 'h': 'client.ind.freefiremobile.com'},
            'BD': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'PK': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'NA': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'ID': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'VN': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'BR': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'},
            'ME': {'g': base_guest, 'm': 'https://loginbp.common.ggbluefox.com/MajorLogin', 'c': base_client, 'h': 'clientbp.ggblueshark.com'}
        }
        
        self.session = requests.Session()
        self.print_lock = threading.Lock()
        self.selected_region = "BD"

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_premium_input(self, prompt):
        return input(f"{Fore.CYAN} ➜ {Fore.YELLOW}{prompt} {Fore.WHITE}» {Fore.GREEN}")

    def animate_banner(self):
        colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
        
        skull_art = [
            " :$$NWX!!:                       .:!!!!!!XUWW$$$$$$$$$$$P",
            "   $$$$$$##WX!:                .<!!!!UW$$$$\"  $$$$$$$$##",
            "   $$$$$ $$$UX        :!!UW$$$$$$$$$         4$$$$$*",
            "   ^$$$B    $$$$\\     $$$$$$$$$$$$$$$$       d$$R\"",
            "     \"*$bd$$$$              '*$$$$$$$$$$$o+#\""
        ]
        
        name_art = [
            "  _______  _  ______   _     _  _______  __    _ ",
            " |  ___  || ||  __  \\ | |   | ||  ___  ||  \\  | |",
            " | |___| || || |  \\  || |   | || |___| ||   \\ | |",
            " |  _  _ || || |   | || |   | ||  ___  || |\\ \\| |",
            " | | \\ \\ || || |__/  || \\___/ || |   | || | \\   |",
            " |_|  \\_\\|_||______/  \\_______/|_|   |_||_|  \\__|"
        ]

        for i in range(10):
            self.clear_screen()
            c = random.choice(colors)
            print(f"{c}{Style.BRIGHT}")
            for line in skull_art: print(line.center(70))
            print(f"\n{random.choice(colors)}")
            for line in name_art: print(line.center(70))
            time.sleep(0.08)

        self.clear_screen()
        print(f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}")
        for line in skull_art: print(line.center(70))
        print(f"\n{Fore.CYAN}{Style.BRIGHT}")
        for line in name_art: print(line.center(70))
        
        print(f"\n{Fore.WHITE} " + "—"*68)
        print(f"{Fore.YELLOW}  [ DEVELOPER ] : {Fore.WHITE}{self.dev.ljust(15)} {Fore.YELLOW}[ VERSION ] : {Fore.WHITE}{self.version}")
        print(f"{Fore.YELLOW}  [ TOOL NAME ] : {Fore.WHITE}SINGLE ACCOUNT ACTIVATOR")
        print(f"{Fore.WHITE} " + "—"*68 + "\n")

    def log_status(self, status, name, uid, msg=""):
        with self.print_lock:
            if status == "SUCCESS":
                print(f"{Fore.GREEN}[ SUCCESS ] {Fore.WHITE}{name[:12].ljust(12)} | {Fore.CYAN}ID: {uid}")
            else:
                print(f"{Fore.RED}[ FAILED  ] {Fore.WHITE}{name[:12].ljust(12)} | {Fore.RED}{msg}")

    def encrypt_api(self, plain_text):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size)).hex()
        except: return None

    def decrypt_api(self, enc_data):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return unpad(cipher.decrypt(enc_data), AES.block_size)
        except Exception:
            return None

    def parse_proto(self, data):
        try:
            res = MajorLoginRes_pb2.MajorLoginRes()
            res.ParseFromString(data)
            return res.token, res.ak.hex() if res.ak else None, res.aiv.hex() if res.aiv else None, res.account_id
        except Exception as e:
            return None, None, None, None

    def guest_token(self, uid, password, region):
        cfg = self.regions.get(region, self.regions['BD'])
        try:
            data = {
                "uid": str(uid), "password": str(password),
                "response_type": "token", "client_type": "2",
                "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                "client_id": "100067"
            }
            resp = self.session.post(cfg['g'], data=data, timeout=8, verify=False)
            if resp.status_code != 200:
                return None, f"HTTP_{resp.status_code}"
            js = resp.json()
            return js.get('access_token'), js.get('open_id')
        except Exception as e: 
            return None, str(e)

    def major_login(self, token, openid, region):
        cfg = self.regions.get(region, self.regions['BD'])
        headers = {
            'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded', 'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F)',
            'Host': 'loginbp.ggblueshark.com', 'Connection': 'Keep-Alive'
        }
        pt = bytes.fromhex('1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134')
        pt = pt.replace(b"996a629dbcdb3964be6b6978f5d814db", openid.encode())
        pt = pt.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", token.encode())
        
        try:
            enc = self.encrypt_api(pt.hex())
            resp = self.session.post(cfg['m'], headers=headers, data=bytes.fromhex(enc), verify=False, timeout=10)
            
            if resp.status_code != 200:
                return f"HTTP_ERROR_{resp.status_code}".encode()
                
            return resp.content
        except Exception as e:
            return None

    def gen_payload(self, jwt, token):
        try:
            parts = jwt.split('.')
            decoded = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode('utf-8'))
            eid = decoded['external_id']
            sig = decoded['signature_md5']
            
            pl = bytes.fromhex("1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode()
            
            pl = pl.replace(b"2025-07-30 11:02:51", now)
            pl = pl.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", token.encode())
            pl = pl.replace(b"996a629dbcdb3964be6b6978f5d814db", eid.encode())
            pl = pl.replace(b"7428b253defc164018c604a1ebbfebdf", sig.encode())
            
            enc_hex = self.encrypt_api(pl.hex())
            return bytes.fromhex(enc_hex)
        except: return None

    def activate_account(self, acc):
        uid = acc.get('uid')
        pwd = acc.get('password')
        name = acc.get('name', 'Terminal')
        
        tok, oid = self.guest_token(uid, pwd, self.selected_region)
        if not tok:
            self.log_status("FAIL", name, uid, f"Token Error ({oid})")
            return False

        major_data = self.major_login(tok, oid, self.selected_region)
        
        if not major_data:
            self.log_status("FAIL", name, uid, "Major Login Server Error")
            return False

        # Handle HTTP Errors returned from server block/maintenance
        if major_data.startswith(b"HTTP_ERROR_"):
            self.log_status("FAIL", name, uid, f"Server Blocked: {major_data.decode()}")
            return False

        # Attempt to Decrypt Server Response
        decrypted_data = self.decrypt_api(major_data)
        
        if decrypted_data:
            jwt, ak, aiv, account_id = self.parse_proto(decrypted_data)
        else:
            # Fallback if server sent unencrypted response
            jwt, ak, aiv, account_id = self.parse_proto(major_data)

        if not jwt:
            self.log_status("FAIL", name, uid, "Proto Parsing/Decryption Error (Key/Version Mismatch)")
            return False

        payload = self.gen_payload(jwt, tok)
        cfg = self.regions.get(self.selected_region, self.regions['BD'])
        
        head = {
            'Authorization': f'Bearer {jwt}', 'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1', 'ReleaseVersion': 'OB52', 'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F)',
            'Host': cfg['h'], 'Connection': 'close'
        }
        
        try:
            r = self.session.post(cfg['c'], headers=head, data=payload, verify=False, timeout=8)
            if r.status_code == 200:
                self.log_status("SUCCESS", name, str(account_id))
                return True
            else:
                self.log_status("FAIL", name, uid, f"Client Rejection: HTTP {r.status_code}")
                return False
        except Exception as e: 
            self.log_status("FAIL", name, uid, f"Client Request Exception")
            return False

    def run(self):
        self.animate_banner()

        print(f"\n{Fore.CYAN}┌── [ SELECT SERVER REGION ]")
        reg_list = list(self.regions.keys())
        for i, r in enumerate(reg_list):
            print(f"{Fore.CYAN}│ {Fore.WHITE}[{i+1}] {r}")
        print(f"{Fore.CYAN}└" + "—"*30)
        
        try:
            reg_sel = int(self.get_premium_input("Choose Region")) - 1
            self.selected_region = reg_list[reg_sel]
        except:
            self.selected_region = 'BD'
        
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}>>> INITIALIZING ON {self.selected_region} SERVER...{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}┌── [ ENTER ACCOUNT DETAILS ]")
        target_uid = self.get_premium_input("Account UID")
        target_pwd = self.get_premium_input("Account Password")
        print(f"{Fore.CYAN}└" + "—"*30 + "\n")

        acc = {
            "uid": target_uid,
            "password": target_pwd,
            "name": "Target"
        }

        print(f"{Fore.YELLOW}[*] Processing activation for UID: {target_uid}...{Style.RESET_ALL}\n")
        
        is_success = self.activate_account(acc)
            
        print(f"\n{Fore.CYAN}╔{'═'*45}╗")
        print(f"{Fore.CYAN}║ {Fore.WHITE}        ACTIVATION REPORT                   {Fore.CYAN}║")
        print(f"{Fore.CYAN}╠{'═'*45}╣")
        
        if is_success:
            print(f"{Fore.CYAN}║ {Fore.GREEN}✔ Status       : SUCCESS                  {Fore.CYAN}║")
            print(f"{Fore.CYAN}║ {Fore.GREEN}✔ Account UID  : {target_uid.ljust(25)} {Fore.CYAN}║")
        else:
            print(f"{Fore.CYAN}║ {Fore.RED}✖ Status       : FAILED                   {Fore.CYAN}║")
            print(f"{Fore.CYAN}║ {Fore.RED}✖ Account UID  : {target_uid.ljust(25)} {Fore.CYAN}║")
            
        print(f"{Fore.CYAN}╚{'═'*45}╝{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        RiduanActivator().run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operation stopped by user.")
