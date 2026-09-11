import type {Decision} from '../../types/domain';
export type VisualState='idle'|'succeeded'|'warning'|'failed'|'skipped'|'matched'|'not_matched';
export function mapDecisionExecution(result:Decision|null){
  const state=(id:string):VisualState=>{if(!result)return'idle';if(id==='decision')return result.decision==='paywall'?'failed':result.decision==='allow_with_warning'?'warning':'succeeded';if(id==='consume')return result.consumed?'succeeded':'skipped';if(id==='meter')return result.meter.bypassed?'skipped':'succeeded';if(id==='policy')return result.decision==='paywall'?'failed':'matched';return'succeeded'};
  return {state};
}
