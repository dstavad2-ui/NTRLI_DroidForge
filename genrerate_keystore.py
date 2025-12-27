import base64
import os
import subprocess

# Settings
keystore_name = "ntrli_release.jks"
alias = "ntrli_alias"
password = "ChangeThisPassword123" # Use a strong password

def generate():
    print("Generating Keystore...")
    # This command uses the keytool bundled with many Android Python IDEs or accessible via termux
    cmd = (
        f"keytool -genkey -v -keystore {keystore_name} "
        f"-keyalg RSA -keysize 2048 -validity 10000 "
        f"-alias {alias} -storepass {password} -keypass {password} "
        f'-dname "CN=NTRLI, OU=DroidForge, O=NTRLI, L=Aalborg, S=North, C=DK"'
    )
    
    try:
        os.system(cmd)
        
        with open(keystore_name, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
            
        print("\n" + "="*30)
        print("YOUR GITHUB SECRET VALUES:")
        print("="*30)
        print(f"ANDROID_KEYSTORE_BASE64:\n{encoded_string}\n")
        print(f"ANDROID_KEY_ALIAS: {alias}")
        print(f"ANDROID_KEYSTORE_PASS: {password}")
        print(f"ANDROID_KEY_PASS: {password}")
        print("="*30)
        print("COPY THE BASE64 STRING ABOVE AND PASTE INTO GITHUB SECRETS.")
        
    except Exception as e:
        print(f"Error: {e}. If keytool is missing, try running this in Termux (pkg install openjdk-17).")

if __name__ == "__main__":
    generate()
