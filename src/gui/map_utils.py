"""Utility functions for map-related functionality"""

def get_map_html_template():
    """Return the HTML template for the map view"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Location Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <style>
            #map {
                height: 100vh;
                width: 100%;
            }
            .crosshair {
                cursor: crosshair !important;
            }
            .dragging {
                cursor: move !important;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
        // Initialize QWebChannel
        var bridge = null;
        new QWebChannel(qt.webChannelTransport, function(channel) {
            bridge = channel.objects.bridge;
        });
        
        // Initialize the map
        var mymap = L.map('map').setView([0, 0], 2);
        
        // Initialize markers storage
        var markers = {};
        var markersGroup = L.featureGroup().addTo(mymap);
        
        // Initialize base layers
        var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        });
        
        var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Imagery &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        });
        
        // Add default layer
        mymap.addLayer(osm);
        
        // Define baseLayers for layer control
        var baseLayers = {
            "OpenStreetMap": osm,
            "Satellite": satellite
        };
        
        // Layer control
        L.control.layers(baseLayers).addTo(mymap);
        
        // Function to add a marker
        function addMarker(lat, lon, name, id) {
            // Remove existing marker if it exists
            if (markers[id]) {
                markersGroup.removeLayer(markers[id]);
                delete markers[id];
            }
            
            var marker = L.marker([lat, lon], {
                draggable: false,
                title: name
            }).bindTooltip(name, {permanent: false, direction: 'auto'});
            
            // Add click handler
            marker.on('click', function(e) {
                // Only emit click event if marker is not draggable
                if (!marker.dragging._enabled && bridge) {
                    bridge.on_marker_click(id);
                }
            });
            
            // Add drag handlers
            marker.on('dragstart', function(e) {
                // Prevent tooltip from showing while dragging
                marker.closeTooltip();
            });
            
            marker.on('dragend', function(e) {
                if (bridge) {
                    var latlng = e.target.getLatLng();
                    bridge.on_marker_moved(id, latlng.lat, latlng.lng);
                }
                // Show tooltip again after drag
                marker.openTooltip();
            });
            
            // Add to group and store reference
            marker.addTo(markersGroup);
            markers[id] = marker;
            return marker;
        }
        
        // Function to make a marker draggable
        function toggleMarkerDrag(id, draggable) {
            var marker = markers[id];
            if (marker) {
                if (draggable) {
                    marker.dragging.enable();
                    marker._icon.style.cursor = 'move';
                    document.getElementById('map').classList.add('dragging');
                } else {
                    marker.dragging.disable();
                    marker._icon.style.cursor = '';
                    document.getElementById('map').classList.remove('dragging');
                }
            }
        }
        
        // Function to clear all markers
        function clearMarkers() {
            markersGroup.clearLayers();
            markers = {};
        }
        
        // Function to fit bounds
        function fitBounds(bounds) {
            mymap.fitBounds(bounds);
        }
        
        // Function to set view
        function setView(lat, lon, zoom) {
            mymap.setView([lat, lon], zoom);
        }
        
        // Function to set crosshair cursor
        function setCrosshairCursor() {
            document.getElementById('map').classList.add('crosshair');
        }
        
        // Function to reset cursor
        function resetCursor() {
            document.getElementById('map').classList.remove('crosshair');
        }
        
        // Add map click handler
        mymap.on('click', function(e) {
            if (bridge) {
                bridge.on_map_clicked(e.latlng.lat, e.latlng.lng);
            }
        });
        </script>
    </body>
    </html>
    """
