/* Suburb explorer. Progressive: with no JS every suburb is still a plain link, in
   the map and in the directory. Inlined into the page by tools/suburbs/emit_pages.py. */
(function(){
  var EASE='cubic-bezier(.16,1,.3,1)', NS='http://www.w3.org/2000/svg';
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
  function init(root){
    var W=+root.dataset.w, H=+root.dataset.h, PPK=+root.dataset.ppk;
    var P=root.dataset.proj.split(',').map(Number);           // minLng, maxLat, kx, scale, pad
    var ZB=JSON.parse(root.dataset.zones);                     // zone -> [x0,y0,x1,y1]
    var D=JSON.parse(root.querySelector('.sx__data').textContent);
    var S=D.s, ZN=D.z, RN=D.r;                                 // S[i]=[name,pc,zoneIdx,regionIdx,area,km,cx,cy]
    var q=function(sel){return root.querySelector(sel);};
    var all=function(sel){return Array.prototype.slice.call(root.querySelectorAll(sel));};
    var stage=q('.sx__stage'), svg=stage.querySelector('svg'), world=q('.sx__world'), labels=q('.sx__labels');
    var subs=[], rows=[];
    all('a.sx__sub').forEach(function(a){subs[+a.dataset.i]=a;});
    all('.sx__dir a[data-i]').forEach(function(a){rows[+a.dataset.i]=a;});
    var tip=q('.sx__tip'), card=q('.sx__card'), me=q('.sx__me');
    var cZone=q('.sx__card-zone'), cName=q('.sx__card-name'), cMeta=q('.sx__card-meta'), cNear=q('.sx__near'),
        cOpen=q('.sx__card-open'), cOpenT=q('.sx__card-open span');
    var input=q('.sx__search input'), list=q('.sx__results'), clearBtn=q('.sx__clear'), locBtn=q('.sx__locate');
    var chips=all('.sx__zone'), regs=all('.sx__reg'), dir=q('.sx__dir'), count=q('.sx__count');
    var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var desktop=window.matchMedia('(min-width:1000px)');
    var s=1,tx=0,ty=0,sel=-1,zone='all',boxes=[],lbls=null,dragged=false,drag=null,active=-1,found=[];

    // ---- view
    function boxOf(i){
      if(!boxes[i]){var b=subs[i].querySelector('path').getBBox();boxes[i]=[b.x,b.y,b.x+b.width,b.y+b.height];}
      return boxes[i];
    }
    function unit(){var r=svg.getBoundingClientRect();return Math.min(r.width/W,r.height/H);}
    // Pan may run a third of the view past the map's edge once zoomed, so an edge suburb
    // (Box Hill, Lang Lang) can still be brought clear of the card instead of pinned under it.
    function clamp(){var mx=s>1.04?W*.34:0,my=s>1.04?H*.34:0;tx=Math.min(mx,Math.max(W-W*s-mx,tx));ty=Math.min(my,Math.max(H-H*s-my,ty));}
    function apply(animate){
      world.style.transition=(animate!==false&&!reduce)?('transform .8s '+EASE):'none';
      world.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')';
      // --k undoes both the zoom and the SVG's own render scale, so labels, pins and ring
      // text stay the same size on screen on a phone as on a desktop.
      world.style.setProperty('--k',String(1/(s*(unit()||1))));
      root.classList.toggle('is-zoomed',s>1.04);
      if(s>1.04)fitLabels();
    }
    function zoomTo(b,pad,max,fy,fx){
      var bw=Math.max(b[2]-b[0],1),bh=Math.max(b[3]-b[1],1);
      s=Math.min(max,Math.max(1,Math.min(W/(bw*pad),H/(bh*pad))));
      tx=W*(fx||.5)-s*((b[0]+b[2])/2);ty=H*(fy||.5)-s*((b[1]+b[3])/2);clamp();apply();
    }
    function zoomBy(f){var cx=(W/2-tx)/s,cy=(H/2-ty)/s;s=Math.min(12,Math.max(1,s*f));tx=W/2-s*cx;ty=H/2-s*cy;clamp();apply();}
    // labels are built on first zoom: 200+ <text> nodes the page never needs otherwise
    function fitLabels(){
      if(!lbls){
        lbls=[];
        for(var i=0;i<S.length;i++){
          var t=document.createElementNS(NS,'text');
          t.setAttribute('class','sx__lbl');t.setAttribute('x',S[i][6]);t.setAttribute('y',S[i][7]);
          t.setAttribute('text-anchor','middle');t.setAttribute('dominant-baseline','middle');
          t.setAttribute('data-z',ZN[S[i][2]][0]);t.textContent=S[i][0];
          labels.appendChild(t);lbls[i]=t;
        }
      }
      var u=unit()*s;
      for(var j=0;j<S.length;j++){var b=boxOf(j);lbls[j].classList.toggle('is-fit',(b[2]-b[0])*u>=S[j][0].length*6.4+10&&(b[3]-b[1])*u>=20);}
    }

    // ---- zones + directory
    function setZone(z,keepView){
      zone=z;root.dataset.zone=z;
      chips.forEach(function(c){var on=c.dataset.zone===z;c.classList.toggle('is-on',on);c.setAttribute('aria-pressed',on?'true':'false');});
      var n=0;
      regs.forEach(function(r){var show=(z==='all'||r.dataset.z===z);r.hidden=!show;if(show)n+=+r.dataset.n;});
      count.textContent=n+' suburbs';
      if(sel>-1&&z!=='all'&&ZN[S[sel][2]][0]!==z)deselect(true);
      if(!keepView)zoomTo(ZB[z],z==='all'?1:1.12,7);
    }

    // ---- selection
    function nearest(i,n){
      var out=[];
      for(var j=0;j<S.length;j++){if(j===i)continue;var dx=S[j][6]-S[i][6],dy=S[j][7]-S[i][7];out.push([dx*dx+dy*dy,j]);}
      out.sort(function(a,b){return a[0]-b[0];});
      return out.slice(0,n).map(function(o){return o[1];});
    }
    function mark(i,on){if(subs[i])subs[i].classList.toggle('is-sel',on);if(rows[i])rows[i].classList.toggle('is-sel',on);}
    function showCard(){card.hidden=false;if(!desktop.matches&&card.scrollIntoView)card.scrollIntoView({block:'nearest',behavior:reduce?'auto':'smooth'});}
    function select(i){
      if(sel>-1)mark(sel,false);
      sel=i;mark(i,true);
      var d=S[i],zk=ZN[d[2]];
      if(zone!=='all'&&zk[0]!==zone)setZone('all',true);
      cZone.innerHTML='<i class="sx__dot" style="--z:var(--z-'+zk[0]+')"></i>'+esc(zk[1]);
      cName.innerHTML=esc(d[0])+(d[1]?' <small>'+d[1]+'</small>':'');
      cMeta.textContent=RN[d[3]]+' · '+d[4]+' km² · '+(d[5]===0?'our studio is here':'about '+d[5]+' km from our Berwick studio');
      cNear.innerHTML='<span class="sx-kick">Nearby</span>'+nearest(i,5).map(function(j){return '<button type="button" data-i="'+j+'">'+esc(S[j][0])+'</button>';}).join('');
      cNear.hidden=false;cOpen.hidden=false;
      cOpen.href=subs[i].getAttribute('href');cOpenT.textContent='Open the '+d[0]+' page';
      showCard();
      // on desktop the card covers the lower left of the map, so aim up and to the right of it
      zoomTo(boxOf(i),3.6,12,desktop.matches?.34:.5,desktop.matches?.6:.5);
      // keep the directory in step without ever scrolling the page itself
      var r=rows[i];
      if(r&&desktop.matches){var reg=r.closest('details');if(reg&&!reg.open)reg.open=true;
        var dr=dir.getBoundingClientRect(),rr=r.getBoundingClientRect();
        if(rr.top<dr.top+44||rr.bottom>dr.bottom)dir.scrollTop+=rr.top-dr.top-dr.height/2;}
    }
    function note(title,text){
      if(sel>-1){mark(sel,false);sel=-1;}
      cZone.textContent='';cName.textContent=title;cMeta.textContent=text;cNear.hidden=true;cOpen.hidden=true;showCard();
    }
    function deselect(keepView){if(sel>-1)mark(sel,false);sel=-1;card.hidden=true;if(!keepView)zoomTo(ZB[zone],zone==='all'?1:1.12,7);}

    // ---- map events
    function subAt(e){var a=e.target.closest&&e.target.closest('a.sx__sub');return a?+a.dataset.i:-1;}
    svg.addEventListener('click',function(e){
      var i=subAt(e);if(i<0)return;
      if(dragged){e.preventDefault();return;}
      if(i===sel)return;                       // second click follows the link
      e.preventDefault();select(i);
    });
    svg.addEventListener('keydown',function(e){if(e.key!=='Enter')return;var i=subAt(e);if(i>-1&&i!==sel){e.preventDefault();select(i);}});
    var hot=-1;
    function setHot(i){if(hot===i)return;if(hot>-1&&rows[hot])rows[hot].classList.remove('is-hot');hot=i;if(i>-1&&rows[i])rows[i].classList.add('is-hot');}
    svg.addEventListener('pointermove',function(e){
      if(drag){
        var u=unit(),dx=(e.clientX-drag.x)/u,dy=(e.clientY-drag.y)/u;
        if(!dragged){if(Math.abs(dx)+Math.abs(dy)<=3)return;dragged=true;root.classList.add('is-dragging');svg.setPointerCapture(drag.id);}
        tx=drag.tx+dx;ty=drag.ty+dy;clamp();apply(false);return;
      }
      if(e.pointerType==='touch')return;
      var i=subAt(e);setHot(i);
      if(i<0){tip.hidden=true;return;}
      var d=S[i];
      tip.innerHTML='<b>'+esc(d[0])+'</b><span>'+(d[1]?d[1]+' · ':'')+(d[5]===0?'our studio':'~'+d[5]+' km from the studio')+'</span>';
      tip.hidden=false;
      var r=stage.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,flip=x>r.width-200;
      tip.style.left=(flip?x-14:x+14)+'px';tip.style.top=(y+16)+'px';tip.classList.toggle('is-flip',flip);
    });
    svg.addEventListener('pointerleave',function(){tip.hidden=true;setHot(-1);});
    // drag to pan once zoomed (mouse / pen). Touch is left to the page scroll.
    svg.addEventListener('pointerdown',function(e){dragged=false;if(e.pointerType==='touch'||s<=1.04||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,tx:tx,ty:ty};});
    function endDrag(){drag=null;root.classList.remove('is-dragging');}
    svg.addEventListener('pointerup',endDrag);svg.addEventListener('pointercancel',endDrag);

    // directory hover lights the suburb on the map
    dir.addEventListener('mouseover',function(e){var a=e.target.closest('a[data-i]');if(a&&subs[+a.dataset.i])subs[+a.dataset.i].classList.add('is-hot');});
    dir.addEventListener('mouseout',function(e){var a=e.target.closest('a[data-i]');if(a&&subs[+a.dataset.i])subs[+a.dataset.i].classList.remove('is-hot');});

    chips.forEach(function(c){c.addEventListener('click',function(){setZone(c.dataset.zone);});});
    all('.sx__ctls button').forEach(function(b){b.addEventListener('click',function(){
      var a=b.dataset.act;if(a==='in')zoomBy(1.6);else if(a==='out')zoomBy(1/1.6);else{deselect(true);setZone('all');}
    });});
    q('.sx__close').addEventListener('click',function(){deselect();});
    cNear.addEventListener('click',function(e){var b=e.target.closest('button[data-i]');if(b)select(+b.dataset.i);});

    // ---- search (combobox)
    function search(v){
      var n=v.trim().toLowerCase(),out=[];
      if(!n)return out;
      for(var i=0;i<S.length;i++){
        var nm=S[i][0].toLowerCase(),rank=-1;
        if(nm.indexOf(n)===0)rank=0;else if(nm.indexOf(' '+n)>-1)rank=1;else if(nm.indexOf(n)>-1)rank=2;else if(S[i][1]&&S[i][1].indexOf(n)===0)rank=3;
        if(rank>-1)out.push([rank,nm.length,S[i][5],i]);
      }
      // best match class first, then the shorter (more exact) name, then the closer suburb
      out.sort(function(a,b){return a[0]-b[0]||a[1]-b[1]||a[2]-b[2];});
      return out.slice(0,8).map(function(o){return o[3];});
    }
    function hi(name,n){var k=name.toLowerCase().indexOf(n);return k<0?esc(name):esc(name.slice(0,k))+'<mark>'+esc(name.slice(k,k+n.length))+'</mark>'+esc(name.slice(k+n.length));}
    function closeList(){list.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');active=-1;}
    function setActive(k){
      active=k;
      Array.prototype.forEach.call(list.children,function(li,j){li.setAttribute('aria-selected',j===k?'true':'false');});
      if(k>-1&&list.children[k]){input.setAttribute('aria-activedescendant',list.children[k].id);list.children[k].scrollIntoView({block:'nearest'});}
    }
    function render(){
      var v=input.value;clearBtn.hidden=!v;found=search(v);
      if(!v.trim()){closeList();return;}
      var n=v.trim().toLowerCase();
      list.innerHTML=found.length?found.map(function(i,k){var d=S[i];
        return '<li role="option" id="sx-opt-'+k+'" data-i="'+i+'" aria-selected="false"><i class="sx__dot" style="--z:var(--z-'+ZN[d[2]][0]+')"></i>'+
          '<span class="n">'+hi(d[0],n)+'</span><span class="m">'+(d[1]?d[1]+' · ':'')+(d[5]===0?'studio':d[5]+' km')+'</span></li>';}).join('')
        :'<li class="none" role="option" aria-disabled="true">No suburb matches that. Call Andy on 0410 939 700 and ask.</li>';
      list.hidden=false;input.setAttribute('aria-expanded','true');setActive(found.length?0:-1);
    }
    function choose(i){input.value=S[i][0];clearBtn.hidden=false;closeList();select(i);}
    input.addEventListener('input',render);
    input.addEventListener('focus',function(){if(input.value.trim())render();});
    input.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){if(list.hidden)render();if(!found.length)return;e.preventDefault();
        setActive((active+(e.key==='ArrowDown'?1:-1)+found.length)%found.length);}
      else if(e.key==='Enter'){if(!list.hidden&&found.length){e.preventDefault();choose(found[Math.max(active,0)]);}}
      else if(e.key==='Escape'){closeList();}
    });
    list.addEventListener('mousedown',function(e){e.preventDefault();});      // keep focus in the input
    list.addEventListener('click',function(e){var li=e.target.closest('li[data-i]');if(li)choose(+li.dataset.i);});
    input.addEventListener('blur',function(){setTimeout(closeList,120);});
    clearBtn.addEventListener('click',function(){input.value='';clearBtn.hidden=true;closeList();input.focus();});

    // ---- near me
    function place(g,x,y){g.style.transform='translate('+x+'px,'+y+'px) scale(var(--k,1))';g.removeAttribute('hidden');}
    locBtn.addEventListener('click',function(){
      if(!navigator.geolocation){note('Location isn’t available','Search for your suburb, or pick it on the map.');return;}
      locBtn.classList.add('is-busy');
      navigator.geolocation.getCurrentPosition(function(pos){
        locBtn.classList.remove('is-busy');
        var x=(pos.coords.longitude-P[0])*P[2]*P[3]+P[4], y=(P[1]-pos.coords.latitude)*P[3]+P[4];
        place(me,x,y);
        var hit=-1,best=1e18,pt=svg.createSVGPoint();pt.x=x;pt.y=y;
        for(var i=0;i<S.length;i++){
          var p=subs[i].querySelector('path');
          if(p.isPointInFill&&p.isPointInFill(pt)){var b=boxOf(i),a=(b[2]-b[0])*(b[3]-b[1]);if(a<best){best=a;hit=i;}}
        }
        if(hit<0){var bd=1e18;for(var j=0;j<S.length;j++){var dx=S[j][6]-x,dy=S[j][7]-y,dd=dx*dx+dy*dy;if(dd<bd){bd=dd;hit=j;}}
          if(Math.sqrt(bd)/PPK>4)hit=-1;}
        if(hit>-1){select(hit);return;}
        var sp=root.dataset.studio.split(',').map(Number),km=Math.round(Math.sqrt(Math.pow(x-sp[0],2)+Math.pow(y-sp[1],2))/PPK);
        note('A little outside our map','You’re about '+km+' km from our Berwick studio. We still take bookings from further out — call Andy on 0410 939 700.');
      },function(){
        locBtn.classList.remove('is-busy');
        note('Couldn’t get your location','No problem — search for your suburb above, or pick it on the map.');
      },{enableHighAccuracy:false,timeout:9000,maximumAge:600000});
    });

    // phones start with the regions folded; on desktop the directory scrolls in its own panel
    if(!desktop.matches)regs.forEach(function(r){r.open=false;});
    window.addEventListener('resize',function(){apply(false);},{passive:true});
    apply(false);
  }
  var els=document.querySelectorAll('.sx');for(var i=0;i<els.length;i++)init(els[i]);
})();
