
function setSliders(){

	for( let i = 0; i < Object.keys( rangeMap ).length; i++ ){
		
		const sliderID = Object.keys( rangeMap )[i]
		const confID = rangeMap[sliderID]
		
		// shared model parameters: set directly from C.conf
		if( confID.model == "shared" ){
			let value
			if( confID.position == "none" ){
				value = confID.modelToRange( sims['MODEL000'].C.conf[confID.key] )
			
			} else {
				value = confID.modelToRange( sims['MODEL000'].C.conf[confID.key][confID.position] )
			}
			document.getElementById( sliderID ).value = value
		}
		// specific parameters: set from the relevant constraint
		else {
			let value = sims[confID.model].C.getConstraint( confID.constraint ).conf[confID.key][confID.position]
			document.getElementById( sliderID ).value = confID.modelToRange( value )
		}
	}
}

function sliderInput(){
	
	for( let i = 0; i < Object.keys( rangeMap ).length; i++ ){
		
		const sliderID = Object.keys( rangeMap )[i]
		const map = rangeMap[sliderID]
		
		const sliderValue = parseFloat( document.getElementById( sliderID ).value )
		const modelValue = map.rangeToModel( sliderValue )
		
		// update logger next to slider
		const bubble = document.getElementById( sliderID ).parentElement.querySelector('.bubble')
		let bubbleText = map.rangeToModel(parseFloat( document.getElementById( sliderID ).value ))
		if( map.hasOwnProperty("bubbleText")) bubbleText = map.bubbleText(parseFloat( document.getElementById( sliderID ).value ))
		bubble.innerHTML = bubbleText
		
		// update model parameters.
		
		// shared parameters : loop and set in every model
		if( map.model == "shared" ){
			for( let mi of model_names ){
				if( map.position == "none" ){
					sims[mi].C.conf[map.key] = modelValue
				} else {
					sims[mi].C.conf[map.key][map.position] = modelValue
				}
			}
		}
		// else set in the specific model and constraint
		else {
			sims[map.model].C.getConstraint(map.constraint).conf[map.key][map.position] = modelValue
		}
				
	}
		
}


function resetSim(){
	
	for( let mi of model_names ){
		sims[mi].running = false
	}
	initialize()
	sliderInput()
	setPlayPause()
}


function setPlayPause(){
	if( sims['MODEL000'].running ){
		$('#playIcon').removeClass('fa-play');$('#playIcon').addClass('fa-pause')
	} else {
		$('#playIcon').removeClass('fa-pause');$('#playIcon').addClass('fa-play')
	}	
}



