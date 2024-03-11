import 'scroll-timeline/dist/scroll-timeline';

window.addEventListener('DOMContentLoaded', function(e) {
  const header = document.querySelector('#head');
  if (header.querySelector('.header-logo.big')) {
    header.style.position = 'fixed';
    header.style.top = 0;
    /*
    header.animate(
      { transform: ['translateY(0)', 'translateY(100px)']},
      { fill: 'both',
        timeline: new ScrollTimeline({
          source: document.documentElement,
        }),
        rangeStart: new CSSUnitValue(0, 'px'),
        rangeEnd: new CSSUnitValue(200, 'px'),
      }
    );
    */
  }

});
