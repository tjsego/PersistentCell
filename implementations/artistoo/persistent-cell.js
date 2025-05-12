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
const prng = require( jsonFile )["artistoo"]["prng"]

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
	
	confChecker(){
		let checker = new CPM.ParameterChecker( this.conf, this.C )
		checker.confCheckParameter( "MU", "KindArray", "NonNegative" )
		checker.confCheckParameter( "XI", "KindArray", "NonNegative" )
		checker.confCheckParameter( "PROTRUDE", "KindArray", "Boolean" )
		checker.confCheckParameter( "RETRACT", "KindArray", "Boolean" )
	}
	
	correctTorusDim( p, dx, i ){
		if( dx > this.halfsize[i] ) return p - this.C.extents[i]
		if( dx < -this.halfsize[i] ) return p + this.C.extents[i]
		return p
	}
	
	correctTorus( pos, reference ){
		let dx = pos.map( (x, i) => pos[i] - reference[i] )
		pos = dx.map( (x,i) => this.correctTorusDim( pos[i], x, i ))
		return pos
	}
	
	
	vec( fromP, toP, normalize = true ){
		let a = []
		for( let i = 0 ; i < fromP.length ; i ++ ){
			a[i] = toP[i]-fromP[i]
			// Correct for torus if necessary
			if( this.C.grid.torus[i] ){
				if( a[i] > this.halfsize[i] ){
					a[i] -= this.C.extents[i]
				} else if( a[i] < -this.halfsize[i] ){
					a[i] += this.C.extents[i]
				}
			}
		}
		if( normalize ) this.normalize(a)
		return a
	}
	
	dot( v1, v2 ) {
		let dot = v1.reduce((acc, n, i) => acc + (n * v2[i]), 0)
		return(dot)
	}
	
	currentCentroid( cid ){
		if( !( cid in this.cellcentroidlists ) ){
			this.C.stat_values = {}
			let centroids = this.C.getStat( CPM.CentroidsWithTorusCorrection )
			this.cellcentroidlists = centroids
		}
		return this.cellcentroidlists[cid]
		
	}
	
	currentDirection( cid ){
		if( !(cid in this.celldirections ) ){
			this.celldirections[cid] = this.randDir(this.C.ndim)
		}
		return this.celldirections[cid]
	}
	
	
	centroidUpdate( sourcei, targeti, src_type, tgt_type ) {
	
		this.dC = { "src" : [0,0], "tgt" : [0,0] }
		
		// update src cell centroid because cell expands with one pix
		if( src_type > 0 ){
		
			let N = this.C.getVolume( src_type )
			let cenOld = this.currentCentroid( src_type )
			let pixAdded = this.correctTorus( this.C.grid.i2p( targeti ), cenOld )
			
			let cenNew = cenOld.map( (x,i) => (x * N + pixAdded[i]) / (N+1)  ) 
			this.dC.src = cenNew.map( (x,i) => x - cenOld[i] )
			
		}
		
		// update tgt cell centroid because cell loses one pix
		if( tgt_type > 0 ){
		
			let N = this.C.getVolume(tgt_type )
			let cenOld = this.currentCentroid( tgt_type )
			let pixRemoved = this.correctTorus( this.C.grid.i2p( targeti ), cenOld )
			
			let cenNew = cenOld.map( (x,i) => (x * N - pixRemoved[i]) / (N-1) ) 
			this.dC.tgt = cenNew.map( (x,i) => x - cenOld[i] )
		
		}
		
	}
	
	correctPosition( p ){
		if( p[0] < 0 ) p[0] += this.C.grid.extents[0]
		if( p[1] < 0 ) p[1] += this.C.grid.extents[1]
		if( p[0] >= this.C.grid.extents[0] ) p[0] -= this.C.grid.extents[0]
		if( p[1] >= this.C.grid.extents[1] ) p[1] -= this.C.grid.extents[1]
	}
	
	postSetpixListener( i, t_old, t_new ){
		if( t_old > 0 ){
			let cen = this.currentCentroid( t_old ).map( (x,i) => x + this.dC.tgt[i] )
			this.correctPosition(cen)
			this.cellcentroidlists[t_old] = cen
		}
		if( t_new > 0 ){
			let cen = this.currentCentroid( t_new ).map( (x,i) => x + this.dC.src[i] )
			this.correctPosition(cen)
			this.cellcentroidlists[t_new] = cen
		}
	}
	
	
	deltaH ( sourcei, targeti, src_type, tgt_type ) {
		
		let dH = 0 
		this.centroidUpdate( sourcei, targeti, src_type, tgt_type )
		
		// protrusion force:
		if( this.conf.PROTRUDE && src_type > 0 ){
			let b = this.currentDirection( src_type )
			let a = this.dC.src
			dH -= this.dot( a, b )
		}
		
		// retraction force:
		if( this.conf.RETRACT && tgt_type > 0 ){
			let b = this.currentDirection( tgt_type )
			let a = this.dC.tgt
			dH -= this.dot( a, b )
		}
		//if( Math.random() < 0.01 ) console.log(dH)
		return dH
	}
	
	// after each MCS, update the target direction with Gaussian angular noise.
	postMCSListener(){
		for( let cid of this.C.cellIDs() ){
			let mu = this.cellParameter( "MU", cid )
			let xi = this.cellParameter( "XI", cid )
			if( !(cid in this.celldirections ) ){
				this.celldirections[cid] = this.randDir(this.C.ndim)
			}
			this.normalize( this.celldirections[cid] )
			let alpha = Math.atan2( this.celldirections[cid][1], this.celldirections[cid][0])
			alpha += this.sampleNorm( 0, xi )
			this.celldirections[cid] = [Math.cos(alpha), Math.sin(alpha)].map( x => x * mu * this.C.getVolume(cid) )
		}
	}
}


let custommethods = {
	drawOnTop : drawOnTop,
	logStats : logStats
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
		let prefdir = new LangevinPRW( 
			{
				MU: [0,configJSON["model_args"]["mu"]], 
				XI: [0,configJSON["model_args"]["xi"]], 
				PROTRUDE: [false,true],
				RETRACT : [false,true]
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
