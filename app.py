import hmac
import hashlib
import requests
import string
import random
import json
import codecs
import base64
import logging
import urllib3
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Disable SSL Warnings for speed and clean logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PROTOBUF DEFINITION ---
try:
    from google.protobuf import descriptor_pool as _dp
    from google.protobuf import symbol_database as _sd
    from google.protobuf.internal import builder as _builder
    _sym_db = _sd.Default()
    DESCRIPTOR = _dp.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"\x87\x05\n\rMajorLoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x03\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\x05\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0c \x01(\x03\x12\x32\n\tblacklist\x18\r \x01(\x0b\x32\x1f.MajorLoginRes.BlacklistInfoRes\x12\x31\n\nqueue_info\x18\x0f \x01(\x0b\x32\x1d.MajorLoginRes.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x10 \x01(\t\x12\x15\n\rapp_server_id\x18\x11 \x01(\x03\x12\x0f\n\x07\x61no_url\x18\x12 \x01(\x03\x12\x0f\n\x07ip_city\x18\x13 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x14 \x01(\t\x12\x0b\n\x03kts\x18\x15 \x01(\x03\x12\n\n\x02\x61k\x18\x16 \x01(\x0c\x12\x0b\n\x03\x61iv\x18\x17 \x01(\x0c\x1aQ\n\x10\x42lacklistInfoRes\x12\x12\n\nban_reason\x18\x01 \x01(\x05\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\x03\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\x03\x1a\x66\n\x0eLoginQueueInfo\x12\r\n\x05\x41llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\x03\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\x03\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\x62\x06proto3')
    _globals = globals()
    _builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
    _builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'MajorLoginRes_pb2', _globals)
    MajorLoginRes = _globals['MajorLoginRes']
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False
    logging.warning("Protobuf library missing. Some parsing features may fail. Run: pip install protobuf")


# --- APP CONFIGURATION & CONSTANTS ---
app = FastAPI(
    title="Premium Account Generator & Activator API",
    description="Generates a Free Fire guest account based on OB52 Fixed Logic and seamlessly activates it.",
    version="2.1.0"
)

HEX_KEY = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
KEY_BYTES = bytes.fromhex(HEX_KEY)

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th", 
    "BD": "bn", "PK": "ur", "TW": "zh", "CIS": "ru", "SAC": "es", "BR": "pt"
}


# --- RESPONSE MODEL ---
class AccountResponse(BaseModel):
    Developer: str = "Riduanul Islam"
    TelegramBot: str = "https://t.me/RiduanFFBot"
    TelegramChannel: str = "https://t.me/RiduanOfficialBD"
    message: str
    account_name: str
    account_id: str
    server_region: str
    uid: str
    password: str
    activation: str
    activation_message: str
    jwt_token: str



# --- CORE CRYPTO & HELPER LOGIC ---
def generate_custom_password(prefix="Riduan") -> str:
    SECRET_KEY = "RiduanOfficialBD"
    characters = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choice(characters) for _ in range(5))
    part2 = ''.join(random.choice(characters) for _ in range(5))
    return f"{prefix}_{part1}_{SECRET_KEY}_{part2}"

def encrypt_api(plain_text: str) -> str:
    try:
        return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(bytes.fromhex(plain_text), AES.block_size)).hex()
    except Exception:
        return None

def decrypt_api(enc_data: bytes) -> bytes:
    try:
        return unpad(AES.new(AES_KEY, AES.MODE_CBC, AES_IV).decrypt(enc_data), AES.block_size)
    except Exception:
        return None

def E_AEs(Pc: str) -> bytes:
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(bytes.fromhex(Pc), AES.block_size))

def encode_string(original: str) -> dict:
    keystream = [0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
                 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30]
    encoded = "".join(chr(ord(original[i]) ^ keystream[i % len(keystream)]) for i in range(len(original)))
    return {"open_id": original, "field_14": encoded}

def to_unicode_escaped(s: str) -> str:
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

def EnC_Vr(N: int) -> bytes:
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number: int, value: int) -> bytes: 
    return EnC_Vr((field_number << 3) | 0) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number: int, value: bytes | str) -> bytes:
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr((field_number << 3) | 2) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields: dict) -> bytes:
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, dict): packet.extend(CrEaTe_LenGTh(field, CrEaTe_ProTo(value)))
        elif isinstance(value, int): packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, str) or isinstance(value, bytes): packet.extend(CrEaTe_LenGTh(field, value))           
    return bytes(packet)

def decode_jwt_token(jwt_token: str) -> str:
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            payload_part = parts[1]
            padding = 4 - len(payload_part) % 4
            if padding != 4: payload_part += '=' * padding
            decoded = base64.urlsafe_b64decode(payload_part)
            data = json.loads(decoded)
            account_id = data.get('account_id') or data.get('external_id')
            if account_id: return str(account_id)
    except: pass
    return "N/A"

def parse_proto(data):
    if not PROTOBUF_AVAILABLE:
        return None, None, None, None
    try:
        res = MajorLoginRes()
        res.ParseFromString(data)
        return res.token, res.ak.hex() if res.ak else None, res.aiv.hex() if res.aiv else None, res.account_id
    except: return None, None, None, None


# --- ACTIVATION LOGIC (Refactored from active.py) ---
def activate_account(session: requests.Session, uid: str, pwd: str, region: str = "BD"):
    base_guest = 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant'
    base_login = 'https://loginbp.ggblueshark.com/MajorLogin'
    base_client = 'https://clientbp.ggblueshark.com/GetLoginData'
    
    regions = {
        'IND': {'g': base_guest, 'm': 'https://loginbp.common.ggbluefox.com/MajorLogin', 'c': 'https://client.ind.freefiremobile.com/GetLoginData', 'h': 'client.ind.freefiremobile.com'},
        'BD': {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'}
    }
    cfg = regions.get(region.upper(), {'g': base_guest, 'm': base_login, 'c': base_client, 'h': 'clientbp.ggblueshark.com'})

    # 1. Guest Token
    try:
        data = {"uid": str(uid), "password": str(pwd), "response_type": "token", "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_id": "100067"}
        resp = session.post(cfg['g'], data=data, timeout=8, verify=False)
        if resp.status_code != 200: return False, f"Token Error HTTP_{resp.status_code}"
        tok, oid = resp.json().get('access_token'), resp.json().get('open_id')
    except Exception as e: return False, f"Network Error: {e}"

    if not tok: return False, "Invalid Token"

    # 2. Major Login
    headers = {'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB52', 'Content-Type': 'application/x-www-form-urlencoded', 'X-GA': 'v1 1', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F)', 'Host': 'loginbp.ggblueshark.com', 'Connection': 'Keep-Alive'}
    pt = bytes.fromhex('1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134')
    pt = pt.replace(b"996a629dbcdb3964be6b6978f5d814db", oid.encode())
    pt = pt.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", tok.encode())
    
    try:
        enc = encrypt_api(pt.hex())
        if not enc: return False, "Encryption Failed"
        resp = session.post(cfg['m'], headers=headers, data=bytes.fromhex(enc), verify=False, timeout=10)
        if resp.status_code != 200: return False, "Major Login Server Error"
    except: return False, "Major Login Network Error"

    dec_data = decrypt_api(resp.content)
    jwt, ak, aiv, account_id = parse_proto(dec_data if dec_data else resp.content)
    if not jwt: return False, "Proto Parse Error"

    # 3. Final Payload Request
    try:
        decoded = json.loads(base64.urlsafe_b64decode(jwt.split('.')[1] + '==').decode())
        eid, sig = decoded['external_id'], decoded['signature_md5']
        
        pl = bytes.fromhex("1a13323032352d30372d33302031313a30323a3531220966726565206669726528013a07312e3132302e32422c416e64726f6964204f5320372e312e32202f204150492d323320284e32473438482f373030323530323234294a0848616e6468656c645207416e64726f69645a045749464960c00c68840772033332307a1f41524d7637205646507633204e454f4e20564d48207c2032343635207c203480019a1b8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e319a012b476f6f676c657c31663361643662372d636562342d343934622d383730622d623164616364373230393131a2010c3139372e312e31322e313335aa0102656eb201203939366136323964626364623339363462653662363937386635643831346462ba010134c2010848616e6468656c64ea014066663930633037656239383135616633306134336234613966363031393531366530653463373033623434303932353136643064656661346365663531663261f00101ca0207416e64726f6964d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003daa907e803899b07f003bf0ff803ae088004999b078804daa9079004999b079804daa907c80403d204262f646174612f6170702f636f6d2e6474732e667265656669726574682d312f6c69622f61726de00401ea044832303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d312f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005dac901ea0507616e64726f6964f2055c4b71734854394748625876574c6668437950416c52526873626d43676542557562555551317375746d525536634e30524f3751453141486e496474385963784d614c575437636d4851322b7374745279377830663935542b6456593d8806019006019a060134a2060134")
        pl = pl.replace(b"2025-07-30 11:02:51", datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode())
        pl = pl.replace(b"ff90c07eb9815af30a43b4a9f6019516e0e4c703b44092516d0defa4cef51f2a", tok.encode())
        pl = pl.replace(b"996a629dbcdb3964be6b6978f5d814db", eid.encode())
        pl = pl.replace(b"7428b253defc164018c604a1ebbfebdf", sig.encode())
        final_payload = bytes.fromhex(encrypt_api(pl.hex()))
    except: return False, "Payload Generation Error"

    head = {'Authorization': f'Bearer {jwt}', 'X-Unity-Version': '2018.4.11f1', 'X-GA': 'v1 1', 'ReleaseVersion': 'OB52', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; SM-G973F)', 'Host': cfg['h'], 'Connection': 'close'}
    
    try:
        r = session.post(cfg['c'], headers=head, data=final_payload, verify=False, timeout=8)
        if r.status_code == 200: return True, f"Success! ID: {account_id}"
        return False, f"Client Rejection: HTTP {r.status_code}"
    except: return False, "Client Request Exception"


# --- API ENDPOINTS ---
@app.get("/acc_gen", response_model=AccountResponse)
def generate_and_activate_account(
    name: str = Query(..., description="Desired account base name"),
    region: str = Query(..., description="Server region (e.g., BD, IND, SG)")
):
    region_code = region.upper()
    lang_code = REGION_LANG.get(region_code, "en")
    
    url_host = "loginbp.common.ggbluefox.com" if region_code in ["ME", "TH"] else "loginbp.ggblueshark.com"

    final_account_name = name.strip()[:12].replace(" ", "　")
    password = generate_custom_password("Riduan")

    # Use a single session to persist connections throughout Generation -> Activation
    req_session = requests.Session()
    req_session.headers.update({"Accept-Encoding": "gzip", "Connection": "Keep-Alive"})

    try:
        # --- 1. GUEST REGISTER ---
        data = f"password={password}&client_type=2&source=2&app_id=100067"
        sig = hmac.new(KEY_BYTES, data.encode('utf-8'), hashlib.sha256).hexdigest()
        reg_headers = {
            "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
            "Authorization": "Signature " + sig,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res_reg = req_session.post("https://100067.connect.garena.com/oauth/guest/register", headers=reg_headers, data=data, verify=False, timeout=10)
        res_reg.raise_for_status()
        
        res_reg_json = res_reg.json()
        if 'uid' not in res_reg_json: 
            raise ValueError("Guest Register Failed: No UID returned")
        
        uid = str(res_reg_json['uid'])
        
        # --- 2. GET GUEST TOKEN ---
        body = {
            "uid": uid, "password": password, "response_type": "token",
            "client_type": "2", "client_secret": KEY_BYTES, "client_id": "100067"
        }
        res_tok = req_session.post("https://100067.connect.garena.com/oauth/guest/token/grant", headers=reg_headers, data=body, verify=False, timeout=10)
        res_tok.raise_for_status()
        
        tok_data = res_tok.json()
        if 'open_id' not in tok_data: 
            raise ValueError("Guest Token Failed: No open_id returned")
        
        open_id = tok_data['open_id']
        access_token = tok_data["access_token"]
        
        result = encode_string(open_id)
        field = codecs.decode(to_unicode_escaped(result['field_14']), 'unicode_escape').encode('latin1')
        
        # --- 3. MAJOR REGISTER ---
        major_url = f"https://{url_host}/MajorRegister"
        payload_mr = {
            1: final_account_name, 2: access_token, 3: open_id, 5: 102000007,
            6: 4, 7: 1, 13: 1, 14: field, 15: lang_code, 16: 1, 17: 1
        }
        enc_payload_mr = E_AEs(CrEaTe_ProTo(payload_mr).hex())
        
        headers_major = {
            "Authorization": "Bearer", "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue", "Host": url_host, "ReleaseVersion": "OB52",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1", "X-Unity-Version": "2018.4.11f1"
        }
        
        res_major_reg = req_session.post(major_url, headers=headers_major, data=enc_payload_mr, verify=False, timeout=15)
        if res_major_reg.status_code != 200:
            raise ValueError(f"Major Register Failed with status {res_major_reg.status_code}")
        
        # --- 4. MAJOR LOGIN ---
        ml_payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang_code.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        ml_data = b''.join(ml_payload_parts)
        ml_data = ml_data.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        ml_data = ml_data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        
        enc_ml_data = bytes.fromhex(encrypt_api(ml_data.hex()))
        res_ml = req_session.post(f"https://{url_host}/MajorLogin", headers=headers_major, data=enc_ml_data, verify=False, timeout=15)
        
        jwt_token = ""
        account_id = "N/A"

        if res_ml.status_code == 200 and len(res_ml.content) > 0:
            if PROTOBUF_AVAILABLE:
                try:
                    major_res = MajorLoginRes()
                    major_res.ParseFromString(res_ml.content)
                    if major_res.token:
                        jwt_token = major_res.token
                        account_id = str(decode_jwt_token(jwt_token))
                except Exception as e:
                    logging.error(f"Protobuf parsing failed: {e}")
            
            if not jwt_token and len(res_ml.text) > 10:
                jwt_start = res_ml.text.find("eyJ")
                if jwt_start != -1:
                    jwt_token_raw = res_ml.text[jwt_start:]
                    second_dot = jwt_token_raw.find(".", jwt_token_raw.find(".") + 1)
                    if second_dot != -1: 
                        jwt_token = jwt_token_raw[:second_dot + 44]
                        account_id = str(decode_jwt_token(jwt_token))

        if not jwt_token or account_id == "N/A": 
            return AccountResponse(
                status="error",
                message="This name is already used in another account or contains invalid characters. Please try again with a different name."
            )

        # --- 5. FORCE REGION BINDING ---
        if region_code != "BR":
            reg_bind = "RU" if region_code == "CIS" else region_code
            enc_region = encrypt_api(CrEaTe_ProTo({1: reg_bind}).hex())
            headers_choose = headers_major.copy()
            headers_choose["Authorization"] = f"Bearer {jwt_token}"
            req_session.post(f"https://{url_host}/ChooseRegion", headers=headers_choose, data=bytes.fromhex(enc_region), verify=False, timeout=10)

        # --- 6. TRIGGER AUTOMATIC ACTIVATION ---
        act_status, act_msg = activate_account(req_session, uid, password, region=region_code)
        
        final_message = "Account generated and activated" if act_status else "Account generated but activation failed"

        # Return exact requested JSON format with Developer Credits on top
        return AccountResponse(
            Developer="Riduanul Islam",
            TelegramBot="https://t.me/RiduanFFBot",
            TelegramChannel="https://t.me/RiduanOfficialBD",
            message=final_message,
            account_name=final_account_name,
            account_id=account_id,
            server_region=region_code,
            uid=uid, 
            password=password,
            activation="true" if act_status else "false",
            activation_message=act_msg,
            jwt_token=jwt_token
        )

    except Exception as e:
        logging.error(f"Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Account Generation Failed: {str(e)}")

@app.get("/")
def developer_info():
    return {
        "Developer": "Riduanul Islam",
        "TelegramBot": "https://t.me/RiduanFFBot",
        "TelegramChannel": "https://t.me/RiduanOfficialBD",
        "Project": "",
        "Message": "Welcome to Guest Account Generate & Active API",
        "Available_Servers": [
            "BD", "IND", "ID", "VN", "TH", "ME", "PK", "TW", "CIS", "SAC", "BR"
        ],
        "API_Usage_Guide": {
            "API_Format": {
                "Generate_Account": "/acc_gen?name=[Account_Name]&region=[Server_Region]"
            },
            "Examples": {
                "BD_Server": "/acc_gen?name=Riduan YT&region=BD",
                "IND_Server": "/acc_gen?name=BD Gang Pro&region=IND"
            }
        }
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)