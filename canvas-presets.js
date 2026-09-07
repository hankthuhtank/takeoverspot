/* Editable compositions, using only the existing structured-canvas schema. */
(function(root){
  'use strict';
  const catalog=[
    ['event-horizon','Event Horizon','Motion','orbit'],['solar','Solar Flare','Motion','glow'],
    ['aurora-studio','Aurora Studio','Motion','morph'],['chromatic','Chromatic','Motion','drift'],
    ['ribbon-club','Ribbon Club','Motion','sweep'],['night-swim','Night Swim','Motion','float'],
    ['satellite','Satellite','Motion','orbit'],['prism','Prism','Motion','tilt'],
    ['acid-house','Acid House','Bold','spin'],['hot-type','Hot Type','Bold','none'],
    ['electric-blue','Electric Blue','Bold','pulse'],['sticker-studio','Sticker Studio','Bold','tilt'],
    ['redline','Redline','Bold','sweep'],['supernova','Supernova','Bold','spin'],
    ['candy-shop','Candy Shop','Bold','bounce'],['ultraviolet','Ultraviolet','Bold','glow'],
    ['swiss','Swiss Standard','Minimal','none'],['negative','Negative Space','Minimal','none'],
    ['gallery','Gallery Wall','Minimal','none'],['cobalt','Cobalt Study','Minimal','none'],
    ['atelier','Atelier','Editorial','none'],['nocturne','Nocturne','Editorial','float'],
    ['issue-one','Issue No. 1','Editorial','none'],['cut-out','Cut & Paste','Editorial','drift'],
    ['terminal-02','Terminal 02','Technical','pulse'],['radar','Radar Room','Technical','orbit'],
    ['signal-lab','Signal Lab','Technical','marquee'],['blueprint-02','Blueprint 02','Technical','none'],
    ['photo-type','Photo / Type','Photo','none'],['contact-sheet','Contact Sheet','Photo','none'],
    ['afterimage','Afterimage','Photo','float'],['frame-by-frame','Frame by Frame','Photo','none']
  ].map(([key,name,category,motion])=>({key,name,category,motion}));
  function create(key,{uid,brand='YOUR BRAND',site='',logo='',photo='',aspect=1}={}){
    let counter=0;uid=uid||(()=>`preset-${++counter}`);aspect=Math.max(.25,Math.min(4,Number(aspect)||1));
    const c={version:1,display:'combined',bg:{type:'solid',color:'#f6f6f0'},layers:[]};
    const add=l=>{c.layers.push({id:uid(),z:1,...l});return l;};
    const bg=(a,b,angle=135)=>{c.bg=b?{type:'gradient',color:a,color2:b,angle}:{type:'solid',color:a};};
    const shape=(kind,x,y,w,h,color,motion='none',rotation=0,opacity=1)=>{
      // Circular ornaments stay circular in wide and tall territory templates.
      if(['ring','orb','star','spark','burst'].includes(kind)){const cx=x+w/2,cy=y+h/2;if(aspect>1)w/=aspect;else h*=aspect;x=cx-w/2;y=cy-h/2;}
      return add({type:'shape',shapeStyle:kind,x:Math.max(-25,Math.min(125,x)),y:Math.max(-25,Math.min(125,y)),w:Math.max(5,Math.min(150,w)),h:Math.max(5,Math.min(150,h)),bg:color,radius:['ring','orb'].includes(kind)?50:0,motion,rotation,opacity,z:0});
    };
    const text=(value,x,y,w,h,font,size,color,align='left',motion='none')=>{
      if(!value)return;
      // Fit a real company name rather than silently truncating it to a short demo.
      let fitted=size;const factor=['condensed','display'].includes(font)?.46:.64;
      for(;fitted>8;fitted--){const lines=String(value).split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(4*w/(factor*fitted)))),0);if(lines*fitted*1.14<=4*h/aspect)break;}
      const lines=String(value).split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(4*w/(factor*fitted)))),0);
      h=Math.max(h,aspect*fitted*1.14*lines/4);y=Math.min(y,97-h);
      return add({type:'text',text:value,x,y,w,h,font,size:fitted,color,align,motion,z:6});
    };
    const title=(color='#111111',font='heavy',x=8,y=31,w=84,h=35,size=36,align='left')=>{
      if(brand.length>32&&w<60){x=8;y=31;w=84;h=38;add({type:'shape',shapeStyle:'rect',x:6,y:28,w:88,h:45,bg:c.bg.color,z:4});}
      return text(brand,x,y,w,h,font,size,color,align);
    };
    const label=(value,color='#73736b',x=8,y=12,w=68)=>text(value,x,y,Math.min(w,(logo?72:96)-x),10,'mono',9,color);
    const foot=(color='#73736b',value=site||'MAKE YOURSELF KNOWN',x=8,y=80,w=84)=>text(value,x,y,w,11,'mono',9,color);
    const particles=(color,opacity=.45)=>shape('particles',0,0,100,100,color,'none',0,opacity);
    const photoPanel=(x,y,w,h)=>photo?add({type:'image',src:photo,x,y,w,h,fit:'cover',z:1}):shape('rect',x,y,w,h,'#7b8379');
    switch(key){
      case'event-horizon':bg('#070a14','#171c36');shape('ring',-8,1,116,98,'#6968fb','orbit');shape('ring',15,18,70,65,'#c7c0ff','pulse',0,.5);particles('#d4dcff',.42);label('TRANSMISSION / 001','#9ba7de');title('#ffffff','tech',12,33,76,30,31,'center');foot('#a7b5f4');break;
      case'solar':bg('#290609','#9f2117');shape('orb',28,-32,102,105,'#ff782a','glow');shape('ring',-18,37,83,83,'#ffb856','orbit',0,.65);label('A NEW ENERGY','#ffd3ac');title('#fff1d1','display',8,34,84,33,43);foot('#ffc9a4');break;
      case'aurora-studio':bg('#041d25','#0c123b');shape('blob',-23,-20,96,71,'#5ce5ad','morph',-24,.6);shape('blob',55,36,80,85,'#745cec','morph',28,.6);particles('#b9ffea',.35);label('ALWAYS IN GOOD COMPANY','#b8e8d6');title('#ffffff','modern',10,34,80,32,34,'center');foot('#b8e8d6');break;
      case'chromatic':bg('#e8e8f2');shape('capsule',-21,0,148,18,'#f36881','drift',-34,.8);shape('capsule',-15,32,138,18,'#6687fb','drift',-34,.8);shape('capsule',-9,67,135,18,'#d2ec42','drift',-34,.9);shape('rect',6,28,88,42,'#f5f5f2','none',0,.9);title('#1f2358','heavy',10,34,80,30,34);foot('#292f60');break;
      case'ribbon-club':bg('#140e28');shape('ribbon',-12,6,125,19,'#fc7461','sweep',-13);shape('ribbon',-10,75,125,16,'#bfabff','sweep',12);label('YOU FOUND US.','#bbaaee',9,24);title('#fff7ec','display',8,37,84,30,44);foot('#161025',site||'COME ON IN',12,81,76);break;
      case'night-swim':bg('#082629','#164a55');shape('ring',-26,34,90,90,'#59b9b0','float',0,.7);shape('ring',42,-38,103,103,'#a1d9cf','drift',0,.4);label('TAKE YOUR TIME','#9dd3c7');title('#efffef','editorial',11,31,78,35,35,'center');foot('#a3d6ce');break;
      case'satellite':bg('#131921');shape('ring',12,8,82,82,'#53616c','orbit');shape('orb',72,9,18,18,'#efcc76','float');shape('spark',7,67,24,24,'#c7e5db','spin');label('IN YOUR ORBIT','#bbc5cf');title('#f5f7ec','modern',10,36,80,31,34,'center');foot('#e4c77c');break;
      case'prism':bg('#221235','#542b6e');shape('diamond',-10,3,58,72,'#f28dbe','tilt',14,.65);shape('diamond',55,28,52,71,'#8096f5','tilt',-14,.75);shape('rect',6,29,88,42,'#26163b','none',0,.8);title('#fff0dc','serif',11,34,78,32,36,'center');label('A DIFFERENT PERSPECTIVE','#e6b9e5');foot('#e6b9e5');break;
      case'acid-house':bg('#d9f244');shape('burst',66,-4,40,40,'#262832','spin');shape('rect',0,72,100,28,'#282934');label('TURN IT UP.','#282934');title('#282934','display',7,30,86,37,46);foot('#d9f244');break;
      case'hot-type':bg('#ed431f');shape('rect',7,9,12,7,'#211e1c');label('INDEPENDENT / ORIGINAL','#211e1c',25,9,64);title('#211e1c','condensed',7,28,86,40,47);foot('#211e1c');break;
      case'electric-blue':bg('#1644f4');shape('spark',69,-4,39,39,'#b4edfa','pulse');shape('rect',7,76,86,6,'#d9f760');title('#ffffff','heavy',7,28,86,37,38);label('IMPOSSIBLE TO MISS','#dce5ff');foot('#dce5ff',site||'THIS WAY FORWARD',8,86);break;
      case'sticker-studio':bg('#f7df38');shape('cutout',-6,3,54,37,'#eb739f','tilt',-8);shape('spark',69,7,24,24,'#326dea','spin');shape('capsule',46,73,60,19,'#20282c','tilt',-9);label('HELLO, WORLD.','#20282c',9,16,67);title('#20282c','heavy',8,38,84,31,34);foot('#ffffff',site||'STICK AROUND',50,77,43);break;
      case'redline':bg('#ecefe8');shape('ribbon',-12,9,125,11,'#fa4928','sweep',-8);shape('rect',7,32,6,38,'#1b252a');title('#1b252a','condensed',18,32,75,38,43);foot('#fa4928');break;
      case'supernova':bg('#32117b');shape('burst',40,-21,80,80,'#fe654b','spin');shape('burst',-15,57,58,58,'#f4d25a','spin');shape('rect',6,30,88,40,'#32117b','none',0,.94);title('#fff4e1','display',10,34,80,30,42,'center');label('GOOD THINGS START HERE','#cfc0ff');foot('#d9c6ff');break;
      case'candy-shop':bg('#f6afd0');shape('capsule',-10,4,71,20,'#c43150','tilt',-24);shape('orb',67,57,43,43,'#faeb82','bounce');label('A LITTLE SOMETHING GOOD','#612b49',8,19);title('#612b49','heavy',8,36,84,33,35);foot('#612b49');break;
      case'ultraviolet':bg('#150729','#3a1076');shape('ring',45,-23,77,77,'#b59dff','glow');shape('capsule',-13,78,122,9,'#e9ff76','sweep',-11);particles('#cfc5ff',.35);title('#f5edff','tech',8,35,84,32,32);label('ON A DIFFERENT FREQUENCY','#beabfc');foot('#e9ff76');break;
      case'swiss':bg('#f4f4ec');shape('rect',7,9,8,8,'#ec412c');label('DESIGNED TO STAND OUT','#363934',22,9,70);title('#212521','heavy',7,33,86,37,36);shape('rect',7,76,86,5,'#212521');foot('#53584c',site||'A SPACE OF YOUR OWN',8,85);break;
      case'negative':bg('#171c1b');label('LESS, BUT BETTER.','#bbc1b5');title('#e7eadd','modern',8,42,75,31,29);shape('rect',85,39,7,35,'#dded93');foot('#9ba48f');break;
      case'gallery':bg('#faf9f5');shape('rect',8,8,84,65,'#dcded5');shape('rect',12,12,76,57,'#f3f3ec');title('#20241d','serif',18,28,64,32,31,'center');foot('#575e51',site||'SELECTED WORKS');break;
      case'cobalt':bg('#eff1e9');shape('rect',0,0,29,100,'#2348ce');label('STUDIO / ONLINE','#2348ce',36,14,57);title('#1e2d57','modern',36,35,57,35,28);foot('#2348ce',site||'TAKE A CLOSER LOOK',36,81,57);break;
      case'atelier':bg('#e9e4d6');label('AN INDEPENDENT PRACTICE','#575b4b');shape('rect',8,25,84,5,'#727a54');title('#303b2c','editorial',8,37,84,34,35);foot('#575b4b');break;
      case'nocturne':bg('#162321');shape('orb',62,-14,47,47,'#a59356','float',0,.7);label('MADE WITH INTENTION','#b9bda3');title('#f1ecdb','serif',10,33,80,35,34,'center');foot('#b9bda3');break;
      case'issue-one':bg('#efece3');text('01',73,7,20,18,'display',29,'#b64635','right');label('THE INDEPENDENT EDITION','#4c4942',8,10,60);shape('rect',8,28,84,5,'#252923');title('#252923','editorial',8,37,84,35,34);foot('#7a473b');break;
      case'cut-out':bg('#f1e8d7');shape('cutout',-8,2,66,34,'#e07a5d','drift',-6);shape('cutout',63,57,47,47,'#557458','float',8);shape('rect',7,29,85,43,'#f1e8d7','none',0,.96);title('#233329','editorial',11,35,78,33,35);foot('#233329');break;
      case'terminal-02':bg('#081813');label('● CONNECTION ESTABLISHED','#8ac59a');shape('rect',7,29,6,36,'#b6ef8d','pulse');title('#d3f4c6','mono',18,31,73,36,30);foot('#84bc92',site||'> YOUR NEXT GOOD FIND');break;
      case'radar':bg('#08262a');shape('ring',18,10,70,70,'#2c8b85','orbit');shape('ring',34,26,37,37,'#79cec0','pulse');shape('orb',72,8,14,14,'#d8ee9a','float');shape('rect',5,37,90,29,'#08262a','none',0,.94);title('#e4f9e5','tech',9,38,82,27,29);label('SIGNAL ACQUIRED','#8bd2c1');foot('#8bd2c1');break;
      case'signal-lab':bg('#e5ebe6');shape('rect',0,0,100,20,'#233933');text('SIGNAL / SIGNAL / SIGNAL',7,5,86,11,'mono',10,'#daeca8','left','marquee');shape('rect',7,32,7,11,'#7d9e68');shape('rect',18,32,7,21,'#536f47');shape('rect',29,32,7,32,'#29442e');title('#233933','modern',43,31,50,39,27);foot('#3f5b4d');break;
      case'blueprint-02':bg('#193f93');shape('rect',7,7,5,86,'#5074b8');shape('rect',7,7,86,5,'#5074b8');shape('ring',62,57,34,34,'#82a6dc');label('DRAWING / 001','#b8d1f4',20,18,71);title('#f3f7ff','mono',20,36,72,34,29);foot('#b8d1f4',site||'BUILT TO BE SEEN',20,80,70);break;
      case'photo-type':bg('#15201c');photoPanel(0,0,100,61);shape('rect',0,60,100,40,'#15201c');title('#f3f4e7','modern',8,64,84,23,28);label(photo?'IN FOCUS':'ADD YOUR PHOTO','#ffffff',8,9);break;
      case'contact-sheet':bg('#edeee6');photoPanel(7,7,48,65);shape('rect',58,7,35,65,'#c6cebb');text('01 /',64,13,24,12,'mono',12,'#4b5741');title('#253321','condensed',62,35,27,31,26);foot('#4b5741');break;
      case'afterimage':bg('#251c37');photoPanel(7,7,86,86);shape('rect',7,50,86,43,'#21142e','none',0,.9);shape('ring',67,1,30,30,'#ddc597','float');title('#f8e8d7','serif',13,57,74,27,31);label(photo?'AFTER THE MOMENT':'ADD YOUR PHOTO','#fff0dc',13,16);break;
      case'frame-by-frame':bg('#161a19');photoPanel(25,7,68,65);text('F\nR\nM',7,12,14,54,'mono',20,'#bdd795');title('#f5f4e9','condensed',7,77,86,17,25);break;
      default:return create('swiss',{uid,brand,site,logo,photo,aspect});
    }
    if(logo&&!['photo-type','contact-sheet','afterimage','frame-by-frame','issue-one'].includes(key)){
      add({type:'image',role:'logo',src:logo,x:77,y:10,w:15,h:15,fit:'contain',z:9});
    }
    return c;
  }
  const api={catalog,create};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.TakeoverPresets=api;
})(typeof window!=='undefined'?window:globalThis);
