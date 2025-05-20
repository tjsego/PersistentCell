let CPM = require("./src/artistoo-cjs.js")
let PRW = require( "./src/PRWextensions.js")
let fs = require('fs')

let jsonFile = "./" + process.argv[2] 
let seed = process.argv[3]
let configJSON = require( jsonFile )["model"]
let outputJSON = require( jsonFile )["sim"]


let img = true
if (seed > 1 ) img = false

const modelName = configJSON["model"]
const lograte = outputJSON["output_per"] || 2
const prng = require( jsonFile )["artistoo"]["prng"]

if( configJSON["cpm_nbs_n"] != 2 ){
	throw( "cpm_nbs_n is set to a value different from 2, which is not (yet) supported. Please change value to 2 to continue.")
}
if( configJSON["cpm_surface_nbs_n"] != 2 ){
	throw( "cpm_surface_nbs_n is set to a value different from 2, which is not (yet) supported. Please change value to 2 to continue.")
}
if(  configJSON["model"] == "MODEL005" ){
	if( configJSON["model_args"]["cpm_force_mode"] != "extension" ){ 	throw( "only cpm_force_mode 'extension' is currently supported in MODEL005. Please change to continue.") }
}
if(  configJSON["model"] == "MODEL005" ){
	if( configJSON["model_args"]["cpm_update_direction"] != "source-to-target-unnorm" ){ throw( "only cpm_update_direction 'source-to-target-unnorm' is currently supported in MODEL005. Please change to continue.") }
}

let outPath = "./results/"+ modelName + "/img/sim" + seed
if (!fs.existsSync(outPath)){
    fs.mkdirSync(outPath)
}

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
		RUNTIME : configJSON["max_time"]+1,
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
	initializeGrid : initializeGrid
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

switch( modelName ){
	
	case 'MODEL000' : {
		// no additional terms to add
		break
	}
	case 'MODEL005' : {
		sim.C.add( new CPM.PersistenceConstraint( 
			{
				LAMBDA_DIR: [0,configJSON["model_args"]["lambda_dir"]], 
				PERSIST: [0,configJSON["model_args"]["persist"]],
				DELTA_T : [0,configJSON["model_args"]["dt"]]
			} ) )
		break
	}
	case 'MODEL003' : {
		const alpha = configJSON["model_args"]["target_angle"]
		let dir_map = { 'source-to-target-unnorm' : "copyVector", 'source-to-target-norm' : "normCopyVector", 'cell-mass-displacement' : "COM" }
		const propdir = dir_map[ configJSON["model_args"]["cpm_update_direction"] ]		
		sim.C.add( new PRW.TargetDirection( 
			{
				LAMBDA_DIR: [0,configJSON["model_args"]["lambda_dir"]], 
				DIR: [[0,0], [Math.cos(alpha),Math.sin(alpha)]],
				FORCE_MODE : configJSON["model_args"]["cpm_force_mode"],
				PROPOSAL_DIR: propdir
			} ) )
		break
	}
	case 'MODEL006' : {
		
		let dir_map = { 'source-to-target-unnorm' : "copyVector", 'source-to-target-norm' : "normCopyVector", 'cell-mass-displacement' : "COM" }
		const propdir = dir_map[ configJSON["model_args"]["cpm_update_direction"] ]		
		sim.C.add( new PRW.LangevinPRW( 
			{
				LAMBDA_DIR:  [0,configJSON["model_args"]["lambda_dir"]], 
				XI: [0,configJSON["model_args"]["xi"]], 
				FORCE_MODE : configJSON["model_args"]["cpm_force_mode"],
				PROPOSAL_DIR: propdir
			} ) )
			break
	}
	default : {
		throw( "Unsupported model " + modelName  )
	}
}


function logStats(){
	let centroid = this.C.getStat( CPM.CentroidsWithTorusCorrection )[1]
	let area = this.C.cellvolume[1]
	let perim = this.C.getConstraint("PerimeterConstraint").cellperimeters[1]
	console.log( this.time + "," + seed + "," + centroid.join(",") + "," + area + "," + perim )		
}

function initializeGrid(){
	let pixList = outputJSON["init"]
	const newID = this.C.makeNewCellID( 1 )
	for( let p of pixList ){
		this.C.setpix( p, newID )
	}
	
}

sim.drawCanvas()
sim.Cim.writePNG( "./results/"+ modelName + "/init.png" )

sim.run()
