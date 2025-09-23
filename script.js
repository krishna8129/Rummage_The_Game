(function(){
    let a=0,b=[],c=document.getElementById("grid"),d=document.getElementById("score");
    for(let i=0;i<100;i++){
        let e=document.createElement("div");
        e.className="cell";
        e.dataset.idx=i;
        c.appendChild(e);
        b.push(e);
    }
    let f=new Set();
    while(f.size<15)f.add(Math.floor(Math.random()*100));
    b.forEach(g=>{
        g.onclick=function(){
            let h=parseInt(this.dataset.idx);
            if(f.has(h)&&!this.classList.contains("found")){
                this.classList.add("found");
                a+=1;
                d.textContent=a;
                if(a===15){
                    alert("Rummage Complete");
                }
            }
        }
    });
})();
