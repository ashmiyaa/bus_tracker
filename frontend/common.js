const STOPS=[["Vidhya Niketan School Ground","7:30"],["Pump Jn","7:35"],["Thottumugham","7:40"],["Kuttamassery","7:50"],["Marampilly","7:55"],["Manjappetty","8:00"],["Mudikkal","8:10"],["Perumbavoor","8:20"],["Pulluvazhy","8:30"],["Payipra","8:35"],["Ilahia Arts College","8:40"],["ICET","8:45"]];
const $=id=>document.getElementById(id);
const mn=t=>{const[a,b]=t.split(":");return +a*60+ +b};
const fmt=m=>{m=Math.round(m);const h=Math.floor(m/60),k=m%60;return(h>12?h-12:h)+":"+String(k).padStart(2,"0")+(h>=12?" PM":" AM")};
const nowMin=()=>{const d=new Date();return d.getHours()*60+d.getMinutes()+d.getSeconds()/60};
