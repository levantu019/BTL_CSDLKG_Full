// Biến lưu các layer và marker
var list_layers = [];

// Tạo GeoJSON từ dữ liệu server gửi về
function createGeoJSON(geom){
    var geojsonObject = {
      'type': 'FeatureCollection',
      'crs': {
        'type': 'name',
        'properties': {
          'name': 'EPSG:32648',
        },
      },
      'features': ''
    };
    geojsonObject['features'] = geom;

    return geojsonObject;
}


function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}


// Hàm show tổng độ dài quãng đường
function append_total_length(length, color_random){
  length = Math.round(length * 1000) / 1000;
  if (length > 1000){
    length = Math.round(length * 1000) / 1000000;
    var str_length = length + "  (km)";
  }
  else{
    var str_length = length + "  (m)";
  }
  let new_line = `<div class="row m-2 info-new-line">
                      <div class="col-sm-4">
                          <div style="width: 30px; height: 30px; background: ${color_random};"></div>
                      </div>
                      <div class="col-sm-8" style="line-height: 30px;">${str_length}</div>
                  </div>`
  $("#length-line").append(new_line);
}


// Tạo biến lưu layer của kết quả
var vectorLayer = null;
var gg;
// Gửi dữ liệu tạo độ điểm click lên server
// Nhận về danh sách GeoJSON của các đoạn đường
function sendData(start, end, algorithm){
    var start_end = [];
    start_end.push({"start_X": start[0]});
    start_end.push({"start_Y": start[1]});
    start_end.push({"end_X": end[0]});
    start_end.push({"end_Y": end[1]});
    start_end.push({"algorithm": algorithm});
    start_end = JSON.stringify(start_end);

    var data_url = "run/way/search/" + start_end;

    $.ajax({
        url: data_url,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            var geojson = JSON.parse(response['res']);
            var color_random = getRandomColor();
            if(geojson != '-1'){
                var way = createGeoJSON(geojson);
                const styles = {
                  'MultiLineString': new ol.style.Style({
                    stroke: new ol.style.Stroke({
                      color: color_random,
                      width: 5,
                    })
                  }),
                };
                const vectorSource = new ol.source.Vector({
                  features: new ol.format.GeoJSON().readFeatures(way),
                });
                vectorLayer = new ol.layer.Vector({
                  source: vectorSource,
                  style: styles['MultiLineString'],
                });
                map.addLayer(vectorLayer);
                list_layers.push(vectorLayer);
                let length = 0;
                way.features.forEach((item) => {
                    length = length + item.properties.f3;
                });
                append_total_length(length, color_random);                
            }
            else{
                alert('Không tìm thấy đường đi');
            }
        },
        error: function (response) {
            alert('Không tìm thấy đường đi');
        }
    })
}


// Kiểm tra xem cả 2 ô input đã có toạ độ chưa
function checkInput(){
    var start = $("#start-point").val();
    var end = $("#end-point").val();

//    Dữ liệu trong input là dạng string, thực hiện chuyển về dạng cặp toạ độ
    var coordinate_start = [parseFloat(start.split(',')[0]), parseFloat(start.split(',')[1])];
    var coordinate_end = [parseFloat(end.split(',')[0]), parseFloat(end.split(',')[1])];
    var algorithm = $("#select-algorithm").val();

    if(start != "" && end != ""){
        sendData(coordinate_start, coordinate_end, algorithm);
    }
}


//----------------------------------------------------
// Lưu lại trạng thái rằng input nào đang được focus, từ đó nhận toạ độ click trên map
var tag_focusing = "";
var id_focusing = "";

$("input").focus(function() {
    tag_focusing = document.activeElement.tagName;
    id_focusing = "#" + document.activeElement.id;
})

function createStyle(src, img) {
  return new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, 0.96],
      crossOrigin: 'anonymous',
      src: src,
      img: img,
      imgSize: img ? [img.width, img.height] : undefined,
    }),
  });
}


// Tạo biến lưu marker
var marker = null;

// Sự kiện khi click vào map
map.on('singleclick', function(evt){
//    Lấy tạo độ click trên map
    var coordinates = evt.coordinate;
    const iconFeature = new ol.Feature(new ol.geom.Point(coordinates));
    iconFeature.set('style', createStyle('../static/image/location.png', undefined));
    marker = new ol.layer.Vector({
        style: function (feature) {
            return feature.get('style');
        },
        source: new ol.source.Vector({features: [iconFeature]}),
      });
    list_layers.push(marker);

//    Nếu đang focus thẻ input thì nhập toạ độ vào thẻ đó và kiểm tra hàm checkInput()
    if(tag_focusing == "INPUT"){
        map.addLayer(marker);
        $(id_focusing).val(coordinates.toString());
        checkInput();
    }
})

$("#select-algorithm").change(function(){
  checkInput();
})

$("#btnRefresh").on('click', function(){
    list_layers.forEach((item) => {
      map.removeLayer(item);
    })
    $("input").val('');
    $("#length-line .info-new-line").remove();
})