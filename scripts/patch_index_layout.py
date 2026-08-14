from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css = '''
<style id="mobile-button-size-final">
@media (max-width:600px){
  /* SOMENTE os botoes: nao altera os icones/recompensas */
  .codes .code .copy,
  .codes .code .iphone{
    position:static!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    box-sizing:border-box!important;
    width:120px!important;
    min-width:120px!important;
    max-width:120px!important;
    height:44px!important;
    min-height:44px!important;
    max-height:44px!important;
    margin:0!important;
    padding:0 8px!important;
    flex:none!important;
    font-size:12px!important;
    line-height:1!important;
    border-radius:10px!important;
    justify-self:center!important;
    overflow:hidden!important;
    white-space:nowrap!important;
  }
  .codes .code .copy{grid-column:1!important;grid-row:3!important}
  .codes .code .iphone{grid-column:2!important;grid-row:3!important}
  .codes .code{grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;column-gap:8px!important}
}
@media (max-width:380px){
  .codes .code .copy,
  .codes .code .iphone{
    width:112px!important;
    min-width:112px!important;
    max-width:112px!important;
    height:42px!important;
    min-height:42px!important;
    max-height:42px!important;
    font-size:11px!important;
  }
  .codes .code{column-gap:6px!important}
}
</style>
'''

s = re.sub(r'<style id="mobile-button-size-final">.*?</style>\s*', '', s, flags=re.S)
if '</head>' in s:
    s = s.replace('</head>', css + '</head>', 1)
else:
    s += css
p.write_text(s, encoding='utf-8')
