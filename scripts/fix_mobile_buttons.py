from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Keep the mobile buttons together, matching the compact spacing used on desktop.
s=s.replace('margin-left:14px;text-align:center;overflow:visible', 'margin-left:4px;text-align:center;overflow:visible')
s=s.replace('margin-left:10px;font-size:9px', 'margin-left:4px;font-size:9px')
p.write_text(s,encoding='utf-8')
