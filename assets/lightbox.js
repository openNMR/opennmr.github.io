/* Click or tap any <button data-zoom> that contains screenshots to open the visible one full size. */
(function(){
  var dlg;
  function build(){
    dlg=document.createElement("dialog");
    dlg.className="lightbox";
    dlg.setAttribute("aria-label","Enlarged screenshot");
    dlg.innerHTML='<button type="button" class="lb-close" aria-label="Close">\u00d7</button><div class="lb-scroll"><img alt=""></div>';
    document.body.appendChild(dlg);
    dlg.addEventListener("click",function(e){
      if(e.target===dlg||e.target.classList.contains("lb-scroll"))dlg.close();
    });
    dlg.querySelector(".lb-close").addEventListener("click",function(){dlg.close()});
  }
  document.addEventListener("click",function(e){
    var b=e.target.closest("[data-zoom]");
    if(!b||!window.HTMLDialogElement)return;
    var imgs=b.querySelectorAll("img"),shown=null;
    for(var i=0;i<imgs.length;i++){if(imgs[i].offsetParent!==null){shown=imgs[i];break}}
    if(!shown)return;
    if(!dlg)build();
    var big=dlg.querySelector("img");
    big.src=shown.currentSrc||shown.src;
    big.alt=shown.alt;
    dlg.showModal();
  });
})();
