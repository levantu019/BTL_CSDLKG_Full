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
        params: {LAYERS: 'BTL:doanduong'}
    })
});

var nutgiaothong = new ol.layer.Image({
    title: 'Nút giao thông',
    visible: false,
    source: new ol.source.ImageWMS({
        ratio: 1,
        url: 'http://localhost:8080/geoserver/BTL/wms',
        params: {LAYERS: 'BTL:nutgiaothong'}
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






//   const fillStyle = new ol.style.Fill({
//     color: [84, 118, 255, 1]
// });

// const strokeStyle = new ol.style.Stroke({
//     color: [46, 45, 45, 1],
//     width: 1.3
// });

// const circleStyle = new ol.style.Circle({
//     fill: new ol.style.Fill({
//         color: [245, 49, 5, 1]
//     }),
//     radius: 7,
//     stroke: strokeStyle
// });