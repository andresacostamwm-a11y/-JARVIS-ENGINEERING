export const DRAWING_SCHEMA_VERSION="1.0";
export interface JarvisNode{node_key:string;node_type:string;label:string;position:{x:number;y:number};asset_id?:string|null;data?:Record<string,unknown>}
export interface JarvisEdge{edge_key:string;source:string;target:string;label?:string|null;edge_type?:string;data?:Record<string,unknown>}
export interface JarvisDrawing{schema_version:string;name:string;drawing_type:string;viewport?:{x?:number;y?:number;zoom?:number};nodes:JarvisNode[];edges:JarvisEdge[]}
