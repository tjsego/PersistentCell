let CPM = require("./src/artistoo-cjs.js")

let scaling = {
	dur : 0.5 * 0.2,
	len : 0.2,
	xi : 1
}

// parms in continuous parametrisation
let contParms = {
	radius : 1,
	area : Math.PI ,
	la : 10,
	perim : 2*Math.PI,
	lp : 5,
	mu : 0.5,
	omega : 0.25
}

let cpmParms = {
	area : contParms.area / Math.pow( scaling.len, 2 ),
	la : contParms.la * Math.pow( scaling.len, 4 ),
	perim : contParms.perim / scaling.len * scaling.xi,
	lp : contParms.lp * Math.pow( scaling.len / scaling.xi, 2 ),
	mu : contParms.mu * scaling.dur * scaling.len,
	omega : contParms.omega
}

 // angular diffusion: normally distributed with mean 0 and variance omega / sqrt(mcs_d)


let config = {

	field_size : [800,800],
	conf : {
		torus : [true,true],					
		seed : 1,		
		T : scaling.len,			
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
		CELLCOLOR : ["00FF00"],	
		zoom : 1,							
		SAVEIMG : false,	
		IMGFRAMERATE : 1,	
		SAVEPATH : "./",
		EXPNAME : "x",		
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
		LAMBDA_DIR: [0,100], 
		PERSIST: [0,.7]	
	} 
)
sim.C.add( pconstraint )


function drawOnTop(){

	let pdc = this.C.getConstraint( "PersistenceConstraint" )
	let ctx = this.Cim.context(), zoom = this.conf["zoom"]
	let prefdir = ( pdc.conf["LAMBDA_DIR"][ cellkind+1 ] > 0  ) || false
	ctx.beginPath()
	ctx.lineWidth = 2*zoom

	for( let i of this.C.cellIDs() ){
		
		// Only draw for cells that have a preferred direction.
		//if( i == 0 ) continue
		prefdir = ( pdc.conf["LAMBDA_DIR"][ this.C.cellKind( i ) ] > 0  ) || false
		if( !prefdir ) continue
			
		ctx.moveTo( 
			pdc.cellcentroidlists[i][0][0]*zoom,
			pdc.cellcentroidlists[i][0][1]*zoom)
		ctx.lineTo( (pdc.cellcentroidlists[i][0][0]+.1*pdc.celldirections[i][0])*zoom,
			(pdc.cellcentroidlists[i][0][1]+.1*pdc.celldirections[i][1])*zoom)
	}
	ctx.stroke()		
}
	

sim.run()
