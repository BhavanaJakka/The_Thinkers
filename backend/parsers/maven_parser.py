import xml.etree.ElementTree as ET
import re

def parse_maven_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []

    # A. pom.xml
    if 'pom.xml' in files_map:
        try:
            tree = ET.parse(files_map['pom.xml'])
            root = tree.getroot()
            # Handle XML namespaces
            ns = {'m': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            prefix = 'm:' if ns else ''

            deps = root.findall(f'.//{prefix}dependency', ns)
            for dep in deps:
                group = dep.find(f'{prefix}groupId', ns)
                artifact = dep.find(f'{prefix}artifactId', ns)
                version = dep.find(f'{prefix}version', ns)

                if group is not None and artifact is not None:
                    g_text = group.text.strip() if group.text else ''
                    a_text = artifact.text.strip() if artifact.text else ''
                    v_text = version.text.strip() if version is not None and version.text else '0.0.0'
                    pkg_name = f"{g_text}:{a_text}"

                    dependencies.append({
                        'name': pkg_name,
                        'version': v_text,
                        'ecosystem': 'Maven',
                        'is_direct': True,
                        'depth': 1,
                        'parent_name': 'root'
                    })
        except Exception as e:
            print(f"[MAVEN PARSER ERROR] pom.xml: {e}")

    # B. build.gradle
    if 'build.gradle' in files_map:
        try:
            with open(files_map['build.gradle'], 'r', encoding='utf-8') as f:
                content = f.read()
            # Match dependencies like implementation 'org.springframework.boot:spring-boot-starter-web:2.7.0'
            matches = re.findall(r"['\"]([a-zA-Z0-9._\-]+:[a-zA-Z0-9._\-]+:[a-zA-Z0-9._\-]+)['\"]", content)
            for m in matches:
                parts = m.split(':')
                if len(parts) >= 3:
                    dependencies.append({
                        'name': f"{parts[0]}:{parts[1]}",
                        'version': parts[2],
                        'ecosystem': 'Maven',
                        'is_direct': True,
                        'depth': 1,
                        'parent_name': 'root'
                    })
        except Exception as e:
            print(f"[GRADLE PARSER ERROR] build.gradle: {e}")

    return dependencies, edges
