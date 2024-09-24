var map = L.map("map").setView([-22.2312106, -54.8358869], 15); // Dourados

L.tileLayer("http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 20,
}).addTo(map);
var removeMarker;

// AO CLICAR NO MAPA
map.on("click", markerOnClick).addTo(map);

function markerOnClick(e) {
  simpleReverseGeocoding(e);
  marker = L.marker([e.latlng.lat, e.latlng.lng]);
  adicionarMarcador(marker);
}

function adicionarMarcador(marker) {
  // Remove o marcador anterior
  if (removeMarker && map.hasLayer(removeMarker)) {
    map.removeLayer(removeMarker);
  }
  map.addLayer(marker);
  removeMarker = marker;
}

async function simpleReverseGeocoding(e) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${e.latlng.lat}&lon=${e.latlng.lng}`,
      {
        method: "GET",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors", // Adicione este cabeçalho para lidar com a política de mesma origem
      }
    );

    if (!response.ok) {
      throw new Error(`Erro na solicitação: ${response.status}`);
    }

    const json = await response.json();
    // Preenchendo o campo de endereço com o número da casa
    document.getElementById("id_endereco").value = (json.address.road ? json.address.road : "") 
        + ", " + (json.address.house_number ? json.address.house_number: "S/N") // Inclui o número da casa ou "S/N"
        + ", " + (json.address.suburb ? json.address.suburb: "") 
        + ", " + (json.address.city ? json.address.city : "")  
        + " - " + (json.address.state ? json.address.state : "") 
        + ", " + (json.address.postcode ? json.address.postcode : "") 
        + ", " + (json.address.country ? json.address.country : "");

    // Atualiza os campos de latitude e longitude
    document.getElementById("id_latitude").value = json.lat;
    document.getElementById("id_longitude").value = json.lon;
    document.getElementById("id_bairro").value = json.address.suburb;

  } catch (error) {
    console.error(error);
  }
}
