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
.reward-chip{display:inline-flex!important;align-items:center!important;gap:5px!important;white-space:nowrap!important}
.reward-chip b{font-size:12px;color:#fff}
/* Usa sempre os PNG/SVG reais das recompensas, nunca emojis ou icones genericos. */
.reward-chip .reward-icon{display:none!important}
.reward-chip::before{content:"";display:inline-block;width:30px;height:30px;background-size:contain;background-position:center;background-repeat:no-repeat;flex:none}
.reward-chip.mystic::before{background-image:url("assets/rewards/mystic.svg")}
.reward-chip.fire::before{background-image:url("assets/rewards/fire.svg")}
.reward-chip.water::before{background-image:url("assets/rewards/water.svg")}
.reward-chip.wind::before{background-image:url("assets/rewards/wind.svg")}
.reward-chip.mana::before{background-image:url("assets/rewards/mana.svg")}
.reward-chip.crystal::before{background-image:url("assets/rewards/crystal.svg")}
.reward-chip.energy::before{content:"⚡";background:none;font-size:26px;line-height:30px;text-align:center}

/* Remove todos os baus/cartoes de recompensas. */
.reward-chest,.gamebox{display:none!important}

@media(max-width:850px){
.code{grid-template-columns:44px minmax(0,1fr);grid-template-rows:auto auto auto;column-gap:12px;row-gap:12px}
.code .gift{grid-column:1;grid-row:1}.code .cinfo{grid-column:2;grid-row:1}
.code .reward-icons{grid-column:1 / -1;grid-row:2;justify-content:flex-start;display:flex!important;padding:0 0 2px;gap:10px}
.code .copy{grid-column:1;grid-row:3;width:100%;margin:0}.code .iphone{grid-column:2;grid-row:3;width:100%;margin:0}
.reward-img{width:30px!important;height:30px!important}.reward-chip::before{width:30px;height:30px}.reward-chip b{font-size:11px}
}
@media(max-width:600px){.reward-icons{gap:9px}.reward-img{width:30px!important;height:30px!important}.reward-chip::before{width:28px;height:28px}.reward-chip b{font-size:10px}.code{padding:16px 14px 18px}}
'''

s = re.sub(r'\n/\* Final reward layout \*/.*?(?=\n</style>)', '', s, flags=re.S)
s = s.replace('</style>', css + '\n</style>', 1)

# Remove every reward chest/gamebox inserted by older versions, including duplicates.
s = re.sub(r'\s*<section class="panel reward-chest"[^>]*>.*?</section>', '', s, flags=re.S)
s = re.sub(r'\s*<div class="reward-chest"[^>]*>.*?</div>', '', s, flags=re.S)
s = re.sub(r'\s*<div class="gamebox"[^>]*>.*?</div>', '', s, flags=re.S)

# Remove old reward-chest CSS blocks if they exist.
s = re.sub(r'\n\.reward-chest\{.*?(?=\n\.)', '\n', s, flags=re.S)
s = re.sub(r'\n\.reward-chest[^\n]*\n', '\n', s)

p.write_text(s, encoding='utf-8')
print('index.html patched: real reward icons enabled and reward chests removed')
