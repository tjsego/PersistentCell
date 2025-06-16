let CPM = require("./artistoo-cjs.js")
let PRW = require( "./PRWextensions.js")
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


let outPath = "./results/"+ out_name + "/img"


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


switch( modelName ){
	
	case 'MODEL000' : {
		// no additional terms to add
		break
	}
	case 'MODEL005' : {
		let dir_map = { 'source-to-target-unnorm' : "copyVector", 'source-to-target-norm' : "normCopyVector", 'cell-mass-displacement' : "COM" }
		const propdir = dir_map[ configJSON["model_args"]["cpm_update_direction"] ]		
		sim.C.add( new PRW.PersistenceConstraint( 
			{
				LAMBDA_DIR: [0,configJSON["model_args"]["lambda_dir"]], 
				PERSIST: [0,0],
				DELTA_T : [0,configJSON["model_args"]["dt"]],
				FORCE_MODE : configJSON["model_args"]["cpm_force_mode"],
				PROPOSAL_DIR: propdir
			} ) )
		let a0 = configJSON["model_args"]["initial_alpha"]
		sim.C.getConstraint( "PersistenceConstraint" ).celldirections[1] = [Math.cos(a0),Math.sin(a0)]
		break
	}
	case 'MODEL003' : {
		const alpha = configJSON["model_args"]["target_angle"]
		let dir_map = { 'source-to-target-unnorm' : "copyVector", 'source-to-target-norm' : "normCopyVector", 'cell-mass-displacement' : "COM" }
		const propdir = dir_map[ configJSON["model_args"]["cpm_update_direction"] ]		
		const ldir = configJSON["model_args"]["lambda_dir"], dirvec = [Math.cos(alpha),Math.sin(alpha)]
		const wconf = {
			LAMBDA_DIR: [0, ldir], 
			DIR: [[0,0], dirvec ],
			FORCE_MODE : configJSON["model_args"]["cpm_force_mode"],
			PROPOSAL_DIR: propdir
		}
		//console.log( wconf )
		sim.C.add( new PRW.TargetDirection( wconf ) )
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
		let a0 = configJSON["model_args"]["initial_alpha"]
		sim.C.getConstraint( "LangevinPRW" ).celldirections[1] = [Math.cos(a0), Math.sin(a0)]
			break
	}
	default : {
		throw( "Unsupported model " + modelName  )
	}
}


function logStats( add = 1 ){
	let centroid = this.C.getStat( CPM.CentroidsWithTorusCorrection )[1]
	let area = this.C.cellvolume[1]
	let perim = this.C.getConstraint("PerimeterConstraint").cellperimeters[1]
	// fix time definition with +1 since the default simulation class does 
	// run step - create outputs - update time
	// rather than (as expected)
	// run step - update time - create outputs.
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

// print header
console.log( "time,id,com_1,com_2,area,surface" )	

// initial conditions
sim.drawCanvas()
sim.logStats( 0 )

sim.Cim.writePNG( "./results/"+ out_name + "/init.png" )

sim.run()
