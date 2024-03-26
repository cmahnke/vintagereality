import { addConsent } from './iframe-consent';
import { initMap } from './maps/osm-map.js';
import { fullscreen } from './fullscreen.js';

window.addConsent = addConsent;
window.initMap = initMap;

require('./3d.js');
require('./header.js');

window.addEventListener("mouseover", turnGlases);

function turnGlases(event){
  const divisor = 50;
  document.querySelectorAll('.list-item .preview').forEach((item) => {
    if (window.innerWidth > window.innerHeight) {
      var divisorY = divisor;
      var divisorX = (window.innerWidth / window.innerHeight) * divisor;
    } else {
      var divisorX = divisor;
      var divisorY = (window.innerHeight / window.innerWidth) * divisor;
    }
    const x = ((window.innerWidth / 2 - event.clientX) * -1) / divisorX;
    const y = (window.innerHeight / 2 - event.clientY) / divisorY;
    const transform = `perspective(50em) rotateY(${x}deg) rotateX(${y}deg)`;
    //console.log(x, y, transform);
    item.style.transform = transform;
  });
}

const resizeIFrame = (mutationList, observer) => {
  for (const mutation of mutationList) {
    if (mutation.type === "childList") {
      mutation.addedNodes.forEach((node) => {
        if (node.classList && node.classList.contains('map-wrapper')) {
          node.parentElement.style.height = node.getBoundingClientRect().height;
        }
      });
    }
  }
}

window.addEventListener('DOMContentLoaded', function(e) {
  var iframes = document.querySelectorAll(".iframe-content");
    for( var i = 0; i < iframes.length; i++) {
      const config = { attributes: false, childList: true, subtree: false };
      iframes[i].height = iframes[i].parentElement.offsetHeight
      const observer = new MutationObserver(resizeIFrame);
      observer.observe(iframes[i], config);
    }
});
