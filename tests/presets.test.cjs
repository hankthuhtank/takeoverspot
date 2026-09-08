const {test}=require('node:test');
const assert=require('node:assert/strict');
const {catalog,create}=require('../canvas-presets.js');
const longBrand='The Independent Architecture and Creative Design Company of North America';
const motions=new Set(['none','float','pulse','drift','glow','tilt','marquee','bounce','spin','shake','zoom','sweep','orbit','morph','flicker']);
test('32 distinct complete compositions, with an animated majority',()=>{
  assert.equal(catalog.length,32);assert.equal(new Set(catalog.map(p=>p.key)).size,32);
  assert.ok(catalog.filter(p=>p.motion!=='none').length>=20);
  const signatures=catalog.map(p=>JSON.stringify(create(p.key,{brand:'ACME'})));
  assert.equal(new Set(signatures).size,32);
});
for(const preset of catalog)test(preset.name+' uses the supported canvas schema at every territory proportion',()=>{
  for(const aspect of [.25,.5,1,2,4])for(const brand of ['ACME',longBrand])for(const logo of ['','https://example.com/logo.png']){
    const c=create(preset.key,{brand,site:'example.com',aspect,logo,photo:'https://example.com/photo.jpg'});
    assert.ok(c.layers.length>0&&c.layers.length<=12);
    assert.ok(c.layers.some(l=>l.type==='text'&&l.text===brand),'Do not truncate the company name');
    assert.equal(new Set(c.layers.map(l=>l.id)).size,c.layers.length);
    for(const l of c.layers){
      assert.ok(['text','image','shape','button'].includes(l.type));
      assert.ok(Number.isFinite(l.x)&&Number.isFinite(l.y)&&Number.isFinite(l.w)&&Number.isFinite(l.h));
      assert.ok(l.x>=-25&&l.x<=125&&l.y>=-25&&l.y<=125,JSON.stringify(l));
      assert.ok(l.w>=5&&l.w<=150&&l.h>=5&&l.h<=150,JSON.stringify(l));
      assert.ok(motions.has(l.motion||'none'));
      if(l.type==='text'){
        assert.ok(l.size>=8&&l.size<=96);
        assert.ok(l.x>=0&&l.y>=0&&l.x+l.w<=100.01&&l.y+l.h<=100.01,JSON.stringify(l));
      }
    }
    if(preset.motion!=='none')assert.ok(c.layers.some(l=>l.motion&&l.motion!=='none'));
  }
});
