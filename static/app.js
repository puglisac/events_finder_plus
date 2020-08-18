// map functions

function initMap() {
	// Creates a goog map
	const v = document.getElementById("venue-card");
	const vname = document.getElementById("venue-name").innerText;
	const vstreet = document.getElementById("address").innerText;
	const vcityState = document.getElementById("city-state").innerText;
	const vlink = document.getElementById("venue-link").href;
	const venue = new google.maps.LatLng(Number(v.dataset.lat), Number(v.dataset.long));

	const map = new google.maps.Map(document.getElementById("map"), {
		// centers map on venue
		center: venue,
		zoom: 15
	});

	const infowindow = new google.maps.InfoWindow({
		// creates an info window for the venue marker
		content: contentString(vname, vstreet, vcityState, vlink),
		maxWidth: 200
	});

	// get parking results from around venue
	getParking(venue, map);

	// create a marker for the venue
	const marker = createMarker(venue, map);

	// add an event listener to the venue marker and open it on click
	marker.addListener("click", () => {
		infowindow.open(map, marker);
	});

	function getParking(loc, map) {
		// does a search for parking around the venue
		const request = {
			location: loc,
			radius: "500",
			type: [ "parking" ]
		};

		service = new google.maps.places.PlacesService(map);
		service.nearbySearch(request, callback);
	}

	function callback(results, status) {
		// for the search results create a parking marker with info window and add event listener
		if (status == google.maps.places.PlacesServiceStatus.OK) {
			for (var i = 0; i < results.length; i++) {
				parking = document.getElementById("parking-results");
				li = document.createElement("li");
				li.classList.add("col-md-6");
				li.setAttribute("id", results[i].place_id);
				li.innerHTML = `<h6>${results[i].name}</h6>
                <p>${results[i].vicinity}</p>`;
				parking.append(li);
				const parkingMarker = createParkingMarker(results[i], map, results[i].place_id);
				const infowindow = createInfoWindow(results[i].name, results[i].vicinity);
				parkingMarker.addListener("click", () => {
					infowindow.open(parkingMarker.get("map"), parkingMarker);
				});
			}
		}
	}
}

function createMarker(place, map) {
	// create a map marker
	return new google.maps.Marker({
		position: place,
		map: map
	});
}

function createParkingMarker(place, map, id) {
	// create a map marking for parking
	return new google.maps.Marker({
		position: place.geometry.location,
		map: map,
		id: id,
		icon: "https://developers.google.com/maps/documentation/javascript/examples/full/images/parking_lot_maps.png"
	});
}

function contentString(name, street, cityState, href) {
	// returns an html string for info windows
	return `
	<div id="content">
	<div id="siteNotice">
	</div>
	<h6 id="firstHeading" class="firstHeading">${name}</h6> 
	<div id="bodyContent"> 
    <p>${street}</p> 
    <p>${cityState}</p>
	<p><a href=${href} target="_blank">
	${href}</a> 
	</p>
	</div> 
	</div>`;
}

function createInfoWindow(name, address) {
	// creates an info window
	return new google.maps.InfoWindow({
		content: `<div id="content">
        <div id="siteNotice">
        </div>
        <h6 id="firstHeading" class="firstHeading">${name}</h6> 
        <div id="bodyContent"> 
        <p>${address}</p>`,
		maxWidth: 200
	});
}

// saved events functions

eventCards = document.querySelectorAll(".event-cards");
// add event listener to event cards
if (eventCards) {
	for (div of eventCards) {
		div.addEventListener("click", handleClick);
	}
}

function handleClick(evt) {
	// when the card is clicked see if event is saved or not and handle click accordingly

	if (evt.target.nodeName == "BUTTON" && evt.target.classList.contains("btn-outline-primary")) {
		addToSaved(evt.target.id);
	} else if (evt.target.nodeName == "BUTTON" && evt.target.classList.contains("btn-primary")) {
		removeFromSaved(evt.target.id);
	} else {
		return;
	}
}

async function addToSaved(id) {
	evtCard = document.getElementById(id);
	evtCard.classList.add("btn-primary");
	evtCard.classList.remove("btn-outline-primary");
	evtCard.innerText = "Saved";
	res = await axios.post("/users/add_event", { id: id });
	return res["data"];
}

async function removeFromSaved(id) {
	evtCard = document.getElementById(id);
	evtCard.classList.remove("btn-primary");
	evtCard.classList.add("btn-outline-primary");
	evtCard.innerText = "Save event";
	res = await axios.post("/users/remove_event", { id: id });
	return res;
}
