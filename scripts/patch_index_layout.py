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

script = '''\n<script id="feedback-date-position-final">\n(function(){\n  function fixFeedbackDates(){\n    var els=document.querySelectorAll('*');\n    els.forEach(function(el){\n      if(el.dataset.feedbackDateFixed==='1') return;\n      if(el.children.length>0) return;\n      var text=(el.textContent||'').trim();\n      var m=text.match(/^\\((\\d{2}\\/\\d{2}\\/\\d{4})\\)\\s*(.+)$/);\n      if(!m) return;\n      var name=m[2];\n      el.dataset.feedbackDateFixed='1';\n      el.innerHTML='<span class="feedback-player-name">'+name+'</span><span class="feedback-player-date">('+m[1]+')</span>';\n      el.style.display='flex';\n      el.style.alignItems='center';\n      el.style.gap='8px';\n      el.style.width='100%';\n      el.style.justifyContent='flex-start';\n      var d=el.querySelector('.feedback-player-date');\n      if(d){d.style.marginLeft='auto';d.style.whiteSpace='nowrap';d.style.fontSize='11px';d.style.color='#a99eb8';}\n    });\n  }\n  fixFeedbackDates();\n  new MutationObserver(fixFeedbackDates).observe(document.body,{childList:true,subtree:true});\n})();\n</script>\n'''
if 'feedback-date-position-final' not in s:
    s=s.replace('</body>',script+'</body>',1)

# Remove visual duplication of the FAQ if more than one FAQ block exists.
faq_fix = '''
<script id="faq-single-block-final">
(function(){
  function keepOneFAQ(){
    var faqs=document.querySelectorAll('.faq');
    for(var i=1;i<faqs.length;i++) faqs[i].remove();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',keepOneFAQ);
  else keepOneFAQ();
  new MutationObserver(keepOneFAQ).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
if 'faq-single-block-final' not in s:
    s=s.replace('</body>',faq_fix+'</body>',1)

p.write_text(s,encoding='utf-8')
