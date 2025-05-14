let CPM = require("./src/artistoo-cjs.js")
let fs = require('fs')

let jsonFile = "./" + process.argv[2] 
let seed = process.argv[3]
let configJSON = require( jsonFile )["model"]
let outputJSON = require( jsonFile )["sim"]


let img = true
if (seed > 1 ) img = false

const modelName = configJSON["model"]
const lograte = outputJSON["output_per"] || 2

const surfN = configJSON["cpm_surface_nbs_n"]
if( surfN != 2 ){
	throw( "cpm_surface_nbs_n is set to " + surfN + ", but values other than 2 are not (yet) supported. Please change to continue.")
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

/* ============ Extend persistenceconstraint for MODEL006 dynamics */
class LangevinPRW extends CPM.PersistenceConstraint {
	
	confChecker(){}
	
	deltaH ( sourcei, targeti, src_type, tgt_type ) {
		if( src_type == 0 || !(src_type in this.celldirections) ) return 0
		let b = this.celldirections[src_type]
		let p1 = this.C.grid.i2p(sourcei), p2 = this.C.grid.i2p(targeti)
		let a = []
		for( let i = 0 ; i < p1.length ; i ++ ){
			a[i] = p2[i]-p1[i]
			// Correct for torus if necessary
			if( this.C.grid.torus[i] ){
				if( a[i] > this.halfsize[i] ){
					a[i] -= this.C.extents[i]
				} else if( a[i] < -this.halfsize[i] ){
					a[i] += this.C.extents[i]
				}
			}
		}
		let dp = 0
		for( let i = 0 ; i < a.length ; i ++ ){
			dp += a[i]*b[i]
		}
		return - dp
	}
	
	
}

// add a drawOnTop method
let custommethods = {
	drawOnTop : drawOnTop,
	logStats : logStats
}
let sim = new CPM.Simulation( config, custommethods )

// print header
console.log( "time,id,com_1,com_2,area,surface" )	

switch( modelName ){
	
	case 'MODEL000' : {
		let pconstraint = new CPM.PersistenceConstraint( 
			{
				LAMBDA_DIR: [0,0], 
				PERSIST: [0,0],
				DELTA_T : [0,10]
			} )
		sim.C.add( pconstraint )
		break
	}
	case 'MODEL005' : {
		let pconstraint = new CPM.PersistenceConstraint( 
			{
				LAMBDA_DIR: [0,configJSON["model_args"]["mu"]], 
				PERSIST: [0,configJSON["model_args"]["persist"]],
				DELTA_T : [0,configJSON["model_args"]["dt"]]
			} )
		sim.C.add( pconstraint )
		break
	}
	case 'MODEL003' : {
		const alpha = configJSON["model_args"]["target_angle"]
	
		let prefdir = new CPM.PreferredDirectionConstraint( 
			{
				LAMBDA_DIR: [configJSON["model_args"]["lambda_dir"],configJSON["model_args"]["lambda_dir"]], 
				DIR: [[Math.cos(alpha),Math.sin(alpha)], [Math.cos(alpha),Math.sin(alpha)]]
			} )
		sim.C.add( prefdir )
		// non-active persistence just for the visualization
		let pconstraint = new CPM.PersistenceConstraint( 
			{
				LAMBDA_DIR: [0,0.000001], 
				PERSIST: [0,0],
				DELTA_T : [0,5]
			} )
		sim.C.add( pconstraint )
		break
	}
	case 'MODEL006' : {
		const omega = configJSON["model_args"]["omega"]
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

function drawOnTop(){

	// ========= draw direction vectors on top
	let pdc = this.C.getConstraint( "PersistenceConstraint" )
	let ctx = this.Cim.context(), zoom = this.conf["zoom"]
	let prefdir = ( pdc.conf["LAMBDA_DIR"][ 1 ] > 0  ) || false
	ctx.beginPath()
	ctx.lineWidth = 2*zoom

	for( let i of this.C.cellIDs() ){
		
		// Only draw for cells that have a preferred direction.
		//if( i == 0 ) continue
		if( !prefdir ) continue

		
		function normalize( a ){
			let norm = 0
			for( let i = 0 ; i < a.length ; i ++ ){
				norm += a[i]*a[i]
			}
			norm = Math.sqrt(norm)
			b = []
			for( let i = 0 ; i < a.length ; i ++ ){
				b.push( a[i] / norm )
			}
			return b
		}
		let cdir = normalize(pdc.celldirections[i])
		
		ctx.moveTo( 
			pdc.cellcentroidlists[i][0][0]*zoom,
			pdc.cellcentroidlists[i][0][1]*zoom)
		ctx.lineTo( (pdc.cellcentroidlists[i][0][0]+5*cdir[0])*zoom,
			(pdc.cellcentroidlists[i][0][1]+5*cdir[1])*zoom)
	}
	ctx.stroke()		
	
	// ========= Add model title and time stamp
	const logger = configJSON["model"] + "; " +this.time + " MCS"
	ctx.font = "10px sans serif";
	ctx.fillStyle = "black"
	ctx.fillText(logger,6*zoom,6*zoom);
}

sim.run()
