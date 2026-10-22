"""Checks every instrument x tuning x scale x key: positions interlock, run stepwise, fingers 0-4.
Run after build.py:  python3 tests/verify_positions.py"""
import asyncio, json, collections, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':900,'height':400})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+ROOT+'/dist/finger-this/index.html'); await pg.wait_for_timeout(400)
        res = await pg.evaluate('''()=>{const f=window.__fretwise,out=[];
          for(const ins of Object.keys(f.INSTR))for(let ti=0;ti<f.INSTR[ins].tun.length;ti++)for(const sc of f.SCALES)for(const [kn,k] of f.KEYS){
            Object.assign(f.S,{instr:ins,key:k,scale:sc.id,notes:'scale',layout:'pos',route:'full',begin:'root'});f.S.tun[ins]=ti;
            const t0=performance.now();let M;try{M=f.buildModel();}catch(e){out.push({ins,ti,sc:sc.id,kn,err:String(e)});continue;}const dt=performance.now()-t0;
            const P=M.positions;let inter=true,step=true,fing=true;
            for(let i=0;i+1<P.length;i++)for(let k=0;k<M.n;k++)if(P[i].T[k]!==P[i+1].B[k])inter=false;
            const sm=[];for(let m=0;m<200;m++)if(M.pcs.has(m%12))sm.push(m);
            for(const p of P){for(let j=1;j<p.notes.length;j++){const a=sm.indexOf(p.notes[j-1].m),b=sm.indexOf(p.notes[j].m);if(b!==a+1)step=false;}
              for(const x of p.notes)if(!(x.finger>=0&&x.finger<=4))fing=false;}
            out.push({ins,ti,sc:sc.id,kn,n:P.length,inter,step,fing,sp:Math.max(...P.map(p=>p.whi-p.wlo)),hi:Math.max(...P.map(p=>p.whi)),lo:P[0]?P[0].wlo:-1,dt});}
          return out;}''')
        errs2=[r for r in res if 'err' in r];print('ERRS',len(errs2),errs2[:6]);res=[r for r in res if 'err' not in r];bad=[r for r in res if not(r['inter'] and r['step'] and r['fing'])]
        print('combos',len(res),'bad',len(bad), bad[:5])
        c=collections.Counter((r['ins'],r['ti'],r['n']) for r in res); print(sorted(c.items()))
        sp=collections.Counter((r['ins'],r['ti'],r['sp']) for r in res); print(sorted(sp.items()))
        print('max ms', max(r['dt'] for r in res))
        short=[(r['ins'],r['ti'],r['sc'],r['kn'],r['n']) for r in res if r['n']<7]; print('short sample',short[:30])
        print('errors',errs); await b.close()
asyncio.run(main())
