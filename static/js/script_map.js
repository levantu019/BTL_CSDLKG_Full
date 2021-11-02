//----------------------------------------------------
// Thêm nút mở sidebar tìm kiếm và hiển thị toạ độ trên nền của map
class btn_sidebar extends ol.control.Control {
    constructor(opts) {
        const opt = opts || {};
        const element = document.getElementById('customElement');

        super({
            element: element,
            target: opt.target
        })
    }
}


// Hiển thị map
format = "image/jpeg";
var bounds = [416937.7221069336, 1654665.3541259766,
            576040.1301206055, 1774944.951100586];

// Đầu tiên, để có thể show map thì phải xét hệ toạ độ
var projection = new ol.proj.Projection({
    code: 'EPSG:32648',
    units: 'm'
});

var view = new ol.View({
    projection: projection,
});

var doanduong = new ol.layer.Image({
    title: 'Đoạn đường',
    source: new ol.source.ImageWMS({
        ratio: 1,
        url: 'http://localhost:8080/geoserver/BTL/wms',
        params: {LAYERS: 'BTL:doanduong2'}
    })
});

var nutgiaothong = new ol.layer.Image({
    title: 'Nút giao thông',
    visible: false,
    source: new ol.source.ImageWMS({
        ratio: 1,
        url: 'http://localhost:8080/geoserver/BTL/wms',
        params: {LAYERS: 'BTL:nutgiaothong2'}
    })
});

var _OSM = new ol.layer.Tile({
    title: 'OSM',
    type: 'base',
    visible: true,
    source: new ol.source.OSM()
})

var groupLayers = new ol.layer.Group({
    title: 'Giao thông',
    fold: 'open',
    layers: [doanduong, nutgiaothong]
});

var groupBases = new ol.layer.Group({
    title: 'Base Map',
    layers: [_OSM]
});

var map = new ol.Map({
    controls: ol.control.defaults().extend([new btn_sidebar()]),
    layer: [],
    target: 'map',
    view: view
});

var mousePositionControl = new ol.control.MousePosition({
    coordinateFormat: ol.coordinate.createStringXY(3),
    projection: projection,
    className: 'mouse-position',
    target: document.getElementById('position_mouse'),
    undefinedHTML: '&nbsp;',
})

//map.addLayer(groupBases);
map.addLayer(groupLayers);
map.addControl(mousePositionControl);

map.getView().fit(bounds, map.getSize());


//----------------------------------------------------
// Thêm layerswitch
var layerSwitcher = new ol.control.LayerSwitcher({
    activationMode: 'click',
    tipLabel: 'Show layer list', // Optional label for button
    collapseTipLabel: 'Hide layer list', // Optional label for button
    groupSelectStyle: 'children' // Can be 'children' [default], 'group' or 'none'
});
map.addControl(layerSwitcher);

// ------------------------------
// POPUP
// -----------------------------
const container = document.getElementById('popup');
const content = document.getElementById('popup-content');

const overlay = new ol.Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250,
    },
});

map.addOverlay(overlay);

const highlightStyle = new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255,255,255,1)',
    }),
    stroke: new ol.style.Stroke({
      color: '#FF0000',
      width: 7,
    }),
  });

const select = new ol.interaction.Select({
    condition: ol.events.condition.pointerMove,
    style: highlightStyle,
});
const selectEvent = select.getFeatures();
select.on('select', function (evt) {
    let coordinate;
    selectEvent.forEach(function (each) {
      let ten = each.getProperties().f2;
      let dodai = Math.round(each.getProperties().f3 * 100) / 100;
      coordinate = each.getProperties().geometry.flatCoordinates;
      let newRowPopup = `<tr><td>${ten}</td><td>${dodai} &nbsp(m)</td></tr>`; 
      $("#attributeTable tbody tr").remove();
      $("#attributeTable tbody").append(newRowPopup);
    });
    overlay.setPosition(coordinate);
});
map.addInteraction(select);
