export function wavBlob(samples:Float32Array, sampleRate:number):Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2), view = new DataView(buffer);
  function text(offset:number,value:string){for(let i=0;i<value.length;i++)view.setUint8(offset+i,value.charCodeAt(i));}
  text(0,'RIFF');view.setUint32(4,36+samples.length*2,true);text(8,'WAVE');text(12,'fmt ');
  view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,sampleRate,true);
  view.setUint32(28,sampleRate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);text(36,'data');view.setUint32(40,samples.length*2,true);
  samples.forEach((sample,i)=>view.setInt16(44+i*2,Math.max(-1,Math.min(1,sample))*32767,true));
  return new Blob([buffer],{type:'audio/wav'});
}

// Short local PCM segments are sent to our backend, not to a browser speech service.
export async function startListening(onChunk:(blob:Blob)=>Promise<void>, onError:(error:Error)=>void):Promise<()=>void> {
  const stream = await navigator.mediaDevices.getUserMedia({audio:{channelCount:1},video:false});
  let context:AudioContext;
  try { context = new AudioContext({sampleRate:16000}); await context.resume(); }
  catch(error){stream.getTracks().forEach(t=>t.stop());throw error;}
  const source=context.createMediaStreamSource(stream), node=context.createScriptProcessor(4096,1,1);
  let chunks:Float32Array[]=[], count=0, closed=false, pending=false;
  node.onaudioprocess=event=>{
    if(closed || pending)return;
    const values=new Float32Array(event.inputBuffer.getChannelData(0));chunks.push(values);count+=values.length;
    if(count>=context.sampleRate*8){
      const merged=new Float32Array(count);let offset=0;for(const chunk of chunks){merged.set(chunk,offset);offset+=chunk.length;}
      chunks=[];count=0;
      if(Math.max(...merged.subarray(0,100))===0 && merged.every(v=>Math.abs(v)<.005))return;
      pending=true;onChunk(wavBlob(merged,context.sampleRate)).catch(error=>onError(error instanceof Error?error:new Error(String(error)))).finally(()=>{pending=false;});
    }
  };
  source.connect(node);node.connect(context.destination);
  return ()=>{closed=true;node.disconnect();source.disconnect();stream.getTracks().forEach(t=>t.stop());void context.close();};
}
