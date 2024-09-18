let CPM = require("./src/artistoo-cjs.js")
let fs = require('fs')

let jsonFile = "./" + process.argv[2] 
let seed = process.argv[3]

let configJSON = require( jsonFile )


let img = true
if (seed > 1 ) img = false

let outPath = "./results/"+ configJSON["model"] + "/img/sim" + seed
if (!fs.existsSync(outPath)){
    fs.mkdirSync(outPath)
}

let config = {

	field_size : [configJSON["len_1"],configJSON["len_2"]],
	conf : {
		torus : [true,true],					
		seed : seed,		
		T : configJSON["cpm_temperature"],			
		LAMBDA_V : [0,configJSON["cpm_area_c"]],					
		V : [0,configJSON["cpm_area_v"]],						
		LAMBDA_P : [0,configJSON["cpm_perim_c"]],
		P : [0,configJSON["cpm_perim_v"]]
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
		LOGRATE : 10

	}
}
/*	---------------------------------- */


// add a drawOnTop method
let custommethods = {
	drawOnTop : drawOnTop,
	logStats : logStats
}
let sim = new CPM.Simulation( config, custommethods )

// print header
console.log( "TimeMCS" + "," + "cellID" + ",x,y" )	

let pconstraint = new CPM.PersistenceConstraint( 
	{
		LAMBDA_DIR: [0,configJSON["model_args"]["mu"]], 
		PERSIST: [0,configJSON["model_args"]["persist"]]
	} )
sim.C.add( pconstraint )

function logStats(){
	let centroid = this.C.getStat( CPM.CentroidsWithTorusCorrection )[1]
	console.log( this.time + "," + seed + "," + centroid.join(",") )		
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
