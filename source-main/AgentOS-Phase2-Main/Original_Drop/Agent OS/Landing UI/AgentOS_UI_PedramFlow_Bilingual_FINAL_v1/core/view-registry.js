import reg from './view-registry.json' assert { type: 'json' };
export const ViewRegistry={ resolve(path){ return reg.views.find(v=>v.path===path)||null; }, all(){return reg.views;} };
