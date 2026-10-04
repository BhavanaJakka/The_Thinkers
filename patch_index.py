import sys
import os

def patch():
    target_file = 'index.html'
    if len(sys.argv) > 1:
        target_file = sys.argv[1]

    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found.")
        sys.exit(1)

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Add JSZip and real-scan.js tag before <script type="text/babel">
    jszip_tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>\n  <script src="real-scan.js"></script>\n'
    if 'jszip.min.js' not in content:
        content = content.replace('<script type="text/babel">', jszip_tag + '  <script type="text/babel">')

    with open('index.fixed.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Patched script structure successfully.")

if __name__ == '__main__':
    patch()
