/* Shared theme logic. Load in <head> (no defer) so a saved choice is applied before first paint. */
(function(){
  var root=document.documentElement;
  try{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")root.dataset.theme=t}catch(e){}
  document.addEventListener("DOMContentLoaded",function(){
    var btn=document.getElementById("theme-toggle");
    if(!btn)return;
    var mq=window.matchMedia("(prefers-color-scheme: light)");
    function current(){return root.dataset.theme||(mq.matches?"light":"dark")}
    function sync(){
      var c=current();
      btn.dataset.mode=c;
      btn.setAttribute("aria-label","Switch to "+(c==="dark"?"light":"dark")+" mode");
    }
    btn.addEventListener("click",function(){
      var next=current()==="dark"?"light":"dark";
      root.dataset.theme=next;
      try{localStorage.setItem("theme",next)}catch(e){}
      sync();
    });
    if(mq.addEventListener)mq.addEventListener("change",sync);
    btn.hidden=false;
    sync();
  });
})();
