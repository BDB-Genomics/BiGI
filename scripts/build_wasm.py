import os
import subprocess
import base64
import re

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    physics_wasm_dir = os.path.join(project_root, "physics_wasm")
    template_path = os.path.join(project_root, "bigi", "render", "template.html")

    print("Step 1: Compiling Rust code to WebAssembly...")
    subprocess.run(
        ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
        cwd=physics_wasm_dir,
        check=True
    )

    wasm_file = os.path.join(
        physics_wasm_dir,
        "target",
        "wasm32-unknown-unknown",
        "release",
        "physics_wasm.wasm"
    )

    if not os.path.exists(wasm_file):
        raise FileNotFoundError(f"Compiled WASM not found at {wasm_file}")

    print("Step 2: Base64 encoding the WASM binary...")
    with open(wasm_file, "rb") as f:
        wasm_bytes = f.read()
    wasm_base64 = base64.b64encode(wasm_bytes).decode("utf-8")

    print(f"WASM size: {len(wasm_bytes)} bytes (Base64 length: {len(wasm_base64)} chars)")

    print("Step 3: Replacing WASM_BASE64 in template.html...")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    pattern = r'(const\s+WASM_BASE64\s*=\s*")[^"]*(";\s*//\s*__WASM_BASE64__)'
    
    # Check if we can find the pattern first
    if not re.search(pattern, template_content):
        raise RuntimeError("Could not find WASM_BASE64 target pattern in template.html")

    new_content = re.sub(pattern, rf'\g<1>{wasm_base64}\g<2>', template_content)

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("WASM successfully updated in template.html!")

if __name__ == "__main__":
    main()
