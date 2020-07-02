# leaflet-velocity 

A extension for Leaflet-velocity  
Using Xarray or netCDF4 to extract the HYCOM GoM expt90.1 and HYCOM GLBy on leaflet-velocity.

Live Demo: https://geo.gcoos.org/data/maps/ocean_current_viewer/

Detail of leaflet-velocity: https://github.com/danwild/leaflet-velocity

## Example use:

```javascript
var velocityLayer = L.velocityLayer({
  displayValues: true,
  displayOptions: {
    velocityType: "Global Wind",
    position: "bottomleft",
    emptyString: "No velocity data",
    angleConvention: "bearingCW",
    displayPosition: "bottomleft",
    displayEmptyString: "No velocity data",
    speedUnit: "m/s"
  },
  data: data, // see demo/*.json, or wind-js-server for example data service

  // OPTIONAL
  minVelocity: 0, // used to align color scale
  maxVelocity: 10, // used to align color scale
  velocityScale: 0.005, // modifier for particle animations, arbitrarily defaults to 0.005
  colorScale: [], // define your own array of hex/rgb colors
  onAdd: null, // callback function
  onRemove: null, // callback function
  opacity: 0.97, // layer opacity, default 0.97

  // optional pane to add the layer, will be created if doesn't exist
  // leaflet v1+ only (falls back to overlayPane for < v1)
  paneName: "overlayPane"
});
```

The angle convention option refers to the convention used to express the wind direction as an angle from north direction in the control.
It can be any combination of `bearing` (angle toward which the flow goes) or `meteo` (angle from which the flow comes),
and `CW` (angle value increases clock-wise) or `CCW` (angle value increases counter clock-wise). If not given defaults to `bearingCCW`.

The speed unit option refers to the unit used to express the wind speed in the control.
It can be `m/s` for meter per second, `k/h` for kilometer per hour or `kt` for knots. If not given defaults to `m/s`.


## Build / watch

```shell
npm install
npm run watch
```
After, if you are unable to see the webpack on your browser, run this on terminal (MacOS)
open /Applications/Google\ Chrome.app --args --allow-file-access-from-files  

## Reference

`leaflet-velocity` is possible because of things like:

- [L.CanvasOverlay.js](https://gist.github.com/Sumbera/11114288)
- [WindJS](https://github.com/Esri/wind-js)
- [earth](https://github.com/cambecc/earth)
