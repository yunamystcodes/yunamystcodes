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

    var activeList=document.getElementById('activeCodesList');
    if(activeList){
      // Remove botões/link soltos que ficaram diretamente dentro da lista.
      // Os botões corretos continuam dentro de cada cartão .code.
      Array.prototype.slice.call(activeList.children).forEach(function(child){
        if(!child.classList.contains('code') && child.tagName!=='DIV') child.remove();
      });

      // Cria uma aba igual à dos códigos expirados.
      var tab=document.getElementById('activeCodesTab');
      if(!tab){
        tab=document.createElement('div');
        tab.className='active-tab';
        tab.id='activeCodesTab';
        tab.innerHTML='<button class="active-toggle" id="activeToggle" type="button"><span>🆕 VER TODOS OS CÓDIGOS ATIVOS</span> <span id="activeCount"></span>　⌄</button><div class="active-panel" id="activePanel"></div>';
        activeList.parentNode.insertBefore(tab,activeList.nextSibling);
      }

      var panel=document.getElementById('activePanel');
      var toggle=document.getElementById('activeToggle');
      var visibleCount=4;

      var cards=Array.prototype.filter.call(activeList.children,function(el){
        return el.classList && el.classList.contains('code');
      });
      var isOpen=panel && panel.classList.contains('open');
      cards.forEach(function(card,index){
        card.classList.toggle('active-extra',!isOpen && index>=visibleCount);
      });

      if(toggle && !toggle.dataset.bound){
        toggle.dataset.bound='1';
        toggle.addEventListener('click',function(){
          var open=panel.classList.toggle('open');
          cards.forEach(function(card,index){
            if(index>=visibleCount) card.classList.toggle('active-extra',!open);
          });
          toggle.querySelector('span').textContent=open?'🆕 OCULTAR CÓDIGOS ATIVOS':'🆕 VER TODOS OS CÓDIGOS ATIVOS';
          toggle.lastChild.textContent=open?'　⌃':'　⌄';
        });
      }

      var count=document.getElementById('activeCount');
      if(count) count.textContent='('+cards.length+')';

      // Botão controla a expansão; não usamos uma caixa com scroll no telemóvel.
      var style=document.getElementById('yunaActiveCodesMobileStyle');
      if(!style){
        style=document.createElement('style');
        style.id='yunaActiveCodesMobileStyle';
        style.textContent='.active-tab{margin-top:10px;border-top:1px solid rgba(255,255,255,.1)}.active-toggle{width:100%;border:0;background:transparent;color:#d99cff;padding:15px 17px;font-size:16px;font-weight:900;cursor:pointer;text-align:center}.active-toggle:hover{background:rgba(168,92,255,.08)}.active-panel{display:none}.active-panel.open{display:block}.active-extra{display:none!important}@media(max-width:600px){.active-toggle{font-size:14px;padding:14px 10px}}';
        document.head.appendChild(style);
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
          navigator.clipboard.writeText(code).then(function(){
            btn.textContent='✓ COPIADO!';
            setTimeout(function(){btn.textContent='▣ COPIAR';},1500);
          }).catch(function(){alert('Código: '+code);});
        });
        list.insertBefore(card,list.firstChild);
      });

      // Recalcula a aba depois de inserir códigos novos.
      var panel=document.getElementById('activePanel');
      var toggle=document.getElementById('activeToggle');
      var cards=Array.prototype.filter.call(list.children,function(el){
        return el.classList && el.classList.contains('code');
      });
      var visibleCount=4;
      var isOpen=panel && panel.classList.contains('open');
      cards.forEach(function(card,index){
        card.classList.toggle('active-extra',!isOpen && index>=visibleCount);
      });
      var count=document.getElementById('activeCount');
      if(count) count.textContent='('+cards.length+')';
      if(toggle && !toggle.dataset.bound){
        toggle.dataset.bound='1';
        toggle.addEventListener('click',function(){
          var open=panel.classList.toggle('open');
          cards.forEach(function(card,index){
            if(index>=visibleCount) card.classList.toggle('active-extra',!open);
          });
          toggle.querySelector('span').textContent=open?'🆕 OCULTAR CÓDIGOS ATIVOS':'🆕 VER TODOS OS CÓDIGOS ATIVOS';
          toggle.lastChild.textContent=open?'　⌃':'　⌄';
        });
      }
    }

    if(typeof window.updateExpiredCodes==='function') window.updateExpiredCodes();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run,{once:true});
  else run();
})();
