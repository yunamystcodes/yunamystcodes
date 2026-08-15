(function(){
  function run(){
    // Correção de texto da parceria.
    document.querySelectorAll('.yuna-partnership-box p').forEach(function(p){
      p.textContent=p.textContent.replace('com o YunaMyst Codes','com a YunaMyst Codes');
    });

    // Garante o botão de parceria no PC junto da FAQ.
    var desktop=document.getElementById('yunaDesktopPartnershipButton');
    var faq=document.getElementById('faq');
    if(desktop && faq && faq.parentNode){faq.parentNode.insertBefore(desktop,faq);}

    // Garante o botão no telemóvel logo depois do WhatsApp.
    var mobile=document.getElementById('yunaPartnershipButton');
    var whats=document.querySelector('.hero .whats');
    if(mobile && whats && whats.parentNode){whats.parentNode.insertBefore(mobile,whats.nextSibling);}

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

    // Usa o mecanismo existente do site para mover automaticamente códigos expirados.
    if(typeof window.updateExpiredCodes==='function') window.updateExpiredCodes();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run,{once:true});
  else run();
})();
