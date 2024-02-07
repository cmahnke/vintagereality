import WebXRPolyfill from 'webxr-polyfill';
window.polyfill = new WebXRPolyfill();
import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { OrbitControls  } from 'three/examples/jsm/controls/OrbitControls.js';

// Inspired by https://github.com/steren/stereo-img/blob/main/stereo-img.js

function angleOfViewFocalLengthIn35mmFormat(focalLengthIn35mmFormat, width, height) {
  // https://en.wikipedia.org/wiki/Angle_of_view#Common_lens_angles_of_view
  // https://en.wikipedia.org/wiki/35_mm_equivalent_focal_length
  // angle of view on the diagonal (35mm is 24 mm (vertically) × 36 mm (horizontal), giving a diagonal of about 43.3 mm)

  const assumedDPI = 600;
  const physicalHeight = (height / assumedDPI) * 25.4;
  const physicalWidth = (width / assumedDPI) * 25.4;
  const diagonal = Math.sqrt(Math.pow(physicalWidth, 2) + Math.pow(physicalHeight, 2));
  console.log(`Physical size is ${physicalWidth}mm x ${physicalHeight}mm, diagonal ${diagonal}mm`);

  const diagonalAngle = 2 * Math.atan(diagonal.toFixed(2) / (2 * focalLengthIn35mmFormat));
  //const diagonalAngle = 2 * Math.atan(43.3 / (2 * focalLengthIn35mmFormat));
  // Pi / 4 for a square.
  const halfAngle = Math.atan(height / (width / 2));
  const horizontalAngle = diagonalAngle * Math.cos(halfAngle);
  const verticalAngle = diagonalAngle * Math.sin(halfAngle);

  return {diagonalAngle, horizontalAngle, verticalAngle};
}

async function init3DViewer (left, right) {
  const assumeFocalLengthIn35mmFormat = 27;
  var angle, stereoData;
  const loader = new THREE.TextureLoader();
  var eyes = [{}, {}];
  var scene = new THREE.Scene();
  scene.background = new THREE.Color( 0x101010 );
  const radius = 10;

  eyes[0].texture = await loader.loadAsync(left);
  eyes[1].texture = await loader.loadAsync(right);

  var width = eyes[0].texture.image.width;
  var height = eyes[0].texture.image.height;
  //var textureDimensions = {};
  angle = angleOfViewFocalLengthIn35mmFormat(assumeFocalLengthIn35mmFormat, width, height);
  const phiLength = angle.horizontalAngle;
  const thetaLength = angle.verticalAngle;
  const thetaStart = Math.PI / 2 - thetaLength / 2;

  stereoData = {
    phiLength: phiLength,
    thetaStart: thetaStart,
    thetaLength: thetaLength
  };

  eyes.forEach(function (item, index) {
    eyes[index].texture.needsUpdate = true;
    eyes[index].material = new THREE.MeshBasicMaterial( { map: item.texture });
    eyes[index].geometry = new THREE.SphereGeometry( radius, 60, 40, -1 * stereoData.phiLength / 2, stereoData.phiLength, stereoData.thetaStart, stereoData.thetaLength);
    eyes[index].geometry.scale( - 1, 1, 1 );
    eyes[index].mesh = new THREE.Mesh( eyes[index].geometry, eyes[index].material);
    eyes[index].mesh.rotation.reorder( 'YXZ' );
    eyes[index].mesh.rotation.y = Math.PI / 2;
    eyes[index].mesh.rotation.x = stereoData.roll || 0;
    eyes[index].mesh.rotation.z = stereoData.pitch || 0;
    eyes[index].mesh.layers.set(index + 1); // display in left eye only // display in right eye only
    scene.add(eyes[index].mesh);
  });

  return scene;
}

function createCanvas(element, width, height) {
  var id = element.getAttribute('id');
  var stereoCanvas = document.createElement('canvas');
  stereoCanvas.setAttribute('id', id + '-canvas');
  stereoCanvas.setAttribute('class', 'stereo-canvas');
  var bbox = element.getBoundingClientRect();

  //TODO: Sizes aren't working since the element isn't visible on initial setup
  element.appendChild(stereoCanvas);
  /*
  if (width !== undefined) {
    canvasWidth = width;
  } else {
    canvasWidth = element.clientWidth;
    canvasWidth = bbox.width;
  }
  stereoCanvas.setAttribute('width', canvasWidth);
  if (height !== undefined) {
    canvasHeight = height;
  } else {
    canvasHeight = element.clientHeight;
    canvasHeight = bbox.height;
  }
  stereoCanvas.setAttribute('height', canvasHeight);
  console.log(`Canvas size is ${canvasWidth} ${canvasHeight}`);
  */
  return stereoCanvas;
}

async function add3DViewer (element, left, right) {
  var scene = await init3DViewer(left, right);
  var width = scene.children[0].material.map.image.width;
  var height = scene.children[0].material.map.image.height;
  //element.dataset.width = width;
  //element.dataset.height = height;

  //var stereoCanvas = createCanvas(element, width, height);
  var stereoCanvas = createCanvas(element);

  const visibilityObserver = new IntersectionObserver(() => {
    if (element.clientWidth) {
      var multiplier = element.clientWidth / width;
      elementHeight = Math.floor(height * multiplier);
      elementWidth = element.clientWidth;
      element.dataset.width = elementWidth;
      element.dataset.height = elementHeight;
      element.style["height"] = elementHeight + "px";
      var canvas = element.querySelector('canvas');
      canvas.setAttribute('width', elementWidth);
      canvas.setAttribute('height', elementHeight);
      canvas.style["height"] = elementHeight + "px";

      console.log(`Tab activated, Element size is ${elementWidth} ${elementHeight}`);
    }
  });
  visibilityObserver.observe(element);

  var renderer = new THREE.WebGLRenderer({canvas: stereoCanvas, antialias: true});
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.xr.enabled = true;
  var as = (width * 2) / height
  //Aspect ratio is about .9:1
  var aspectRatio = height / width;
  var initialHeight = element.clientWidth * aspectRatio;

  console.log("Height: " + height + ", width: " + width + ", canvas height: " + initialHeight + " client width: " + element.clientWidth);

  stereoCanvas.style.aspectRatio = 'auto 1 / ' + aspectRatio;
  renderer.setSize(stereoCanvas.clientWidth, initialHeight, false);

  // TODO: Should we use component size instead?
  var camera = new THREE.PerspectiveCamera( 70, element.clientWidth / element.clientHeight, 1, 2000 );
  camera.layers.enable( 1 );

  const controls = new OrbitControls(camera, renderer.domElement);
  camera.position.set(0, 0, 0.1);
  controls.update();

  var button = VRButton.createButton(renderer);
  button.style.bottom = '30px';
  button.style.opacity = '.85';
  button.addEventListener("click", function(event) {
    var state;
    if (event.target.dataset.state) {
      state = event.target.dataset.state;
    } else {
      state = false;
    }
    if (!state) {
      renderer.setSize(window.innerWidth, window.innerHeight);
      window.scrollTo(0, 0);
      button.style.zIndex = 10000;
      button.style.position = "fixed";
      button.style.opacity = '.85';
      event.target.dataset.state = true;
    } else {
      button.style.opacity = '.85';
      button.style.position = "absolute";
      event.target.dataset.state = false;
    }
  });
  element.appendChild(button);

  renderer.setAnimationLoop( () => {
    renderer.render(scene, camera );
  });

  const resizeObserver = new ResizeObserver(() => {
    renderer.setSize(stereoCanvas.clientWidth, stereoCanvas.clientHeight);
    camera.aspect = stereoCanvas.clientWidth / stereoCanvas.clientHeight;
    camera.updateProjectionMatrix();
  });

  resizeObserver.observe(stereoCanvas);
  return renderer;
}

function addFullScreen(element, left, right) {
  function toggleScroll() {
    var body = document.querySelector("body");
    if (body.style["overflow"] === 'hidden') {
      body.style["overflow"] = "unset";
    } else {
      body.style["overflow"] = "hidden";
    }
  }

  function addButton(element, inactiveInner, activeInner) {
    var id = element.getAttribute('id');
    var button = document.createElement('button');
    button.innerHTML = inactiveInner;
    button.classList.add("fullscreen-button");
    button.setAttribute('id', id + '-button');
    button.addEventListener("click", function(event) {
      if (!element.classList.contains("active")) {
        button.innerHTML = activeInner;
        element.classList.add("active");
        toggleScroll();
        window.scrollTo(0, 0);
        button.style.zIndex = 10000;
        button.style.position = "fixed";
      } else {
        button.innerHTML = inactiveInner;
        element.classList.remove("active");
        toggleScroll();
        button.style.position = "absolute";
      }
    });
    element.appendChild(button);
    return button;
  }

  function init(element, left, right) {
    leftImg = document.createElement('img');
    leftImg.src = left;
    leftImg.classList.add("left-img");
    leftImg.classList.add("fullscreen-viewer-image");
    rightImg = document.createElement('img');
    rightImg.src = right;
    rightImg.classList.add("right-img");
    rightImg.classList.add("fullscreen-viewer-image");
    element.appendChild(leftImg);
    element.appendChild(rightImg);
  }

  init(element, left, right);
  element.classList.add("fullscreen-viewer");
  var button = addButton(element, 'Vollbild', 'Vollbild beenden');

}

window.addFullScreen = addFullScreen;
window.add3DViewer = add3DViewer;
