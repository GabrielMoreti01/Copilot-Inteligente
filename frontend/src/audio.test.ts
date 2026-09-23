import {describe,it,expect,vi,afterEach} from 'vitest';
import {wavBlob} from './audio';
import {api,json} from './api';
describe('contratos do cliente',()=>{
 afterEach(()=>vi.unstubAllGlobals());
 it('produz WAV PCM mono válido',async()=>{const blob=wavBlob(new Float32Array([0,.5,-.5]),16000);const bytes=await blob.arrayBuffer();const view=new DataView(bytes);expect(view.getUint32(24,true)).toBe(16000);expect(view.getUint16(22,true)).toBe(1);expect(view.getUint32(40,true)).toBe(6);expect(view.getInt16(46,true)).toBe(16383);});
 it('envia JSON para a API local',async()=>{const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({id:'trip'})});vi.stubGlobal('fetch',fetch);expect(await api('/trips',json({modo:'demo'}))).toEqual({id:'trip'});expect(fetch).toHaveBeenCalledWith('/api/trips',expect.objectContaining({method:'POST'}));});
 it('propaga erro de serviço indisponível',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,json:async()=>({detail:'Modelo indisponível'})}));await expect(api('/config')).rejects.toThrow('Modelo indisponível');});
});
