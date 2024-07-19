let CPM = require("./src/artistoo-cjs.js")

 
let scaling = {
	dur : 1 * 0.2,
	len : 0.2,
	xi : 3
}

// parms in continuous parametrisation
let contParms = {
	radius : 1,
	area : Math.PI ,
	la : 10,
	perim : 2*Math.PI,
	lp : 5,
	mu : 20*0.5,
	k : -Math.log(0.5)/1
}

let cpmParms = {
	area : contParms.area / Math.pow( scaling.len, 2 ),
	la : contParms.la * Math.pow( scaling.len, 4 ),
	perim : contParms.perim / scaling.len * scaling.xi,
	lp : contParms.lp * Math.pow( scaling.len / scaling.xi, 2 ),
	mu : contParms.mu * scaling.dur * scaling.len,
	persist : contParms.k * scaling.dur
}

 // angular diffusion: normally distributed with mean 0 and variance omega / sqrt(mcs_d)


let config = {

	field_size : [100,100],
	conf : {
		torus : [true,true],					
		seed : 1,		
		T : 2*scaling.len,			
		LAMBDA_V : [0,cpmParms.la],					
		V : [0,cpmParms.area],						
		LAMBDA_P : [0,cpmParms.lp],
		P : [0,cpmParms.perim]
	},
	simsettings : {
		NRCELLS : [1],					
		BURNIN : 0,
		RUNTIME : 4000,
		CANVASCOLOR : "eaecef",
		CELLCOLOR : ["CC0000"],	
		zoom : 3,							
		SAVEIMG : true,	
		IMGFRAMERATE : 10,	
		SAVEPATH : "./results/img/example",
		EXPNAME : "example",		
		STATSOUT : { browser: false, node: true },
		LOGRATE : 10

	}
}
/*	---------------------------------- */


// add a drawOnTop method
let custommethods = {
	drawOnTop : drawOnTop
}
let sim = new CPM.Simulation( config, custommethods )



let pconstraint = new CPM.PersistenceConstraint( 
	{
		LAMBDA_DIR: [0,cpmParms.mu], 
		PERSIST: [0,cpmParms.persist],
		DELTA_T : [0,30]
	} 
)
sim.C.add( pconstraint )


function drawOnTop(){

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
}
	

sim.run()
