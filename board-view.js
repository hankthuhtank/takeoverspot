/* One square coordinate system for artwork, hit targets, and territory masks. */
(function(root){
  'use strict';
  function measureBoard(width,height,zoom=1){
    const w=Math.max(1,width),h=Math.max(1,height);
    const fit=Math.min(w,h),size=fit*Math.max(1,Math.min(4,zoom));
    return {fit,size,width:Math.max(w,size),height:Math.max(h,size),left:Math.max(0,(w-size)/2),top:Math.max(0,(h-size)/2)};
  }
  function containFrame(width,height,aspect){
    const w=Math.min(Math.max(1,width),Math.max(1,height)*aspect);
    return {width:w,height:w/aspect};
  }
  if(typeof module==='object'&&module.exports){module.exports={measureBoard,containFrame};return;}
  const doc=root.document,byId=id=>doc.getElementById(id),board=byId('board');
  if(!board)return;
  const space=byId('boardSpace'),surface=byId('boardSurface'),map=byId('boardMap');
  let zoom=1,mode='fit',layout=null,queued=false,drag=null,suppressClick=false,editorObserved=false;
  const observer=new ResizeObserver(schedule);
  observer.observe(board);
  function schedule(){if(!queued){queued=true;requestAnimationFrame(()=>{queued=false;resize();fitEditor();});}}
  function resize(){
    const w=board.clientWidth,h=board.clientHeight;
    if(!w||!h)return;
    const cx=layout?(board.scrollLeft+w/2-layout.left)/layout.size:.5;
    const cy=layout?(board.scrollTop+h/2-layout.top)/layout.size:.5;
    if(mode==='fit')zoom=1;
    if(mode==='explore')zoom=Math.min(4,Math.max(w,h)/Math.min(w,h));
    layout=measureBoard(w,h,zoom);
    space.style.width=layout.width+'px';space.style.height=layout.height+'px';
    surface.style.width=layout.size+'px';surface.style.height=layout.size+'px';
    surface.style.left=layout.left+'px';surface.style.top=layout.top+'px';
    board.scrollLeft=cx*layout.size+layout.left-w/2;
    board.scrollTop=cy*layout.size+layout.top-h/2;
    const enlarged=zoom>1.01;
    board.classList.toggle('is-zoomed',enlarged);
    byId('boardNavigator').hidden=!enlarged;
    byId('boardFit').classList.toggle('active',!enlarged);
    byId('boardFit').setAttribute('aria-pressed',String(!enlarged));
    byId('boardExplore').classList.toggle('active',mode==='explore'&&enlarged);
    byId('boardExplore').setAttribute('aria-pressed',String(mode==='explore'&&enlarged));
    byId('boardZoomLevel').textContent=Math.round(zoom*100)+'%';
    byId('boardZoomOut').disabled=!enlarged;
    byId('boardZoomIn').disabled=zoom>=4;
    byId('boardViewHint').textContent=enlarged?'Drag to explore · map to jump':'Every spot. One page.';
    updateMap();
  }
  function setView(next,value){mode=next;zoom=value||zoom;resize();}
  byId('boardFit').onclick=()=>setView('fit');
  byId('boardExplore').onclick=()=>setView('explore');
  byId('boardZoomOut').onclick=()=>setView('manual',Math.max(1,zoom-.5));
  byId('boardZoomIn').onclick=()=>setView('manual',Math.min(4,zoom+.5));
  for(let n=1;n<=16;n++){
    const b=doc.createElement('button');b.type='button';b.textContent=String(n).padStart(2,'0');
    b.setAttribute('aria-label','View spot '+n);
    b.onclick=()=>{if(!layout)return;board.scrollTo({left:layout.left+((n-1)%4+.5)*layout.size/4-board.clientWidth/2,top:layout.top+(Math.floor((n-1)/4)+.5)*layout.size/4-board.clientHeight/2,behavior:'instant'});};
    map.appendChild(b);
  }
  function updateMap(){
    if(!layout)return;
    const frame=byId('boardMapWindow');
    frame.style.left=Math.max(0,(board.scrollLeft-layout.left)/layout.size)*100+'%';
    frame.style.top=Math.max(0,(board.scrollTop-layout.top)/layout.size)*100+'%';
    frame.style.width=Math.min(1,board.clientWidth/layout.size)*100+'%';
    frame.style.height=Math.min(1,board.clientHeight/layout.size)*100+'%';
  }
  board.addEventListener('scroll',updateMap,{passive:true});
  board.addEventListener('keydown',e=>{
    if(e.target!==board||zoom<=1)return;
    const moves={ArrowLeft:[-120,0],ArrowRight:[120,0],ArrowUp:[0,-120],ArrowDown:[0,120]};
    if(moves[e.key]){e.preventDefault();board.scrollBy(...moves[e.key]);}
    if(e.key==='Home'){e.preventDefault();setView('fit');}
  });
  board.addEventListener('pointerdown',e=>{
    suppressClick=false;
    if(e.pointerType!=='mouse'||e.button!==0||zoom<=1||e.target.closest('button'))return;
    drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:board.scrollLeft,top:board.scrollTop,moved:false};
  });
  board.addEventListener('pointermove',e=>{
    if(!drag||e.pointerId!==drag.id)return;
    const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
    if(!drag.moved&&Math.hypot(dx,dy)<6)return;
    drag.moved=true;e.preventDefault();board.setPointerCapture(e.pointerId);
    board.classList.add('is-dragging');board.scrollLeft=drag.left-dx;board.scrollTop=drag.top-dy;
  });
  function endDrag(){if(drag?.moved)suppressClick=true;drag=null;board.classList.remove('is-dragging');}
  board.addEventListener('pointerup',endDrag);
  board.addEventListener('pointercancel',endDrag);
  board.addEventListener('lostpointercapture',endDrag);
  board.addEventListener('dragstart',e=>{if(zoom>1)e.preventDefault();});
  board.addEventListener('click',e=>{if(suppressClick){e.preventDefault();e.stopImmediatePropagation();suppressClick=false;}},true);
  function fitEditor(){
    const stage=byId('canvasStage'),wrap=stage?.parentElement;
    if(!stage||!wrap||!wrap.clientWidth||!wrap.clientHeight)return;
    if(!editorObserved){observer.observe(wrap);editorObserved=true;}
    const style=getComputedStyle(wrap),parts=stage.style.aspectRatio.split('/').map(Number);
    const aspect=parts[0]/(parts[1]||1)||1;
    const frame=containFrame(wrap.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight),wrap.clientHeight-parseFloat(style.paddingTop)-parseFloat(style.paddingBottom),aspect);
    stage.style.setProperty('width',frame.width+'px','important');
    stage.style.setProperty('height',frame.height+'px','important');
  }
  root.TakeoverBoard={refresh(){
    [...map.children].forEach((b,i)=>{const action=byId('spotActions')?.children[i];b.classList.toggle('is-owned',!!action?.querySelector('.take-pill'));});
    schedule();
  },fitEditor:schedule};
  schedule();
})(typeof window!=='undefined'?window:globalThis);
