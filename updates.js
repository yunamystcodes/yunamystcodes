(function(){
  function run(){
    // Correção de texto da parceria.
    document.querySelectorAll('.yuna-partnership-box p').forEach(function(p){
      p.textContent=p.textContent.replace('com o YunaMyst Codes','com a YunaMyst Codes');
    });

    // PC: a parceria fica no topo direito da caixa da FAQ, como estava antes.
    var desktop=document.getElementById('yunaDesktopPartnershipButton');
    var faq=document.getElementById('faq');
    if(desktop && faq){
      faq.style.position='relative';
      faq.insertBefore(desktop,faq.firstChild);
      desktop.style.cssText='display:flex!important;position:absolute!important;top:7px!important;right:7px!important;margin:0!important;width:auto!important;max-width:155px!important;min-height:46px!important;padding:7px 9px!important;z-index:5!important;';
      var picon=desktop.querySelector('.picon');
      if(picon) picon.style.cssText='width:30px!important;height:30px!important;font-size:16px!important;';
      var small=desktop.querySelector('small');
      if(small) small.style.cssText='font-size:8px!important;';
      var strong=desktop.querySelector('strong');
      if(strong) strong.style.cssText='font-size:15px!important;';
    }

    // Telemóvel: parceria logo depois do WhatsApp.
    var mobile=document.getElementById('yunaPartnershipButton');
    var whats=document.querySelector('.hero .whats');
    if(mobile && whats && whats.parentNode){
      whats.parentNode.insertBefore(mobile,whats.nextSibling);
    }

    // No telemóvel, mostrar todos os códigos ativos dentro de uma área própria com scroll.
    // Isto evita que a lista fique cortada e impede botões soltos de aparecerem fora dos cartões.
    var activeList=document.getElementById('activeCodesList');
    if(activeList){
      var style=document.getElementById('yunaActiveCodesMobileStyle');
      if(!style){
        style=document.createElement('style');
        style.id='yunaActiveCodesMobileStyle';
        style.textContent='@media(max-width:600px){#activeCodesList{max-height:68vh!important;overflow-y:auto!important;overflow-x:hidden!important;padding:2px 4px 8px!important;scrollbar-width:thin;-webkit-overflow-scrolling:touch}#activeCodesList::-webkit-scrollbar{width:6px}#activeCodesList::-webkit-scrollbar-thumb{background:#a85cff;border-radius:8px}.codes>button.copy,.codes>a.iphone{display:none!important}.yuna-active-hint{display:block!important}}@media(min-width:601px){.yuna-active-hint{display:none!important}}.yuna-active-hint{margin:4px 0 9px;text-align:center;color:#d99cff;font-size:11px;font-weight:800;}';
        document.head.appendChild(style);
      }
      if(!document.querySelector('.yuna-active-hint')){
        var hint=document.createElement('div');
        hint.className='yuna-active-hint';
        hint.textContent='↕ Desliza para ver todos os códigos ativos';
        activeList.parentNode.insertBefore(hint,activeList);
      }
    }

    // Garante os códigos publicados em 15/08/2026.
    var list=document.getElementById('activeCodesList');
    if(list){
      var codes=[
        ['YYDSSWC26ZAN','2026-08-22T00:00:00','https://withhive.me/313/YYDSSWC26ZAN'],
        ['4MINGYIDAOXIAN','2026-08-22T00:00:00','https://withhive.me/313/4MINGYIDAOXIAN']
      ];
      codes.forEach(function(item){
        var code=item[0];
        if(list.querySelector('[data-code="'+code+'"]')) return;
        var card=document.createElement('article');
        card.className='code';
        card.dataset.code=code;
        card.dataset.expires=item[1];
        card.innerHTML='<div class="gift">🎁</div><div class="cinfo"><strong>'+code+'</strong><small>🆕 Código novo de 15/08/2026</small></div><div class="reward-icons" aria-label="Recompensas"><span class="reward-chip"><span class="reward-unknown">🎁</span><b>Recompensa</b></span></div><button class="copy" type="button">▣ COPIAR</button><a class="iphone" href="'+item[2]+'" target="_blank" rel="noopener"><span class="iphone-full"> LINK IPHONE</span><span class="iphone-short"> LINK</span></a>';
        var btn=card.querySelector('.copy');
        btn.addEventListener('click',function(){
          navigator.clipboard.writeText(code).then(function(){btn.textContent='✓ COPIADO!';setTimeout(function(){btn.textContent='▣ COPIAR';},1500);}).catch(function(){alert('Código: '+code);});
        });
        list.insertBefore(card,list.firstChild);
      });
    }

    if(typeof window.updateExpiredCodes==='function') window.updateExpiredCodes();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run,{once:true});
  else run();
})();
