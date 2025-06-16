let CPM = require("./artistoo-cjs.js")
let fs = require('fs')

let jsonFile = process.argv[2] 
let seed = process.argv[3]
let configJSON = require( jsonFile )["model"]
let outputJSON = require( jsonFile )["sim"]


let img = true
if (seed > 1 ) img = false

const modelName = configJSON["model"]
const lograte = outputJSON["output_per"] || 2
const prng = require( jsonFile )["artistoo"]["prng"]
const out_name = require( jsonFile )["artistoo"]["output_name"]

if( configJSON["cpm_nbs_n"] != 2 ){
	throw( "cpm_nbs_n is set to a value different from 2, which is not (yet) supported. Please change value to 2 to continue.")
}
if( configJSON["cpm_surface_nbs_n"] != 2 ){
	throw( "cpm_surface_nbs_n is set to a value different from 2, which is not (yet) supported. Please change value to 2 to continue.")
}
if( modelName != "MODEL008" ){
	throw( "chemotaxis.js is only for MODEL008; did you mean to run persistent-cell.js?")
}

let outPath = "./results/"+ out_name + "/img"
fs.mkdirSync(outPath, { recursive: true })

let config = {

	field_size : [configJSON["len_1"],configJSON["len_2"]],
	conf : {
		torus : [true,true],					
		seed : seed,		
		T : configJSON["cpm_temperature"],			
		LAMBDA_V : [0,configJSON["cpm_area_v"]],					
		V : [0,configJSON["cpm_area_c"]],						
		LAMBDA_P : [0,configJSON["cpm_perim_v"]],
		P : [0,configJSON["cpm_perim_c"]]
	},
	simsettings : {
		NRCELLS : [1],					
		BURNIN : 0,
		RUNTIME : configJSON["max_time"],
		CANVASCOLOR : "eaecef",
		CELLCOLOR : ["CC0000"],	
		zoom : 3,							
		SAVEIMG : img,	
		IMGFRAMERATE : 10,	
		SAVEPATH : outPath,
		EXPNAME : configJSON["model"]+"-seed"+seed,		
		STATSOUT : { browser: false, node: true },
		LOGRATE : lograte

	}
}
/*	---------------------------------- */


let custommethods = {
	logStats : logStats,
	initializeGrid : initializeGrid,
	postMCSListener : postMCSListener,
	drawCanvas : drawCanvas
}
let sim = new CPM.Simulation( config, custommethods )
switch( prng ){
	case "MersenneTwister" : {
		// do nothing, this is the artistoo default
		break
	}
	case 'MathRandom' : {
		// replace the prng
		sim.C.random = function() { return Math.random() }
		break
	}
	default : {
		throw( "Unsupported random number generator " + prng  )
	}
	
}

// print header
console.log( "time,id,com_1,com_2,area,surface" )	

sim.g = new CPM.Grid2D(sim.C.extents, [true,true], "Float32"),
sim.gi = new CPM.CoarseGrid( sim.g, 1 ),
sim.C.add( new CPM.ChemotaxisConstraint( {
	LAMBDA_CH: [0,configJSON["model_args"]["lambda_chem"]],
	CH_FIELD : sim.gi }
) )

function postMCSListener(){
	let center = configJSON["model_args"]["chemo_source_position"]
	const Nds = configJSON["model_args"]["diffusion_steps_per_mcs"]
	
	const effective_prod = configJSON["model_args"]["chemo_production_rate_per_mcs"] / Nds
	const effective_D = configJSON["model_args"]["diffusion_coefficient_per_mcs"] / Nds
	const effective_decay = configJSON["model_args"]["chemo_decay_rate_per_mcs"] / Nds
	
	for( let i = 1 ; i <= Nds ; i ++ ){
		this.g.setpix( center, effective_prod+this.g.pixt(center) )
		this.g.diffusion( effective_D )
		this.g.multiplyBy( 1-effective_decay )
	}
	
}

function logStats( add = 1 ){
	let centroid = this.C.getStat( CPM.CentroidsWithTorusCorrection )[1]
	let area = this.C.cellvolume[1]
	let perim = this.C.getConstraint("PerimeterConstraint").cellperimeters[1]
	console.log( (this.time+add) + "," + seed + "," + centroid.join(",") + "," + area + "," + perim )		
}

function initializeGrid(){

	//this.C.setpix( [50,50], this.C.makeNewCellID( 1 ) )

	let pixList = outputJSON["init_voxels"]
	//console.log(pixList)
	const newID = this.C.makeNewCellID( 1 )
	for( let p of pixList ){
		this.C.setpix( p, newID )
	}
	
}

function drawCanvas(){
	if( !this.helpClasses["canvas"] ){ this.addCanvas() }
	this.Cim.drawField( this.g )
	this.Cim.drawCellBorders( 1, "000000" )
}

sim.drawCanvas()
sim.logStats(0)
sim.Cim.writePNG( "./results/"+ out_name + "/init.png" )

sim.run()
