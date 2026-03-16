import os
import time
import shutil
import subprocess

INPUT_DIR = os.getenv('INPUT_DIR', '/app/inputs')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/outputs')

IMAGE_EXTS = {'.bmp', '.tiff', '.tif', '.gif', '.png', '.jpeg', '.jpg'}
PACKAGE_EXTS = {'.rpm', '.tgz', '.slp', '.pkg', '.deb'}

def process_files():
    if not os.path.exists(INPUT_DIR) or not os.path.exists(OUTPUT_DIR):
        return

    # Filter out hidden files and failed attempts
    files = [f for f in os.listdir(INPUT_DIR) if 
             os.path.isfile(os.path.join(INPUT_DIR, f)) and 
             not f.startswith('.') and 
             not f.startswith('FAILED_')]
    
    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        
        # 1. Parse the Tag and Determine "True" Extension
        if ".target." in filename:
            parts = filename.split(".target.")
            original_full_name = parts[0]
            target_ext = parts[1] 
        else:
            # FIX: Use the actual file extension if no tag exists
            original_full_name = filename
            target_ext = os.path.splitext(filename)[1].replace('.', '') or 'mp4'

        # 2. PHYSICAL RENAME: Strip the tag so Alien/FFmpeg don't get confused
        # From: discord.deb.target.rpm -> To: discord.deb
        real_input_path = os.path.join(INPUT_DIR, original_full_name)
        
        # Safety: If a file with the same name exists, remove it first
        if os.path.exists(real_input_path) and real_input_path != input_path:
            os.remove(real_input_path)
            
        os.rename(input_path, real_input_path)
        
        # Update pointer to the clean filename
        current_input = real_input_path
        base_name = os.path.splitext(original_full_name)[0]
        original_ext = os.path.splitext(original_full_name)[1].lower()
        output_filename = None

        try:
            # --- PACKAGES (Alien) ---
            if original_ext in PACKAGE_EXTS:
                print(f"[*] Package: {original_full_name} -> {target_ext}")
                
                # Alien now sees the correct extension at the end of current_input
                subprocess.run([
                    'fakeroot', 'alien', 
                    f'--to-{target_ext}', 
                    '--verbose', '--fixperms', current_input
                ], cwd=OUTPUT_DIR, check=True)
                
                # Find the renamed result
                for f in os.listdir(OUTPUT_DIR):
                    if f.endswith(f'.{target_ext}') and (base_name[:4].lower() in f.lower()):
                        output_filename = f"{base_name}.{target_ext}"
                        os.rename(os.path.join(OUTPUT_DIR, f), os.path.join(OUTPUT_DIR, output_filename))
                        break

            # --- IMAGES (FFmpeg) ---
            elif original_ext in IMAGE_EXTS:
                output_filename = f"{base_name}_converted.{target_ext}"
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                print(f"[*] Image: {original_full_name} -> {output_filename}")
                subprocess.run(['ffmpeg', '-y', '-i', current_input, '-update', '1', output_path], check=True)

            # --- VIDEO/AUDIO (FFmpeg) ---
            else:
                output_filename = f"{base_name}.{target_ext}"
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                print(f"[*] Media: {original_full_name} -> {output_filename}")
                subprocess.run([
                    'ffmpeg', '-y', '-i', current_input, 
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '128k', '-pix_fmt', 'yuv420p',
                    output_path
                ], check=True)

            # 3. Final Cleanup: Remove the "real" input file on success
            if os.path.exists(current_input):
                os.remove(current_input)
            
            print(f"[+] Success! Task completed for {original_full_name}")

        except Exception as e:
            print(f"[!] Error processing {original_full_name}: {e}")
            # If it fails, tag it so we don't loop forever
            if os.path.exists(current_input):
                failed_path = os.path.join(INPUT_DIR, f"FAILED_{original_full_name}")
                os.rename(current_input, failed_path)
    
if __name__ == "__main__":
    print(f"[-] Transformo Worker (Universal) active...")
    while True:
        process_files()
        time.sleep(5)