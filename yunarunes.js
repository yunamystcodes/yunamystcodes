/* YunaRunes — monster/build UI */
(function(){
  const monsters=[
    {name:'Veromos',family:'Ifrit',element:'Dark',emoji:'👹',awakening:'2º Despertar',sets:['Violent','Focus'],slots:['SPD','HP%','HP%'],stats:['HP','DEF','SPD','ACC'],use:'PvE / suporte',skills:['Dark Strike','Conversion','Beneficial Effect Removal']},
    {name:'Bella',family:'Inugami',element:'Light',emoji:'🐺',awakening:'2º Despertar',sets:['Swift','Energy'],slots:['SPD','HP%','HP%'],stats:['SPD','HP','DEF','ACC'],use:'PvE / suporte',skills:['Scratch','Defense Break','Heal & Cleanse']},
    {name:'Raoq',family:'Inugami',element:'Fire',emoji:'🐺',awakening:'2º Despertar',sets:['Fatal','Blade'],slots:['ATK%','ATK%','ATK%'],stats:['ATK','CR','CD','SPD'],use:'PvE / early game',skills:['Scratch','Team Up','Extra Turn']},
    {name:'Loren',family:'Cow Girl',element:'Light',emoji:'🏹',awakening:'2º Despertar',sets:['Swift','Focus'],slots:['SPD','HP%','HP%'],stats:['SPD','HP','ACC','DEF'],use:'PvE / bosses',skills:['Cross Fire','Wild Shot','Defense Break / ATB Control']},
    {name:'Fran',family:'Fairy Queen',element:'Light',emoji:'🧚',awakening:null,sets:['Swift','Energy'],slots:['SPD','HP%','HP%'],stats:['SPD','HP','DEF','ACC'],use:'PvE / suporte',skills:['Light Fairy Blessing','Heal','Immunity']},
    {name:'Megan',family:'Mystic Witch',element:'Water',emoji:'🧙',awakening:null,sets:['Swift','Focus'],slots:['SPD','HP%','HP%'],stats:['SPD','HP','ACC','DEF'],use:'PvE / Arena',skills:['Essence Drain','Toad Poison','ATB Boost']}
  ];
  const esc=s=>String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const art=(m,stage)=>`<div class="yuna-monster-portrait ${stage==='2a'?'is-2a':''}"><div class="yuna-portrait-glow"></div><span>${m.emoji}</span></div>`;

  function mount(){
    if(document.querySelector('.yuna-runes-shell'))return;
    const anchor=document.querySelector('main')||document.querySelector('.container')||document.body;
    const shell=document.createElement('section');shell.className='yuna-runes-shell';shell.id='yunarunes';
    shell.innerHTML=`
      <div class="yuna-runes-head">
        <div><div class="yuna-runes-title">YunaRunes</div><div class="yuna-runes-sub">Monster Search · Builds · Runes · Skills</div></div>
        <input class="yuna-runes-search" placeholder="Pesquisar monstro, família ou elemento..." aria-label="Pesquisar monstro">
      </div>
      <div class="yuna-runes-filters">${['Todos','Fire','Water','Wind','Light','Dark'].map((x,i)=>`<button class="yuna-runes-filter ${i===0?'active':''}" data-filter="${x}">${x}</button>`).join('')}</div>
      <div class="yuna-runes-grid"></div><div class="yuna-detail"></div>`;
    anchor.appendChild(shell);
    const grid=shell.querySelector('.yuna-runes-grid'),detail=shell.querySelector('.yuna-detail'),search=shell.querySelector('.yuna-runes-search');let filter='Todos';

    function render(){
      const q=search.value.toLowerCase().trim();
      const list=monsters.filter(m=>(filter==='Todos'||m.element===filter)&&(!q||`${m.name} ${m.family} ${m.element}`.toLowerCase().includes(q)));
      grid.innerHTML=list.map(m=>`<article class="yuna-monster-card" data-i="${monsters.indexOf(m)}">
        <div class="yuna-card-portrait">${art(m,'normal')}</div>
        <div class="yuna-monster-name">${esc(m.name)}</div><div class="yuna-monster-family">${esc(m.family)}</div>
        <div class="yuna-monster-meta"><span class="yuna-chip">${esc(m.element)}</span>${m.awakening?'<span class="yuna-chip">2A</span>':''}</div>
      </article>`).join('')||'<div style="color:#aaa0b9;padding:20px">Nenhum monstro encontrado.</div>';
    }

    function open(m){
      detail.classList.add('open');
      let stage='normal';
      const draw=()=>{
        const is2a=stage==='2a' && !!m.awakening;
        detail.innerHTML=`
          <div class="yuna-detail-top">
            <div class="yuna-detail-art-wrap">${art(m,stage)}</div>
            <div class="yuna-detail-info"><div class="yuna-kicker">MONSTER BUILD</div><h2>${esc(m.name)}</h2><p class="yuna-detail-family">${esc(m.family)} · ${esc(m.element)}</p>
              <div class="yuna-awakenings"><button class="yuna-awakening ${!is2a?'active':''}" data-stage="normal">Normal</button>${m.awakening?`<button class="yuna-awakening ${is2a?'active':''}" data-stage="2a">2º Despertar</button>`:''}</div>
              <p class="yuna-use">Uso recomendado: <b>${esc(m.use)}</b></p>
            </div>
          </div>
          <div class="yuna-tabs"><button class="yuna-tab active" data-tab="overview">Overview</button><button class="yuna-tab" data-tab="runes">Runes</button><button class="yuna-tab" data-tab="skills">Skills</button></div>
          <div class="yuna-tab-content active" data-content="overview"><div class="yuna-section-title">Prioridades de stats</div><div class="yuna-stats">${m.stats.map(x=>`<span class="yuna-stat"><b>${esc(x)}</b><small> prioridade</small></span>`).join('')}</div><div class="yuna-summary-grid"><div><small>Elemento</small><strong>${esc(m.element)}</strong></div><div><small>Família</small><strong>${esc(m.family)}</strong></div><div><small>Estado</small><strong>${is2a?'2º Despertar':'Normal'}</strong></div></div></div>
          <div class="yuna-tab-content" data-content="runes"><div class="yuna-section-title">Build recomendada</div><div class="yuna-rune-build">${m.sets.map((s,i)=>`<div class="yuna-rune-slot"><div><b>${esc(s)} Set</b><span>Slot ${i===0?'2':'4/6'}</span></div><strong>${esc(m.slots[i]||'HP%')}</strong><small>Substats: SPD · HP% · DEF% · ACC</small></div>`).join('')}</div></div>
          <div class="yuna-tab-content" data-content="skills"><div class="yuna-section-title">Skills</div><div class="yuna-stats">${m.skills.map((x,i)=>`<span class="yuna-stat"><b>${i+1}</b> ${esc(x)}</span>`).join('')}</div></div>`;
        detail.querySelectorAll('.yuna-awakening').forEach(b=>b.onclick=()=>{stage=b.dataset.stage;draw()});
        detail.querySelectorAll('.yuna-tab').forEach(b=>b.onclick=()=>{detail.querySelectorAll('.yuna-tab,.yuna-tab-content').forEach(x=>x.classList.remove('active'));b.classList.add('active');detail.querySelector(`[data-content="${b.dataset.tab}"]`).classList.add('active')});
      };
      draw();detail.scrollIntoView({behavior:'smooth',block:'nearest'});
    }
    grid.onclick=e=>{const c=e.target.closest('.yuna-monster-card');if(c)open(monsters[+c.dataset.i])};
    shell.querySelectorAll('.yuna-runes-filter').forEach(b=>b.onclick=()=>{shell.querySelectorAll('.yuna-runes-filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.filter;render()});
    search.oninput=render;render();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();
})();
