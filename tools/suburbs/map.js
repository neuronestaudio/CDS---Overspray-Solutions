(function(){
  var EASE='cubic-bezier(.16,1,.3,1)';
  function init(root){
    var W=+root.dataset.w, H=+root.dataset.h;
    var zones=JSON.parse(root.dataset.zones), zoneNames=JSON.parse(root.dataset.zoneNames);
    var stage=root.querySelector('.sam__stage'), svg=stage.querySelector('svg');
    var world=root.querySelector('.sam__world');
    var subs=Array.prototype.slice.call(root.querySelectorAll('a.sam__sub'));
    var tip=root.querySelector('.sam__tip'), tipName=tip.querySelector('.sam__tip-name'), tipMeta=tip.querySelector('.sam__tip-meta');
    var card=root.querySelector('.sam__card');
    var cardZone=card.querySelector('.sam__card-zone'), cardName=card.querySelector('.sam__card-name'),
        cardMeta=card.querySelector('.sam__card-meta'), cardLink=card.querySelector('.sam__card-link'),
        cardLinkText=card.querySelector('.sam__card-link-text');
    var input=root.querySelector('.sam__search input');
    var zoneButtons=Array.prototype.slice.call(root.querySelectorAll('.sam__zone'));
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var s=1,tx=0,ty=0,selected=null,dragged=false,drag=null;
    function boxOf(a){return a.dataset.box.split(',').map(Number);}
    function unit(){var r=svg.getBoundingClientRect();return Math.min(r.width/W,r.height/H);}
    function apply(animate){
      world.style.transition=(animate!==false&&!reduce)?('transform .8s '+EASE):'none';
      world.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')';
      world.style.setProperty('--k',String(1/s));
      root.classList.toggle('is-zoomed',s>1.04);
      fitLabels();
    }
    function clamp(){tx=Math.min(0,Math.max(W-W*s,tx));ty=Math.min(0,Math.max(H-H*s,ty));}
    function zoomTo(b,pad,max){
      var bw=Math.max(b[2]-b[0],1),bh=Math.max(b[3]-b[1],1);
      s=Math.min(max,Math.max(1,Math.min(W/(bw*pad),H/(bh*pad))));
      tx=W/2-s*((b[0]+b[2])/2); ty=H/2-s*((b[1]+b[3])/2); clamp(); apply();
    }
    function zoomBy(f){var cx=(W/2-tx)/s,cy=(H/2-ty)/s;s=Math.min(9,Math.max(1,s*f));tx=W/2-s*cx;ty=H/2-s*cy;clamp();apply();}
    function fitLabels(){var u=unit()*s;for(var i=0;i<subs.length;i++){var b=boxOf(subs[i]);subs[i].classList.toggle('is-fit',(b[2]-b[0])*u>=64&&(b[3]-b[1])*u>=22);}}
    function setZone(z){root.dataset.zone=z;zoneButtons.forEach(function(btn){btn.classList.toggle('is-on',btn.dataset.zone===z);});if(selected){selected.classList.remove('is-selected');selected=null;}card.setAttribute('data-empty','');zoomTo(zones[z],z==='all'?1:1.14,6);}
    function describe(a){var d=a.dataset;var area=d.area?(' · '+d.area+' km²'):'';return {name:d.name,meta:d.postcode+' · '+(zoneNames[d.zone]||'')+area};}
    function select(a){
      if(selected)selected.classList.remove('is-selected');
      selected=a;a.classList.add('is-selected');
      var info=describe(a);
      cardZone.textContent=zoneNames[a.dataset.zone]||'Selected suburb';
      cardName.textContent=info.name;cardMeta.textContent=info.meta;
      cardLink.href=a.getAttribute('href');cardLinkText.textContent='Open '+info.name;
      card.removeAttribute('data-empty');
      if(root.dataset.zone!==a.dataset.zone){root.dataset.zone=a.dataset.zone;zoneButtons.forEach(function(btn){btn.classList.toggle('is-on',btn.dataset.zone===a.dataset.zone);});}
      zoomTo(boxOf(a),3.4,9);
    }
    svg.addEventListener('click',function(e){var a=e.target.closest('a.sam__sub');if(!a)return;if(dragged){e.preventDefault();return;}if(a===selected)return;e.preventDefault();select(a);});
    svg.addEventListener('keydown',function(e){if(e.key!=='Enter')return;var a=e.target.closest('a.sam__sub');if(a&&a!==selected){e.preventDefault();select(a);}});
    svg.addEventListener('pointermove',function(e){if(e.pointerType==='touch')return;var a=e.target.closest('a.sam__sub');if(!a){tip.hidden=true;return;}var info=describe(a);tipName.textContent=info.name;tipMeta.textContent=info.meta;tip.hidden=false;var r=stage.getBoundingClientRect();var x=e.clientX-r.left,y=e.clientY-r.top;var flip=x>r.width-190;tip.style.left=(flip?x-14:x+14)+'px';tip.style.top=(y+14)+'px';tip.classList.toggle('is-flip',flip);});
    svg.addEventListener('pointerleave',function(){tip.hidden=true;});
    svg.addEventListener('pointerdown',function(e){dragged=false;if(e.pointerType==='touch'||s<=1.04||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,tx:tx,ty:ty};});
    svg.addEventListener('pointermove',function(e){if(!drag)return;var u=unit();var dx=(e.clientX-drag.x)/u,dy=(e.clientY-drag.y)/u;if(!dragged){if(Math.abs(dx)+Math.abs(dy)<=3)return;dragged=true;root.classList.add('is-dragging');svg.setPointerCapture(drag.id);}tx=drag.tx+dx;ty=drag.ty+dy;clamp();apply(false);});
    function endDrag(){drag=null;root.classList.remove('is-dragging');}
    svg.addEventListener('pointerup',endDrag);svg.addEventListener('pointercancel',endDrag);
    zoneButtons.forEach(function(btn){btn.addEventListener('click',function(){setZone(btn.dataset.zone);});});
    root.querySelectorAll('.sam__ctls button').forEach(function(btn){btn.addEventListener('click',function(){var act=btn.dataset.act;if(act==='in')zoomBy(1.6);else if(act==='out')zoomBy(1/1.6);else setZone('all');});});
    function findByName(q){var n=q.trim().toLowerCase();if(!n)return null;return subs.filter(function(a){return a.dataset.name.toLowerCase()===n;})[0]||subs.filter(function(a){return a.dataset.name.toLowerCase().indexOf(n)===0;})[0]||null;}
    input.addEventListener('change',function(){var a=findByName(input.value);if(a)select(a);});
    input.addEventListener('keydown',function(e){if(e.key!=='Enter')return;var a=findByName(input.value);if(!a)return;e.preventDefault();if(a===selected)window.location.href=a.getAttribute('href');else select(a);});
    window.addEventListener('resize',fitLabels,{passive:true});
    apply(false);
  }
  var els=document.querySelectorAll('.sam');for(var i=0;i<els.length;i++)init(els[i]);
})();
