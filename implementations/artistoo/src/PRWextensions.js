'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

var CPMfile = __dirname + '/artistoo-cjs.js'
var CPM = _interopDefault(require(CPMfile));

/** Version of the {@link SoftConstraint} meant specifically for creating 
 * "work terms" defined on $\Delta H$ level. 
 * 
 * Assuming there is some 
 * target direction $\vec{b}$ or $\vec{b}(\sigma)$ (defined on global or cell level), the 'work' associated with 
 * the  proposed movement $\vec{dx}$ associated with copy attempt $s \rightarrow t$ 
 * involving cells with {@link CellId} $\sigma_s, \sigma_t$ is defined as: 
 * 
 * $$ \Delta H_\text{dir} = \delta_s \lambda_\text{dir}(\sigma_s) \left( \vec{dx}(\sigma_s) \cdot \vec{b}(\sigma_s) \right) + \delta_t \lambda_\text{dir}(\sigma_t) \left( \vec{dx}(\sigma_t) \cdot \vec{b}(\sigma_t) \right) $$
 * 
 * 
 * where $\lambda_\text{dir}$, $(\delta_s,\delta_t)$ and the exact definition of $\vec{dx}$ 
 * depend on 
 * the configuration (see {@link WorkTerm#constructor} below). $\vec{b}$ and its temporal dynamics (if any)
 * are defined in the subclass.
 * 
 * Note that when $\vec{dx}$ and $\vec{b}$ are both normalized, the dot product is equal 
 * to the cosine of their angle (i.e. 1 if perfectly aligned and -1 if opposite).
 * 
 * This constraint works with torus (periodic boundaries) as long as the field size is "large enough". 
 * 
 * @experimental 
 * */

 
class WorkTerm extends CPM.SoftConstraint {



	/** The constructor of a WorkTerm requires a conf
	 * object with several parameters.
	 * @param {object} conf - parameter object for this constraint.
	 * @param {PerKindNonNegative} conf.LAMBDA_DIR - magnitude of the force exerted on the cell.
	 * @param {PerKindNonNegative} conf.DELTA_T - number of MCS used to track the "recent" displacement of the cell centroid.
	 * @param {string} conf.FORCE_MODE - set to "extension" ($\delta_s = 1, \delta_t = 0$), "retraction" ($\delta_s = 0, \delta_t = 1$), or "reciprocal" ($\delta_s = 1, \delta_t = 1$).
	 * @param {string} conf.PROPOSAL_DIR - define $\vec{dx}$ as the "copyVector" (from $s \rightarrow t$, unnormalized),  "normCopyVector" (idem, but normalized to unit length), or "COM" (the centroid displacement that this copy attempt would induce for this cell, multiplied by the current number of pixels in that cell.)
	 * */
	constructor(conf){
		super(conf)
		
		/** Cache centroids over the previous conf.DELTA_T MCS to determine directions.
		@type {CellObject}
		*/
		this.cellcentroidhistory = {}
		
		/** Can be used to track centroids after each copy (important for efficiency 
		* in COM-based terms).
		@type {CellObject}
		*/
		this.cellcentroids = {}
		this.pixelSum  = true
		
		/** Target direction of movement of each cell.
		@type {CellObject}
		*/
		this.celldirections = {}
		
	}
	
	/** this function samples a random number from a normal distribution
	@param {number} [mu=0] - mean of the normal distribution.
	@param {number} [sigma=1] - SD of the normal distribution.
	@return {number} the random number generated.
	@private
	*/
	sampleNorm (mu=0, sigma=1) {
		let u1 = this.C.random()
		let u2 = this.C.random()
		let z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(Math.PI*2 * u2)
		return z0 * sigma + mu
	}
	
	/** This function samples a random direction vector with length 1. Specifically, 
	* it samples each coordinate from a standard Gaussian and normalizes the resulting vector.
	@param {number} [n=3] - number of dimensions of the space to make the vector in.
	@return {number[]} - a normalized direction vector.
	*/
	randDir (n=3) {
		let dir = []
		while(n-- > 0){
			dir.push(this.sampleNorm())
		}
		this.normalize(dir)
		return dir
	}
	
	/** Retrieve the current centroid of a cell.
	* @param {CellId} [cid] - the cell to get the centroid of.
	* @return {ArrayCoordinate} - position of the centroid.
	*/
	currentCentroid( cid ){
		if( !( cid in this.cellcentroids ) ){
			this.C.stat_values = {}
			let centroids = this.C.getStat( CPM.CentroidsWithTorusCorrection )
			if( this.pixelSum ){
				for( let cid of this.C.cellIDs() ){
					this.cellcentroids[cid] = centroids[cid].map( x => Math.round( x * this.C.getVolume(cid) ) )
				}
			} else {
				this.cellcentroids = centroids
			}
		}
		
		
			return this.cellcentroids[cid]
			
		
	}
	
	/* TO DO specifically if COM-based, we cache updated centroids after each event.*/
	postSetpixListener( pix_i, t_old, t_new ){
			
		let targetPixel = this.C.grid.i2p( pix_i ) 
		
		if( t_old > 0 ){
		
			const N = this.C.getVolume( t_old )
			let cen = this.currentCentroid( t_old )

			this.cellcentroids[t_old] = cen.map( (x,i) => {
				let targeti = this.correctTorusDim( targetPixel[i], targetPixel[i]-(x/N) , i )
				let xnew = ( x - targeti )
				let grid_dim = this.C.grid.extents[i]
				if( xnew/N < 0 ) xnew += N*grid_dim
				if( xnew/N >= grid_dim ) xnew -= N*grid_dim
				return  xnew
			})
			
		}
		if(  t_new > 0 ){
		
			
			let N = this.C.getVolume( t_new )			
			let cen = this.currentCentroid( t_new )
			
			this.cellcentroids[t_new] = cen.map( (x,i) => {
				let targeti = this.correctTorusDim( targetPixel[i], targetPixel[i]-(x/N) , i )
				let xnew = ( x + targeti )
				let grid_dim = this.C.grid.extents[i]
				if( xnew/N < 0 ) xnew += N*grid_dim
				if( xnew/N >= grid_dim ) xnew -= N*grid_dim
				return  xnew
			})
		}
	}
	
	/** Retrieve the current target direction of a cell.
	* @param {CellId} [cid] - the cell to get the direction of.
	* @return {number[]} - the direction.
	*/
	currentDirection( cid ){
		if( !(cid in this.celldirections ) ){
			this.celldirections[cid] = this.randDir(this.C.ndim)
		}
		return this.celldirections[cid]
	}
	
	/** This method checks that all required parameters for the {@link WorkTerm} are present in the object supplied to
	the constructor, and that they are of the right format. It throws an error when this
	is not the case.*/
	generalConfChecker(){
		
		/** attach ParameterChecker so it can be used for the subclass confChecker as well.
		@private
		@type {Object}
		*/
		this.checker = new CPM.ParameterChecker( this.conf, this.C )
		this.checker.confCheckParameter( "LAMBDA_DIR", "KindArray", "NonNegative" )
		//this.checker.confCheckParameter( "DELTA_T", "KindArray", "NonNegative" )
		this.checker.confCheckParameter( "FORCE_MODE", "SingleValue", "String", [ "extension", "retraction", "reciprocal" ] )
		this.checker.confCheckParameter( "PROPOSAL_DIR", "SingleValue", "String", [ "copyVector", "normCopyVector", "COM" ] )
		
	}
	
	/** This method should be defined in the subclass to specify additional parameters.*/
	confChecker(){
		// will be overwritten by the class extension
		throw( "confChecker should be defined for this term!")
	}
	
	/** Set the CPM attached to this constraint.
	@param {CPM} C - the CPM to attach.*/
	set CPM(C){
		
		/** @ignore */
		this.halfsize = C.extents.map( x => Math.floor( x/2 ) )
		super.CPM = C
		this.generalConfChecker()
		this.confChecker()
		this.setCPMListener()
	}
	
	/** Can be be defined in the subclass for anything that needs to run after this term is added to a CPM.
	@listens {WorkTerm#set CPM}*/
	setCPMListener(){
		// can be used in subclass.
	}
	
	/** Helper function to shift a point along the periodic boundary in the ith dimension,
	*  minimizing a given absolute distance dx to some reference point. 
	*
	* The shifted point no longer necessarily lies within the grid
	* dimensions, so it can be $< 0$ or $\geq$ the field size. For example, in a grid of width 100 with a 
	* reference point of 99, a point with x = 1 will be shifted to x = 101 instead to minimize |dx| = |101-99|=2 (instead of |1-99|=98).
	* 
	* If 'pos' = 'dx', we are finding the minimal distance along that dimension given the periodic boundary.
	* 
	* @param {ArrayCoordinate} [pos] - point to shift
	* @param {ArrayCoordinate} [dx] - the displacement vector from the reference point to 'pos' whose absolute magnitude we want to minimize.
	* @param {Integer} [i] - the dimension where we are shifting.
	* @return {ArrayCoordinate} - the point shifted along the indicated dimension.
	*/
	correctTorusDim( p, dx, i ){
		let corr = 0
		while( dx > this.halfsize[i] ){ 
			dx -= this.C.extents[i]
			corr -= 1
		}
		while( dx < -this.halfsize[i] ){ 
			dx += this.C.extents[i]
			corr += 1
		}
		
		return p + corr * this.C.extents[i]
	}
	
	/** Helper function to shift a point along the periodic boundary to minimize distance to a reference point. 
	* The shifted point no longer necessarily lies within the grid
	* dimensions, so it can be $< 0$ or $\geq$ the field size. For example, in a grid of width 100 with a 
	* reference point of 99, a point with x = 1 will be shifted to x = 101 instead to minimize |dx| = |101-99|=2 (instead of |1-99|=98).
	* 
	* @param {ArrayCoordinate} [pos] - point to shift
	* @param {ArrayCoordinate} [reference] - reference point, the 'anchor' from which we are shifting the point.
	* @return {ArrayCoordinate} - shifted position of the point. 
	*/
	correctTorus( pos, reference ){
		let dx = pos.map( (x, i) => pos[i] - reference[i] )
		pos = dx.map( (x,i) => this.correctTorusDim( pos[i], x, i ))
		return pos
	}
	/** Correct a position to be within grid dimensions according to periodic boundary. 
	* @param {ArrayCoordinate} [p] - position to correct along periodic boundary
	* @return {ArrayCoordinate} - shifted to lie within grid dimensions.
	*/
	correctPosition( p ){
		
		for( let dim = 0; dim < this.C.grid.extents.length; dim++ ){
			
			let grid_dim = this.C.grid.extents[dim]
		
			while( p[dim] < 0 ) p[dim] += grid_dim
			while( p[dim] >= grid_dim ) p[dim] -= grid_dim
		}
		return p
	}


	/** Create a vector between two points, corrected for periodic boundary to yield the shortest vector.
	* @param {ArrayCoordinate} [fromP] - start point of the vector
	* @param {ArrayCoordinate} [toP] - end point of the vector
	* @return {ArrayCoordinate} - vector between the points, corrected for periodic boundary.
	*/
	vec( fromP, toP ){
		let a = toP.map( (x,i) => { 
			let dx = x - fromP[i]
			let out = this.correctTorusDim( dx, dx, i ) 
			return out
		} )		
		return a
	}
	
	/** Compute the dot product of two vectors.
	* @param {number[]} [v1] - vector 1
	* @param {number[]} [v2] - vector 2
	* @return {number} - the dot product.
	*/
	dotProduct( v1, v2 ) {
		return v1.reduce((acc, n, i) => acc + (n * v2[i]), 0)
	}
	
	/** Normalize a vector to unit length
	* @param {number[]} [a] - the vector to normalize.
	* @return {number[]} - the normalized vector.
	*/
	normalize( a ){
		let norm = Math.sqrt( this.dotProduct( a,a ) )
		return a.map( x => x / norm )
	}

	/** Multiply a vector by a constant along each dimension.
	* @param {number[]} [vec] - the vector to scale.
	* @param {number[]} [c] - the constant to scale with.
	* @return {number[]} - the scaled vector.
	*/
	multiplyBy( vec, c ) {
		return vec.map( x => x*c )
	}
	
	/** The vector src -> tgt associated with the copy attempt.
	* @param {IndexCoordinate} [sourcei] - the source pixel of the copy attempt.
	* @param {IndexCoordinate} [targeti] - the target pixel of the copy attempt.
	* @param {Boolean} [normalize=false] - should vector be normalized to unit length?
	* @return {ArrayCoordinate} - copy vector associated with the copy attempt.
	*/
	copyMovementVector( sourcei, targeti, normalize = false ){
		let a = this.vec( this.C.grid.i2p( sourcei) , this.C.grid.i2p( targeti ) ) 
		if( normalize ){ a = this.normalize(a) }
		return a
	}
	
	
	/** The dispacementvector of the centroid that would be induced by the proposed copy
	* attempt.
	* @param {CellId} [cid] - the cell to get the proposed displacement for.
	* @param {IndexCoordinate} [targeti] - which pixel are we updating?
	* @param {string} [mode="gain"] - does this copy attempt imply "gain" or "loss" of a pixel for cell cid?
	* @return {ArrayCoordinate} - displacement vector of the cell centroid associated with the copy attempt.
	*/
	centroidMovementVector( cid, targeti, N, mode = "gain" ){

		if( cid == 0 ){ return new Array(this.C.grid.extents.length).fill(0) }
	
		let cenOld = this.currentCentroid( cid ).map( x => x / N )
		cenOld = this.correctPosition( cenOld )
		
		let targetPixelRelPos = this.C.grid.i2p( targeti ).map( (x,i) => { 
			let dx = x - cenOld[i] 
			return this.correctTorusDim( dx, dx, i )
		} )
			
		// check if we're looking at a cell that is gaining a pixel or losing one.
		switch( mode ) {
		case "gain" : {
			return targetPixelRelPos
		}
		case "loss" : {
			return targetPixelRelPos.map( x => -x )
		}
		default : {
			throw( "unknown mode " + mode + "; should be either 'gain' or 'loss'.")
		}
		}
		
	}

	/** Define the "proposal displacement" $\vec{dx}$ associated with a copy attempt as either
	* {@link copyMovementVector} or {@link centroidMovementVector} (multiplied by cell mass) depending 
	* on configuration in this.conf.PROPOSAL_DIR (see {@link WorkTerm#constructor}).
	* @param {IndexCoordinate} [sourcei] - source pixel of the copy attempt
	* @param {IndexCoordinate} [targeti] - which pixel are we updating?
	* @param {CellId} [cid] - for which cell are we computing the proposal displacement? This is only relevant when PROPOSAL_DIR = "COM".
	* @param {string} [mode="gain"] - does this copy attempt imply "gain" or "loss" of a pixel for cell cid?
	* @return {ArrayCoordinate} - proposal vector associated with the copy attempt.
	*/
	proposalVector( sourcei, targeti, cid, mode = "gain" ){
		
		switch( this.conf.PROPOSAL_DIR ){
		case "copyVector": {
			return this.copyMovementVector( sourcei, targeti )
		}
		case "normCopyVector" : {
			return this.copyMovementVector( sourcei, targeti , true )
		}
		case "COM" : {
			if( cid == 0 ) return [0,0]
			let vec = this.centroidMovementVector( cid, targeti, this.C.getVolume(cid), mode )
			//console.log(vec)
			return vec
		}
		}
		
	}
	
	/** This method defines $\vec{b}$ and should be defined in the subclass.
	* @param {IndexCoordinate} sourcei - source of the copy attempt
	* @param {IndexCoordinate} targeti - target of the copy attempt
	* @param {CellId} cid - the cell for which we want to know the target direction.
	* @returns {number[]} the target direction.
	*/
	/* eslint-disable no-unused-vars*/
	targetVector( sourcei, targeti, cid ){
		throw( "targetVector method undefined; must be defined in subclass!" )
	}

	/** Method to compute the work $\Delta H$ on a given cell due to the 'gain' or 'loss' 
	* of a pixel during the copy attempt.
	* @param {IndexCoordinate} sourcei - coordinate of the source pixel that tries to copy.
	* @param {IndexCoordinate} targeti - coordinate of the target pixel the source is trying
	* to copy into.
	* @param {CellId} cid - cell we are computing the work for.
	* @param {string} [mode="gain"] - does this copy attempt imply "gain" or "loss" of a pixel for cell cid?
	* @return {number} the change in Hamiltonian ("work") for this copy attempt and this constraint.*/ 
	deltaHCell( sourcei, targeti, cid, mode ) {
		let l = this.cellParameter("LAMBDA_DIR", cid)
		if( l == 0 )  return 0
		let target = this.targetVector( sourcei, targeti, cid )
		let proposal = this.proposalVector( sourcei, targeti, cid, mode )
		let dH = - l *  this.dotProduct( target, proposal )
		//console.log(dH)
		return dH
	}
	
	/** Method to compute the work $\Delta H$ for this term.
	 @param {IndexCoordinate} sourcei - coordinate of the source pixel that tries to copy.
	 @param {IndexCoordinate} targeti - coordinate of the target pixel the source is trying
	 to copy into.
	 @param {CellId} src_type - cellid of the source pixel.
	 @param {CellId} tgt_type - cellid of the target pixel. 
	 @return {number} the change in Hamiltonian ("work") for this copy attempt and this constraint.*/ 
	deltaH( sourcei, targeti, src_type, tgt_type ) {
		switch( this.conf.FORCE_MODE ){
		case "extension" : {
			let dH = this.deltaHCell( sourcei, targeti, src_type, "gain" )
			//console.log(dH)
			return dH
		}
		case "retraction" : {
			let dH = this.deltaHCell( sourcei, targeti, tgt_type, "loss" )
			//console.log(dH)
			return dH
		}
		case "reciprocal" : {
			let dH = this.deltaHCell( sourcei, targeti, src_type, "gain" ) + this.deltaHCell( sourcei, targeti, tgt_type, "loss" )
			//console.log(dH)
			return dH
		}
		}
	}

}


/** Version of a {@link WorkTerm} setting a fixed target direction $\vec{b}$ in the 
 * Hamiltonian as defined in {@link WorkTerm}. See that documentation for further details.
 * Unless further extended with some dynamics, this yields ballistic motion.
 * 
 * 
 * This constraint works with torus (periodic boundaries) as long as the field size is "large enough". 
 * 
 * @experimental 
 * */

class TargetDirection extends WorkTerm {

	/** In addition to the configuration required for the {@link WorkTerm#constructor}, 
	* we now also define the (fixed) target direction.
		* @param {object} conf - parameter object for this constraint.
	 * @param {PerKindNonNegative} conf.LAMBDA_DIR - magnitude of the force exerted on the cell.
	 * @param {PerKindNonNegative} conf.DELTA_T - number of MCS used to track the "recent" displacement of the cell centroid.
	 * @param {string} conf.FORCE_MODE - set to "extension" ($\delta_s = 1, \delta_t = 0$), "retraction" ($\delta_s = 0, \delta_t = 1$), or "reciprocal" ($\delta_s = 1, \delta_t = 1$).
	 * @param {string} conf.PROPOSAL_DIR - define $\vec{dx}$ as the "copyVector" (from $s \rightarrow t$, unnormalized),  "normCopyVector" (idem, but normalized to unit length), or "COM" (the centroid displacement that this copy attempt would induce for this cell, multiplied by the current number of pixels in that cell.)
	 * @param {ArrayCoordinate[]} conf.DIR - define the target direction vector.
	*/
	constructor( conf ){
		super( conf )
	}
	
	/** This method checks that all required parameters are present in the
	 * object supplied to the constructor, and that they are of the right
	 * format. It throws an error when this is not the case. It will be run after
	 * the {@link WorkTerm#generalConfChecker}.
	 * */
	confChecker(){

		// Custom check for the attractionpoint
		let checker = new CPM.ParameterChecker( this.conf, this.C )
		checker.confCheckPresenceOf( "DIR" )
		let pt = this.conf["DIR"]
		if( !( pt instanceof Array ) ){
			throw( "DIR must be an array with the start and end coordinate of the preferred direction vector!" )
		}
		for( let p of pt ){
		
			if( !checker.isCoordinate(p) ){
				throw("DIR elements must be coordinate arrays with the same dimensions as the grid!")
			}
		}
	}
	
	/** This method defines $\vec{b}$ and returns the (normalized) target direction as specified 
	* through {@link cellParameter}.
	* @param {IndexCoordinate} sourcei - source of the copy attempt
	* @param {IndexCoordinate} targeti - target of the copy attempt
	* @param {CellId} cid - the cell for which we want to know the target direction.
	* @returns {number[]} the target direction normalized to unit length.
	*/
	/* eslint-disable no-unused-vars*/
	targetVector( sourcei, targeti, cid ){
		return this.normalize( this.cellParameter( "DIR" , cid ) )
	}

}




/*class AttractionPoint extends WorkTerm {

	confChecker(){

		// Custom check for the attractionpoint
		this.checker.confCheckPresenceOf( "ATTRACTIONPOINT" )
		let pt = this.conf["ATTRACTIONPOINT"]
		if( !this.checker.isCoordinate(pt) ){
			throw( "ATTRACTIONPOINT must be a coordinate array with the same " +
				"dimensions as the grid!" )
		}
	}
	
	targetVector( sourcei, targeti, cid ){
		
		let attractor = this.cellParameter("ATTRACTIONPOINT", cid )
		let v = this.vec( this.C.grid.i2p( sourcei) , attractor )
		return this.normalize(v)
	}

}*/

class LangevinPRW extends WorkTerm {
	
	confChecker(){
		let checker = new CPM.ParameterChecker( this.conf, this.C )
		checker.confCheckParameter( "XI", "KindArray", "NonNegative" )
		// check dimensionality; angles currently only defined in 2D
		const ndim = this.C.extents.length
		if( ndim != 2 ){ throw( "LangevinPRW constraint currently only supported in 2D, your CPM is " + ndim + "D!" ) }
	}

	targetVector( sourcei, targeti, cid ){
		return this.currentDirection(cid)
	}
		
	// after each MCS, update the target direction with Gaussian angular noise.
	postMCSListener(){
		for( let cid of this.C.cellIDs() ){
			let xi = this.cellParameter( "XI", cid )
			let di = this.currentDirection(cid)
			let alpha = Math.atan2( di[1], di[0])
			alpha += this.sampleNorm( 0, xi )
			this.celldirections[cid] = [Math.cos(alpha), Math.sin(alpha)]
		}
	}
}

class PersistenceConstraint extends WorkTerm {
	
	confChecker(){
		this.checker.confCheckParameter( "PERSIST", "KindArray", "Probability" )
		this.checker.confCheckParameter( "DELTA_T", "KindArray", "NonNegative" )
	}
	
	targetVector( sourcei, targeti, cid ){
		return this.currentDirection(cid)
	}
	
	// add latest centroid to the centroidlist, and remove older points until 
	// length is <= delta_t
	updateCentroidHistory( cid, centroid ) {
	
		let dt = this.cellParameter("DELTA_T", cid )
			
		if( !(cid in this.cellcentroidlists ) ){
			this.cellcentroidlists[t] = []
		}
		
		this.cellcentroidlists[t].unshift(centroid)
		
		while( this.cellcentroidlists[cid].length > dt ){
			this.cellcentroidlists[cid].pop()
		}
		
	}
	
	// compute cell's displacement over the centroid history (normalized)
	recentDisplacement( cid, current, norm = true ) {
		
		let last = this.cellcentroidlists[cid].pop()
		let dx = current.map( (x,i) => {
			let ddim = x - last[i]
			this.correctTorusDim( ddim, ddim, i )
		} )
		
		if( norm ) dx = this.normalize(dx)
		
		return dx
		
	}
	
	// update target direction of each cell according to:
	// u_new = Ppersist*u_old + (1-Ppersist) * dispVector
	// where dispVector is the (unnormalized) empirical displacement vector over the last DELTA_T steps
	postMCSListener(){
		for( let cid of this.C.cellIDs() ){
			
			let ci = this.currentCentroid( cid )
			this.updateCentroidHistory( cid, ci ) 
			
			// note, dt could change during execution
			if( this.cellcentroidlists[cid].length == dt ){
				
				// check cell's recent displacement;
				let dx = this.recentDisplacement( cid, ci ) 
				
				// dx can be NaN after normalization if the cell has not moved.
				// in that case, the cell has lost persistent memory; give new random intrinsic dir.
				if( dx.some( d => Number.isNaN(d) ) ){
					this.celldirections[cid] = this.randDir(this.C.ndim)
				}
				
				// apply angular diffusion to target direction if needed
				let per = this.cellParameter("PERSIST", cid )
				if( per < 1 ){

					let cdir = this.currentDirection(cid)
					let newdir = this.normalize( dx.map( (x,i) => (1-per)*x + per * cdir[i] ) )
					this.celldirections[cid] = newdir
					
				}
				// note if per = 1 we don't have to update at all and revert to a fixed
				// direction (i.e. ballistic motion)
			}
			
		}
	}
	
}


exports.WorkTerm = WorkTerm
exports.TargetDirection = TargetDirection
//exports.AttractionPoint = AttractionPoint
exports.PersistenceConstraint = PersistenceConstraint
exports.LangevinPRW = LangevinPRW