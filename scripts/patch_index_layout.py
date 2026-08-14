from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css = '''
/* Final reward layout */
.reward-icons{display:flex!important;align-items:center;justify-content:center;gap:12px;min-width:0;flex-wrap:wrap}
.reward-img{width:32px!important;height:32px!important;display:inline-block!important;background-size:contain!important;background-position:center!important;background-repeat:no-repeat!important}
.reward-mystic{background-image:url("assets/rewards/mystic.svg")!important}
.reward-fire{background-image:url("assets/rewards/fire.svg")!important}
.reward-water{background-image:url("assets/rewards/water.svg")!important}
.reward-wind{background-image:url("assets/rewards/wind.svg")!important}
.reward-mana{background-image:url("assets/rewards/mana.svg")!important}
.reward-crystal{background-image:url("assets/rewards/crystal.svg")!important}
.reward-chip b{font-size:12px;color:#fff}
@media(max-width:850px){
.code{grid-template-columns:44px minmax(0,1fr);grid-template-rows:auto auto auto;column-gap:12px;row-gap:12px}
.code .gift{grid-column:1;grid-row:1}.code .cinfo{grid-column:2;grid-row:1}
.code .reward-icons{grid-column:1 / -1;grid-row:2;justify-content:flex-start;display:flex!important;padding:0 0 2px;gap:10px}
.code .copy{grid-column:1;grid-row:3;width:100%;margin:0}.code .iphone{grid-column:2;grid-row:3;width:100%;margin:0}
.reward-img{width:30px!important;height:30px!important}.reward-chip b{font-size:11px}
}
@media(max-width:600px){.reward-icons{gap:9px}.reward-img{width:30px!important;height:30px!important}.reward-chip b{font-size:10px}.code{padding:16px 14px 18px}}
'''

# Replace the previous reward-layout patch so the workflow remains idempotent.
s = re.sub(r'\n/\* Final reward layout \*/.*?(?=\n</style>)', '', s, flags=re.S)
s = s.replace('</style>', css + '\n</style>', 1)

# Remove every reward chest inserted by older versions, including duplicate mobile copies.
s = re.sub(r'\s*<section class="panel reward-chest"[^>]*>.*?</section>', '', s, flags=re.S)
s = re.sub(r'\s*<div class="reward-chest"[^>]*>.*?</div>', '', s, flags=re.S)

# Remove old reward-chest CSS.
s = re.sub(r'\n\.reward-chest\{.*?\n\.reward-chest \.chest-icon\{.*?\n', '\n', s, flags=re.S)
s = re.sub(r'\n\.reward-chest[^\n]*\n', '\n', s)

p.write_text(s, encoding='utf-8')
print('index.html patched: reward chests removed')
