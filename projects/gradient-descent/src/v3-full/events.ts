// Single event table for GradientV3Full. Every frame comes from the one Fish alignment (word-level).
import al0 from './alignment.json';
import {Alignment,wordFrame} from '../v3-shared/words';
export const al=al0 as Alignment;
const w=(p:string,n=0)=>wordFrame(al,p,n);
export const G={
 ai:w('AI'),much:w('很大程度'),downhill:w('在下山'),shan:w('下山'),
 but:w('可是'),blind:w('看不见山'),err:w('只知道误差'),errWord:w('误差'),where:w('往哪走'),
 data:w('用学习时长'),score:w('预测成绩'),line:w('一条直线'),params:w('两个参数'),slope:w('斜率a'),intercept:w('截距b'),
 map:w('摊成'),eachPoint:w('每个点'),lift:w('把误差抬起来'),mountain:w('就成了山'),
 stand:w('站在这里'),alongA:w('沿a量坡'),alongB:w('沿b量坡'),combine:w('合起来'),negGrad:w('负梯度'),
 idea:w('这个想法'),y1847:w('一八四七'),cauchy:w('柯西'),fnSmall:w('让函数'),bianxiao:w('变小'),
 stepSize:w('但步子'),small:w('太小'),smallVal:w('一点一六五'),large:w('太大'),over:w('冲过'),largeVal:w('二点五五一'),ok:w('合适'),okVal:w('零点零五五'),
 walk:w('一步步走'),thisLine:w('这条线'),fit:w('贴上了数据'),
};
export const S={hook:0,data:G.data-4,teach:G.map-2,cauchy:G.idea-4,chalk:G.stepSize-4,end:G.walk-4};
export const DURATION=al.frames+40;
const rel=(f:number,base:number)=>f-base;
// teaching scene (reused v2 layout), local frames
const t=(f:number)=>rel(f,S.teach);
export const TEACH_T={
 planeIn:[0,14],axes:[6,22],target:[t(G.eachPoint)-10,t(G.eachPoint)+2],point:[t(G.eachPoint),t(G.eachPoint)+10],guides:[t(G.eachPoint)+8,t(G.eachPoint)+22],
 tilt:[t(G.lift),t(G.lift)+28],rise:[t(G.lift)+6,t(G.mountain)+4],proj:[t(G.mountain)-6,t(G.mountain)+6],labels:[t(G.mountain)-2,t(G.mountain)+10],bar:[t(G.lift)+10,t(G.mountain)+6],
 cut:t(G.stand),compA:[t(G.alongA),t(G.alongA)+14],compB:[t(G.alongB),t(G.alongB)+14],para:[t(G.combine),t(G.combine)+12],result:[t(G.combine)+6,t(G.combine)+22],fadeComp:[t(G.negGrad)-4,t(G.negGrad)+6],
 move:[t(G.negGrad)+2,t(G.negGrad)+22],side:[99998,99999],delta:[99998,99999],
} as const;
const c=(f:number)=>rel(f,S.chalk);
export const CHALK_E={start:c(S.chalk)+2,three:c(G.stepSize),small:c(G.small),smallVal:c(G.smallVal),large:c(G.large),over:c(G.over),largeVal:c(G.largeVal),ok:c(G.ok),okVal:c(G.okVal)};
