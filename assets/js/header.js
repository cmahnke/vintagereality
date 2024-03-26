/*
window.addEventListener('DOMContentLoaded', function(e) {
  const menu = document.querySelector('#head.home .lazy-wrap');
  const duration = '0.3s';

  var lastTop;
  var toTop;
  var anim;
  if (menu) {
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (((lastTop / 100) * 85 > menu.getBoundingClientRect().top) || (menu.getBoundingClientRect().top > (lastTop / 100) * 115)) {
          toTop = menu.getBoundingClientRect().top;
          console.log("Break detected");
          clearInterval(anim);
          anim = setInterval(frame, 10);
        } else {
          //console.log(menu.getBoundingClientRect().top, lastTop);
          //console.log("-->", (menu.getBoundingClientRect().top / 100) * 85, (menu.getBoundingClientRect().top / 100) * 115)
        }


        lastTop = menu.getBoundingClientRect().top;
      }
    });
    resizeObserver.observe(menu);
  }
});
*/
/*
import 'scroll-timeline/dist/scroll-timeline';

window.addEventListener('DOMContentLoaded', function(e) {
  const header = document.querySelector('#head.home');
  const headerContainer = document.querySelector('#head.home .header-container');
  const logo = document.querySelector('#head.home .header-logo');
  const glasses = document.querySelector('#head.home .header-logo svg');
  const vintage = document.querySelector('#head.home .header-logo .header-logo-first');
  const reality = document.querySelector('#head.home .header-logo .header-logo-second');
  const menu = document.querySelector('#head.home .header-menu');

  if (header) {
    header.animate({
      backgroundSize: ["100% 100%", "100% 400%"],
    	height: ['100vh', '6rem'],
    	fontSize: ['calc(4vw + 1em)', 'calc(1vw + 1em)'],
      zIndex: ['0', '10']
    },
    {
    	fill: "both",
    	timeline: new ScrollTimeline({
    		source: document.documentElement,
    	}),
    	rangeStart: '0',
    	rangeEnd: '90vh',
    });

    headerContainer.animate({
    	height: ['100vh', '6rem'],
      //left: ['50%', '0%'],
      //transform: ['-50%', '0%']
    },
    {
    	fill: "both",
    	timeline: new ScrollTimeline({
    		source: document.documentElement,
    	}),
    	rangeStart: '0',
    	rangeEnd: '90vh',
    });

    logo.animate({
      height: ["calc(100vh - 2rem)", "6rem"],
      left: ["50%", "0%"],
      transform: ["translate(-50%)", ""]
    },
    {
      fill: "both",
      timeline: new ScrollTimeline({
        source: document.documentElement,
      }),
      rangeStart: '0',
      rangeEnd: '90vh',
    });

    glasses.animate({
      opacity: [".7", ".0"],
      transform: ["translate(-50%, -50%) scale(3) rotate(25deg)", "translate(-50%, -50%) scale(1) rotate(0deg)"],
      top: ["50%", "0%"]
    },
    {
      fill: "both",
      timeline: new ScrollTimeline({
        source: document.documentElement,
      }),
      rangeStart: '0',
      rangeEnd: '90vh',
    });

    vintage.animate({
      height: ["calc(50vh - 4rem)", "6rem"],
      width: ["70em", "16em"]
    },
    {
      fill: "both",
      timeline: new ScrollTimeline({
        source: document.documentElement,
      }),
      rangeStart: '0',
      rangeEnd: '90vh',
    });


    reality.animate({
      height: ["calc(50vh - 4rem)", "6rem"],
      top: ["calc(100vh / 2 - 4rem)", "0"],
    },
    {
      fill: "both",
      timeline: new ScrollTimeline({
        source: document.documentElement,
      }),
      rangeStart: '0',
      rangeEnd: '90vh',
    });


    menu.animate({
      width: ["100%", "60%"],
    },
    {
      fill: "both",
      timeline: new ScrollTimeline({
        source: document.documentElement,
      }),
      rangeStart: '0',
      rangeEnd: '90vh',
    });
  }
});
*/
