import './3d';

window.addEventListener("mouseover", turnGlases);

function turnGlases(event: MouseEvent): void {
  const divisor = 50;
  document.querySelectorAll<HTMLElement>('.list-item .preview').forEach((item) => {
    let divisorX: number;
    let divisorY: number;
    if (window.innerWidth > window.innerHeight) {
      divisorY = divisor;
      divisorX = (window.innerWidth / window.innerHeight) * divisor;
    } else {
      divisorX = divisor;
      divisorY = (window.innerHeight / window.innerWidth) * divisor;
    }
    const x = ((window.innerWidth / 2 - event.clientX) * -1) / divisorX;
    const y = (window.innerHeight / 2 - event.clientY) / divisorY;
    const transform = `perspective(50em) rotateY(${x}deg) rotateX(${y}deg)`;
    //console.log(x, y, transform);
    item.style.transform = transform;
  });
}

const resizeIFrame = (mutationList: MutationRecord[], _observer: MutationObserver) => {
  for (const mutation of mutationList) {
    if (mutation.type === "childList") {
      mutation.addedNodes.forEach((node) => {
        if (node instanceof Element && node.classList.contains('map-wrapper')) {
          node.parentElement!.style.height = node.getBoundingClientRect().height + 'px';
        }
      });
    }
  }
}

window.addEventListener('DOMContentLoaded', function() {
  const iframes = document.querySelectorAll(".iframe-content");
  for (let i = 0; i < iframes.length; i++) {
    const iframe = iframes[i] as HTMLIFrameElement;
    const config: MutationObserverInit = { attributes: false, childList: true, subtree: false };
    iframe.height = String(iframe.parentElement!.offsetHeight);
    const observer = new MutationObserver(resizeIFrame);
    observer.observe(iframe, config);
  }
});
