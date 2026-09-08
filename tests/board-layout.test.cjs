const {test}=require('node:test');
const assert=require('node:assert/strict');
const {measureBoard,containFrame}=require('../board-view.js');

const viewports=[[320,568],[360,800],[390,844],[430,932],[768,1024],[1024,768],[1366,768],[1440,900],[1920,1080],[844,390],[2560,1080]];
for(const [width,height] of viewports){
  test(`All 16 remain visible at ${width}×${height}, including wrapped header`,()=>{
    for(const chrome of [100,170,250]){
      const h=Math.max(50,height-chrome),b=measureBoard(width,h);
      assert.equal(b.size,Math.min(width,h));
      assert.ok(b.left>=0&&b.top>=0);
      assert.ok(b.left+b.size<=width+.01);
      assert.ok(b.top+b.size<=h+.01);
      assert.equal(b.width,width);assert.equal(b.height,h);
    }
  });
  test(`Every cell is reachable with square geometry at ${width}×${height}`,()=>{
    const h=Math.max(50,height-170);
    for(const zoom of [1,1.5,2,3,4]){
      const b=measureBoard(width,h,zoom);
      for(let n=0;n<16;n++){
        const x=b.left+(n%4+.5)*b.size/4,y=b.top+(Math.floor(n/4)+.5)*b.size/4;
        const scrollX=Math.max(0,Math.min(b.width-width,x-width/2));
        const scrollY=Math.max(0,Math.min(b.height-h,y-h/2));
        assert.ok(x>=scrollX&&x<=scrollX+width);
        assert.ok(y>=scrollY&&y<=scrollY+h);
      }
    }
  });
}
test('All sixteen territory aspect ratios fit the editor without squeezing or overflow',()=>{
  for(let cols=1;cols<=4;cols++)for(let rows=1;rows<=4;rows++){
    for(const [w,h] of [[280,250],[340,300],[760,520],[230,170]]){
      const f=containFrame(w,h,cols/rows);
      assert.ok(f.width<=w+.001&&f.height<=h+.001);
      assert.ok(Math.abs(f.width/f.height-cols/rows)<.00001);
      assert.ok(Math.abs(f.width-w)<.001||Math.abs(f.height-h)<.001);
    }
  }
});
