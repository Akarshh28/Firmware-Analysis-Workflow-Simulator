import { Pipeline } from "../Types/pipeline";

export const defaultPipeline: Pipeline = {

id:"pipeline1",

name:"Firmware Analysis",

nodes:[

{

id:"1",

toolName:"binwalk",

status:"idle",

progress:0

},

{

id:"2",

toolName:"strings",

status:"idle",

progress:0

},

{

id:"3",

toolName:"entropy",

status:"idle",

progress:0

},

{

id:"4",

toolName:"ghidra",

status:"idle",

progress:0

},

{

id:"5",

toolName:"cutter",

status:"idle",

progress:0

},

{

id:"6",

toolName:"angr",

status:"idle",

progress:0

},

{

id:"7",

toolName:"pdf_report",

status:"idle",

progress:0

}

],

edges:[

{from:"1",to:"2"},

{from:"2",to:"3"},

{from:"3",to:"4"},

{from:"4",to:"5"},

{from:"5",to:"6"},

{from:"6",to:"7"}

]

};