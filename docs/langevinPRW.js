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
			let b = this.celldirections[src_type]
			let a = this.dC.src
			dH -= this.dot( a, b )
		}
		
		// retraction force:
		if( this.conf.RETRACT && tgt_type > 0 ){
			let b = this.celldirections[tgt_type]
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