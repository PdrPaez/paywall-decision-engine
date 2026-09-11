export type Subject = { subject_id:string; subject_type:string; display_name:string; device_id?:string|null };
export type Content = { content_id:string; title:string; access_tier:string; published:boolean };
export type Policy = { policy_id:string; matched:boolean; terminal:boolean; decision?:string|null; reason_code?:string|null; duration_ms:number };
export type TraceStep = { name:string; policy_id?:string|null; decision?:string; duration_ms?:number };
export type Decision = { decision_id:string; decision:string; reason_code:string; explanation:string; consumed:boolean; meter:{used:number;limit:number;remaining:number;bypassed:boolean}; subscription:{state:string;plan:string}; entitlements:string[]; trace_id:string; duration_ms:number; policies:Policy[]; trace:{steps:TraceStep[]} };
export type BillingResult = { event_id:string; accepted:boolean; duplicate:boolean; projection_applied:boolean; reason:string; projection_version?:number };
