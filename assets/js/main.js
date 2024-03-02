import { addConsent } from './iframe-consent';
import { initMap } from './maps/osm-map.js';
import { fullscreen } from './fullscreen.js';

window.addConsent = addConsent;
window.initMap = initMap;

require('./3d.js');

import stickybits from 'stickybits'
window.stickybits = stickybits;

let mql = window.matchMedia('(max-width: 35em)');

//if (!mql.matches) {
  var sticky = stickybits('.header-menu', { useStickyClasses: true, stuckClass: "sticky-top"});
//}

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
